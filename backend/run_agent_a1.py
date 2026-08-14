"""
backend/run_agent_a1.py — Executive Autonomous Runner for ContentPedagogyAgent
The Agent autonomously determines curriculum topics, builds 8 main examples, explanations, comparisons, and exercises.
"""

import sys
import asyncio
import logging

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

import os
if not os.getenv("OPENAI_API_KEY"):
    pass

from agents.content_agent import ContentPedagogyAgent

async def run_agent():
    print("=" * 75)
    print("🤖 Starting Polyglot ContentPedagogyAgent (Autonomous Curriculum Generation)")
    print("=" * 75)

    agent = ContentPedagogyAgent()

    # Fully Autonomous Generation — Agent determines topic structure and count itself
    summary = await agent.run_full_autonomous_generation(
        target_language_code="en",
        native_language_code="fa",
        level_code="A1",
    )

    print("\n" + "=" * 75)
    print(f"🎉 Agent Autonomous Execution Complete!")
    print(f"📌 Total Topics Autonomously Created by Agent: {summary['topics_count']}")
    print("=" * 75)

if __name__ == "__main__":
    asyncio.run(run_agent())
