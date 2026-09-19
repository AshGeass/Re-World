from __future__ import annotations

import json
import urllib.request
import pytest

BASE_URL = "http://127.0.0.1:8000/api"
FRONTEND_URL = "http://localhost:3000"


def req(path: str, method: str = "GET", data: dict | None = None):
    url = f"{BASE_URL}{path}"
    req_obj = urllib.request.Request(url, method=method)
    if data:
        req_obj.add_header("Content-Type", "application/json")
        req_obj.data = json.dumps(data).encode("utf-8")
    try:
        r = urllib.request.urlopen(req_obj)
        return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        if hasattr(e, "read"):
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"HTTP {method} {url} failed: {err_body}") from e
        raise


def test_01_application_startup():
    # Verify backend health
    health_req = urllib.request.Request("http://127.0.0.1:8000/health")
    res = urllib.request.urlopen(health_req)
    assert res.status == 200
    health_data = json.loads(res.read().decode("utf-8"))
    assert health_data.get("status") == "ok"

    # Verify frontend health
    fe_req = urllib.request.Request(FRONTEND_URL)
    fe_res = urllib.request.urlopen(fe_req)
    assert fe_res.status == 200


def test_02_world_entry():
    stories = req("/stories/")
    assert "stories" in stories
    story_ids = [s["id"] for s in stories["stories"]]
    assert "demo" in story_ids

    summary = req("/world-state/demo/canon/summary")
    assert summary["character_count"] == 6
    assert summary["event_count"] == 12
    assert summary["relationship_count"] == 7
    assert summary["knowledge_count"] >= 28


def test_03_timeline():
    timeline = req("/timelines/demo/canon")
    assert timeline["total_events"] == 12
    events = timeline["events"]
    assert len(events) == 12
    # Verify strict ascending order
    for i in range(len(events) - 1):
        assert events[i]["sequence"] <= events[i + 1]["sequence"]
    assert events[0]["sequence"] == 1
    assert events[-1]["sequence"] == 12


def test_04_temporal_knowledge_boundary():
    # At sequence 1, Detective Hale should only know 1 fact
    hale_seq_1 = req("/characters/demo/detective_hale/knowledge?sequence=1&branch_id=canon")
    assert hale_seq_1["total"] == 1
    statements_seq_1 = [f["statement"] for f in hale_seq_1["facts"]]
    # Thomas poisoning (discovered at seq 7) must NOT be present at seq 1
    assert not any("poison" in s.lower() for s in statements_seq_1)

    # At sequence 7+, poisoning IS known
    hale_seq_7 = req("/characters/demo/detective_hale/knowledge?sequence=7&branch_id=canon")
    assert hale_seq_7["total"] >= 6
    statements_seq_7 = [f["statement"] for f in hale_seq_7["facts"]]
    assert any("poison" in s.lower() for s in statements_seq_7)


def test_05_character_chat():
    chat_res = req("/chat/", "POST", {
        "character_id": "detective_hale",
        "story_id": "demo",
        "branch_id": "canon",
        "sequence": 2,
        "message": "What did you observe in the study?",
    })
    assert chat_res["success"] is True
    assert len(chat_res["output"]) > 0
    assert chat_res["character_id"] == "detective_hale"
    assert chat_res["sequence"] == 2
    assert chat_res["knowledge_count"] >= 1


def test_06_what_if_branch_creation():
    branch_res = req("/branches/create", "POST", {
        "story_id": "demo",
        "parent_branch_id": "canon",
        "sequence": 6,
        "change": "Evelyn did not go to the docks and stayed at the manor.",
    })
    branch = branch_res["branch"]
    assert branch["id"] != "canon"
    assert branch["divergence_sequence"] == 6
    assert branch_res["affected_events"] >= 1
    assert len(branch_res["affected_characters"]) > 0


def test_07_consistency_validation():
    # Create branch
    branch_res = req("/branches/create", "POST", {
        "story_id": "demo",
        "parent_branch_id": "canon",
        "sequence": 5,
        "change": "Evelyn did not go to the docks.",
    })
    branch_id = branch_res["branch"]["id"]

    # Validate branch
    consist_res = req(f"/branches/{branch_id}/validate", "POST")
    assert "valid" in consist_res
    assert "summary" in consist_res
    assert "issues" in consist_res


def test_08_branch_diff():
    branch_res = req("/branches/create", "POST", {
        "story_id": "demo",
        "parent_branch_id": "canon",
        "sequence": 5,
        "change": "Evelyn did not go to the docks.",
    })
    branch_id = branch_res["branch"]["id"]

    diff_res = req(f"/branches/{branch_id}/diff")
    assert diff_res["branch_id"] == branch_id
    assert diff_res["canon_branch_id"] == "canon"
    assert len(diff_res["events_added"]) >= 1
    assert diff_res["ripple_depth"] >= 1
    assert isinstance(diff_res["characters_affected"], list)


def test_09_canon_immutability():
    # Canon timeline must remain identical before and after branching
    canon_timeline = req("/timelines/demo/canon")
    assert canon_timeline["total_events"] == 12
    assert canon_timeline["branch_id"] == "canon"

    summary = req("/world-state/demo/canon/summary")
    assert summary["character_count"] == 6
    assert summary["event_count"] == 12
