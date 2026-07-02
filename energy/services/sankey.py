###########################
# energy/services/sankey.py
###########################


# energy/services/sankey.py

from devices.models import Device


def build_live_sankey(user, flow):
    """
    Erzeugt die Sankey-Struktur für das Live-Dashboard.

    Regeln:

    Links:
        - Producer
        - Batterie nur bei Entladung

    Mitte:
        - SUM
        - optional Etage
        - optional Raum

    Rechts:
        - Consumer
        - Batterie nur bei Netzladung
    """

    devices = (
        Device.objects
        .filter(
            home__user=user,
            active=True,
            pending_delete=False,
            configured=True,
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

    def add_node(node_id, label, kind):
        if node_id in known_nodes:
            return

        nodes.append({
            "id": node_id,
            "label": label,
            "type": kind,
        })

        known_nodes.add(node_id)

    #
    # zentrale Summe
    #

    add_node(
        "sum",
        "Σ Energie",
        "sum",
    )

    #
    # Producer links
    #

    producers = []

    #
    # Consumer rechts
    #

    consumers = []

    for device in devices:

        config = getattr(device, "config", None)

        if not config:
            continue

        role = config.role

        if not role:
            continue

        role_key = role.key

        node_id = f"device_{device.id}"

        add_node(
            node_id,
            config.display_name(),
            "device",
        )

        #
        # PRODUCER
        #

        if role_key == "producer":

            producers.append(node_id)

            links.append({
                "source": node_id,
                "target": "sum",
                "value": 1,
            })

        #
        # CONSUMER
        #

        elif role_key == "consumer":

            #
            # Nur Leistungswerte ins Sankey
            #

            if config.measurement_type not in [
                "power",
                "active_power",
            ]:
                continue

            consumers.append((device, node_id))

        #
        # BATTERY
        #

        elif role_key == "battery":

            #
            # V1:
            # später anhand aktueller Leistung
            # entscheiden:
            #
            #   Entladung -> links
            #   Netzladung -> rechts
            #
            pass

    #
    # Verbraucher-Seite
    #

    for device, node_id in consumers:

        config = device.config

        floor = config.floor
        room = config.room

        current_target = "sum"

        #
        # Etage
        #

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

        #
        # Raum
        #

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

        #
        # Gerät
        #

        links.append({
            "source": current_target,
            "target": node_id,
            "value": 1,
        })

    return {
        "nodes": nodes,
        "links": links,
    }
