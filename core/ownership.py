##################
# core/ownership.py
###################

from django.db import models
from django.db.models import Q

"""
    Owner Pattern:
      - Genau eines von owner_user / owner_member ist gesetzt
      - owner_user => tenant muss NULL sein (Standalone)
      - owner_member => tenant muss gesetzt sein (Tenant-Kontext)

    prefix muss pro Model eindeutig sein (z.B. 'energyasset', 'device', 'location').
"""


def owner_xor_constraints(prefix: str):
    return [
        models.CheckConstraint(
            name=f"{prefix}_owner_xor",
            condition=(
                (Q(owner_user__isnull=False) & Q(owner_membership__isnull=True))
                | (Q(owner_user__isnull=True) & Q(owner_membership__isnull=False))
            ),
        ),
        models.CheckConstraint(
            name=f"{prefix}_user_requires_no_tenant",
            condition=(Q(owner_user__isnull=True) | Q(tenant__isnull=True)),
        ),
        models.CheckConstraint(
            name=f"{prefix}_membership_requires_tenant",
            condition=(Q(owner_membership__isnull=True) | Q(tenant__isnull=False)),
        ),
    ]
