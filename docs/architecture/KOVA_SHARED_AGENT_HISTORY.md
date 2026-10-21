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

Core owns the single capability/connection registry and its authorization; the canonical web app owns its UI at `/mcp`. `/agents` is the agent-routing overview, not a second connection-health/capability registry. Use stable references back to Core records rather than duplicate account or permission records.

| Route | Ownership and implementation evidence |
|---|---|
| `/mcp` | Single canonical registry UI location; current ConnectionCenter is a dated source snapshot. Live owner-protected registry behavior is not established. |
| `/agents` | Existing AgentHub routing/provider overview; link to the `/mcp` registry for connections/capabilities. |
| `/agents/capabilities` | Older documentation name retained only as a compatibility alias for `/mcp`. Not an implemented route/redirect in the inspected source; any future alias must reuse or redirect to the same registry and authorization. |
| `/assistant` | Existing ModulePlaceholder for user-facing orchestration, not proof of a working runtime. |
| `/agents/history`, `/agents/routing` | Planned history/policy views; no routes found in the inspected source. History uses Core's Agent Ledger, not a second task store. |
| `/world` | Existing ModulePlaceholder for AI World provenance. |
| `/system` | Planned health view; no route found in the inspected source. |

Evidence: canonical web main [`28debe0`](https://github.com/Kathrynhiggs21/kovaos-site/blob/28debe0edaaa7fc818a617bf4ec11dc55ad8d97b/client/src/App.tsx) registers `/mcp` as ConnectionCenter and `/agents` as AgentHub. No `/agents/capabilities` alias exists there. ConnectionCenter's snapshot is not wrapped in AccessGate by that router, so current owner access control must not be claimed from the route name. Source inspection does not verify a deployed route or current provider access. See [ADR-005's registry compatibility rule](ADR-005-SECOND-BRAIN-ASSISTANT-HUB.md#registry-ownership-and-route-compatibility); it supersedes the previous live-registry designation of `/agents/capabilities` in this document. No runtime route or provider setting is changed by this correction.

## Principle

KOVA remembers and organizes the work. Agents perform specialized work.
