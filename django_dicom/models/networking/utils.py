"""
Utilities for the networking module.
"""

from pynetdicom import AllStoragePresentationContexts

MAX_PORT_NUMBER = 65535
"""
Maximal possible port number.
"""

UID_MAX_LENGTH = 64
"""
Maximal presentation context UID length.
"""

PRESENTATION_CONTEXTS = sorted(
    [
        (str(context.abstract_syntax), context.abstract_syntax.name)
        for context in AllStoragePresentationContexts
    ],
    key=lambda choice: choice[1],
)
"""
Tuples of presentation context UIDs and string representations.
"""
