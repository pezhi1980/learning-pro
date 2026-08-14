# BACKEND ARCHITECTURE CONTRACT

The Backend must preserve clear separation of responsibilities.

## SOURCE AUTHORITY
`curriculum/`

## DATA CONTRACTS
`schemas/`

## AI CONTENT GENERATION
`agents/`

## DETERMINISTIC ENFORCEMENT
`validators/`

## WORKFLOW ORCHESTRATION
`services/`


## DEPENDENCY DIRECTION

```text
Curriculum repositories
        ↓
Curriculum Service
        ↓
Curriculum Assignment Service
        ↓
Agent Input Schema
        ↓
Content Generation Agent
        ↓
Agent Output Schema
        ↓
Validators
        ↓
Lesson Generation Service decision
        ↓
ACCEPT or REJECT
```


## RESPONSIBILITY RULES

1. Agent must not validate itself as final authority.

2. Validators must not generate educational content.

3. Repositories must not call the Agent.

4. Schemas must not make curriculum decisions.

5. Curriculum Service must not generate lessons.

6. Assignment Service must not invent curriculum.

7. Lesson Generation Service must orchestrate, not replace specialized component responsibilities.

8. Source authority and AI generation must remain separate.

9. Curriculum authorization must happen before generation.

10. Backend enforcement must happen after generation.

11. Only validated content may enter the accepted lesson pipeline.

## MASTER PRINCIPLE

* SOURCE DEFINES TRUTH.
* BACKEND DEFINES TARGETS.
* AGENT GENERATES CONTENT.
* VALIDATORS ENFORCE CONSTRAINTS.
* SERVICE CONTROLS THE WORKFLOW.
