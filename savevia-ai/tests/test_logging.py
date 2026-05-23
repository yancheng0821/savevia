import json


def test_logger_outputs_json(capsys):
    from app.core.logging import configure_logging, get_logger

    configure_logging(log_level="INFO", json_output=True)
    log = get_logger("test")
    log.info("hello", user_id=42, request_id="abc")

    captured = capsys.readouterr()
    line = captured.out.strip().splitlines()[-1]
    payload = json.loads(line)

    assert payload["event"] == "hello"
    assert payload["user_id"] == 42
    assert payload["request_id"] == "abc"
    assert payload["level"] == "info"
    assert "timestamp" in payload


def test_logger_respects_log_level(capsys):
    from app.core.logging import configure_logging, get_logger

    configure_logging(log_level="WARNING", json_output=True)
    log = get_logger("test")
    log.info("should-not-appear")
    log.warning("should-appear")

    captured = capsys.readouterr()
    out = captured.out
    assert "should-not-appear" not in out
    assert "should-appear" in out
