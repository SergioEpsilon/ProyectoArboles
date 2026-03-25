#!/usr/bin/env python
"""Quick test of metrics endpoints after initialization fix."""
import json
import urllib.request
import time

BASE_URL = "http://127.0.0.1:5000"

def test_insert_and_metrics():
    """Test insertion and verify metrics track changes."""
    
    # Test 1: Initial metrics (empty tree)
    print("=== Test 1: Initial metrics (empty tree) ===")
    try:
        resp = urllib.request.urlopen(f"{BASE_URL}/metrics?modo=AVL")
        data = json.loads(resp.read().decode())
        print(json.dumps(data, indent=2))
        print(f"Nodes: {data['structural']['nodes']}")
        print(f"Rotations (all): {data['total_rotations']}")
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    # Test 2: Insert node
    print("\n=== Test 2: Insert node (valor=10) ===")
    try:
        payload = json.dumps({"valor": 10, "modo": "AVL"}).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}/insert",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"Inserted successfully. Tree has {data['arbol']['nodes'] if isinstance(data['arbol'], dict) else 'unknown'} nodes")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 3: Check metrics after insertion
    print("\n=== Test 3: Metrics after insertion ===")
    try:
        resp = urllib.request.urlopen(f"{BASE_URL}/metrics?modo=AVL")
        data = json.loads(resp.read().decode())
        print(json.dumps(data, indent=2))
        print(f"Nodes: {data['structural']['nodes']} (expected: 1)")
        print(f"Height: {data['structural']['height']} (expected: 0)")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 4: Insert multiple nodes to trigger rotation
    print("\n=== Test 4: Insert nodes to trigger rotation (20, 5, 15) ===")
    for val in [20, 5, 15]:
        try:
            payload = json.dumps({"valor": val, "modo": "AVL"}).encode('utf-8')
            req = urllib.request.Request(
                f"{BASE_URL}/insert",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                print(f"Inserted {val}")
        except Exception as e:
            print(f"ERROR inserting {val}: {e}")
    
    # Test 5: Check metrics with rotations
    print("\n=== Test 5: Metrics after multiple insertions (check for rotations) ===")
    try:
        resp = urllib.request.urlopen(f"{BASE_URL}/metrics?modo=AVL")
        data = json.loads(resp.read().decode())
        print(json.dumps(data, indent=2))
        print(f"Total Rotations: {data['total_rotations']} (may be > 0 if balancing occurred)")
        print(f"Nodes: {data['structural']['nodes']} (expected: 4)")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 6: Reset metrics
    print("\n=== Test 6: Reset metrics ===")
    try:
        payload = json.dumps({}).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}/metrics/reset",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            print(f"Reset result: {result}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 7: Verify reset
    print("\n=== Test 7: Metrics after reset (counters should be 0) ===")
    try:
        resp = urllib.request.urlopen(f"{BASE_URL}/metrics?modo=AVL")
        data = json.loads(resp.read().decode())
        print(json.dumps(data, indent=2))
        print(f"Rotation counters after reset: LL={data['rotations']['LL']}, LR={data['rotations']['LR']}, RR={data['rotations']['RR']}, RL={data['rotations']['RL']}")
        print(f"Cancellations after reset: {data['cancellations']}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("Testing Metrics API...")
    print(f"Backend URL: {BASE_URL}\n")
    test_insert_and_metrics()
    print("\n=== All tests completed ===")
