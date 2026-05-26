import sys
import os
import json

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.orchestrator import Orchestrator

def analyze_self():
    project_root = os.getcwd()
    orchestrator = Orchestrator(project_root)
    graph = orchestrator.analyze()
    
    output_file = "dependency_graph.json"
    with open(output_file, "w") as f:
        f.write(graph.model_dump_json(indent=2))
    
    print(f"Graph written to {output_file}")
    print(f"Total nodes: {len(graph.nodes)}")
    print(f"Total edges: {len(graph.edges)}")

if __name__ == "__main__":
    analyze_self()
