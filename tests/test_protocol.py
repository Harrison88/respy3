"""Test the RESP3 protocol reader and writer.

Using the commands and responses defined in redis_commands.py,
feed the responses through a Resp3Reader instance and make sure the correct
object is returned.
"""

import pytest

from respy3 import protocol
from .redis_commands import redis_commands


@pytest.fixture
def reader():
    """A fresh instance of protocol.Resp3Reader for every test."""
    return protocol.Resp3Reader()


@pytest.mark.parametrize("command_data", redis_commands.values())
def test_command_responses(reader, command_data):
    """It parses responses correctly for each command."""
    print("About to test", command_data["response_value"])
    reader.feed(command_data["response"])
    result = reader.get_object()
    assert result == command_data["response_value"]
    assert reader.state_stack == []
    assert reader.new_state_stack == []


@pytest.mark.parametrize("command_data", redis_commands.values())
def test_command_responses_one_byte(reader, command_data):
    """It parses responses correctly, when data is fed one byte at a time."""
    print("About to test", command_data["response_value"], "one byte at a time")
    for b in (i.to_bytes(1, "little") for i in command_data["response"]):
        print("Getting object")
        result = reader.get_object()
        print("Got result:", result)
        print(reader.state_stack)
        assert result is reader.sentinel
        print("Feeding", b)
        reader.feed(b)

    print(reader.state_stack)
    result = reader.get_object()
    print("Got result:", result)
    assert result == command_data["response_value"]
    assert reader.state_stack == []
    assert reader.new_state_stack == []


@pytest.mark.parametrize("command_data", redis_commands.values())
def test_command_responses_two_bytes(reader, command_data):
    """It parses responses correctly, when data is fed two bytes at a time."""
    second = False
    for b in (i.to_bytes(1, "little") for i in command_data["response"]):
        if not second:
            reader.feed(b)
            second = True
        else:
            result = reader.get_object()
            assert result is reader.sentinel
            second = False
            reader.feed(b)

    result = reader.get_object()
    assert result == command_data["response_value"]
    assert reader.state_stack == []
    assert reader.new_state_stack == []


def test_boolean(reader):
    """It parses boolean responses correctly. # noqa

    This is separate from the redis_commands tests because, as far as I could
    find, there is currently no redis command that returns a boolean value.
    """
    reader.feed(b"#t\r\n")
    assert reader.get_object() is True
    reader.feed(b"#f\r\n")
    assert reader.get_object() is False
    reader.feed(b"#wrong\r\n")
    with pytest.raises(protocol.ProtocolError):
        reader.get_object()


def test_blob_error(reader):
    """It parses blob errors correctly."""
    for byte in b"!21\r\nSYNTAX invalid syntax\r\n":
        assert reader.get_object() is reader.sentinel
        reader.feed(byte.to_bytes(1, "little"))
    assert reader.get_object() == protocol.RedisError(b"SYNTAX", b"invalid syntax")


def test_big_number(reader):
    """It parses big numbers correctly."""
    reader.feed(b"(3492890328409238509324850943850943825024385\r\n")
    assert reader.get_object() == 3492890328409238509324850943850943825024385


@pytest.mark.parametrize("command_data", redis_commands.items())
def test_write_command(command_data):
    """It packs the command correctly."""
    command, data = command_data
    actual = protocol.write_command(*command.split(b" "))
    expected = data["encoded"]

    assert actual == expected
