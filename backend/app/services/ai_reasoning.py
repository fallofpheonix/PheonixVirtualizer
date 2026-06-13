import os
import google.generativeai as genai
import httpx
from typing import List, Dict, Any, Optional
from ..models.types import Violation, GraphNode

class AIReasoningService:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower() # 'gemini' or 'ollama'
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        
        # Configure Gemini if provider is gemini
        self.gemini_enabled = False
        if self.provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_enabled = True
            else:
                print("Warning: GOOGLE_API_KEY not found. AI Reasoning will fail for Gemini.")

    async def analyze_violation(self, violation: Violation, affected_nodes: List[GraphNode], project_root: str) -> str:
        # Load code snippets for context
        code_context = []
        for node in affected_nodes:
            if node.path:
                abs_path = os.path.join(project_root, node.path)
                if os.path.isfile(abs_path):
                    try:
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            # Get first 100 lines for context
                            lines = f.readlines()[:100]
                            code_context.append(f"--- File: {node.path} ---\n{''.join(lines)}")
                    except Exception:
                        pass

        prompt = f"""
You are a Staff Systems Architect. You are resolving architectural violations in a large monorepo.

VIOLATION: {violation.message}
RULE: {violation.ruleId}
SEVERITY: {violation.severity}

CODE CONTEXT:
{"".join(code_context)}

TASK:
1. DIAGNOSE: Why does this violation exist in this specific code?
2. PLAN: Provide a step-by-step refactoring plan to fix it.
3. FIX: Provide the specific code changes (imports, interface extractions, etc.) needed.

Be extremely specific. Use the provided filenames.
"""
        if self.provider == "ollama":
            return await self._call_ollama(prompt)
        elif self.provider == "gemini" and self.gemini_enabled:
            return await self._call_gemini(prompt)
        else:
            return "AI Reasoning Provider not configured. Set AI_PROVIDER and relevant keys."

    async def _call_gemini(self, prompt: str) -> str:
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    async def _call_ollama(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.ollama_url, json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                })
                return response.json().get("response", "No response from Ollama")
        except Exception as e:
            return f"Ollama Error: {str(e)}"

ai_reasoning_service = AIReasoningService()
