##############################################
# integrations/services/energy_flow_service.py
##############################################

from integrations.models import InboundWebhookEvent


class EnergyFlowService:

    @staticmethod
    def get_energy_flow(tenant_slug: str):
        latest = (
            InboundWebhookEvent.objects
            .filter(tenant__slug=tenant_slug)
            .order_by("-received_at")
            .first()
        )

        # ✅ Fallback
        if not latest or not latest.payload:
            return EnergyFlowService.get_demo_flow()

        payload = latest.payload
        measurements = payload.get("measurements", [])

        producers = []
        consumers = []

        for m in measurements:
            value = m.get("value", 0)
            meter_id = m.get("meter_id")

            if value > 0:
                producers.append({"id": meter_id, "value": value})
            elif value < 0:
                consumers.append({"id": meter_id, "value": abs(value)})

        if not producers or not consumers:
            return EnergyFlowService.get_demo_flow()

        nodes = []
        flows = []

        # Positionen
        y_step = 80

        # Producer Nodes (links)
        for i, p in enumerate(producers):
            nodes.append({
                "id": p["id"],
                "name": p["id"],
                "type": "solar",
                "x": 100,
                "y": 150 + i * y_step
            })

        # Consumer Nodes (rechts)
        for i, c in enumerate(consumers):
            nodes.append({
                "id": c["id"],
                "name": c["id"],
                "type": "home",
                "x": 400,
                "y": 150 + i * y_step
            })

        # ✅ Grid + Battery (immer vorhanden)
        nodes.append({
            "id": "grid",
            "name": "Netz",
            "type": "grid",
            "x": 250,
            "y": 60
        })

        nodes.append({
            "id": "battery",
            "name": "Batterie",
            "type": "battery",
            "x": 250,
            "y": 320
        })

        total_production = sum(p["value"] for p in producers)
        total_consumption = sum(c["value"] for c in consumers)

        # 🔥 1. Producer → Consumer Verteilung
        for p in producers:
            for c in consumers:
                share = min(p["value"], c["value"])

                if share <= 0:
                    continue

                flows.append({
                    "id": f"{p['id']}-{c['id']}",
                    "from": p["id"],
                    "to": c["id"],
                    "value": round(share, 2),
                    "unit": "kWh",
                    "color": "#16a34a",
                    "path": "M100,200 Q250,150 400,200",
                })

                p["value"] -= share
                c["value"] -= share

        # 🔥 2. Überschuss → Batterie / Netz
        if total_production > total_consumption:
            surplus = total_production - total_consumption

            flows.append({
                "id": "solar-battery",
                "from": producers[0]["id"],
                "to": "battery",
                "value": round(surplus, 2),
                "unit": "kWh",
                "color": "#10b981",
                "path": "M100,200 Q200,300 250,320",
            })

        # 🔥 3. Defizit → Netz
        elif total_consumption > total_production:
            deficit = total_consumption - total_production

            flows.append({
                "id": "grid-home",
                "from": "grid",
                "to": consumers[0]["id"],
                "value": round(deficit, 2),
                "unit": "kWh",
                "color": "#ef4444",
                "path": "M250,60 Q320,120 400,200",
            })

        return {
            "nodes": nodes,
            "flows": flows,
        }

    @staticmethod
    def get_demo_flow():
        return {
            "nodes": [
                {"id": "solar", "name": "Solaranlage", "type": "solar", "x": 100, "y": 200},
                {"id": "home1", "name": "Haushalt A", "type": "home", "x": 400, "y": 150},
                {"id": "home2", "name": "Haushalt B", "type": "home", "x": 400, "y": 250},
                {"id": "grid", "name": "Netz", "type": "grid", "x": 250, "y": 60},
                {"id": "battery", "name": "Batterie", "type": "battery", "x": 250, "y": 320},
            ],
            "flows": [
                {
                    "id": "demo1",
                    "from": "solar",
                    "to": "home1",
                    "value": 5,
                    "unit": "kWh",
                    "color": "#f97316",
                    "path": "M100,200 Q250,150 400,150",
                },
                {
                    "id": "demo2",
                    "from": "solar",
                    "to": "home2",
                    "value": 3,
                    "unit": "kWh",
                    "color": "#6366f1",
                    "path": "M100,200 Q250,250 400,250",
                },
            ],
        }
    