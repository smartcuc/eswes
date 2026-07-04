###########################
# energy/services/sankey.py
###########################

from devices.models import Device
from devices.models import DeviceMetric
from energy.services.signals import get_ems_signals



def get_latest_power(device):

    metric = (
        DeviceMetric.objects
        .filter(
            device=device,
            metric_key="value",
        )
        .order_by("-timestamp")
        .first()
    )

    return metric.value if metric else 0



def get_device_by_identifier(devices, identifier):

    for device in devices:
        if device.identifier == identifier:
            return device

    return None


def build_live_sankey(user, flow):

    devices = (
        Device.objects
        .filter(
            home__user=user,
            configured=True,
            active=True,
            pending_delete=False,
        )
        .select_related(
            "config",
            "config__role",
            "config__floor",
            "config__room",
        )
    )

    grid_device = get_device_by_identifier(
        devices,
        "grid_total_power",
    )

    battery_device = get_device_by_identifier(
        devices,
        "battery_power",
    )

    total_device = get_device_by_identifier(
        devices,
        "total_active_power",
    )

    signals = get_ems_signals(user)

    grid_power = (
        signals["grid"]["import"]
        or 0
    )

    battery_power = (
        signals["battery"]["discharge"]
        or 0
    )

    total_consumption = (
        signals["load"]["consumption"]
        or 0
    )


    nodes = []
    links = []

    known_nodes = set()

    def add_node(node_id, label, node_type):

        if node_id in known_nodes:
            return

        nodes.append({
            "id": node_id,
            "label": label,
            "type": node_type,
        })

        known_nodes.add(node_id)

    #
    # PRODUCER
    #

    add_node(
        "pv",
        "PV",
        "producer",
    )

    add_node(
        "battery",
        "Batterie",
        "producer",
    )

    add_node(
        "grid",
        "Netz",
        "producer",
    )

    #
    # SUM
    #

    add_node(
        "sum",
        "Σ Energie",
        "sum",
    )

    #
    # CONSUMER
    #

    consumers = []

    for device in devices:

        config = getattr(device, "config", None)

        if not config:
            continue

        role = config.role

        if not role:
            continue

        if role.key != "consumer":
            continue

        if config.measurement_type != "power":
            continue

        node_id = f"device_{device.id}"
        
        label = (
            config.name
            or getattr(device, "name", None)
            or device.identifier
        )

        power = get_latest_power(device)

        if power <= 0:
            continue

        add_node(
            node_id,
            label,
            "consumer",
        )
        
        consumers.append({
            "node_id": node_id,
            "floor": config.floor,
            "room": config.room,
            "power": power,
        })

    #
    # SUM -> FLOOR -> ROOM -> DEVICE
    #
    tracked_consumption = 0

    for consumer in consumers:

        current_target = "sum"

        floor = consumer["floor"]

        if floor:

            floor_id = f"floor_{floor.id}"

            add_node(
                floor_id,
                floor.name,
                "floor",
            )

            links.append({
                "source": "sum",
                "target": floor_id,
                "value": consumer["power"],
            })

            current_target = floor_id

        room = consumer["room"]

        if room:

            room_id = f"room_{room.id}"

            add_node(
                room_id,
                room.name,
                "room",
            )

            links.append({
                "source": current_target,
                "target": room_id,
                "value": consumer["power"],
            })

            current_target = room_id

        links.append({
            "source": current_target,
            "target": consumer["node_id"],
            "value": consumer["power"],
        })

        tracked_consumption += consumer["power"]

    links.append({
            "source": "pv",
            "target": "sum",
            "value": flow["pv_to_load"],
        })

    if battery_power > 0:

        links.append({
            "source": "battery",
            "target": "sum",
            "value": flow["battery_to_load"],
        })

    if grid_power > 0:

        links.append({
            "source": "grid",
            "target": "sum",
            "value": flow["grid_to_load"],
        })

    
    untracked = max(
        total_consumption - tracked_consumption,
        0,
    )  
    
    if untracked > 0:

        add_node(
            "untracked",
            "Nicht erfasst",
            "consumer",
        )

        links.append({
            "source": "sum",
            "target": "untracked",
            "value": untracked,
        })


    if tracked_consumption > total_consumption:
        tracked_consumption = total_consumption

    return {
            "nodes": nodes,
            "links": links,
        }
