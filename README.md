# PheonixVirtualizer

**PheonixVirtualizer** is a language-agnostic, real-time 3D dependency intelligence engine and architectural sentinel. It allows developers to visualize, govern, and refactor complex codebases using hardware-accelerated 3D graphs and AI-powered reasoning.

## 🚀 Key Features

-   **Multi-Language Perception:** Native AST extraction for Python, JavaScript, TypeScript (TSX), and Go using Tree-sitter.
-   **Real-Time Reflexes:** Watchdog-based filesystem monitoring with WebSocket broadcasting for instant 3D updates as you code.
-   **Architectural Governance:** Strict enforcement of design boundaries via `.pheonix.yml` (e.g., "UI cannot import from Database").
-   **Intelligence Layer:** On-demand architectural refactoring strategies powered by Google Gemini 1.5 Flash.
-   **LOD Scaling:** Level-of-Detail API endpoints for high-performance rendering of massive repositories (10k+ nodes).
-   **QE Framework:** Self-verifying pipeline with a "Golden Dataset" regression suite and deep "Flight Data Recorder" diagnostics.
-   **CI/CD Ready:** CLI Gatekeeper and GitHub Action integration to block architectural violations in PRs.

## 🛠️ Architecture

```
Codebase → Tree-sitter (Parse) → Normalizer (Resolve) → RuleEngine (Enforce) → 3D UI (Visualize)
```

-   **Backend:** FastAPI (Python), multiprocessing parser workers, SQLite cache.
-   **Frontend:** React, TypeScript, Three.js (3d-force-graph) with O(1) adjacency optimization.
-   **AI:** Gemini 1.5 Flash for structural reasoning.

## 🚦 Getting Started

### Prerequisites
-   Python 3.11+
-   Node.js 18+
-   Google Gemini API Key (optional, for AI features)

### Installation
1.  **Clone the repo:**
    ```bash
    git clone https://github.com/fallofpheonix/PheonixVirtualizer
    cd PheonixVirtualizer
    ```

2.  **Setup Backend:**
    ```bash
    pip install -r backend/requirements.txt
    export GOOGLE_API_KEY=your_key_here
    python backend/app/main.py
    ```

3.  **Setup Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

4.  **Run CLI Analysis:**
    ```bash
    python backend/cli.py --path . --fail-on high
    ```

## 📜 Governance (.pheonix.yml)
Define your architectural laws in the project root:
```yaml
project_name: "MyProject"
rules:
  - id: "layer-violation"
    severity: "high"
    message: "Core logic must not depend on external API adapters."
    from_path: "src/core/"
    to_path: "src/adapters/api/"
    action: "DENY"
```

## 🛡️ License
MIT

---
**Witness the fate of your code. Enforce the order of your design.**
