"""
RFC 5703 MIME extension for sifter3 (partial).
Supports: header :mime :anychild :contenttype
"""
from email.message import Message
from typing import TYPE_CHECKING, Text, List, Optional, Union, SupportsInt

from sifter.grammar.test import Test
from sifter.grammar.string import compare as string_compare, expand_variables
from sifter.grammar.state import EvaluationState
from sifter.validators.stringlist import StringList
from sifter.validators.tag import Tag, Comparator, MatchType
from sifter.grammar.sieveobject import SieveObject

if TYPE_CHECKING:
    from sifter.grammar.tag import Tag as TagGrammar
    from sifter.grammar.string import String


class MimeExtension(SieveObject):
    HANDLER_ID = 'MIME'
    EXTENSION_NAME = 'mime'

    @classmethod
    def handler_type(cls) -> Text:
        return 'extension'

    @classmethod
    def handler_id(cls) -> Text:
        return cls.EXTENSION_NAME


# --- Patch TestHeader to understand :mime/:anychild/:contenttype ---
import sifter.tests.header as _header_mod

_OriginalTestHeader = _header_mod.TestHeader
_orig_init = _OriginalTestHeader.__init__
_orig_evaluate = _OriginalTestHeader.evaluate

_MIME_TAG_NAMES = {'MIME', 'ANYCHILD', 'CONTENTTYPE', 'TYPE', 'SUBTYPE', 'PARAM'}


def _patched_init(self, arguments=None, tests=None):
    mime_mode = False
    anychild = False
    contenttype = False
    filtered = []

    if arguments:
        for arg in arguments:
            s = str(arg).upper().lstrip(':')
            if s == 'MIME':
                mime_mode = True
            elif s == 'ANYCHILD':
                anychild = True
            elif s == 'CONTENTTYPE':
                contenttype = True
            elif s in ('TYPE', 'SUBTYPE', 'PARAM'):
                pass  # ignore unsupported sub-tags
            else:
                filtered.append(arg)

    _orig_init(self, filtered if mime_mode else arguments, tests)
    self._mime_mode = mime_mode
    self._anychild = anychild
    self._contenttype = contenttype


def _patched_evaluate(self, message: Message, state: EvaluationState) -> bool:
    if not getattr(self, '_mime_mode', False):
        return _orig_evaluate(self, message, state)

    state.check_required_extension('mime', 'MIME header tests')

    parts = list(message.walk())
    if not getattr(self, '_anychild', False):
        parts = parts[:1]

    for part in parts:
        if part.is_multipart():
            continue
        for header_name in self.headers:
            header_name = expand_variables(header_name, state)
            if getattr(self, '_contenttype', False):
                raw = part.get_content_type()
                for key in self.keylist:
                    key = expand_variables(key, state)
                    if string_compare(raw, key, state, self.comparator, self.match_type):
                        return True
            else:
                for value in (part.get_all(header_name) or []):
                    for key in self.keylist:
                        key = expand_variables(key, state)
                        if string_compare(value, key, state, self.comparator, self.match_type):
                            return True
    return False


try:
    _MIME_EXTRA = {
        'mime_tag':     Tag(('MIME',)),
        'anychild':     Tag(('ANYCHILD',)),
        'contenttype':  Tag(('CONTENTTYPE',)),
        'type_tag':     Tag(('TYPE',)),
        'subtype_tag':  Tag(('SUBTYPE',)),
        'param_tag':    Tag(('PARAM',)),
    }
    _OriginalTestHeader.TAGGED_ARGS = {**_OriginalTestHeader.TAGGED_ARGS, **_MIME_EXTRA}
    _OriginalTestHeader.__init__ = _patched_init
    _OriginalTestHeader.evaluate = _patched_evaluate
except Exception:
    pass
