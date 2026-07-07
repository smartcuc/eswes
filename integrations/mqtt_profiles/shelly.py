class ShellyParser:

    def normalize(self, metrics):

        if "apower" in metrics:
            metrics["power"] = metrics.pop("apower")

        return metrics