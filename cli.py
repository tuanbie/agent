"""Tiny REPL client for coding-agent-server — run this from any machine that
can reach the server (same LAN, over a tunnel, etc.) to "code via CLI" against
it remotely.

Usage:
    AGENT_URL=http://<server-ip>:8787 AGENT_TOKEN=... python cli.py
"""

import os
import sys

import requests

URL = os.environ.get("AGENT_URL", "http://127.0.0.1:8787").rstrip("/")
TOKEN = os.environ.get("AGENT_TOKEN")

HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


def main() -> None:
    try:
        health = requests.get(f"{URL}/health", timeout=10).json()
    except requests.RequestException as exc:
        print(f"Can't reach {URL}: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Connected to {URL}")
    print(f"  model:     {health.get('model')}")
    print(f"  workspace: {health.get('workspace')}")
    print("Type a message and press Enter. Ctrl+C to quit, '/reset' to clear history.\n")

    while True:
        try:
            message = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not message:
            continue

        if message == "/reset":
            requests.post(f"{URL}/reset", headers=HEADERS, timeout=30)
            print("(conversation reset)\n")
            continue

        try:
            resp = requests.post(
                f"{URL}/chat",
                json={"message": message},
                headers=HEADERS,
                timeout=600,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"error: {exc}\n")
            continue

        print(f"agent> {resp.json()['response']}\n")


if __name__ == "__main__":
    main()
