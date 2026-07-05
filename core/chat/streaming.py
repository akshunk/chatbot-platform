import json
from typing import AsyncGenerator


async def format_sse_stream(
    stream: AsyncGenerator[str, None],
) -> AsyncGenerator[str, None]:
    async for chunk in stream:
        if chunk:
            yield f"data: {json.dumps({'content': chunk})}\n\n"
    yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
