# main.py
import time
from src.environment import Environment

def run_simulation():
    """Initializes and runs the logistics simulation."""
    # Create the environment
    env = Environment()

    # Print the initial state
    env.get_status_report()

    # Run the simulation for 10 "ticks" (i.e., 10 minutes)
    for i in range(10):
        env.tick()
        # In a real simulation, you'd update driver positions here
        env.get_status_report()
        time.sleep(1) # Pause for 1 second to make the simulation readable

    print("\n🏁 Simulation finished.")

if __name__ == "__main__":
    run_simulation()