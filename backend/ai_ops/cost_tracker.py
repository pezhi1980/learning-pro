# backend/ai_ops/cost_tracker.py
"""
ROLE: AI COST TRACKER

Tracks token consumption, computes estimated USD costs, cache hits, and retries.
Maintains aggregated cost metrics per provider, model, and request.
"""

import logging
from typing import Any, Dict, List, Optional
from backend.ai_ops.ai_ops_models import CostRecord

logger = logging.getLogger(__name__)

# Standard model price table (USD per 1,000 tokens / units)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o": {"input": 0.0025 / 1000.0, "output": 0.010 / 1000.0},
    "gpt-4o-mini": {"input": 0.00015 / 1000.0, "output": 0.0006 / 1000.0},
    "whisper-1": {"input": 0.006 / 1000.0, "output": 0.0},
    "tts-1": {"input": 0.015 / 1000.0, "output": 0.0},
    "mock": {"input": 0.0, "output": 0.0},
}


class AICostTracker:
    """
    Repository for logging and aggregating AI operational costs.
    """

    def __init__(self):
        self._records: List[CostRecord] = []

    @staticmethod
    def calculate_usd_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        pricing = MODEL_PRICING.get(model.lower(), MODEL_PRICING["gpt-4o"])
        cost = (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])
        return round(cost, 6)

    def record_cost(
        self,
        request_id: str,
        provider: str = "openai",
        model: str = "gpt-4o",
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_hit: bool = False,
        retry_count: int = 0,
    ) -> CostRecord:

        cost_usd = 0.0 if cache_hit else self.calculate_usd_cost(model, input_tokens, output_tokens)

        record = CostRecord(
            request_id=request_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            cache_hit=cache_hit,
            retry_count=retry_count,
        )

        self._records.append(record)
        logger.info(f"Recorded cost for request '{request_id}' (${cost_usd:.6f}, cache_hit={cache_hit}).")
        return record

    def get_cost_summary(self) -> Dict[str, Any]:
        total_requests = len(self._records)
        total_input_tokens = sum(r.input_tokens for r in self._records)
        total_output_tokens = sum(r.output_tokens for r in self._records)
        total_cost_usd = round(sum(r.cost_usd for r in self._records), 4)
        cache_hits = sum(1 for r in self._records if r.cache_hit)
        total_retries = sum(r.retry_count for r in self._records)

        return {
            "total_requests": total_requests,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_cost_usd": total_cost_usd,
            "cache_hits": cache_hits,
            "total_retries": total_retries,
        }
