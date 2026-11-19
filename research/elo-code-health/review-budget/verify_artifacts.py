"""Verify cross-artifact byte bindings without refitting or executing subject code."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify() -> dict:
    checks = []
    def bound(record: str, field: str, target: str) -> None:
        data = json.loads((ROOT / record).read_text())
        actual = digest(ROOT / target)
        checks.append({"record": record, "field": field, "target": target,
                       "expected": data[field], "actual": actual,
                       "passed": data[field] == actual})
    for record in ("models/accepted-results.json", "models/accepted-grid-results.json"):
        bound(record, "input_sha256", "corpus/rounds.jsonl")
    bound("models/accepted-results.json", "protocol_sha256", "models/PROTOCOL.md")
    bound("models/external-results.json", "external_sha256", "external-corpus/rounds.jsonl")
    bound("models/external-results.json", "training_sha256", "models/structured-training.jsonl")
    bound("models/external-results.json", "locked_settings_sha256", "models/external-locked-settings.json")
    base = "capture-recapture/"
    for field, target in (("source_sha256", "sources/umd-total.cc"),
                          ("parser_sha256", "empirical.py"),
                          ("protocol_sha256", "EMPIRICAL-PROTOCOL.md"),
                          ("amendment_sha256", "EMPIRICAL-AMENDMENT.md"),
                          ("manual_oracle_sha256", "MANUAL-ORACLE.md")):
        bound(base + "empirical-results.json", field, base + target)
    for field, target in (("normalized_sha256", "normalized-matrices.json"),
                          ("protocol_sha256", "COVERAGE-PROTOCOL.md")):
        bound(base + "coverage-results.json", field, base + target)
    for field, target in (("script_sha256", "simulate.py"),
                          ("protocol_sha256", "SIMULATION-PROTOCOL.md")):
        bound(base + "simulation-results.json", field, base + target)
    bound("evidence-graph/cli-checks.json", "bundle_sha256", "evidence-graph/paneweft.bundle.json")
    bound("evidence-graph/checks.json", "bundle_sha256", "evidence-graph/paneweft.bundle.json")
    latest = "advisory-prototype/smoke-records/observation-3329b5b6982026312359dca4bc85e90ecd8cb04af8b0706511b31c6d72848b46.json"
    bound(latest, "collector_sha256", "advisory-prototype/collector.py")
    cli = json.loads((ROOT / "evidence-graph/cli-checks.json").read_text())
    checks.append({"record": "evidence-graph/cli-checks.json", "check": "roundtrip-and-honest-freshness",
                   "passed": cli["passed"] is True and cli["roundtrip_edges"] == 11
                   and cli["freshness"]["status"] == "unverified"})
    return {"scope": "Cross-artifact byte integrity only; not scientific validity or source authentication.",
            "checks": checks, "passed": all(c["passed"] for c in checks)}

if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
