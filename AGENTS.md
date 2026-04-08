# AGENTS.md

## Project Overview
SkyBalance: Flask backend + static frontend tree visualizer (AVL/BST) with critical depth penalties and stress testing.

## Repository Layout
- `backend/app.py` - Flask API entrypoint (single tree instances, in-memory state)
- `backend/models/` - Tree models (`base_tree.py`, `avl.py`, `bst.py`, `node.py`, `tree_printer.py`)
- `backend/services/` - Business logic (8 services: tree_serializer, tree_service, flight_factory, history, version, queue_persistence, metrics, depth_penalty)
- `backend/routes/` - Flask Blueprints (`depth_routes.py`, `stress_routes.py`)
- `backend/structures/` - Helper data structures (`cola.py`, `pila.py`)
- `backend/tests/` - Unit tests (`test_tree_models.py`, `test_tree_service.py`)
- `test_*.py` (root) - Integration/API tests (`test_metrics.py`, `test_rotations.py`) - run against live backend
- `frontend/` - Static UI (HTML/CSS/JS) with grid visualization
- `data/` - JSON configs + persistence files

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
cd backend; python app.py

# Run frontend (separate terminal)
cd frontend; python -m http.server 8000
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

### Unit Tests (in `backend/tests/`)
```powershell
# All unit tests
python -m unittest discover -s backend/tests -p "test_*.py"

# Single test file
python -m unittest backend.tests.test_tree_models
python -m unittest backend.tests.test_tree_service

# Single test case (requires live backend)
python -m unittest backend.tests.test_tree_models.TestAVL.test_ll_rotation_balances_tree
```

### Integration Tests (root level - requires backend running on port 5000)
```powershell
# Start backend first in separate terminal:
cd backend; python app.py

# Then run integration tests:
python test_metrics.py           # Test metrics tracking after inserts
python test_rotations.py         # Test AVL rotation scenarios
```

### Quick Compile Check (all Python files)
```powershell
Get-ChildItem backend -Recurse -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }
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

# Metrics
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:5000/metrics?modo=AVL'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/metrics/reset -ContentType "application/json" -Body '{}'

# Queue
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/queue/enqueue -ContentType "application/json" -Body '{"valor":25,"modo":"AVL","flow_id":1}'
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:5000/queue/list?modo=AVL'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/queue/process -ContentType "application/json" -Body '{"modo":"AVL","flow_slots":3}'

# Versioning
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/version/save -ContentType "application/json" -Body '{"name":"baseline","modo":"AVL"}'
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:5000/version/list
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/version/restore -ContentType "application/json" -Body '{"name":"baseline","modo":"AVL"}'
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

### Tree Architecture (Current)
- Shared BST/AVL operations live in `BaseTree`.
- `AVL` overrides post-insert behavior to trigger balancing.
- `tree_printer.py` centralizes ASCII tree rendering for both models.
- Keep API-compatible traversal wrappers (`breadthFirstSearch`, `preOrderTraversal`, `inOrderTraversal`, `posOrderTraversal`).

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
| POST | `/version/save` | Save named tree snapshot |
| GET  | `/version/list` | List saved snapshots |
| POST | `/version/restore` | Restore named snapshot |
| POST | `/queue/enqueue` | Enqueue pending insertion |
| GET  | `/queue/list` | List pending insertions |
| POST | `/queue/process` | Process queued insertions |
| GET  | `/metrics` | Read real-time analytics |
| POST | `/metrics/reset` | Reset analytics counters |
| GET  | `/depth-limit/get` | Get critical depth threshold |
| POST | `/depth-limit/set` | Set depth threshold + apply penalties |
| GET  | `/stress/status` | Get stress test status |
| POST | `/stress/enable` | Enable random stress testing |
| POST | `/stress/disable` | Disable stress testing |
| POST | `/stress/rebalance` | Force AVL rebalancing |

## Cursor/Copilot Rules
No project-level rules found (check `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` if added).