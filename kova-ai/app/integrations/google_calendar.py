"""Bounded read-only Calendar adapter. No caller-selectable accounts or URLs."""

import os
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import quote, urlsplit
from zoneinfo import ZoneInfo
import httpx

CONFIG_NAMES = (
    "KOVA_GOOGLE_CLIENT_ID",
    "KOVA_GOOGLE_CLIENT_SECRET",
    "KOVA_GOOGLE_CALENDAR_REFRESH_TOKEN",
    "KOVA_GOOGLE_CALENDAR_ID",
)
READ_SCOPES = {
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
}
IDENTITY_SCOPES = {
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
}


def day_window(day: str) -> tuple[str, str]:
    parsed = date.fromisoformat(day)
    if parsed.isoformat() != day:
        raise ValueError("Use a YYYY-MM-DD date")
    try:
        zone = ZoneInfo(os.getenv("KOVA_TIMEZONE", "America/New_York"))
    except (KeyError, ValueError) as error:
        raise RuntimeError("Server timezone needs configuration") from error
    start = datetime.combine(parsed, time.min, zone)
    end = datetime.combine(parsed + timedelta(days=1), time.min, zone)
    return start.isoformat(), end.isoformat()


def occurrence_start(value: dict) -> str:
    if isinstance(value.get("date"), str):
        return date.fromisoformat(value["date"]).isoformat()
    stamp = datetime.fromisoformat(value["dateTime"].replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Calendar times must have an offset")
    return stamp.astimezone(timezone.utc).isoformat()


def normalize_events(items: list[dict]) -> list[dict]:
    records = {}
    for item in items:
        if item.get("status") == "cancelled":
            continue
        event_id = item["id"]
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("Incomplete event identity")
        start = item["start"]
        end = item["end"]
        occurrence_start(start)
        occurrence_start(end)
        key = (
            item.get("iCalUID") or event_id,
            occurrence_start(item.get("originalStartTime") or start),
        )
        link = item.get("htmlLink", "")
        parsed_link = urlsplit(link)
        safe_link = (
            link
            if parsed_link.scheme == "https"
            and parsed_link.hostname in {"calendar.google.com", "www.google.com"}
            and not parsed_link.username
            and not parsed_link.password
            else None
        )
        records[key] = {
            "id": event_id,
            "title": str(item.get("summary") or "(Untitled event)")[:300],
            "start": start,
            "end": end,
            "source": "google_calendar",
            "url": safe_link,
        }
    return sorted(records.values(), key=lambda event: occurrence_start(event["start"]))


async def read_calendar(day: str, transport=None) -> dict:
    checked = datetime.now(timezone.utc).isoformat()
    missing = [name for name in CONFIG_NAMES if not os.getenv(name, "").strip()]
    base = {
        "source": "google_calendar",
        "date": day,
        "events": [],
        "last_checked": checked,
    }
    if missing:
        return {
            **base,
            "status": "needs_connection",
            "reason": "Approved read-only Calendar connection is not configured.",
            "missing": missing,
        }
    try:
        begin, end = day_window(day)
        async with httpx.AsyncClient(
            timeout=10.0, follow_redirects=False, transport=transport
        ) as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": os.environ["KOVA_GOOGLE_CLIENT_ID"],
                    "client_secret": os.environ["KOVA_GOOGLE_CLIENT_SECRET"],
                    "refresh_token": os.environ["KOVA_GOOGLE_CALENDAR_REFRESH_TOKEN"],
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            token_data = response.json()
            scopes = set(token_data.get("scope", "").split())
            token = token_data.get("access_token")
            if (
                not isinstance(token, str)
                or not token
                or not (scopes & READ_SCOPES)
                or scopes - READ_SCOPES - IDENTITY_SCOPES
            ):
                return {
                    **base,
                    "status": "broken",
                    "reason": "Read-only Calendar grant could not be verified.",
                }
            items = []
            seen_pages = set()
            page = None
            for _ in range(10):
                params = {
                    "timeMin": begin,
                    "timeMax": end,
                    "singleEvents": "true",
                    "orderBy": "startTime",
                    "maxResults": 100,
                    "fields": "kind,items(id,iCalUID,summary,start,end,status,htmlLink,originalStartTime),nextPageToken",
                }
                if page:
                    params["pageToken"] = page
                response = await client.get(
                    "https://www.googleapis.com/calendar/v3/calendars/"
                    + quote(os.environ["KOVA_GOOGLE_CALENDAR_ID"], safe="")
                    + "/events",
                    params=params,
                    headers={"Authorization": "Bearer " + token},
                )
                response.raise_for_status()
                payload = response.json()
                rows = payload.get("items", [])
                if payload.get("kind") != "calendar#events":
                    raise ValueError("Unverified Calendar response")
                if not isinstance(rows, list) or any(
                    not isinstance(row, dict) for row in rows
                ):
                    raise ValueError("Incomplete Calendar response")
                items.extend(rows)
                page = payload.get("nextPageToken")
                if page is not None and not isinstance(page, str):
                    raise ValueError("Invalid page token")
                if not page:
                    return {
                        **base,
                        "status": "connected",
                        "events": normalize_events(items),
                        "complete": True,
                    }
                if page in seen_pages:
                    raise ValueError("Repeated page token")
                seen_pages.add(page)
            return {
                **base,
                "status": "partial",
                "events": normalize_events(items),
                "complete": False,
                "reason": "Calendar exceeded the bounded scan; some events are omitted.",
            }
    except httpx.HTTPStatusError as error:
        code = error.response.status_code
        return {
            **base,
            "status": "needs_connection" if code in {400, 401, 403} else "broken",
            "reason": "Calendar authorization or read failed.",
            "http_status": code,
        }
    except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError, OSError):
        return {
            **base,
            "status": "broken",
            "reason": "Calendar read could not be verified.",
        }
