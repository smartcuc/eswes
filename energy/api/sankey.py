###########################
# energy/services/sankey.py
###########################

from devices.models import Device


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
    # Linke Seite
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
    # Mitte
    #

    add_node(
        "sum",
        "Σ Energie",
        "sum",
    )

    #
    # Producer -> Sum
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
    # Consumer
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

        node_id = f"device_{device.id}"

        add_node(
            node_id,
            config.display_name(),
            "consumer",
        )

        consumers.append(node_id)

    #
    # Sum -> Consumer
    #
    # Noch Dummy-Werte.
    # Richtige Verteilung kommt später.
    #

    for consumer in consumers:

        links.append({
            "source": "sum",
            "target": consumer,
            "value": 1,
        })

    return {
        "nodes": nodes,
        "links": links,
    }
