from __future__ import annotations

import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000/api"


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
        print(f"ERROR on {path}: {e}")
        if hasattr(e, "read"):
            print(e.read().decode("utf-8"))
        return None


def run_e2e_tests():
    # TEST 2: World Entry
    print("TEST 2: World Entry")
    stories = req("/stories/")
    assert stories is not None, "Failed to get stories"
    story_ids = [s["id"] for s in stories["stories"]]
    print(f"Stories found: {story_ids}")
    assert "demo" in story_ids, "Demo story not found"

    summary = req("/world-state/demo/canon/summary")
    print(f"World Summary: {summary}")
    assert summary["character_count"] == 6, f"Expected 6 characters, got {summary['character_count']}"

    # TEST 3: Timeline
    print("\nTEST 3: Timeline")
    timeline = req("/timelines/demo/canon")
    print(f"Timeline events: {timeline['total_events']}")
    assert timeline["total_events"] == 12, f"Expected 12 events, got {timeline['total_events']}"
    assert timeline["events"][0]["sequence"] <= timeline["events"][-1]["sequence"]

    # TEST 4: Temporal Knowledge Boundary
    print("\nTEST 4: Temporal Knowledge Boundary")
    knowledge_seq_1 = req("/characters/demo/evelyn_cross/knowledge?sequence=1&branch_id=canon")
    facts_seq_1 = [f["statement"] for f in knowledge_seq_1["facts"]]
    print(f"Evelyn facts at Seq 1: {len(facts_seq_1)}")

    knowledge_seq_10 = req("/characters/demo/evelyn_cross/knowledge?sequence=10&branch_id=canon")
    facts_seq_10 = [f["statement"] for f in knowledge_seq_10["facts"]]
    print(f"Evelyn facts at Seq 10: {len(facts_seq_10)}")

    hale_seq_1 = req("/characters/demo/detective_hale/knowledge?sequence=1&branch_id=canon")
    hale_seq_12 = req("/characters/demo/detective_hale/knowledge?sequence=12&branch_id=canon")
    print(f"Hale facts at Seq 1: {len(hale_seq_1['facts'])}, at Seq 12: {len(hale_seq_12['facts'])}")
    assert len(hale_seq_1["facts"]) < len(hale_seq_12["facts"]), "Knowledge horizon should expand at higher sequence"

    # TEST 5: Character Chat
    print("\nTEST 5: Character Chat")
    chat_res = req("/chat/", "POST", {
        "character_id": "detective_hale",
        "story_id": "demo",
        "branch_id": "canon",
        "sequence": 5,
        "message": "What do you know about the murder?",
    })
    print(f"Chat Success: {chat_res['success']}")
    print(f"Chat Output: {chat_res['output'][:100]}...")
    print(f"Knowledge Used: {chat_res['knowledge_count']}")
    assert chat_res["success"] is True

    # TEST 6: What-If Branch
    print("\nTEST 6: What-If")
    branch_res = req("/branches/create", "POST", {
        "story_id": "demo",
        "parent_branch_id": "canon",
        "sequence": 5,
        "change": "Evelyn did not go to the docks.",
    })
    branch_id = branch_res["branch"]["id"]
    print(f"Created branch: {branch_id}")
    assert branch_id != "canon"

    # TEST 7: Consistency
    print("\nTEST 7: Consistency")
    consist_res = req(f"/branches/{branch_id}/validate", "POST")
    print(f"Consistency Valid: {consist_res['valid']}")
    print(f"Consistency Summary: {consist_res['summary'][:100]}...")
    assert "valid" in consist_res

    # TEST 8: Branch Diff
    print("\nTEST 8: Branch Diff")
    diff_res = req(f"/branches/{branch_id}/diff")
    print(f"Diff Ripple Depth: {diff_res['ripple_depth']}")
    print(f"Added Events: {len(diff_res['events_added'])}")
    print(f"Removed Events: {len(diff_res['events_removed'])}")
    assert diff_res["ripple_depth"] >= 1

    # TEST 9: Canon Immutability
    print("\nTEST 9: Canon Immutability")
    canon_timeline = req("/timelines/demo/canon")
    print(f"Canon events count: {canon_timeline['total_events']}")
    assert canon_timeline["total_events"] == 12, "Canon was mutated!"

    print("\nALL BACKEND TESTS PASSED")


if __name__ == "__main__":
    run_e2e_tests()
