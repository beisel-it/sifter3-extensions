"""
RFC 5490 mailbox extension for sifter3.

Implements:
- mailboxexists <string-list>  → test if mailboxes exist (configurable via state)
- fileinto :create             → patch CommandFileInto to accept :create tag

For testing, mailboxexists defaults to True (all mailboxes exist).
Override via state.mailboxes = {"INBOX.Work", "INBOX.Sent"} to be explicit.
"""
from email.message import Message
from typing import Text

from sifter.grammar.test import Test
from sifter.grammar.string import expand_variables
from sifter.grammar.state import EvaluationState
from sifter.validators.stringlist import StringList
from sifter.validators.tag import Tag
from sifter.grammar.sieveobject import SieveObject


class MailboxExtension(SieveObject):
    HANDLER_ID = 'MAILBOX'
    EXTENSION_NAME = 'mailbox'

    @classmethod
    def handler_type(cls) -> Text:
        return 'extension'

    @classmethod
    def handler_id(cls) -> Text:
        return cls.EXTENSION_NAME


class TestMailboxExists(Test):
    """
    mailboxexists <mailbox-names: string-list>

    Returns True if all listed mailboxes exist.
    In test mode: checks state.mailboxes if set, otherwise defaults to True.
    """
    HANDLER_ID = 'MAILBOXEXISTS'
    EXTENSION_NAME = 'mailbox'
    POSITIONAL_ARGS = [StringList()]

    def evaluate(self, message: Message, state: EvaluationState) -> bool:
        state.check_required_extension('mailbox', 'MAILBOXEXISTS')

        mailboxes = self.positional_args[0]
        if not isinstance(mailboxes, list):
            mailboxes = [mailboxes]

        # If state has an explicit mailboxes set, check against it.
        # Otherwise default to True (optimistic: assume all exist).
        known = getattr(state, 'mailboxes', None)
        if known is None:
            return True

        for mb in mailboxes:
            mb = expand_variables(mb, state)
            if mb not in known:
                return False
        return True


# --- Patch CommandFileInto to accept :create tag ---
import sifter.commands.fileinto as _fileinto_mod

_OrigFileInto = _fileinto_mod.CommandFileInto
_orig_fi_init = _OrigFileInto.__init__
_orig_fi_evaluate = _OrigFileInto.evaluate


def _fi_patched_init(self, arguments=None, tests=None, **kwargs):
    create = False
    filtered = []
    if arguments:
        for arg in arguments:
            if str(arg).upper().lstrip(':') == 'CREATE':
                create = True
            else:
                filtered.append(arg)
    _orig_fi_init(self, filtered if create else arguments, tests, **kwargs)
    self._create = create


def _fi_patched_evaluate(self, message: Message, state: EvaluationState) -> None:
    _orig_fi_evaluate(self, message, state)
    # :create is a server-side hint; no action needed in test evaluation


try:
    existing = _OrigFileInto.TAGGED_ARGS or {}
    _OrigFileInto.TAGGED_ARGS = {**existing, 'create': Tag(('CREATE',))}
    _OrigFileInto.__init__ = _fi_patched_init
    _OrigFileInto.evaluate = _fi_patched_evaluate
except Exception as e:
    import warnings
    warnings.warn(f"mailbox extension patch failed: {e}")
