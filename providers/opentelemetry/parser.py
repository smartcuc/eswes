###################################
# providers/opentelemetry/parser.py
###################################


def get_attr(attributes, key):

    for attr in attributes:

        if attr.get("key") != key:
            continue

        value = attr.get("value", {})

        return (
            value.get("stringValue")
            or value.get("doubleValue")
            or value.get("intValue")
            or value.get("boolValue")
        )

    return None
