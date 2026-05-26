import sys
import os
import argparse
import json
import asyncio

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.orchestrator import Orchestrator
from app.models.types import ViolationSeverity, NodeStatus

def run_cli():
    parser = argparse.ArgumentParser(description="PheonixVirtualizer CI Gatekeeper")
    parser.add_argument("--path", type=str, default=".", help="Path to the repository to analyze")
    parser.add_argument("--fail-on", type=str, choices=["high", "medium", "low", "none"], default="high", 
                        help="Minimum severity to trigger a non-zero exit code")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    print(f"--- PheonixVirtualizer Analysis Start ---")
    orchestrator = Orchestrator(args.path)
    graph = orchestrator.analyze()
    
    violations = graph.violations
    
    # Severity mapping for threshold comparison
    severity_map = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
        "info": 0,
        "none": -1
    }
    
    threshold = severity_map.get(args.fail_on, 3)
    
    fail_count = 0
    print(f"\n[Results]")
    print(f"Total Nodes: {len(graph.nodes)}")
    print(f"Total Edges: {len(graph.edges)}")
    print(f"Total Violations: {len(violations)}")
    
    for v in violations:
        v_severity = severity_map.get(v.severity.value, 0)
        status_prefix = "[FAIL]" if v_severity >= threshold else "[WARN]"
        
        if v_severity >= threshold:
            fail_count += 1
            
        print(f"{status_prefix} {v.severity.value.upper()}: {v.message}")
        print(f"  Nodes: {', '.join(v.sourceNodeIds)}")
        print(f"  Rule: {v.ruleId}")
    
    if args.json:
        with open("analysis_report.json", "w") as f:
            json.dump(graph.model_dump(), f, indent=2)
    
    print(f"\n--- Analysis Complete ---")
    if fail_count > 0:
        print(f"Gatekeeper: REJECTED. {fail_count} violations above threshold '{args.fail_on}'.")
        sys.exit(1)
    else:
        print(f"Gatekeeper: PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    run_cli()
