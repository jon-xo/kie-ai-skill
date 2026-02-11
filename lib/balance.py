#!/usr/bin/env python3
"""
Check kie.ai account balance and credit usage
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

API_KEY = os.getenv("KIE_API_KEY")
BASE_URL = "https://api.kie.ai/api/v1"

if not API_KEY:
    print("Error: KIE_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

def get_balance():
    """Get account balance from API"""
    url = f"{BASE_URL}/chat/credit"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("code") == 200:
                return result.get("data", 0.0)
            else:
                return None
    except:
        return None


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
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    args = parser.parse_args()
    
    # Get real balance from API
    balance = get_balance()
    tasks = get_local_usage()
    
    # JSON output mode
    if args.json:
        output = {
            "balance": balance,
            "balance_usd": balance * 0.005 if balance else None,
            "tasks": {
                "total": len(tasks),
                "by_model": {}
            }
        }
        
        if tasks:
            model_counts = {}
            for task in tasks:
                model = task.get("model", "unknown")
                model_counts[model] = model_counts.get(model, 0) + 1
            output["tasks"]["by_model"] = model_counts
        
        print(json.dumps(output, indent=2))
        return
    
    # Human-readable output
    print("💰 kie.ai Balance")
    print("")
    
    if balance is not None:
        balance_usd = balance * 0.005
        print(f"Remaining: {balance:,.0f} credits (${balance_usd:.2f})")
        print("")
        
        # Estimate images remaining
        est_images = int(balance / 20)  # Conservative estimate for Nano Banana Pro
        print(f"~{est_images} images left")
        print("(Nano Banana Pro @ ~20 credits/image)")
        print("")
    else:
        print("⚠️  Could not fetch balance from API")
        print("Check: https://kie.ai/logs")
        print("")
    
    # Show local usage if available
    if tasks:
        # Count tasks by model
        model_counts = {}
        for task in tasks:
            model = task.get("model", "unknown")
            model_counts[model] = model_counts.get(model, 0) + 1
        
        total_tasks = len(tasks)
        
        # Estimate credits used
        credit_estimates = {
            "nano-banana-pro": 20,
            "google/nano-banana": 4,
            "flux-kontext": 50,
        }
        
        total_credits_used = 0
        for model, count in model_counts.items():
            est = credit_estimates.get(model, 20)
            total_credits_used += est * count
        
        used_usd = total_credits_used * 0.005
        
        print(f"Used (local): ~{total_credits_used:,.0f} credits (~${used_usd:.2f})")
        print(f"Tasks: {total_tasks} ({', '.join(f'{count}× {model}' for model, count in model_counts.items())})")
        print("")
    
    print("Web UI: https://kie.ai/logs")


if __name__ == "__main__":
    main()
