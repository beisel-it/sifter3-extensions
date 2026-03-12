"""
RFC 5233 subaddress extension for sifter3.

Adds :user and :detail address-parts to address/envelope tests.
Monkey-patches sifter.grammar.string.address_part AND all modules
that imported it directly.
"""
import sifter.grammar.string
import sifter.tests.address
from sifter.validators.tag import Tag
from sifter.grammar.sieveobject import SieveObject
from typing import Text, Optional

_original_address_part = sifter.grammar.string.address_part


def _patched_address_part(address: Text, part: Optional[Text] = None) -> Text:
    if part is None:
        part = 'ALL'
    part_upper = str(part).lstrip(":").upper()
    if part_upper == 'USER':
        return address.rsplit('@', 1)[0].split('+', 1)[0]
    if part_upper == 'DETAIL':
        localpart = address.rsplit('@', 1)[0]
        parts = localpart.split('+', 1)
        return parts[1] if len(parts) > 1 else ''
    return _original_address_part(address, part)


# Patch the module-level function
sifter.grammar.string.address_part = _patched_address_part

# Also patch the direct import in sifter.tests.address (and our envelope module)
sifter.tests.address.address_part = _patched_address_part  # type: ignore

# Patch via sifter.grammar.string module reference used in address.py evaluate()
import sifter.grammar
sifter.grammar.string.address_part = _patched_address_part

# Extend the address_part Tag validator to accept USER/DETAIL
try:
    sifter.tests.address.TestAddress.TAGGED_ARGS['address_part'] = Tag(
        ('LOCALPART', 'DOMAIN', 'ALL', 'USER', 'DETAIL')
    )
except (AttributeError, KeyError):
    pass


class SubaddressExtension(SieveObject):
    """Marker class to register the subaddress extension."""

    HANDLER_ID = 'SUBADDRESS'
    EXTENSION_NAME = 'subaddress'

    @classmethod
    def handler_type(cls) -> Text:
        return 'extension'

    @classmethod
    def handler_id(cls) -> Text:
        return cls.EXTENSION_NAME
