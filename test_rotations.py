#!/usr/bin/env python
"""Test rotation tracking with guaranteed rotation scenarios."""
import json
import urllib.request

BASE_URL = "http://127.0.0.1:5000"

def api_call(method, endpoint, data=None):
    """Helper to make API calls."""
    url = f"{BASE_URL}{endpoint}"
    if data:
        payload = json.dumps(data).encode('utf-8')
    else:
        payload = None
    
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"} if data else {},
            method=method
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode())
        return {"error": error_data}

def test_rotations():
    """Test scenarios that guarantee AVL rotations."""
    
    print("=== Clean start ===")
    api_call("POST", "/clear", {})
    
    print("\n=== Test: LL Case Rotation ===")
    print("Inserting: 30, 20, 10 (should trigger LL rotation)")
    
    for val in [30, 20, 10]:
        result = api_call("POST", "/insert", {"valor": val, "modo": "AVL"})
        print(f"  Inserted {val}")
    
    metrics = api_call("GET", "/metrics?modo=AVL", None)
    print(f"  LL rotations: {metrics['rotations']['LL']} (expected: 1)")
    print(f"  Total rotations: {metrics['total_rotations']} (expected: 1)")
    print(f"  Structural: nodes={metrics['structural']['nodes']}, height={metrics['structural']['height']}")
    
    print("\n=== Test: RR Case Rotation ===")
    api_call("POST", "/clear", {})
    print("Inserting: 10, 20, 30 (should trigger RR rotation)")
    
    for val in [10, 20, 30]:
        result = api_call("POST", "/insert", {"valor": val, "modo": "AVL"})
        print(f"  Inserted {val}")
    
    metrics = api_call("GET", "/metrics?modo=AVL", None)
    print(f"  RR rotations: {metrics['rotations']['RR']} (expected: 1)")
    print(f"  Total rotations: {metrics['total_rotations']} (expected: 1)")
    print(f"  Structural: nodes={metrics['structural']['nodes']}, height={metrics['structural']['height']}")
    
    print("\n=== Test: LR Case Rotation ===")
    api_call("POST", "/clear", {})
    print("Inserting: 30, 10, 20 (should trigger LR rotation)")
    
    for val in [30, 10, 20]:
        result = api_call("POST", "/insert", {"valor": val, "modo": "AVL"})
        print(f"  Inserted {val}")
    
    metrics = api_call("GET", "/metrics?modo=AVL", None)
    print(f"  LR rotations: {metrics['rotations']['LR']} (expected: 1)")
    print(f"  Total rotations: {metrics['total_rotations']} (expected: 1)")
    print(f"  Structural: nodes={metrics['structural']['nodes']}, height={metrics['structural']['height']}")
    
    print("\n=== Test: RL Case Rotation ===")
    api_call("POST", "/clear", {})
    print("Inserting: 10, 30, 20 (should trigger RL rotation)")
    
    for val in [10, 30, 20]:
        result = api_call("POST", "/insert", {"valor": val, "modo": "AVL"})
        print(f"  Inserted {val}")
    
    metrics = api_call("GET", "/metrics?modo=AVL", None)
    print(f"  RL rotations: {metrics['rotations']['RL']} (expected: 1)")
    print(f"  Total rotations: {metrics['total_rotations']} (expected: 1)")
    print(f"  Structural: nodes={metrics['structural']['nodes']}, height={metrics['structural']['height']}")
    
    print("\n=== Test: Multiple Rotations ===")
    api_call("POST", "/clear", {})
    print("Inserting: 50,25,75,10,30,60,80,5,15 (should trigger multiple rotations)")
    
    for val in [50, 25, 75, 10, 30, 60, 80, 5, 15]:
        result = api_call("POST", "/insert", {"valor": val, "modo": "AVL"})
        print(f"  Inserted {val}", end="")
        metrics = api_call("GET", "/metrics?modo=AVL", None)
        print(f" → Total rotations so far: {metrics['total_rotations']}")
    
    final_metrics = api_call("GET", "/metrics?modo=AVL", None)
    print(f"\nFinal metrics:")
    print(f"  LL={final_metrics['rotations']['LL']}, LR={final_metrics['rotations']['LR']}, "
          f"RR={final_metrics['rotations']['RR']}, RL={final_metrics['rotations']['RL']}")
    print(f"  Total rotations: {final_metrics['total_rotations']}")
    print(f"  Nodes: {final_metrics['structural']['nodes']}, Height: {final_metrics['structural']['height']}")

if __name__ == "__main__":
    print("Testing AVL Rotation Tracking...")
    print(f"Backend URL: {BASE_URL}\n")
    test_rotations()
    print("\n=== Rotation tests completed ===")
