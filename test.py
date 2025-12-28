# @title Import necessary libraries
import os
import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.models.lite_llm import LiteLlm
from google.genai import types # For creating message Content/Parts
from dotenv import load_dotenv  
import warnings
import logging
from src.modules.agents.utils.llm.call_agent_asnyc import call_agent_async

load_dotenv()

# Ignore all warnings
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")


# --- Define Model Constants for easier use ---

# Using Mistral via LiteLLM
# Make sure MISTRAL_API_KEY is set in your .env file
MODEL_MISTRAL = "mistral/mistral-small-latest"

print("\nEnvironment configured.")
AGENT_MODEL = LiteLlm(model=MODEL_MISTRAL)

agent = Agent(
    name="helper_agent",
    model=AGENT_MODEL, # LiteLlm wrapper for Mistral
    description="Helpful assistant",
    instruction="",
    tools=[], # Pass the function directly
)

async def main():
    print(f"Agent '{agent.name}' created using model '{AGENT_MODEL}'.")
    session_service = InMemorySessionService()

    # Define constants for identifying the interaction context
    APP_NAME = "helper_agent_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001" # Using a fixed ID for simplicity

    # Create the specific session where the conversation will happen
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    runner = Runner(
    agent=agent, # The agent we want to run
    app_name=APP_NAME,   # Associates runs with our app
    session_service=session_service # Uses our session manager
)
    print(f"Runner created for agent '{runner.agent.name}'.")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        response = await call_agent_async(user_input, runner, USER_ID, SESSION_ID)
        print(f"Agent: {response}")  
if __name__ == "__main__":
    asyncio.run(main())

