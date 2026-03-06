import requests
import random
import time

TASKROUTE_URL = "http://127.0.0.1:8000/optimize"

# tasks our agent might want to perform
TASK_TYPES = [
    "image_generation",
    "text_generation",
    "data_processing"
]

# starting capital for the agent
INITIAL_AGENT_BUDGET = 0.10


def decide_priority(task):
    """
    Simple reasoning layer that decides what matters most
    depending on the task.
    """

    if task == "image_generation":
        return "quality"

    if task == "text_generation":
        return "cost"

    if task == "data_processing":
        return "speed"

    return "cost"


def run_agent():

    remaining_budget = INITIAL_AGENT_BUDGET
    provider_history = {}

    print("\n==============================")
    print("Autonomous Buyer Agent Started")
    print("==============================\n")

    print("Initial Budget:", remaining_budget)
    print()

    for step in range(10):

        if remaining_budget <= 0:
            print("Budget exhausted. Agent shutting down.")
            break

        # choose a task randomly
        task = random.choice(TASK_TYPES)

        # reasoning step
        priority = decide_priority(task)

        print("Step", step + 1)
        print("Task:", task)
        print("Agent Reasoning: prioritizing", priority)

        # request execution plan from TaskRoute
        request_payload = {
            "task_type": task,
            "budget_usd": remaining_budget,
            "priority": priority
        }

        try:
            response = requests.post(TASKROUTE_URL, json=request_payload)
            data = response.json()
        except Exception as e:
            print("Error contacting TaskRoute:", e)
            continue

        if not data.get("ok") or "recommendations" not in data:
            print("TaskRoute error:", data.get("error", "Unknown error. No recommendations."))
            print()
            continue

        best = data["recommendations"]["best_cost"]

        provider = best["provider"]
        model = best["name"]
        cost = best["estimated_cost"]

        # check if budget allows execution
        if cost > remaining_budget:
            print("Task skipped. Cost exceeds remaining budget.")
            print()
            continue

        # deduct cost
        remaining_budget -= cost

        # update provider usage history
        provider_history[provider] = provider_history.get(provider, 0) + 1

        print("Selected Provider:", provider)
        print("Model:", model)
        print("Execution Cost:", cost)
        print("Remaining Budget:", round(remaining_budget, 4))

        if provider_history[provider] > 3:
            print("Observation: provider heavily used. May consider alternatives.")

        print("---------------------------------\n")

        time.sleep(2)


if __name__ == "__main__":
    run_agent()