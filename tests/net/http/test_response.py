"""
Test the 'net.http.response' module.
"""

# third-party
from pytest import mark

# module under test
from runtimepy.net.http.response import AsyncResponse

# built-in
from tests.resources import resource


@mark.asyncio
async def test_async_response_basic():
    """Test basic async responses."""

    inst = AsyncResponse(resource("test_bigger.txt"))
    assert await inst.size() > 0
    async for chunk in inst.process():
        assert chunk
