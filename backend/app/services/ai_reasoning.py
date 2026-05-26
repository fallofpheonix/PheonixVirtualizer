import os
import google.generativeai as genai
from typing import List, Dict, Any
from ..models.types import Violation, GraphNode

class AIReasoningService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.enabled = False
            print("Warning: GOOGLE_API_KEY not found. AI Reasoning will be disabled.")

    async def analyze_violation(self, violation: Violation, affected_nodes: List[GraphNode]) -> str:
        if not self.enabled:
            return "AI Reasoning is disabled. Please provide a GOOGLE_API_KEY in your environment."

        # Construct a compressed topological context
        nodes_context = "\n".join([
            f"- {n.label} ({n.kind}): {n.path}" for n in affected_nodes
        ])

        prompt = f"""
You are a Staff Systems Architect. A deterministic dependency engine has detected an architectural violation.

Violation: {violation.message}
Rule ID: {violation.ruleId}
Severity: {violation.severity}

Affected Nodes:
{nodes_context}

Task:
1. Explain why this specific violation is harmful to the system's long-term maintainability.
2. Propose a deterministic refactoring strategy to resolve this violation (e.g., Dependency Injection, Interface Abstraction, or Mediator pattern).
3. Focus on structural integrity rather than specific code implementations.

Keep your response concise, professional, and architecturally sound.
"""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"Error during AI analysis: {str(e)}"

ai_reasoning_service = AIReasoningService()
