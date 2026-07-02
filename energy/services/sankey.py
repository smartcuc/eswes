###########################
# energy/services/sankey.py
###########################

from devices.models import Device
from devices.models import DeviceMetric


def get_latest_power(device):

    metric = (
        DeviceMetric.objects
        .filter(
            device=device,
            metric_key="power",
        )
        .order_by("-timestamp")
        .first()
    )

    return metric.value if metric else 0


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
    # PRODUCER -> SUM
    #

    if flow.get("pv_to_load", 0) > 0:

        links.append({
            "source": "pv",
            "target": "sum",
            "value": flow["pv_to_load"],
        })

    if flow.get("battery_to_load", 0) > 0:

        links.append({
            "source": "battery",
            "target": "sum",
            "value": flow["battery_to_load"],
        })

    if flow.get("grid_to_load", 0) > 0:

        links.append({
            "source": "grid",
            "target": "sum",
            "value": flow["grid_to_load"],
        })

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

        add_node(
            node_id,
            label,
            "consumer",
        )

        consumers.append({
            "node_id": node_id,
            "floor": config.floor,
            "room": config.room,
            "power": 1,  # später echte Leistung
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
                "value": 1,
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
                "value": 1,
            })

            current_target = room_id

        links.append({
            "source": current_target,
            "target": consumer["node_id"],
            "value": consumer["power"],
        })

        tracked_consumption += consumer["power"]

#
# TEMPORÄR
# solange flow noch leer ist
#

    #if not links:

    links.append({
            "source": "pv",
            "target": "sum",
            "value": 3000,
        })

    links.append({
            "source": "battery",
            "target": "sum",
            "value": 1000,
        })

    links.append({
            "source": "grid",
            "target": "sum",
            "value": 500,
        })
    
    total_input = 4500
    total_input = (

    flow.get("pv_to_load", 0)
    + flow.get("battery_to_load", 0)
    + flow.get("grid_to_load", 0)
    )
    
    untracked = max(
        total_input - tracked_consumption,
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

    return {
            "nodes": nodes,
            "links": links,
        }



    # return {
    #     "nodes": [
    #         {
    #             "id": "pv",
    #             "label": "PV",
    #             "type": "producer",
    #         },
    #         {
    #             "id": "battery",
    #             "label": "Batterie",
    #             "type": "producer",
    #         },
    #         {
    #             "id": "grid",
    #             "label": "Netz",
    #             "type": "producer",
    #         },
    #         {
    #             "id": "sum",
    #             "label": "Σ Energie",
    #             "type": "sum",
    #         },
    #     ],
    #     "links": [
    #         {
    #             "source": "pv",
    #             "target": "sum",
    #             "value": flow["pv_to_load"],
    #         },
    #         {
    #             "source": "battery",
    #             "target": "sum",
    #             "value": flow["battery_to_load"],
    #         },
    #         {
    #             "source": "grid",
    #             "target": "sum",
    #             "value": flow["grid_to_load"],
    #         },
    #     ],
    # }