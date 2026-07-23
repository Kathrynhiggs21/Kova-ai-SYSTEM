# KOVA Dashboard v1 Specification

## Purpose

Dashboard v1 is the first usable KOVA command center. It should show today, current projects, integrations, blockers, and next actions without requiring Katy to hunt through 47 tabs wearing a trench coat.

## Primary User

Katy. Secondary users later may include collaborators, family, or project agents, but v1 is personal-first.

## Layout

### Top Bar
- KOVA logo/name
- Current date/time
- System status
- Quick command input
- Notification indicator

### Main Cards

1. **Today Card**
   - Calendar events
   - reminders
   - top 3 priorities
   - urgent alerts

2. **Daily Digest Card**
   - latest generated digest
   - send status: email / phone / push
   - regenerate button

3. **Projects Card**
   - KOVA OS
   - Scribbles by Marcy
   - Rio & Cleo
   - Reagan/family
   - Health/medical
   - Finance

4. **Integrations Card**
   - GitHub
   - Manus
   - Dropbox
   - Google Calendar
   - Notion
   - OpenAI Platform
   - Google Contacts
   - Gmail
   - Drive

5. **Blockers Card**
   - missing credentials
   - broken automations
   - access needed
   - stale tasks

6. **Next Actions Card**
   - one-click action list
   - owner
   - due date
   - confidence

7. **Memory/Notes Card**
   - recent decisions
   - saved preferences
   - project notes

## Data Model

```json
{
  "dashboard_date": "2026-07-06",
  "top_priorities": [],
  "integrations": [],
  "projects": [],
  "blockers": [],
  "next_actions": [],
  "digest": {},
  "notifications": []
}
```

## MVP Behavior

- Read from static JSON/config first.
- Later upgrade to live API data.
- Never display secrets.
- Show setup-needed states clearly.
- Prioritize useful summaries over flashy charts.

## Design Style

- Clean
- Mobile-first
- Cards/timelines/toasts
- Slightly playful labels
- Friendly but not cutesy
- Dark/light mode later

## First Implementation Recommendation

Use the existing `kovaos-site` or `kova-ai-site` repo for the public-facing dashboard shell, while this repo remains the system command center and documentation source of truth.
