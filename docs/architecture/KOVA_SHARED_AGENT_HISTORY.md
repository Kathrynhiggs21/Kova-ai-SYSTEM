# KOVA Shared Agent History and Auto-Routing

## Decision

KOVA is the persistent orchestration and memory layer. Specialized AI agents are interchangeable workers.

All KOVA surfaces use one permission-aware history model. Work performed through an authorized agent is normalized back into KOVA so another authorized agent can continue without rebuilding context.

## Execution loop

1. Understand the user's goal.
2. Retrieve relevant KOVA history and current canonical records.
3. Resolve current source of truth and superseded records.
4. Select the best available authorized agent or tool for each subtask.
5. Supply only the minimum relevant context.
6. Execute within the worker's permissions.
7. Validate the result against KOVA architecture, security and task requirements.
8. Record useful results, provenance, artifacts, decisions and actions back into KOVA.

## Agent Ledger

Every material agent run should support these fields:

- task_id
- parent_task_id
- originating_surface
- module
- project
- topic_tags
- agent_provider
- agent_name
- model_or_version
- account_scope
- connection_id
- capabilities_used
- permissions_used
- source_refs
- input_context_refs
- output_summary
- artifact_refs
- decisions
- actions
- approval_state
- validation_state
- status
- started_at
- completed_at
- supersedes
- superseded_by

The ledger stores references and provenance. It must not duplicate entire source systems when a stable canonical reference is available.

## Context policy

Central availability does not mean broadcast access. KOVA retrieves the relevant authorized slice for each task. Worker agents receive only the context needed for their assignment.

Personal, family, finance, health, work/KOVA and other scopes remain tagged and permission-aware.

## Auto Agent Router

Default mode is AUTO.

Routing considers:
- task capability fit
- required data/tool access
- current authorization
- model/agent quality for the task
- prior validated outcomes
- latency
- cost
- privacy sensitivity
- required approval level
- service availability

One request may be decomposed across multiple agents. KOVA remains the orchestrator and reconciles results into canonical state.

## Safety and approvals

Choosing an agent automatically does not authorize consequential actions automatically. Existing confirmation and permission boundaries remain in force.

Never store provider passwords, API secrets, recovery codes or private credentials in the Agent Ledger.

## Canonical surfaces

- /assistant — user-facing orchestration
- /agents — agent registry, capability matrix and connection health
- /agents/history — normalized Agent Ledger
- /agents/capabilities — live capability registry
- /agents/routing — routing policy and diagnostics
- /world — AI World provenance and source exploration
- /system — overall health and connection failures

## Principle

KOVA remembers and organizes the work. Agents perform specialized work.
