from .generic import GenericParser
from .shelly import ShellyParser
from .iobroker import IoBrokerParser


PARSERS = {
    "generic": GenericParser,
    "shelly": ShellyParser,
    "iobroker": IoBrokerParser,
}


def get_parser(slug):
    parser_cls = PARSERS.get(
        slug,
        GenericParser,
    )

    return parser_cls()
