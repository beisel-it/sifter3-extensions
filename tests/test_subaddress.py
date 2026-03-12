import email
from sifter.grammar.command_list import CommandList
import sifter.parser as p


EML_SUBADDRESS = """\
Return-Path: <sender@example.com>
Delivered-To: florian+work@beisel.org
From: Sender <sender@example.com>
To: florian+work@beisel.org
Subject: Subaddress Test
Date: Thu, 12 Mar 2026 10:00:00 +0100
Message-ID: <sub-test@example.com>
MIME-Version: 1.0
Content-Type: text/plain

Test.
"""

EML_NO_SUBADDRESS = """\
Return-Path: <sender@example.com>
Delivered-To: florian@beisel.org
From: Sender <sender@example.com>
To: florian@beisel.org
Subject: No Subaddress
Date: Thu, 12 Mar 2026 10:00:00 +0100
Message-ID: <nosub-test@example.com>
MIME-Version: 1.0
Content-Type: text/plain

Test.
"""


def _run(script: str, eml: str):
    msg = email.message_from_string(eml)
    rules: CommandList = p.parse_string(script)
    return rules.evaluate(msg)


def test_envelope_detail_matches():
    script = 'require ["envelope","subaddress"]; if envelope :detail :matches "to" "*" { keep; }'
    actions = _run(script, EML_SUBADDRESS)
    assert actions is not None


def test_envelope_user_matches():
    script = 'require ["envelope","subaddress"]; if envelope :user :is "to" "florian" { keep; }'
    actions = _run(script, EML_SUBADDRESS)
    assert actions is not None


def test_envelope_detail_empty_no_subaddress():
    script = 'require ["envelope","subaddress"]; if envelope :detail :is "to" "" { keep; }'
    actions = _run(script, EML_NO_SUBADDRESS)
    assert actions is not None
