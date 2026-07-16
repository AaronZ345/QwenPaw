# -*- coding: utf-8 -*-
import click
import pytest
from click.testing import CliRunner

from qwenpaw.cli.cron_cmd import (
    _build_spec_from_cli,
    _resolve_update_spec,
    cron_group,
)


def _agent_spec(**overrides):
    values = {
        "task_type": "agent",
        "schedule_type": "cron",
        "name": "Background refresh",
        "cron": "0 * * * *",
        "run_at": None,
        "repeat_every_days": None,
        "repeat_end_type": None,
        "repeat_until": None,
        "repeat_count": None,
        "channel": "console",
        "target_user": "u1",
        "target_session": "console:u1",
        "text": "Refresh the index",
        "timezone": "UTC",
        "enabled": True,
        "mode": "final",
        "silent": False,
    }
    values.update(overrides)
    return _build_spec_from_cli(**values)


def _resolve_agent_update(spec, **overrides):
    values = {
        "spec": spec,
        "task_type": None,
        "schedule_type": None,
        "name": None,
        "cron": None,
        "run_at": None,
        "repeat_every_days": None,
        "repeat_end_type": None,
        "repeat_until": None,
        "repeat_count": None,
        "channel": None,
        "target_user": None,
        "target_session": None,
        "text": None,
        "timezone": None,
        "enabled": None,
        "mode": None,
        "silent": None,
        "save_result_to_inbox": None,
        "share_session": None,
        "timeout_seconds": None,
        "tool_safety": None,
    }
    values.update(overrides)
    return _resolve_update_spec(**values)


def test_build_agent_spec_includes_silent_delivery():
    payload = _agent_spec(silent=True)

    assert payload["dispatch"]["silent"] is True


def test_build_text_spec_rejects_silent_delivery():
    with pytest.raises(click.UsageError, match="only supported.*agent"):
        _agent_spec(task_type="text", silent=True)


def test_create_help_exposes_silent_delivery_flag():
    result = CliRunner().invoke(cron_group, ["create", "--help"])

    assert result.exit_code == 0
    assert "--silent / --no-silent" in result.output


def test_update_preserves_advanced_runtime_and_request_fields():
    existing = _agent_spec()
    existing["runtime"].update(
        {
            "max_concurrency": 4,
            "misfire_grace_seconds": 1800,
        },
    )
    existing["request"].update(
        {
            "model": "custom-model",
            "request_context": {"source_tag": "ops"},
        },
    )

    updated = _resolve_agent_update(
        existing,
        name="Renamed refresh",
    )

    assert updated["name"] == "Renamed refresh"
    assert updated["runtime"]["max_concurrency"] == 4
    assert updated["runtime"]["misfire_grace_seconds"] == 1800
    assert updated["request"]["model"] == "custom-model"
    assert updated["request"]["request_context"] == {"source_tag": "ops"}


def test_update_replaces_prompt_without_dropping_request_extensions():
    existing = _agent_spec()
    existing["request"]["request_context"] = {"source_tag": "ops"}

    updated = _resolve_agent_update(
        existing,
        text="Refresh only changed documents",
    )

    content = updated["request"]["input"][0]["content"]
    assert content[0]["text"] == "Refresh only changed documents"
    assert updated["request"]["request_context"] == {"source_tag": "ops"}
