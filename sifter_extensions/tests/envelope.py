from email.message import Message
import email.utils
from typing import (
    TYPE_CHECKING,
    cast,
    Text,
    List,
    Optional,
    Union,
    SupportsInt
)

from sifter.validators.tag import Tag, Comparator, MatchType
import sifter.grammar
from sifter.grammar.test import Test
import sifter.grammar.string
from sifter.grammar.string import expand_variables
from sifter.validators.stringlist import StringList
from sifter.grammar.state import EvaluationState

if TYPE_CHECKING:
    from sifter.grammar.tag import Tag as TagGrammar
    from sifter.grammar.string import String

# Maps Sieve envelope parts to email headers (proxy for SMTP envelope)
ENVELOPE_MAP = {
    'from': ['Return-Path'],
    'to': ['Delivered-To', 'X-Original-To'],
}


# RFC 5228 section 5.4
class TestEnvelope(Test):

    HANDLER_ID = 'ENVELOPE'
    EXTENSION_NAME = 'envelope'
    TAGGED_ARGS = {
        'comparator': Comparator(),
        'match_type': MatchType(),
        'address_part': Tag(('LOCALPART', 'DOMAIN', 'ALL', 'USER', 'DETAIL')),
    }
    POSITIONAL_ARGS = [
        StringList(),
        StringList(),
    ]

    def __init__(
        self,
        arguments: Optional[List[Union['TagGrammar', SupportsInt, List[Union[Text, 'String']]]]] = None,
        tests: Optional[List['Test']] = None
    ) -> None:
        super().__init__(arguments, tests)

        self.envelope_parts = self.positional_args[0]
        self.keylist = self.positional_args[1]
        self.match_type = self.comparator = self.address_part = None
        if 'comparator' in self.tagged_args:
            self.comparator = self.tagged_args['comparator'][1][0]  # type: ignore
        if 'match_type' in self.tagged_args:
            self.match_type = self.tagged_args['match_type'][0]
        if 'address_part' in self.tagged_args:
            self.address_part = self.tagged_args['address_part'][0]

    def evaluate(self, message: Message, state: EvaluationState) -> bool:
        state.check_required_extension('envelope', 'ENVELOPE')

        if not isinstance(self.envelope_parts, list):
            raise ValueError('TestEnvelope.envelope_parts is not a list')
        if not isinstance(self.keylist, list):
            raise ValueError('TestEnvelope.keylist is not a list')

        for part in self.envelope_parts:
            part = expand_variables(part, state).lower()
            header_names = ENVELOPE_MAP.get(part, [part])

            header_values: List[Text] = []
            for header in header_names:
                header_values.extend(message.get_all(header, []))

            addresses: List[Text] = []
            for msg_address in email.utils.getaddresses(header_values):
                if msg_address[1] != '':
                    addresses.append(
                        sifter.grammar.string.address_part(
                            msg_address[1],
                            cast(Text, self.address_part)
                        )
                    )

            for address in addresses:
                for key in self.keylist:
                    key = expand_variables(key, state)
                    if sifter.grammar.string.compare(
                        address,
                        key,
                        state,
                        self.comparator,
                        cast(Text, self.match_type)
                    ):
                        return True
        return False
