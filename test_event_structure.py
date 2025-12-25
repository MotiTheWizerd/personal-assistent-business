import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.modules.shared.domain.bus import InMemoryEventBus
from src.modules.example.user_created import UserCreated

def on_user_created(event: UserCreated):
    print(f"HANDLER: User created! Username: {event.username}, Email: {event.email}")
    print(f"HANDLER: Event ID: {event.event_id}, Occurred On: {event.occurred_on}")

def main():
    print("Setting up Event Bus...")
    bus = InMemoryEventBus()

    print("Subscribing to UserCreated event...")
    bus.subscribe(UserCreated, on_user_created)

    print("Publishing UserCreated event...")
    event = UserCreated(username="jdoe", email="jdoe@example.com")
    bus.publish(event)
    
    print("Done.")

if __name__ == "__main__":
    main()
