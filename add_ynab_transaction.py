#!/usr/bin/env python3
"""Add a transfer transaction to YNAB.

Transaction: Chequing (1781) -> MasterCard (0167), $2,515.02, May 20 2026
"""

import json
import urllib.request
import urllib.error

ACCESS_TOKEN = "b9F8psbEjOQ-F27FkMH--zCPTKgTrVbeep2jETXTXxg"
BUDGET_ID = "feb1a2ca-2ccc-4e3c-b619-dfb54770e039"
BASE_URL = f"https://api.ynab.com/v1/budgets/{BUDGET_ID}"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


def api_get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def api_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def find_account(accounts, last_four):
    for a in accounts:
        if not a["deleted"] and str(a.get("last_four", "")) == last_four:
            return a
    return None


def main():
    print("Fetching accounts...")
    data = api_get("/accounts")
    accounts = data["data"]["accounts"]

    chequing = find_account(accounts, "1781")
    mastercard = find_account(accounts, "0167")

    if not chequing:
        print("ERROR: Could not find Chequing account ending in 1781")
        print("Available accounts:")
        for a in accounts:
            if not a["deleted"]:
                print(f"  {a['name']} (last four: {a.get('last_four', 'N/A')})")
        return

    if not mastercard:
        print("ERROR: Could not find MasterCard account ending in 0167")
        print("Available accounts:")
        for a in accounts:
            if not a["deleted"]:
                print(f"  {a['name']} (last four: {a.get('last_four', 'N/A')})")
        return

    print(f"Found: {chequing['name']} (id: {chequing['id']})")
    print(f"Found: {mastercard['name']} (id: {mastercard['id']})")

    # YNAB amounts are in milliunits (1000 = $1.00), outflow is negative
    amount_milliunits = -2_515_020  # -$2,515.02

    payload = {
        "transaction": {
            "account_id": chequing["id"],
            "date": "2026-05-20",
            "amount": amount_milliunits,
            "payee_id": None,
            "payee_name": None,
            "transfer_account_id": mastercard["id"],
            "memo": "MasterCard payment",
            "cleared": "cleared",
            "approved": True,
        }
    }

    print("\nCreating transfer transaction...")
    result = api_post("/transactions", payload)
    txn = result["data"]["transaction"]
    print(f"Success! Transaction ID: {txn['id']}")
    print(f"  Date:   {txn['date']}")
    print(f"  Amount: ${abs(txn['amount']) / 1000:.2f}")
    print(f"  From:   {chequing['name']}")
    print(f"  To:     {mastercard['name']}")


if __name__ == "__main__":
    main()
