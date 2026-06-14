#######################
# providers/registry.py
#######################

from .tibber import TibberProvider
from .sungrow import SungrowProvider
from .device import DeviceProvider


PROVIDERS = {
    TibberProvider.id: TibberProvider(),
    SungrowProvider.id: SungrowProvider(),
    DeviceProvider.id: DeviceProvider(),
}


def get_provider(provider_id: str):
    return PROVIDERS.get(provider_id)
