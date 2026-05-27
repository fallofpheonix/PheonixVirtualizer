# Contributing to PheonixVirtualizer

Thank you for your interest in contributing to PheonixVirtualizer! We welcome all contributions, from bug reports to new feature implementations and parser expansions.

## 🚀 How to Contribute

### 1. Reporting Bugs
-   Use the [GitHub Issue Tracker](https://github.com/fallofpheonix/PheonixVirtualizer/issues).
-   Include a clear description, reproduction steps, and a snippet of the code that caused the issue.

### 2. Feature Requests
-   Open an issue to discuss your idea before starting implementation.
-   Focus on the "Intelligence" or "Breadth" frontiers.

### 3. Parser Support
-   We use [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) for AST extraction.
-   If you want to add support for a new language:
    1.  Create a new parser class in `backend/app/parsers/`.
    2.  Implement the `BaseParser` interface.
    3.  Add the language grammar to `backend/requirements.txt`.
    4.  Register the parser in `ParserFactory`.

### 4. Pull Request Process
-   Ensure all tests in the **QE Framework** pass: `pytest tests/test_scenarios.py`.
-   Add a new test scenario in `tests/fixtures/scenarios/` if you are adding logic.
-   Include an entry in `.pheonix.yml` if your change introduces new architectural laws.

## 🛠️ Development Setup
See the [README.md](./README.md) for installation and setup instructions.

## 📜 Code of Conduct
Please be respectful and professional in all interactions. See our [Code of Conduct](./CODE_OF_CONDUCT.md) for details.
