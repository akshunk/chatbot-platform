from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/conversations")
async def list_conversations(request: Request):
    history = request.app.state.history
    convs = history.list_conversations()
    return [c.to_dict() for c in convs]


@router.post("/conversations")
async def create_conversation(request: Request):
    body = await request.json() or {}
    history = request.app.state.history
    conv = history.create_conversation(
        title=body.get("title", "New Conversation"),
        model=body.get("model", request.app.state.models_config.get("default", "default")),
        provider=body.get("provider", request.app.state.default_provider),
        personality=body.get("personality", "default"),
    )
    history.save_conversation(conv)
    return conv.to_dict()


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str, request: Request):
    history = request.app.state.history
    conv = history.load_conversation(conv_id)
    if not conv:
        return {"error": "Conversation not found"}, 404
    messages = history.get_messages(conv_id)
    return {
        "conversation": conv.to_dict(),
        "messages": [m.to_dict() for m in messages],
    }


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str, request: Request):
    history = request.app.state.history
    history.delete_conversation(conv_id)
    return {"status": "deleted"}
