"""
Test the 'channel.registry' module.
"""

# module under test
from runtimepy.channel.registry import ChannelRegistry

# internal
from tests.resources import resource


def test_channel_registry_basic():
    """Test basic interactions with a channel registry."""

    registry = ChannelRegistry.decode(
        resource("channels", "sample_registry.yaml")
    )
    assert registry

    assert registry.registry_normalize(
        registry.registry_normalize("test.bool")
    )

    other = ChannelRegistry()
    other.register_from_other(registry)
    other.register_from_other(registry)

    assert list(other.search("test"))
