from main import to_str, build_chat_messages


def test_to_str_plain_string():
    assert to_str("hello") == "hello"


def test_to_str_dict_with_text():
    assert to_str({"text": "hi", "type": "text"}) == "hi"


def test_to_str_dict_with_content():
    assert to_str({"content": "hi", "type": "text"}) == "hi"


def test_to_str_dict_with_text_list():
    """Gradio sends content as list of structured blocks."""
    val = [{"text": "Hello", "type": "text"}, {"text": "world", "type": "text"}]
    assert to_str(val) == "Hello world"


def test_to_str_none():
    assert to_str(None) == ""


def test_to_str_empty():
    assert to_str("") == ""


def test_to_str_int():
    assert to_str(42) == "42"


def test_to_str_nested():
    val = {"text": [{"text": "nested", "type": "text"}], "type": "text"}
    assert to_str(val) == "nested"


def test_build_first_message():
    """No history — only the current message."""
    result = build_chat_messages("hello", [])
    assert result == [{"role": "user", "content": "hello"}]


def test_build_history_dicts():
    """Gradio 6 format: list[dict]."""
    history = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hey"},
    ]
    result = build_chat_messages("what's up", history)
    assert result == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hey"},
        {"role": "user", "content": "what's up"},
    ]


def test_build_history_tuples():
    """Legacy format: list[tuple[str, str]]."""
    history = [("hi", "hey")]
    result = build_chat_messages("what's up", history)
    assert result == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hey"},
        {"role": "user", "content": "what's up"},
    ]


def test_build_content_is_list_of_dicts():
    """Bug 2: content was a list of structured blocks."""
    history = [
        {"role": "user", "content": [{"text": "hello", "type": "text"}]},
        {"role": "assistant", "content": [{"text": "world", "type": "text"}]},
    ]
    result = build_chat_messages("more", history)
    assert result == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "world"},
        {"role": "user", "content": "more"},
    ]


def test_build_message_is_dict():
    """Bug 3: Gradio passes message as dict."""
    result = build_chat_messages({"text": "hello", "type": "text"}, [])
    assert result == [{"role": "user", "content": "hello"}]


def test_build_message_is_dict_with_history():
    """Message is dict AND history has structured content."""
    history = [
        {"role": "user", "content": [{"text": "hi", "type": "text"}]},
        {"role": "assistant", "content": [{"text": "hey", "type": "text"}]},
    ]
    result = build_chat_messages({"text": "what's up", "type": "text"}, history)
    assert result == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hey"},
        {"role": "user", "content": "what's up"},
    ]


def test_build_history_role_preserved():
    """Bug 1: history role was hardcoded to 'user'."""
    history = [{"role": "assistant", "content": "hello"}]
    result = build_chat_messages("ping", history)
    assert result == [
        {"role": "assistant", "content": "hello"},
        {"role": "user", "content": "ping"},
    ]
