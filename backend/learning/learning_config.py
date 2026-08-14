# backend/learning/learning_config.py
"""
ROLE: LEARNING CONFIGURATION

Centralized configuration module for learning backend parameters, algorithms, and bounds.
Prevents scattering learning constants across code files.
"""

from pydantic import BaseModel


class LearningConfig(BaseModel):
    """
    Configurable parameters for mastery updates, review intervals, target selection, and novelty budgets.
    """

    # Mastery Incremental Weights
    mastery_gain_factor: float = 0.15
    mastery_penalty_factor: float = 0.20
    stability_gain_factor: float = 0.10
    stability_penalty_factor: float = 0.15

    # Target Thresholds
    mastery_threshold: float = 0.85
    strengthening_threshold: float = 0.60
    learning_threshold: float = 0.20

    # Decision Engine Bounds & Budget
    novelty_budget_max_new_targets: int = 1  # 1 primary new learning burden per activity
    max_review_targets_per_session: int = 5
    max_repair_targets_per_session: int = 3
    max_supporting_allowed_items: int = 5

    # Review Scheduling Base Intervals (Days)
    review_interval_short_days: int = 1
    review_interval_moderate_days: int = 3
    review_interval_long_days: int = 7
    review_interval_mastered_days: int = 14
