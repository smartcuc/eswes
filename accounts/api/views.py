#######################
# accounts/api/views.py
#######################

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Tenant
from accounts.models import MagicLoginToken
from accounts.models import (
    UserSettings,
    UserProfile,
    TenantInvite,
    TenantMembership,
)

User = get_user_model()

class UserSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     # ✅ FALLBACK für nicht eingeloggte User
    #     if isinstance(request.user, AnonymousUser):
    #         return Response({
    #             "onboarding_step": "welcome",
    #             "usage_mode": "standalone"
    #         })

    #     # ✅ normaler User
    #     settings, _ = request.user.settings.__class__.objects.get_or_create(
    #         user=request.user
    #    )

    def get(self, request):
        settings, _ = UserSettings.objects.get_or_create(user=request.user)

        return Response({
            "onboarding_step": settings.onboarding_step,
            "usage_mode": settings.usage_mode,
        })


class UpdateOnboardingStepView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        step = request.data.get("step")

        settings, _ = UserSettings.objects.get_or_create(user=request.user)
        settings.onboarding_step = step
        settings.save()

        return Response({"status": "ok"})


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        user.first_name = data.get("first_name", "")
        user.last_name = data.get("last_name", "")
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)

        profile.street = data.get("street", "")
        profile.city = data.get("city", "")
        profile.postal_code = data.get("postal_code", "")
        profile.house_number = data.get("house_number", "")
        profile.country = data.get("country", "DE")
        profile.save()

        return Response({"status": "saved"})


class UserUsageModeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mode = request.data.get("usage_mode")

        if mode not in ["standalone", "tenant", "hybrid"]:
            return Response({"error": "invalid usage_mode"}, status=400)

        settings, _ = UserSettings.objects.get_or_create(user=request.user)
        settings.usage_mode = mode
        settings.save()

        return Response({"status": "saved"})
    

class UserLanguageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        lang = request.data.get("language")

        if lang not in ["de", "en"]:
            return Response({"error": "invalid language"}, status=400)

        settings = request.user.settings
        settings.language = lang
        settings.save()

        return Response({"status": "saved"})
    

class UseInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        invite = get_object_or_404(
            TenantInvite,
            token=token,
            is_active=True
        )

        if invite.used_count >= invite.max_uses:
            return Response({"error": "invite used"}, status=400)

        membership, created = TenantMembership.objects.get_or_create(
            user=request.user,
            tenant=invite.tenant,
            defaults={"role": invite.role}
        )

        invite.used_count += 1
        invite.save()

        return Response({
            "status": "joined",
            "tenant": invite.tenant.name,
            "role": membership.role
        })
    

class CreateInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant_id = request.data.get("tenant_id")
        role = request.data.get("role", "viewer")

        tenant = get_object_or_404(Tenant, id=tenant_id)

        is_admin = TenantMembership.objects.filter(
            user=request.user,
            tenant=tenant,
            role="admin",
            is_active=True
        ).exists()

        if not is_admin:
            return Response({"error": "not allowed"}, status=403)

        invite = TenantInvite.objects.create(
            tenant=tenant,
            role=role,
            max_uses=10
        )

        return Response({
            "link": f"{settings.FRONTEND_URL}/join?token={invite.token}",
            "token": str(invite.token)
        })

   
class MyTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = request.user.memberships.filter(is_active=True).first()

        if not membership:
            return Response({"tenant": None})

        tenant = membership.tenant

        members = TenantMembership.objects.filter(
            tenant=tenant,
            is_active=True
        ).select_related("user")

        invites = TenantInvite.objects.filter(tenant=tenant)

        return Response({
            "tenant": {
                "id": str(tenant.id),
                "name": tenant.name
            },
            "members": [
                {
                    "id": str(m.user.id),
                    "email": m.user.email,
                    "role": m.role
                }
                for m in members
            ],
            "invites": [
                {
                    "token": str(i.token),
                    "role": i.role,
                    "used": i.used_count
                }
                for i in invites
            ]
        })
    

class UpdateMemberRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant_id = request.data.get("tenant_id")
        user_id = request.data.get("user_id")
        new_role = request.data.get("role")

        if new_role not in ["admin", "editor", "viewer"]:
            return Response({"error": "invalid role"}, status=400)

        is_admin = TenantMembership.objects.filter(
            user=request.user,
            tenant_id=tenant_id,
            role="admin",
            is_active=True
        ).exists()

        if not is_admin:
            return Response({"error": "not allowed"}, status=403)

        membership = get_object_or_404(
            TenantMembership,
            tenant_id=tenant_id,
            user_id=user_id
        )

        membership.role = new_role
        membership.save()

        return Response({"status": "updated"})
    
    
class RemoveMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant_id = request.data.get("tenant_id")
        user_id = request.data.get("user_id")

        is_admin = TenantMembership.objects.filter(
            user=request.user,
            tenant_id=tenant_id,
            role="admin",
            is_active=True
        ).exists()

        if not is_admin:
            return Response({"error": "not allowed"}, status=403)

        membership = get_object_or_404(
            TenantMembership,
            tenant_id=tenant_id,
            user_id=user_id
        )

        membership.is_active = False
        membership.save()

        return Response({"status": "removed"})
    

class DeactivateInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        invite = get_object_or_404(TenantInvite, token=token)

        is_admin = TenantMembership.objects.filter(
            user=request.user,
            tenant=invite.tenant,
            role="admin",
            is_active=True
        ).exists()

        if not is_admin:
            return Response({"error": "not allowed"}, status=403)

        invite.is_active = False
        invite.save()

        return Response({"status": "deactivated"})


class RequestMagicLinkView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "email required"}, status=400)

        user, _ = User.objects.get_or_create(email=email)

        # ✅ Rate limit (optional aber gut)
        last_token = MagicLoginToken.objects.filter(user=user).order_by("-created_at").first()

        if last_token and last_token.created_at > timezone.now() - timedelta(seconds=60):
            return Response({"error": "too many requests"}, status=429)

        # ✅ alte Tokens löschen (optional aber sauber)
        MagicLoginToken.objects.filter(user=user, is_used=False).delete()

        token = MagicLoginToken.objects.create(user=user)

        link = f"{settings.FRONTEND_URL}/magic-login?token={token.token}"

        send_mail(
            subject="Dein Login-Link",
            message=f"Klicke hier zum Login:\n\n{link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"status": "sent"})


class MagicLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return Response({"error": "missing token"}, status=400)

        magic = get_object_or_404(
            MagicLoginToken,
            token=token,
            is_used=False
        )

        # ✅ Ablauf prüfen (falls du TTL eingebaut hast)
        if hasattr(magic, "is_expired") and magic.is_expired():
            return Response({"error": "link expired"}, status=400)

        # ✅ Token invalidieren
        magic.is_used = True
        magic.save()

        user = magic.user

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })