# KOVA OS Integration Matrix

## Status Legend

- **Planned** = desired but not connected
- **Designed** = spec exists
- **Ready for setup** = can be connected once credentials/scopes are provided
- **Active** = working integration exists
- **Blocked** = needs access, export, or decision

| Integration | Purpose | Current Status | Next Action | Risk |
|---|---|---:|---|---|
| GitHub | Repos, issues, PRs, docs, CI/CD | Active for repo docs/issues | Use this repo as command center | Repo sprawl |
| Manus | Agent builds, project handoffs, generated assets | Blocked/External | Export project docs/assets into repo or Drive | Content trapped in Manus links |
| Dropbox | File sync/storage | Planned | Pick canonical KOVA Dropbox folder | Duplicate file chaos |
| Google Calendar | Daily agenda, reminders, schedule intelligence | Active in assistant layer | Keep KOVA runtime scopes minimal and verify each write | OAuth scopes |
| Notion | Docs, tasks, project dashboards | Active in assistant layer | Use as a view; keep canonical technical state in GitHub | Duplicate dashboards |
| OpenAI Platform | API keys, model routing, assistants, tool layer | Ready for setup | Create project + store key in deployment secrets | Public secret leakage |
| Google Contacts | People/entity registry | Ready for setup | Define VIP contacts, family, vendors, collaborators | Privacy/scoping |
| Gmail | Daily digest, triage, labels, urgent email detection | Available in assistant layer | Keep separate KOVA and personal account routing explicit | Too much noise or wrong account |
| Google Drive | File index, docs, project folder sync | Active in assistant layer | Run metadata-first inventory and lifecycle updates | Duplicate versions |
| Google Photos | Memory/timeline/media organization | Planned | Define albums and access model | Sensitive/private media |
| Zapier / Make / n8n | Optional automation bridges | Fallback | Use only when native connector, MCP or official API is insufficient | Brittle or duplicated workflows |
| Twilio/SMS | Phone alerts | Planned | Use only for high-value alerts | Notification overload |

## Integration Build Rule

Every integration must have:

1. Owner/account
2. Purpose
3. Data pulled
4. Data written
5. OAuth/API scope
6. Secret storage location
7. Automation trigger
8. Failure behavior
9. Digest output
10. Privacy note

## Priority Setup Order

1. GitHub command center
2. Calendar digest
3. Gmail digest
4. Drive/Dropbox file index
5. Notion docs/tasks
6. OpenAI Platform model/API layer
7. Contacts entity registry
8. Manus export/sync

## Automation rule

Routine organization, status propagation, duplicate detection and reporting are automatic. Deletion, permission changes, financial commitments, external messages and ambiguous destructive actions require approval. See [KOVA Automation Policy](../architecture/KOVA_AUTOMATION_POLICY.md).
