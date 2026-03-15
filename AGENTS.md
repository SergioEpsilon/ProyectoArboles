# AGENTS.md

## Project Overview
SkyBalance: Flask backend + static frontend tree visualizer (AVL/BST).

## Repository Layout
- `backend/app.py` - Flask API entrypoint
- `backend/models/` - Tree models (`avl.py`, `bst.py`, `node.py`)
- `backend/services/` - Business logic (`tree_serializer.py`, `tree_service.py`, `flight_factory.py`)
- `backend/structures/` - Helper data structures
- `frontend/index.html` - Main UI
- `frontend/js/` - Frontend scripts (`main.js`, `api.js`, `render.js`)
- `data/` - JSON sample files

## Environment
- Python: 3.8+
- Dependencies: `flask`, `flask-cors`
- OS: Windows-first (keep commands portable)

## Setup & Run
```powershell
# Setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask flask-cors

# Run backend
cd backend && python app.py

# Run frontend (separate terminal)
cd frontend && python -m http.server 8000
```

## Build & Lint
```powershell
# Compile all Python files
Get-ChildItem backend -Recurse -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }

# Single file
python -m py_compile backend/app.py

# Lint (if installed)
python -m flake8 backend
python -m black backend
```

## Test Commands
```powershell
# Unittest
python -m unittest discover -s backend -p "test_*.py"
python -m unittest backend.tests.test_avl
python -m unittest backend.tests.test_avl.TestAVL.test_insert_balances

# Pytest (if adopted)
python -m pytest
python -m pytest backend/tests/test_avl.py::TestAVL::test_insert_balances
```

## API Smoke Tests (PowerShell)
```powershell
# Insert
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/insert -ContentType "application/json" -Body '{"valor":10,"modo":"AVL"}'

# Delete
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/delete -ContentType "application/json" -Body '{"valor":10,"modo":"AVL"}'

# Modify
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/modify -ContentType "application/json" -Body '{"old_valor":40,"new_valor":35,"modo":"AVL","codigo":"NEW","origen":"A","destino":"B"}'

# Export
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/export-json -ContentType "application/json" -Body '{"modo":"AVL"}'
```

## Python Code Style

### Naming Conventions
- `snake_case` - functions, variables, methods
- `PascalCase` - classes
- `UPPER_SNAKE_CASE` - constants

### Type Hints (Required for New Code)
```python
from typing import Optional, Dict, List, Any

def process_node(node: Optional[Node], data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pass
```

### Imports Order
1. Standard library (`from __future__`, `typing`, etc.)
2. Third-party (`flask`, `flask_cors`)
3. Local modules (`from models...`, `from services...`)

One import per line unless tightly related.

### Docstrings
Use concise docstrings for public classes/functions:
```python
class TreeSerializer:
    """Converts tree nodes to/from dictionaries for frontend, snapshots, and export."""
```

### Error Handling
- NEVER use bare `except:` - catch specific exceptions
- Return structured JSON errors with HTTP codes in Flask
- Validate request payloads before tree operations
- Use `try/except` in API endpoints:
```python
try:
    result = process_data(data)
except ValueError as exc:
    return jsonify({"error": str(exc)}), 422
```

### Python Compatibility Rule
Legacy models use camelCase getters/setters (`getValue`, `setParent`, etc.):
- Do NOT rename existing public methods
- New internal helpers use `snake_case`
- Use wrappers for compatibility, not breaking changes

## JavaScript Code Style

### Naming
- `camelCase` for all identifiers
- Meaningful variable/function names
- DOM IDs: lowercase with hyphens (`flight-modal`, `val-input`)

### Best Practices
- Use `const`/`let` - never `var` in new code
- Prefer arrow functions for callbacks
- Keep DOM manipulation in `render.js`
- UI text in Spanish unless task specifies otherwise

## Data Serialization Rules

### API Responses (Stable Contracts)
```json
{"arbol": {...}}      // Tree for frontend
{"resultado": [...]}  // Traversal results
{"error": "..."}     // Error messages
```

### Export Format (`/export-json`)
- Must serialize hierarchical structure via `left`/`right` keys
- Include per-node: `value`, `height`, `balance_factor`, `metadata`
- Include business fields: `base_price`, `final_price`, `passengers`, `priority`

### Never Hardcode
- Local file paths for JSON input
- Assume specific node value ranges

## Tree Logic Constraints
- BST: strict ordering (left < parent < right)
- AVL: must maintain balance after insert/delete
- `delete` - removes single node, follows BST rules
- `cancel` - removes node + all descendants
- `modify` - delete old + insert new (same tree mode)

## Change Checklist (Required)
- [ ] Code runs with `python app.py`
- [ ] Syntax check passes (`py_compile`)
- [ ] At least one API endpoint tested
- [ ] No unrelated files modified
- [ ] Frontend export matches tree state

## Current API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/insert` | Insert flight node |
| POST | `/delete` | Delete single node |
| POST | `/modify` | Modify node (delete + insert) |
| POST | `/cancel` | Remove node + subtree |
| POST | `/undo` | Revert last action |
| POST | `/clear` | Clear tree |
| POST | `/traversal` | Inorder/preorder/postorder |
| POST | `/load-json` | Load from JSON file |
| POST | `/export-json` | Export tree to JSON |

## Cursor/Copilot Rules
No project-level rules found. If added later to `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md`, treat as higher-priority instructions.