import pytest
import os
import json
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.orchestrator import Orchestrator
from app.models.types import NodeStatus

SCENARIOS_DIR = "tests/fixtures/scenarios"

def get_scenarios():
    if not os.path.exists(SCENARIOS_DIR):
        return []
    return [d for d in os.listdir(SCENARIOS_DIR) if os.path.isdir(os.path.join(SCENARIOS_DIR, d))]

@pytest.mark.parametrize("scenario_name", get_scenarios())
def test_architectural_scenario(scenario_name):
    scenario_path = os.path.join(SCENARIOS_DIR, scenario_name)
    expected_file = os.path.join(scenario_path, "expected.json")
    
    if not os.path.exists(expected_file):
        pytest.skip(f"No expected.json found for {scenario_name}")

    with open(expected_file, 'r') as f:
        expected = json.load(f)

    # Run analysis
    orchestrator = Orchestrator(scenario_path)
    graph = orchestrator.analyze()

    # Assertions based on "Golden Dataset"
    assert len(graph.nodes) == expected.get("node_count"), f"Node count mismatch for {scenario_name}"
    assert len(graph.edges) == expected.get("edge_count"), f"Edge count mismatch for {scenario_name}"
    
    # Violation count can be tricky if we add more default rules, but let's check
    if "violation_count" in expected:
        assert len(graph.violations) == expected.get("violation_count"), f"Violation count mismatch for {scenario_name}"

    if "verified_edges" in expected:
        verified_count = len([e for e in graph.edges if e.status == NodeStatus.VERIFIED])
        assert verified_count == expected.get("verified_edges"), f"Verified edges count mismatch for {scenario_name}"
