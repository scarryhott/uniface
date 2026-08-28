from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from closure_supernet.api_proof_completion import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.continuation_models import ContinuationSystemCreate
from closure_supernet.proof_completion_models import (
    AdmissionCreate,
    BalanceCreate,
    DerivationCreate,
    ProofSystemCreate,
)
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.turing_being_models import (
    LifeActionWitness,
    LifeReactionWitness,
    TuringBeingLifeCreate,
    TuringBeingReturnCreate,
)


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "proof-completion.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def branching_relation() -> ProofSystemCreate:
    return ProofSystemCreate(
        name="two sources meet without mutual proof",
        presentations=["a", "b", "c"],
        steps=[
            {"source": "a", "target": "b", "label": "a→b"},
            {"source": "b", "target": "b", "label": "b→b"},
            {"source": "c", "target": "b", "label": "c→b"},
        ],
    )


def cycle_relation() -> ProofSystemCreate:
    return ProofSystemCreate(
        name="four return cycle",
        presentations=["0", "1", "2", "3"],
        steps=[
            {"source": "0", "target": "1", "label": "return"},
            {"source": "1", "target": "2", "label": "return"},
            {"source": "2", "target": "3", "label": "return"},
            {"source": "3", "target": "0", "label": "return"},
        ],
    )


