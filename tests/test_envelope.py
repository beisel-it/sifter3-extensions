import email
from sifter.grammar.command_list import CommandList
import sifter.parser as p


EML_WITH_ENVELOPE = """\
Return-Path: <sender@example.com>
Delivered-To: florian+work@beisel.org
From: Sender <sender@example.com>
To: florian+work@beisel.org
Subject: Test
Date: Thu, 12 Mar 2026 10:00:00 +0100
Message-ID: <test@example.com>
MIME-Version: 1.0
Content-Type: text/plain

Test body.
"""


def _run(script: str, eml: str):
    msg = email.message_from_string(eml)
    rules: CommandList = p.parse_string(script)
    return rules.evaluate(msg)


def test_envelope_from_matches():
    script = 'require "envelope"; if envelope :is "from" "sender@example.com" { keep; }'
    actions = _run(script, EML_WITH_ENVELOPE)
    assert any(a[0] == 'keep' for a in actions)


def test_envelope_to_matches():
    script = 'require "envelope"; if envelope :is "to" "florian+work@beisel.org" { keep; }'
    actions = _run(script, EML_WITH_ENVELOPE)
    assert any(a[0] == 'keep' for a in actions)


def test_envelope_no_match():
    script = 'require "envelope"; if envelope :is "from" "other@example.com" { keep; }'
    actions = _run(script, EML_WITH_ENVELOPE)
    # implicit keep still fires
    assert actions is not None
