from __future__ import annotations

from datetime import timedelta

from app.ai.schemas import DetectedType, StructuredUnderstanding
from app.core.clock import combine_user_datetime, local_now, now_utc, parse_hhmm


class ActionTemplateService:
    def build_actions(self, understanding: StructuredUnderstanding, timezone: str | None) -> list[dict]:
        actions: list[dict] = []

        if understanding.detected_type == DetectedType.list and understanding.list_items:
            count = len(understanding.list_items)
            actions.extend(
                [
                    {"action_kind": "save_list", "title": f"Сохранить список ({count})", "payload": {}},
                    {"action_kind": "split_into_tasks", "title": "Разбить на задачи", "payload": {}},
                    {"action_kind": "save_task", "title": "Сохранить одной задачей", "payload": {}},
                ]
            )
        elif understanding.due_at_iso:
            actions.extend(
                [
                    {"action_kind": "remind_at_detected_time", "title": self._detected_time_label(understanding), "payload": {}},
                    {"action_kind": "save_task_without_date", "title": "Сохранить без даты", "payload": {}},
                    {"action_kind": "save_task", "title": "Сохранить как задачу", "payload": {}},
                ]
            )
        elif understanding.detected_type == DetectedType.task:
            actions.extend(
                [
                    {"action_kind": "save_task", "title": "Сохранить как задачу", "payload": {}},
                    {"action_kind": "remind_tomorrow_10", "title": "Поставить на завтра", "payload": {}},
                    {"action_kind": "save_task_without_date", "title": "Сохранить без даты", "payload": {}},
                ]
            )
        else:
            actions.extend(
                [
                    {"action_kind": "save_task", "title": "Сохранить как задачу", "payload": {}},
                    {"action_kind": "save_list", "title": "Сохранить как список", "payload": {}},
                    {"action_kind": "save_task_without_date", "title": "Сохранить без даты", "payload": {}},
                ]
            )

        actions = actions[:3]
        actions.append({"action_kind": "keep_in_inbox", "title": "Оставить во входящих", "payload": {}})
        return actions

    def resolve_due_at(self, action_kind: str, understanding: StructuredUnderstanding, timezone: str | None):
        if action_kind == "remind_tomorrow_10":
            base = local_now(timezone).date() + timedelta(days=1)
            return combine_user_datetime(base, parse_hhmm("10:00"), timezone)
        if action_kind == "remind_today_evening":
            base = local_now(timezone)
            candidate_date = base.date() if base.hour < 19 else base.date() + timedelta(days=1)
            return combine_user_datetime(candidate_date, parse_hhmm("19:00"), timezone)
        if action_kind == "remind_at_detected_time" and understanding.due_at:
            return understanding.due_at.astimezone(now_utc().tzinfo)
        return None

    def _detected_time_label(self, understanding: StructuredUnderstanding) -> str:
        due_at = understanding.due_at
        if not due_at:
            return "Поставить на это время"
        return f"Поставить на {due_at.day}.{due_at.month:02d} в {due_at:%H:%M}"
