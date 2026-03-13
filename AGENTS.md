# AGENTS.md

## Purpose
This file defines execution commands and coding conventions for coding agents working in this repository.
Project: SkyBalance tree visualizer (Flask backend + static frontend).

## Repository Layout
- `backend/app.py`: Flask API entrypoint.
- `backend/models/`: tree models (`avl.py`, `bst.py`, `node.py`).
- `backend/services/`: service layer (currently sparse/empty).
- `backend/structures/`: helper data structures.
- `frontend/index.html`: main UI.
- `frontend/js/`: frontend scripts (currently mostly empty).
- `frontend/css/`: styles.
- `data/`: JSON samples (`ModoTopologia.json`, `ModoInsercion.json`).

## Environment Baseline
- Python: 3.8+
- OS: Windows-first development, but keep commands portable when possible.
- Backend dependencies used in code: `flask`, `flask-cors`.

## Setup Commands
1. Create virtual environment:
```powershell
python -m venv .venv
```
2. Activate on PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```
3. Install dependencies:
```powershell
pip install flask flask-cors
```
4. Optional (if requirements file is added later): `pip install -r backend/requirements.txt`

## Run Commands
1. Start backend API:
```powershell
cd backend
python app.py
```
2. Start frontend static server:
```powershell
cd frontend
python -m http.server 8000
```
3. Open frontend URL:
- `http://localhost:8000`

## Build / Compile Commands
This project is interpreted (no binary build), but syntax checks are required.

1. Compile all backend Python files:
```powershell
Get-ChildItem backend -Recurse -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }
```
2. Compile a single Python file:
```powershell
python -m py_compile backend/app.py
```

## Lint / Format Commands
No linter is enforced in-repo yet. Preferred local checks:

1. Basic Python style check (if installed):
```powershell
python -m flake8 backend
```
2. Python formatting (if installed):
```powershell
python -m black backend
```
3. If ESLint is introduced, lint `frontend/js` and keep config in repo root.
If tooling is not installed, do not block delivery.

## Test Commands
There are currently no committed test files. Use these commands as standard once tests exist.

1. Run all unittest tests:
```powershell
python -m unittest discover -s backend -p "test_*.py"
```
2. Run a single unittest module:
```powershell
python -m unittest backend.tests.test_avl
```
3. Run a single unittest test case/method:
```powershell
python -m unittest backend.tests.test_avl.TestAVL.test_insert_balances
```
4. If pytest is adopted, run all tests:
```powershell
python -m pytest
```
5. If pytest is adopted, run one test:
```powershell
python -m pytest backend/tests/test_avl.py::TestAVL::test_insert_balances
```

## API Validation Commands
Quick smoke checks with PowerShell:

1. Insert node:
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/insert -ContentType "application/json" -Body '{"valor":10,"modo":"AVL"}'
```
2. Delete node:
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/delete -ContentType "application/json" -Body '{"valor":10,"modo":"AVL"}'
```
3. Traversal:
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/traversal -ContentType "application/json" -Body '{"modo":"AVL","tipo":"inorder"}'
```

## Coding Style - General
- Keep changes minimal and task-focused.
- Preserve existing architecture unless explicitly refactoring.
- Avoid dead code and commented-out legacy blocks.
- Prefer small functions with single responsibility.

## Coding Style - Python
- Follow PEP 8 for new code.
- Indentation: 4 spaces.
- Naming:
  - `snake_case` for functions/variables.
  - `PascalCase` for classes.
  - `UPPER_SNAKE_CASE` for constants.
- Type hints:
  - Add type hints for new/modified public methods.
  - Use `Optional[T]`, `list[T]`, `dict[str, Any]` as appropriate.
- Docstrings:
  - Add concise docstrings to public classes/functions.
- Imports order:
  1. Standard library
  2. Third-party
  3. Local modules
- Keep one import per line unless tightly related.

## Python Compatibility Rule
Current model classes use camelCase getters/setters (`getValue`, `setParent`, etc.).
- Do not rename existing public methods unless the task requires a migration.
- New internal helper methods should use snake_case.
- For compatibility layers, prefer wrappers over breaking API changes.

## Error Handling
- Do not use bare `except:`.
- Catch specific exceptions where possible.
- In Flask endpoints, return structured JSON errors with HTTP codes.
- Validate request payloads before operating on trees.
- Avoid `print` for recoverable errors in API paths; return JSON messages.

## Data and Serialization Rules
- Keep API response shapes stable (`{"arbol": ...}`, `{"resultado": ...}`).
- For tree serialization, include only required fields for frontend rendering.
- If adding flight metadata, ensure backward-compatible defaults.
- Never hardcode local file paths for JSON input.

## Frontend Style
- Use `const`/`let` (avoid `var` in new code).
- Use camelCase for JS identifiers.
- Keep DOM IDs/classes meaningful and consistent.
- Move inline script logic from HTML to `frontend/js/*.js` when touching related areas.
- Keep UI text in Spanish unless task states otherwise.

## Tree Logic Constraints
- Preserve BST ordering rules strictly.
- AVL operations must keep balance after insert/delete.
- Traversal outputs must remain deterministic and API-compatible.
- For delete/cancel semantics, document whether descendants are affected.

## Change Checklist for Agents
- Code runs locally with backend start command.
- Syntax check passes (`py_compile`).
- Modified endpoints tested with at least one API call.
- No unrelated files changed.
- Update this file if new mandatory tools are introduced.

## Cursor / Copilot Rules Status
Checked paths:
- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`

Current status: no project-level Cursor/Copilot rule files were found.
If these files are later added, agents must treat them as higher-priority project instructions.
