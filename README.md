# SkyBalance

A web application for visualizing and managing binary search trees (BST and AVL) with flight management capabilities.

## Features

- **Tree Visualization**: Interactive SVG rendering of binary trees
- **Tree Operations**: Insert, delete, modify, and cancel flights
- **AVL Balancing**: Automatic self-balancing for AVL trees
- **Undo/Redo**: History stack for reverting operations
- **Versioning**: Save and restore tree snapshots
- **Metrics**: Track rotations and cancellations
- **Queue Simulation**: Process pending insertions with flow control
- **Depth Penalties**: Configure critical depth pricing
- **Stress Mode**: Disable auto-balancing for testing

## Quick Start

### Backend Setup

```powershell
# Create virtual environment
python -m venv .venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install flask flask-cors

# Run backend
cd backend
python app.py
```

### Frontend Setup

```powershell
# In a new terminal
cd frontend
python -m http.server 8000
```

### Access

- Frontend: http://localhost:8000
- Backend API: http://127.0.0.1:5000

## API Endpoints

### Tree Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/insert` | Insert flight node |
| POST | `/delete` | Delete single node |
| POST | `/modify` | Modify node value/metadata |
| POST | `/cancel` | Remove node + subtree |
| POST | `/undo` | Revert last action |
| POST | `/clear` | Clear all nodes |
| POST | `/traversal` | Inorder/preorder/postorder |

### Data Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/load-json` | Load from JSON |
| POST | `/export-json` | Export to JSON |
| POST | `/version/save` | Save version |
| GET | `/version/list` | List versions |
| POST | `/version/restore` | Restore version |

### Queue

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/queue/enqueue` | Add to queue |
| GET | `/queue/list` | View queue |
| POST | `/queue/process` | Process N items |

### Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/metrics` | Get statistics |
| POST | `/metrics/reset` | Reset counters |

## JSON Format

### Flight Metadata

```json
{
  "codigo": "SB100",
  "origen": "NYC",
  "destino": "LAX",
  "horaSalida": "10:00",
  "precioBase": 500,
  "precioFinal": 450,
  "pasajeros": 150,
  "prioridad": 1,
  "promocion": false,
  "alerta": false
}
```

### Insertion Mode JSON

```json
{
  "vuelos": [
    {"codigo": "SB100", "origen": "NYC", ...},
    {"codigo": "SB050", "origen": "LAX", ...}
  ]
}
```

### Topology Mode JSON

```json
{
  "codigo": "SB100",
  "origen": "NYC",
  "izquierdo": {
    "codigo": "SB050",
    "izquierdo": null,
    "derecho": null
  },
  "derecho": null
}
```

## Project Structure

```
SkyBalance/
├── backend/
│   ├── app.py              # Flask entry point
│   ├── models/             # Tree models
│   │   ├── node.py
│   │   ├── base_tree.py
│   │   ├── bst.py
│   │   └── avl.py
│   ├── services/          # Business logic
│   ├── routes/           # Flask blueprints
│   └── tests/            # Unit tests
├── frontend/
│   ├── index.html        # Main UI
│   ├── js/               # JavaScript
│   └── css/              # Styles
├── data/                 # Sample JSON files
├── test_rotations.py      # Integration tests
└── README.md
```

## Technologies

- **Backend**: Flask, Python 3.8+
- **Frontend**: Vanilla JavaScript, SVG, CSS3
- **No database**: In-memory storage

## License

MIT