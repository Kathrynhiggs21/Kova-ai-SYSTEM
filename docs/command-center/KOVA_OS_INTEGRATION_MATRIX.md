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
| Google Calendar | Daily agenda, reminders, schedule intelligence | Ready for setup | Define digest calendar queries and event categories | OAuth scopes |
| Notion | Docs, tasks, project dashboards | Planned | Pick KOVA workspace/database structure | Duplicate with GitHub docs |
| OpenAI Platform | API keys, model routing, assistants, tool layer | Ready for setup | Create project + store key in deployment secrets | Public secret leakage |
| Google Contacts | People/entity registry | Ready for setup | Define VIP contacts, family, vendors, collaborators | Privacy/scoping |
| Gmail | Daily digest, triage, labels, urgent email detection | Planned | Define labels and digest rules | Too much noise |
| Google Drive | File index, docs, project folder sync | Planned | Pick KOVA master folder | Duplicate versions |
| Google Photos | Memory/timeline/media organization | Planned | Define albums and access model | Sensitive/private media |
| Make.com | Automation layer | Designed | Build daily digest scenario | Brittle workflows |
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
