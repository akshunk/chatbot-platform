from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from core.chat.message import Message

router = APIRouter()


@router.get("/conversations/{conv_id}/messages")
async def get_messages(conv_id: str, request: Request):
    history = request.app.state.history
    messages = history.get_messages(conv_id)
    return [m.to_dict() for m in messages]


@router.post("/conversations/{conv_id}/messages")
async def send_message(conv_id: str, request: Request):
    body = await request.json()
    content = body.get("content", "")
    model = body.get("model", request.app.state.default_model)
    temperature = body.get("temperature", 0.7)

    history = request.app.state.history

    conv = history.load_conversation(conv_id)
    if not conv:
        return {"error": "Conversation not found"}, 404

    user_msg = Message(
        conversation_id=conv_id,
        role="user",
        content=content,
    )
    history.add_message(user_msg)

    raw_history = history.get_messages(conv_id)
    formatted_history = [
        {"role": m.role, "content": m.content} for m in raw_history[:-1]
    ]

    generator = request.app.state.response_generator

    async def stream():
        full_response = ""
        async for chunk in generator.generate_stream(
            user_message=content,
            model=model,
            temperature=temperature,
            history=formatted_history,
        ):
            full_response += chunk
            yield {"event": "content", "data": chunk}

        assistant_msg = Message(
            conversation_id=conv_id,
            role="assistant",
            content=full_response,
        )
        history.add_message(assistant_msg)

        conv.touch()
        history.save_conversation(conv)

        yield {"event": "done", "data": assistant_msg.id}

    return EventSourceResponse(stream())


@router.post("/conversations/{conv_id}/messages/{msg_id}/feedback")
async def submit_feedback(conv_id: str, msg_id: str, request: Request):
    body = await request.json()
    feedback = body.get("feedback")
    if feedback not in ("thumbs_up", "thumbs_down"):
        return {"error": "Invalid feedback"}, 400

    history = request.app.state.history
    history.update_message_feedback(conv_id, msg_id, feedback)

    feedback_dir = request.app.state.history.data_dir / "feedback"
    feedback_dir.mkdir(parents=True, exist_ok=True)
    import json
    from datetime import datetime, timezone
    entry = {
        "conversation_id": conv_id,
        "message_id": msg_id,
        "feedback": feedback,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(feedback_dir / f"{msg_id}.json", "w") as f:
        json.dump(entry, f)

    return {"status": "ok"}


@router.post("/conversations/{conv_id}/regenerate")
async def regenerate(conv_id: str, request: Request):
    body = await request.json() or {}
    model = body.get("model", request.app.state.default_model)
    temperature = body.get("temperature", 0.7)

    history = request.app.state.history
    conv = history.load_conversation(conv_id)
    if not conv:
        return {"error": "Conversation not found"}, 404

    messages = history.get_messages(conv_id)
    if not messages or messages[-1].role != "assistant":
        return {"error": "No assistant message to regenerate"}, 400

    last_user_msg = None
    for m in reversed(messages):
        if m.role == "user":
            last_user_msg = m.content
            break

    if not last_user_msg:
        return {"error": "No user message found"}, 400

    history.update_message_feedback(conv_id, messages[-1].id, "regenerated")

    formatted_history = [
        {"role": m.role, "content": m.content} for m in messages[:-1]
    ]

    generator = request.app.state.response_generator

    async def stream():
        full_response = ""
        async for chunk in generator.generate_stream(
            user_message=last_user_msg,
            model=model,
            temperature=temperature,
            history=formatted_history,
        ):
            full_response += chunk
            yield {"event": "content", "data": chunk}

        assistant_msg = Message(
            conversation_id=conv_id,
            role="assistant",
            content=full_response,
        )
        history.add_message(assistant_msg)

        conv.touch()
        history.save_conversation(conv)

        yield {"event": "done", "data": assistant_msg.id}

    return EventSourceResponse(stream())
