# KOVA Agent Router Policy v1

mode: AUTO

## Routing score

KOVA should rank only agents that are currently authorized and available.

Suggested factors:
- capability_fit: 30
- required_access_fit: 25
- validated_quality_history: 15
- privacy_fit: 10
- reliability: 10
- latency: 5
- cost_efficiency: 5

Hard gates:
- authorization required
- required tool/data access required
- provider/account scope respected
- consequential actions retain confirmation requirements

## Multi-agent work

KOVA may decompose a request when specialists materially improve the outcome. Each subtask receives a task ID and parent task ID and writes its material result back to the Agent Ledger.

## Learning

Routing history may improve future ranking only from validated outcomes. A provider name alone is not evidence that it is best for a task.

## Fallback

If the preferred worker is unavailable, KOVA selects the next qualified worker. If no worker has the required permission or connection, KOVA reports the missing connection instead of simulating success.
