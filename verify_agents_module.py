import requests
import sys
import os
import json
from dotenv import load_dotenv

# Ensure src is in pythonpath
sys.path.append(os.getcwd())
load_dotenv()

def check(response, expected_status=200):
    if response.status_code != expected_status:
        print(f"FAILED: Expected {expected_status}, got {response.status_code}")
        print(response.text)
        sys.exit(1)
    return response.json()

def main():
    print("Skipping database reset to preserve data...")
    # reset_db()
    
    base_url = "http://localhost:8000"
    
    # Check for MISTRAL_API_KEY
    if not os.getenv("MISTRAL_API_KEY"):
        print("WARNING: MISTRAL_API_KEY not found in .env. Agent chat might fail.")
    
    import time
    timestamp = int(time.time())
    
    # 1. Create a Manager
    print("\n1. Creating Manager...")
    manager_data = {
        "first_name": "Agent",
        "last_name": "Manager",
        "username": f"agent_mgr_{timestamp}",
        "email": f"agent.mgr.{timestamp}@example.com",
        "password": "secretpassword"
    }
    response = requests.post(f"{base_url}/managers/", json=manager_data)
    manager = check(response)
    manager_id = manager["id"]
    
    # 2. Create an Agent
    print("2. Creating Agent...")
    agent_data = {
        "name": f"mistral_helper_{timestamp}",
        "description": "Helper agent using Mistral",
        "model": "mistral/mistral-small-latest",
        "instruction": "You are a helpful assistant.",
        "manager_id": manager_id
    }
    response = requests.post(f"{base_url}/agents/", json=agent_data)
    agent_response = check(response, 201)
    agent_id = agent_response["id"]
    print(f"Agent created with ID: {agent_id}")

    # 3. Chat with Agent
    print("3. Chatting with Agent...")
    chat_request = {
        "query": "Hello, who are you?",
        "session_id": "verify_session_1"
    }
    response = requests.post(f"{base_url}/agents/{agent_id}/chat", json=chat_request)
    chat_response = check(response)
    print(f"Agent Response: {chat_response['response']}")
    
    print("\nSUCCESS: Agents module verification passed!")

if __name__ == "__main__":
    main()
