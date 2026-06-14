###################
# providers/base.py
###################

from typing import Dict, Optional


SignalDict = Dict[str, Optional[float]]
ProviderData = Dict[str, SignalDict]


class BaseProvider:
    """
    Base class for all energy providers.
    Providers return structured, partial energy data.
    """

    id: str = "base"
    label: str = "Base Provider"
    category: str = "system"  # system | device | meter

    def fetch_signals(self, user) -> ProviderData:
        return {
            "grid": {
                "import": None,
                "export": None,
            },
            "load": {
                "consumption": None,
            },
            "pv": {
                "production": None,
                "power": None,
            },
            "battery": {
                "charge": None,
                "discharge": None,
                "soc": None,
            },
        }
