# KOVA Daily Digest v1 Specification

## Goal

Send a clean, useful summary every morning at **9:00 AM America/New_York**.

## Output Channels

- Email
- Phone notification/SMS/push later
- Dashboard card
- Markdown archive

## Digest Sections

1. **Today**
   - date
   - weather optional later
   - calendar events
   - appointments

2. **Top 3 Priorities**
   - practical actions only
   - no giant guilt avalanche

3. **Important Email**
   - urgent senders
   - bills/finance
   - school/Reagan
   - health/medical
   - project/client/vendor items

4. **Files Changed**
   - Drive
   - Dropbox
   - GitHub
   - Notion
   - Manus exports

5. **Project Pulse**
   - KOVA OS
   - Scribbles by Marcy
   - Rio & Cleo
   - Reagan/family
   - Health
   - Finance

6. **Blockers**
   - missing keys
   - broken syncs
   - decisions needed
   - external people/apps blocking progress

7. **Next Concrete Actions**
   - max 5
   - written as commands
   - include owner if known

## Draft Digest Schema

```json
{
  "digest_date": "2026-07-06",
  "timezone": "America/New_York",
  "send_time": "09:00",
  "channels": ["email", "dashboard"],
  "calendar": [],
  "priority_email": [],
  "files_changed": [],
  "project_pulse": [],
  "blockers": [],
  "next_actions": []
}
```

## Automation Layer

Recommended v1:

- Make.com or Google Apps Script fetches source data.
- AI summarizes into Markdown.
- Output is saved to `reports/digests/YYYY-MM-DD.md`.
- Email is sent to Katy.
- Dashboard reads latest digest.

## Guardrails

- Do not send every notification.
- Summarize the mess.
- Flag only important things.
- Never expose secrets.
- Include source links where possible.

## First MVP

Use Calendar + GitHub + manual project status first. Add Gmail/Drive once OAuth and labels are stable.
