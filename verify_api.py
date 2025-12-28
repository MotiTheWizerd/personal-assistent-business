import subprocess
import time
import urllib.request
import json
import os
import sys

def verify_api():
    # Start the server
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--port", "8001"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Starting server on port 8001...")
    time.sleep(5)  # Wait for server to start

    try:
        # 1. Create Manager
        url = "http://localhost:8001/api/managers/"
        data = {
            "first_name": "Test",
            "last_name": "Manager",
            "username": "testmanager",
            "email": "test@example.com",
            "password": "securepassword123"
        }
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print("Create API Response:", result)
            assert result["first_name"] == "Test"
            assert result["email"] == "test@example.com"
            assert "id" in result
            assert "password" not in result # Password should not be returned

        # 2. List Managers
        with urllib.request.urlopen("http://localhost:8001/api/managers/") as response:
            result = json.loads(response.read().decode())
            print("List API Response:", result)
            assert len(result) >= 1
            assert result[0]["username"] == "testmanager"

        print("VERIFICATION SUCCESSFUL!")

    except Exception as e:
        print(f"VERIFICATION FAILED: {e}")
        outs, errs = proc.communicate(timeout=1)
        print("Server Output:", outs.decode())
        print("Server Errors:", errs.decode())
        
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    verify_api()
