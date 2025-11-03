import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"  # Adjust to your API URL

def test_read_bulkhead():
    """Test read operations bulkhead (max 50 concurrent)"""
    results = {
        "success": 0,
        "rejected": 0,
        "errors": 0
    }
    
    def make_request(i):
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=15)
            if response.status_code == 200:
                results["success"] += 1
                print(f"✓ Request {i}: Success")
            elif response.status_code == 503:
                results["rejected"] += 1
                print(f"✗ Request {i}: Rejected (Bulkhead limit)")
            else:
                results["errors"] += 1
                print(f"! Request {i}: Error {response.status_code}")
        except Exception as e:
            results["errors"] += 1
            print(f"! Request {i}: Exception - {str(e)}")
    
    # Send 100 concurrent requests (should reject ~50)
    print("\n=== Testing Read Bulkhead (100 concurrent requests) ===")
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(make_request, i) for i in range(100)]
        for future in as_completed(futures):
            future.result()
    
    print(f"\nResults:")
    print(f"Success: {results['success']}")
    print(f"Rejected (503): {results['rejected']}")
    print(f"Errors: {results['errors']}")

def test_write_bulkhead():
    """Test write operations bulkhead (max 10 concurrent)"""
    results = {
        "success": 0,
        "rejected": 0,
        "errors": 0
    }
    
    def make_request(i):
        try:
            payload = {
                "nombre": f"Test Project {i}",
                "description": f"Test description {i}"
            }
            response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=35)
            if response.status_code in [200, 201]:
                results["success"] += 1
                print(f"✓ Request {i}: Success")
            elif response.status_code == 503:
                results["rejected"] += 1
                print(f"✗ Request {i}: Rejected (Bulkhead limit)")
            else:
                results["errors"] += 1
                print(f"! Request {i}: Error {response.status_code}")
        except Exception as e:
            results["errors"] += 1
            print(f"! Request {i}: Exception - {str(e)}")
    
    # Send 30 concurrent requests (should reject ~20)
    print("\n=== Testing Write Bulkhead (30 concurrent requests) ===")
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(make_request, i) for i in range(30)]
        for future in as_completed(futures):
            future.result()
    
    print(f"\nResults:")
    print(f"Success: {results['success']}")
    print(f"Rejected (503): {results['rejected']}")
    print(f"Errors: {results['errors']}")

def test_mixed_load():
    """Test mixed read/write operations"""
    print("\n=== Testing Mixed Load ===")
    
    def read_request(i):
        try:
            response = requests.get(f"{BASE_URL}/projects")
            print(f"Read {i}: {response.status_code}")
        except Exception as e:
            print(f"Read {i}: Error - {str(e)}")
    
    def write_request(i):
        try:
            payload = {
                "nombre": f"Mixed Test {i}",
                "description": f"Mixed test {i}"
            }
            response = requests.post(f"{BASE_URL}/projects", json=payload)
            print(f"Write {i}: {response.status_code}")
        except Exception as e:
            print(f"Write {i}: Error - {str(e)}")
    
    with ThreadPoolExecutor(max_workers=80) as executor:
        # 60 reads + 20 writes
        futures = []
        for i in range(60):
            futures.append(executor.submit(read_request, i))
        for i in range(20):
            futures.append(executor.submit(write_request, i))
        
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    print("Starting Bulkhead Tests...")
    print("Make sure your API is running!")
    time.sleep(2)
    
    test_read_bulkhead()
    time.sleep(3)
    
    test_write_bulkhead()
    time.sleep(3)
    
    test_mixed_load()