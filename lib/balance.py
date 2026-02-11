#!/usr/bin/env python3
"""
Check kie.ai account balance and credit usage

Note: kie.ai API doesn't currently expose a balance endpoint.
This script provides local tracking and directs users to the web UI.
"""

import json
import os
import sys
from pathlib import Path

def get_local_usage():
    """Get local task history and estimate usage"""
    state_file = Path.home() / ".openclaw" / "workspace" / "skills" / "kie-ai" / ".task-state.json"
    
    if not state_file.exists():
        return []
    
    try:
        with open(state_file) as f:
            state = json.load(f)
            # State is a dict of task_id -> task_data
            return list(state.values())
    except:
        return []


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Check kie.ai account balance")
    parser.add_argument("--local", action="store_true", help="Show local usage tracking only")
    
    args = parser.parse_args()
    
    print("💰 kie.ai Account Balance")
    print("=" * 50)
    print("")
    print("⚠️  Balance API not available")
    print("")
    print("The kie.ai API doesn't currently expose account balance")
    print("information. To check your balance:")
    print("")
    print("  Web UI:  https://kie.ai/logs")
    print("  Billing: https://kie.ai/billing")
    print("")
    
    # Show local usage tracking
    tasks = get_local_usage()
    
    if tasks:
        print("📊 Local Task History")
        print("=" * 50)
        
        # Count tasks by model
        model_counts = {}
        for task in tasks:
            model = task.get("model", "unknown")
            model_counts[model] = model_counts.get(model, 0) + 1
        
        total_tasks = len(tasks)
        print(f"Total tasks:        {total_tasks}")
        print("")
        print("By model:")
        for model, count in sorted(model_counts.items(), key=lambda x: -x[1]):
            print(f"  {model:<20} {count:>4} tasks")
        
        print("")
        print("Estimated cost:")
        
        # Estimate credits (rough)
        credit_estimates = {
            "nano-banana-pro": 20,
            "google/nano-banana": 4,
            "flux-kontext": 50,
        }
        
        total_credits = 0
        for model, count in model_counts.items():
            est = credit_estimates.get(model, 20)  # Default 20
            model_total = est * count
            total_credits += model_total
            print(f"  {model:<20} ~{model_total:>6.0f} credits")
        
        print(f"  {'TOTAL':<20} ~{total_credits:>6.0f} credits")
        print(f"  {'(USD)':<20} ~${total_credits * 0.005:>6.2f}")
        print("")
        print("Note: These are estimates based on typical pricing.")
        print("Check the web UI for actual consumption.")
    else:
        print("No local task history found.")
        print("")
    
    print("")
    print("💡 Tip: kie.ai logs page shows exact credit usage per task")


if __name__ == "__main__":
    main()
