# backend/routers/intelligence_router.py
"""
ROLE: ADVANCED LEARNING INTELLIGENCE REST API ROUTER

Exposes FastAPI REST endpoints for:
- Spaced Repetition review-due target lookup
- Curriculum Knowledge Graph relationship querying
- Personalized Opportunity Ranking
- Session Novelty & Cognitive Load validation
"""

import logging
from typing import Any, Dict, List, Optional, Set
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.intelligence import (
    AdvancedMasteryService,
    KnowledgeGraphService,
    NoveltyControlService,
    PersonalizationService,
    SpacedRepetitionEngine,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/intelligence", tags=["Advanced Learning Intelligence"])

srs_engine = SpacedRepetitionEngine()
mastery_service = AdvancedMasteryService(srs_engine=srs_engine)
graph_service = KnowledgeGraphService()
personalization_service = PersonalizationService()
novelty_service = NoveltyControlService()


class RankOpportunitiesRequest(BaseModel):
    learner_id: str
    candidate_target_ids: List[str]
    preferences: Optional[Dict[str, Any]] = None


class CheckNoveltyRequest(BaseModel):
    proposed_grammar_target_ids: List[str] = []
    proposed_vocab_target_ids: List[str] = []
    task_complexity_index: float = 1.0
    known_target_ids: Set[str] = set()


@router.get("/knowledge-graph/relationships")
async def get_knowledge_graph_relationships():
    return graph_service.list_edges()


@router.post("/recommendations/rank")
async def rank_learning_opportunities(req: RankOpportunitiesRequest):
    return personalization_service.rank_learning_opportunities(
        learner_id=req.learner_id,
        candidate_target_ids=req.candidate_target_ids,
        preferences=req.preferences,
    )


@router.post("/novelty/check")
async def check_session_novelty(req: CheckNoveltyRequest):
    is_valid, violations, stats = novelty_service.validate_session_novelty(
        proposed_grammar_target_ids=req.proposed_grammar_target_ids,
        proposed_vocab_target_ids=req.proposed_vocab_target_ids,
        task_complexity_index=req.task_complexity_index,
        known_target_ids=req.known_target_ids,
    )
    return {"is_valid": is_valid, "violations": violations, "stats": stats}
