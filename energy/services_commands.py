#############################
# energy/services_commands.py
#############################


from energy.models import Device, DeviceCommand


def queue_command(
    device: Device, command: str, payload: dict, dedup_key: str = ""
) -> DeviceCommand:
    if dedup_key:
        existing = DeviceCommand.objects.filter(
            dedup_key=dedup_key, status__in=["queued", "sent"]
        ).first()
        if existing:
            return existing

    return DeviceCommand.objects.create(
        device=device,
        command=command,
        payload=payload,
        dedup_key=dedup_key or "",
        status="queued",
    )