def test_completion_is_proof_and_geometry_does_not_replace_balance(
    tmp_path: Path,
) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.proof_completion.create_system(
                branching_relation()
            )
            evaluation = system["evaluation"]
            assert evaluation["completion_eq_proof"] is True
            assert evaluation["completion_eq_nonempty_derivation"] is True
            assert evaluation["meta_abstraction_surjective"] is True
            assert evaluation["truth_admission"]["extensive"] is True
            assert evaluation["truth_admission"]["idempotent"] is True
            assert evaluation["truth_admission"]["admit_isLeast"] is True
            assert evaluation["balance_le_geometry"] is True
            assert evaluation["balance_eq_geometry"] is False
            assert evaluation["geometry_does_not_replace_proof"] is True
            assert evaluation["admits_relation"]["a"] == ["a", "b"]
            assert "c" not in evaluation["admits_relation"]["a"]

            proof = runtime.proof_completion.derivation_witness(
                system["id"], "a", "b"
            )
            assert proof["admitted"] is True
            assert proof["length"] == 1
            assert proof["trace"] == ["a", "b"]
            assert proof["completion_eq_proof"] is True

            no_proof = runtime.proof_completion.derivation_witness(
                system["id"], "a", "c"
            )
            assert no_proof["admitted"] is False
            assert no_proof["completion_proposition"] is False

            admission = runtime.proof_completion.admission_witness(
                system["id"], ["a"]
            )
            assert admission["admitted_set"] == ["a", "b"]
            assert admission["extensive"] is True
            assert admission["idempotent"] is True

            balance = runtime.proof_completion.balance_witness(
                system["id"], "a", "c"
            )
            assert balance["balanced"] is False
            assert balance["geometry_related"] is True
            assert balance["geometry_implies_balance"] is False
            assert balance[
                "geometry_does_not_replace_forward_or_reverse_proof"
            ] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_closed_return_makes_balance_equal_geometry(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.proof_completion.create_system(cycle_relation())
            evaluation = system["evaluation"]
            assert evaluation["return_closes"] is True
            assert evaluation["balance_eq_geometry"] is True
            assert evaluation["completion_object_cardinality"] == 1
            assert evaluation["proof_is_counting_for_deterministic_return"] is True
            proof = runtime.proof_completion.derivation_witness(
                system["id"], "0", "3"
            )
            assert proof["trace"] == ["0", "1", "2", "3"]
            assert proof["length"] == 3
            balance = runtime.proof_completion.balance_witness(
                system["id"], "0", "3"
            )
            assert balance["balanced"] is True
            assert balance["closure_equality_under_closed_return"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_multiple_proofs_remain_in_one_reopenable_fibre(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.proof_completion.create_system(
                ProofSystemCreate(
                    name="two proof paths",
                    presentations=["a", "b", "c", "d"],
                    steps=[
                        {"source": "a", "target": "b", "label": "left-1"},
                        {"source": "b", "target": "d", "label": "left-2"},
                        {"source": "a", "target": "c", "label": "right-1"},
                        {"source": "c", "target": "d", "label": "right-2"},
                    ],
                )
            )
            first = await runtime.proof_completion.create_derivation(
                system["id"], DerivationCreate(source="a", target="d")
            )
            alternate = await runtime.proof_completion.create_derivation(
                system["id"],
                DerivationCreate(
                    source="a", target="d", path=["a", "c", "d"]
                ),
            )
            assert first["evaluation"]["admitted"] is True
            assert alternate["evaluation"]["trace"] == ["a", "c", "d"]
            assert first["evaluation"]["completion_proposition"] is True
            assert alternate["evaluation"]["completion_proposition"] is True
            assert first["id"] != alternate["id"]
            assert first["metadata"]["canonical_derivation_selected"] is False
            assert alternate["metadata"]["canonical_derivation_selected"] is False
            event = runtime.supernet_store.get_event(
                alternate["integration_event_id"]
            )
            assert event["current_stage"] == "RETURNED"
            assert event["current_verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_every_continuation_is_linked_to_proof_completion(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            continuation = await runtime.continuation.create_system(
                ContinuationSystemCreate(
                    name="proof-bearing ball continuation",
                    presentations=["0", "1", "2", "3"],
                    step={"0": "1", "1": "2", "2": "3", "3": "0"},
                    origin="0",
                )
            )
            assert continuation["proof_system_id"] is not None
            assert continuation["evaluation"]["rule_is_admits"] is True
            assert continuation["evaluation"]["completion_eq_proof"] is True
            assert continuation["evaluation"]["balance_eq_geometry"] is True
            proof = runtime.proof_completion_store.get_system(
                continuation["proof_system_id"]
            )
            assert proof["continuation_system_id"] == continuation["id"]
            assert proof["geometry_completion_system_id"] == continuation[
                "completion_system_id"
            ]
            event = runtime.supernet_store.get_event(
                continuation["integration_event_id"]
            )
            returned = event["state_history"][-1]
            assert proof["id"] in returned["returned_resource_ids"]
            assert returned["verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_turing_being_qg_proof_requires_truth_and_is_total(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            life = await runtime.turing_being.create_life_event(
                TuringBeingLifeCreate(
                    name="life before proof abstraction",
                    global_hair_executor="global hair zero",
                    local_ball_reactor="local ball infinity",
                    action=LifeActionWitness(
                        exact_occurrence="executor opens the reactor"
                    ),
                )
            )
            with pytest.raises(ValueError):
                await runtime.proof_completion.create_from_turing_being(
                    life["id"]
                )
            completed = await runtime.turing_being.complete_return(
                life["id"],
                TuringBeingReturnCreate(
                    reaction=LifeReactionWitness(
                        exact_occurrence="reactor returns to global hair"
                    )
                ),
            )
            assert completed["translational_truth_receipt"]["complete"] is True
            proof = await runtime.proof_completion.create_from_turing_being(
                life["id"]
            )
            evaluation = proof["evaluation"]
            assert proof["turing_being_life_event_id"] == life["id"]
            assert all(
                len(evaluation["admits_relation"][item]) == 8
                for item in proof["presentations"]
            )
            assert evaluation["completion_object_cardinality"] == 1
            assert evaluation["max_shortest_proof_length"] <= 5
            qg = runtime.proof_completion.projection()["canonical_qg"]
            assert qg["qg_total"] is True
            assert qg["qg_shortProof"] is True
            assert qg["completion_single_point"] is True
            assert qg["beat_balance_iff_reactor"] is True
            assert qg["beatDecide_correct"] is True
            assert qg["non_admitted_example"]["decision"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_proof_completion_api_black_mirror_and_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/proof-completion")
        assert page.status_code == 200
        assert "Completion is proof after meta abstraction" in page.text

        created = client.post(
            "/network/proofs/systems",
            json={
                "name": "API proof system",
                "presentations": ["a", "b", "c"],
                "steps": [
                    {"source": "a", "target": "b", "label": "a→b"},
                    {"source": "b", "target": "b", "label": "b→b"},
                    {"source": "c", "target": "b", "label": "c→b"},
                ],
            },
        )
        assert created.status_code == 200, created.text
        system = created.json()
        assert system["evaluation"]["completion_eq_proof"] is True

        derivation = client.get(
            f"/network/proofs/systems/{system['id']}/derivation",
            params={"source": "a", "target": "b"},
        )
        assert derivation.status_code == 200
        assert derivation.json()["trace"] == ["a", "b"]

        admission = client.post(
            f"/network/proofs/systems/{system['id']}/admissions",
            json={"seeds": ["a"]},
        )
        assert admission.status_code == 200, admission.text
        assert admission.json()["evaluation"]["admitted_set"] == ["a", "b"]

        balance = client.get(
            f"/network/proofs/systems/{system['id']}/balance",
            params={"left": "a", "right": "c"},
        )
        assert balance.status_code == 200
        assert balance.json()["balanced"] is False
        assert balance.json()["geometry_related"] is True

        field = client.get("/network/proofs/field")
        assert field.status_code == 200, field.text
        payload = field.json()
        assert payload["stats"]["systems"] == 1
        assert payload["completion_is_proof_truncation"] is True
        assert payload["geometry_does_not_replace_proof"] is True

        lens = client.get("/supernet/project", params={"lens": "proof"})
        assert lens.status_code == 200, lens.text
        assert lens.json()["lens"] == "proof"
        assert lens.json()["stats"]["visible_events"] >= 1

        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        caps = capabilities.json()
        assert caps["completion_eq_proof"] is True
        assert caps["black_mirror_reopens_completion_to_proof_fibre"] is True
        assert caps["canonical_derivation_selected"] is False
        assert caps["determination_issues_truth"] is False
        assert app.version == "3.3.0"
