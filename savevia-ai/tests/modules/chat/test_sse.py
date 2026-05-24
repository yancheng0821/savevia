"""Tests for SSE frame serialisation. Goal: byte-match Java SseEmitter output."""


def test_conversation_event_uses_plain_id_no_json():
    from app.modules.chat.sse import format_conversation_event
    assert format_conversation_event(1234) == "event:conversation\ndata:1234\n\n"


def test_done_event_has_empty_data():
    from app.modules.chat.sse import format_done_event
    assert format_done_event() == "event:done\ndata:\n\n"


def test_message_event_wraps_in_json_with_t_key():
    from app.modules.chat.sse import format_message_event
    out = format_message_event("hello")
    assert out == 'event:message\ndata:{"t":"hello"}\n\n'


def test_message_event_escapes_quotes_backslashes_newlines_tabs():
    from app.modules.chat.sse import format_message_event
    out = format_message_event('a"b\\c\nd\re\tf')
    assert out == 'event:message\ndata:{"t":"a\\"b\\\\c\\nd\\re\\tf"}\n\n'


def test_message_event_preserves_leading_and_trailing_spaces():
    """The whole reason we JSON-wrap message content is to keep whitespace."""
    from app.modules.chat.sse import format_message_event
    out = format_message_event("  hi  ")
    assert out == 'event:message\ndata:{"t":"  hi  "}\n\n'


def test_tool_call_event_uses_compact_json_no_spaces():
    from app.modules.chat.sse import format_tool_call_event
    out = format_tool_call_event(name="get_user_cards", args={"foo": 1})
    assert out == 'event:tool_call\ndata:{"name":"get_user_cards","args":{"foo":1}}\n\n'


def test_tool_call_event_with_empty_args():
    from app.modules.chat.sse import format_tool_call_event
    out = format_tool_call_event(name="get_user_cards", args={})
    assert out == 'event:tool_call\ndata:{"name":"get_user_cards","args":{}}\n\n'


def test_tool_result_event_with_data():
    from app.modules.chat.sse import format_tool_result_event
    out = format_tool_result_event(
        name="get_best_card", success=True, content="best is X", data={"id": 1},
    )
    assert out == (
        'event:tool_result\n'
        'data:{"name":"get_best_card","success":true,"content":"best is X","data":{"id":1}}\n\n'
    )


def test_tool_result_event_omits_data_key_when_none():
    from app.modules.chat.sse import format_tool_result_event
    out = format_tool_result_event(
        name="x", success=False, content="err", data=None,
    )
    assert out == 'event:tool_result\ndata:{"name":"x","success":false,"content":"err"}\n\n'


def test_error_event_uses_json_with_code_and_message():
    from app.modules.chat.sse import format_error_event
    out = format_error_event(code="CHAT_QUOTA_EXCEEDED", message="too many")
    assert out == (
        'event:error\ndata:{"code":"CHAT_QUOTA_EXCEEDED","message":"too many"}\n\n'
    )


def test_error_event_escapes_special_chars():
    from app.modules.chat.sse import format_error_event
    out = format_error_event(code="X", message='bad "input"\nline')
    assert (
        out == 'event:error\ndata:{"code":"X","message":"bad \\"input\\"\\nline"}\n\n'
    )
