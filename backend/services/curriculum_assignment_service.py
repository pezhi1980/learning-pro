# backend/services/curriculum_assignment_service.py
"""
ROLE: CURRICULUM ASSIGNMENT SERVICE

This service is responsible for preparing exact, source-authorized curriculum targets for the Content Generation Agent.

CORE RULES:
1. Every target must be verified against CurriculumService (Authoritative Source of Truth).
2. Target Content and Allowed Supporting Content remain strictly distinct.
3. Lexeme and Sense remain distinct.
4. Ambiguity causes immediate failure (no guessing or fuzzy matching).
5. The service never adds or removes curriculum targets automatically.
6. Returns fully resolved AgentInput objects.
"""

from typing import Any, Dict, List, Optional, Set
from backend.curriculum import CurriculumService, GrammarSourceItem, VocabularySourceItem
from backend.schemas import (
    AgentInput,
    BackendError,
    CurriculumAssignmentRequest,
    ErrorDetail,
    ErrorType,
    GenerationMode,
    GrammarTarget,
    SourceReference,
    VocabularySenseTarget,
    VocabularyTarget,
)


class CurriculumAssignmentError(Exception):
    """Exception raised when curriculum assignment validation or authorization fails."""

    def __init__(self, message: str, error_type: ErrorType, details: Optional[List[ErrorDetail]] = None, request_id: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or []
        self.request_id = request_id

    def to_backend_error(self) -> BackendError:
        return BackendError(
            request_id=self.request_id,
            error_type=self.error_type,
            error_code=f"ERR_ASSIGNMENT_{self.error_type.value.upper()}",
            message=self.message,
            details=self.details,
            retryable=False,
        )


class CurriculumAssignmentService:
    """
    Authoritative Curriculum Assignment Service.
    Maps CurriculumAssignmentRequest -> AgentInput without inventing content.
    """

    def __init__(self, curriculum_service: Optional[CurriculumService] = None):
        self.curriculum_service = curriculum_service or CurriculumService()

    def build_agent_input(self, request: CurriculumAssignmentRequest) -> AgentInput:
        """
        Main entrypoint: validates request and constructs a fully-resolved AgentInput object.
        """
        # 1. Resolve Target Grammar
        target_grammar_list: List[GrammarTarget] = []
        seen_grammar_ids: Set[str] = set()

        for g_id in request.target_grammar_ids:
            if g_id in seen_grammar_ids:
                continue
            target_g = self.resolve_grammar_target(g_id, request_id=request.request_id)
            target_grammar_list.append(target_g)
            seen_grammar_ids.add(g_id)

        # 2. Resolve Allowed Grammar
        allowed_grammar_codes_list: List[str] = []
        seen_allowed_grammar: Set[str] = set()

        for g_id in request.allowed_grammar_ids:
            item = self._find_grammar_item(g_id, request_id=request.request_id)
            code = item.grammar_code
            if code not in seen_allowed_grammar:
                allowed_grammar_codes_list.append(code)
                seen_allowed_grammar.add(code)

        # 3. Resolve Target Vocabulary
        target_vocab_list: List[VocabularyTarget] = []
        vocab_target_by_id: Dict[str, VocabularyTarget] = {}
        seen_vocab_ids: Set[str] = set()

        for v_id in request.target_vocabulary_ids:
            if v_id in seen_vocab_ids:
                continue
            target_v = self.resolve_vocabulary_target(v_id, request_id=request.request_id)
            target_vocab_list.append(target_v)
            vocab_target_by_id[target_v.learning_object_id] = target_v
            seen_vocab_ids.add(v_id)

        # 4. Resolve Target Vocabulary Senses
        for s_id in request.target_vocabulary_sense_ids:
            sense_target, parent_item = self.resolve_vocabulary_sense(s_id, request_id=request.request_id)
            # Verify consistency if parent item is part of target_vocabulary
            if parent_item.source_item_id in vocab_target_by_id:
                existing_vocab = vocab_target_by_id[parent_item.source_item_id]
                # Ensure sense is not duplicated
                if not any(s.sense_id == sense_target.sense_id for s in existing_vocab.senses):
                    existing_vocab.senses.append(sense_target)
            else:
                # Target Vocabulary Sense supplied without root item in target_vocabulary_ids:
                # Construct VocabularyTarget specifically for this sense item
                source_ref = SourceReference(
                    source_id=parent_item.source_id,
                    source_type="vocabulary",
                    level=parent_item.document_level,
                    source_item_id=parent_item.source_item_id,
                    page=parent_item.page,
                    metadata={"row_number": parent_item.row_number},
                )
                vocab_target = VocabularyTarget(
                    learning_object_id=parent_item.source_item_id,
                    item=parent_item.lexeme,
                    part_of_speech=parent_item.part_of_speech,
                    source=source_ref,
                    senses=[sense_target],
                )
                target_vocab_list.append(vocab_target)
                vocab_target_by_id[parent_item.source_item_id] = vocab_target

        # 5. Resolve Allowed Vocabulary Items & Sense IDs
        allowed_vocab_items_list: List[str] = []
        seen_allowed_vocab: Set[str] = set()

        for v_id in request.allowed_vocabulary_ids:
            v_item = self._find_vocabulary_item(v_id, request_id=request.request_id)
            if v_item.lexeme not in seen_allowed_vocab:
                allowed_vocab_items_list.append(v_item.lexeme)
                seen_allowed_vocab.add(v_item.lexeme)

        allowed_sense_ids_list: List[str] = []
        seen_allowed_senses: Set[str] = set()

        for s_id in request.allowed_vocabulary_sense_ids:
            sense_target, _ = self.resolve_vocabulary_sense(s_id, request_id=request.request_id)
            if sense_target.sense_id not in seen_allowed_senses:
                allowed_sense_ids_list.append(sense_target.sense_id)
                seen_allowed_senses.add(sense_target.sense_id)

        # 6. Sanity Checks for Generation Mode
        self._validate_generation_mode_constraints(
            mode=request.generation_mode,
            target_grammar=target_grammar_list,
            target_vocab=target_vocab_list,
            learner_errors=request.learner_errors,
            request_id=request.request_id,
        )

        # 7. Construct AgentInput
        return AgentInput(
            request_id=request.request_id,
            target_language=request.target_language,
            native_language=request.native_language,
            generation_mode=request.generation_mode,
            target_grammar=target_grammar_list,
            allowed_grammar_codes=allowed_grammar_codes_list,
            target_vocabulary=target_vocab_list,
            allowed_vocabulary_items=allowed_vocab_items_list,
            allowed_vocabulary_sense_ids=allowed_sense_ids_list,
            task_difficulty=request.task_difficulty,
            learner_errors=request.learner_errors,
            constraints=request.constraints,
        )

    # ── Deterministic Helper Methods ───────────────────────────────────────────

    def _find_grammar_item(self, identifier: str, request_id: Optional[str] = None) -> GrammarSourceItem:
        # First try exact ID lookup
        item = self.curriculum_service.get_grammar_by_id(identifier)
        if item:
            return item

        # Next try by Grammar Code
        matches = self.curriculum_service.find_all_grammar_by_code(identifier)
        if not matches:
            raise CurriculumAssignmentError(
                message=f"Grammar target '{identifier}' not found in authoritative source.",
                error_type=ErrorType.unknown_grammar_code,
                details=[ErrorDetail(field="target_grammar_ids", received=identifier)],
                request_id=request_id,
            )
        if len(matches) > 1:
            matching_ids = [m.source_item_id for m in matches]
            raise CurriculumAssignmentError(
                message=f"Grammar code '{identifier}' is ambiguous ({len(matches)} matching source items: {matching_ids}). Disambiguation required.",
                error_type=ErrorType.conflicting_input,
                details=[ErrorDetail(field="target_grammar_ids", expected="exact_source_item_id", received=identifier)],
                request_id=request_id,
            )
        return matches[0]

    def resolve_grammar_target(self, identifier: str, request_id: Optional[str] = None) -> GrammarTarget:
        item = self._find_grammar_item(identifier, request_id=request_id)
        source_ref = SourceReference(
            source_id=item.source_id,
            source_type="grammar",
            level=item.document_level,
            source_item_id=item.source_item_id,
            page=item.page,
            metadata={"core_inventory_raw": item.core_inventory_raw, "row_number": item.row_number},
        )
        return GrammarTarget(
            learning_object_id=item.source_item_id,
            grammar_code=item.grammar_code,
            label=item.label,
            source=source_ref,
        )

    def _find_vocabulary_item(self, identifier: str, request_id: Optional[str] = None) -> VocabularySourceItem:
        # First try exact ID lookup
        item = self.curriculum_service.get_vocabulary_by_id(identifier)
        if item:
            return item

        # Next try by lexeme
        matches = self.curriculum_service.find_vocabulary_by_lexeme(identifier)
        if not matches:
            raise CurriculumAssignmentError(
                message=f"Vocabulary item '{identifier}' not found in authoritative source.",
                error_type=ErrorType.unknown_vocabulary_item,
                details=[ErrorDetail(field="target_vocabulary_ids", received=identifier)],
                request_id=request_id,
            )
        if len(matches) > 1:
            matching_ids = [m.source_item_id for m in matches]
            raise CurriculumAssignmentError(
                message=f"Vocabulary lexeme '{identifier}' is ambiguous ({len(matches)} matching source items: {matching_ids}). Disambiguation required.",
                error_type=ErrorType.conflicting_input,
                details=[ErrorDetail(field="target_vocabulary_ids", expected="exact_source_item_id", received=identifier)],
                request_id=request_id,
            )
        return matches[0]

    def resolve_vocabulary_target(self, identifier: str, request_id: Optional[str] = None) -> VocabularyTarget:
        item = self._find_vocabulary_item(identifier, request_id=request_id)
        source_ref = SourceReference(
            source_id=item.source_id,
            source_type="vocabulary",
            level=item.document_level,
            source_item_id=item.source_item_id,
            page=item.page,
            metadata={"row_number": item.row_number},
        )

        senses: List[VocabularySenseTarget] = []
        if item.guideword:
            senses.append(
                VocabularySenseTarget(
                    sense_id=f"{item.source_item_id}:sense",
                    guideword=item.guideword,
                    source=source_ref,
                )
            )

        return VocabularyTarget(
            learning_object_id=item.source_item_id,
            item=item.lexeme,
            part_of_speech=item.part_of_speech,
            source=source_ref,
            senses=senses,
        )

    def resolve_vocabulary_sense(self, identifier: str, parent_lexeme: Optional[str] = None, request_id: Optional[str] = None) -> (VocabularySenseTarget, VocabularySourceItem):
        item = self.curriculum_service.get_vocabulary_by_id(identifier)
        if not item:
            # Check if identifier ends with :sense
            clean_id = identifier.replace(":sense", "")
            item = self.curriculum_service.get_vocabulary_by_id(clean_id)

        if not item:
            raise CurriculumAssignmentError(
                message=f"Vocabulary Sense source item '{identifier}' not found.",
                error_type=ErrorType.unknown_vocabulary_sense,
                details=[ErrorDetail(field="target_vocabulary_sense_ids", received=identifier)],
                request_id=request_id,
            )

        if parent_lexeme and item.lexeme.lower().strip() != parent_lexeme.lower().strip():
            raise CurriculumAssignmentError(
                message=f"Vocabulary Sense '{identifier}' (lexeme '{item.lexeme}') does not match expected parent lexeme '{parent_lexeme}'.",
                error_type=ErrorType.conflicting_input,
                details=[ErrorDetail(field="target_vocabulary_sense_ids", expected=parent_lexeme, received=item.lexeme)],
                request_id=request_id,
            )

        source_ref = SourceReference(
            source_id=item.source_id,
            source_type="vocabulary",
            level=item.document_level,
            source_item_id=item.source_item_id,
            page=item.page,
            metadata={"row_number": item.row_number},
        )

        sense_target = VocabularySenseTarget(
            sense_id=f"{item.source_item_id}:sense",
            guideword=item.guideword,
            source=source_ref,
        )
        return sense_target, item

    def _validate_generation_mode_constraints(
        self,
        mode: GenerationMode,
        target_grammar: List[GrammarTarget],
        target_vocab: List[VocabularyTarget],
        learner_errors: List[Any],
        request_id: Optional[str] = None,
    ):
        if mode == GenerationMode.grammar_micro_lesson:
            if not target_grammar:
                raise CurriculumAssignmentError(
                    message="Generation mode 'grammar_micro_lesson' requires at least one target Grammar item.",
                    error_type=ErrorType.invalid_input,
                    details=[ErrorDetail(field="target_grammar_ids", expected="at_least_1_target")],
                    request_id=request_id,
                )
        elif mode == GenerationMode.vocabulary_lesson:
            if not target_vocab:
                raise CurriculumAssignmentError(
                    message="Generation mode 'vocabulary_lesson' requires at least one target Vocabulary item or Sense.",
                    error_type=ErrorType.invalid_input,
                    details=[ErrorDetail(field="target_vocabulary_ids", expected="at_least_1_target")],
                    request_id=request_id,
                )
        elif mode == GenerationMode.grammar_repair:
            if not target_grammar and not learner_errors:
                raise CurriculumAssignmentError(
                    message="Generation mode 'grammar_repair' requires target Grammar items or learner error context.",
                    error_type=ErrorType.invalid_input,
                    details=[ErrorDetail(field="target_grammar_ids", expected="target_or_learner_errors")],
                    request_id=request_id,
                )
        elif mode == GenerationMode.vocabulary_repair:
            if not target_vocab and not learner_errors:
                raise CurriculumAssignmentError(
                    message="Generation mode 'vocabulary_repair' requires target Vocabulary items or learner error context.",
                    error_type=ErrorType.invalid_input,
                    details=[ErrorDetail(field="target_vocabulary_ids", expected="target_or_learner_errors")],
                    request_id=request_id,
                )
