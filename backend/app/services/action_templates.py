from __future__ import annotations

from datetime import timedelta

from app.ai.schemas import DetectedType, StructuredUnderstanding, SuggestionAction
from app.core.clock import combine_user_datetime, local_now, now_utc, parse_hhmm


class ActionTemplateService:
    def build_actions(self, understanding: StructuredUnderstanding, timezone: str | None) -> list[dict]:
        actions: list[dict] = []
        seen: set[str] = set()

        def add(action_kind: str, title: str, payload: dict | None = None) -> None:
            if action_kind in seen:
                return
            if action_kind == SuggestionAction.keep_in_inbox.value:
                return
            seen.add(action_kind)
            actions.append({"action_kind": action_kind, "title": title, "payload": payload or {}})

        for suggestion in understanding.suggestions:
            payload = {}
            if suggestion.action == SuggestionAction.continue_conversation and understanding.follow_up_question:
                payload = {"prompt": understanding.follow_up_question}
            add(suggestion.action.value, suggestion.label, payload)

        for item in self._fallback_actions(understanding, timezone):
            add(item["action_kind"], item["title"], item.get("payload"))
            if len(actions) >= 3:
                break

        while len(actions) < 3:
            add("save_task", "Сохранить как задачу")
            if len(actions) >= 3:
                break
            add("continue_conversation", "Уточнить", {"prompt": understanding.follow_up_question or "Продолжим разбирать это вместе?"})
            if len(actions) >= 3:
                break
            add("save_task_without_date", "Сохранить без даты")

        actions = actions[:3]
        actions.append({"action_kind": "keep_in_inbox", "title": "Оставить во входящих", "payload": {}})
        return actions

    def _fallback_actions(self, understanding: StructuredUnderstanding, timezone: str | None) -> list[dict]:
        if understanding.detected_type == DetectedType.list:
            base = [
                {"action_kind": "save_list", "title": self._list_label(understanding), "payload": {}},
            ]
            if understanding.follow_up_question:
                base.append({
                    "action_kind": "continue_conversation",
                    "title": "Уточнить список",
                    "payload": {"prompt": understanding.follow_up_question},
                })
            base.append({"action_kind": "split_into_tasks", "title": "Разбить на задачи", "payload": {}})
            return base

        if understanding.due_at_iso:
            base = [
                {"action_kind": "remind_at_detected_time", "title": self._detected_time_label(understanding), "payload": {}},
                {"action_kind": "save_task_without_date", "title": "Сохранить без даты", "payload": {}},
            ]
            if understanding.follow_up_question:
                base.insert(1, {
                    "action_kind": "continue_conversation",
                    "title": "Обсудить дальше",
                    "payload": {"prompt": understanding.follow_up_question},
                })
            else:
                base.append({"action_kind": "save_task", "title": "Сохранить как задачу", "payload": {}})
            return base

        if understanding.detected_type == DetectedType.task:
            base = [
                {"action_kind": "save_task", "title": "Сохранить как задачу", "payload": {}},
                {"action_kind": "remind_tomorrow_10", "title": "Поставить на завтра", "payload": {}},
            ]
            if understanding.follow_up_question:
                base.append({
                    "action_kind": "continue_conversation",
                    "title": "Обсудить дальше",
                    "payload": {"prompt": understanding.follow_up_question},
                })
            else:
                base.append({"action_kind": "save_task_without_date", "title": "Сохранить без даты", "payload": {}})
            return base

        base = [
            {"action_kind": "save_task", "title": "Сохранить как задачу", "payload": {}},
            {"action_kind": "save_list", "title": "Сохранить как список", "payload": {}},
        ]
        if understanding.follow_up_question:
            base.append({
                "action_kind": "continue_conversation",
                "title": "Уточнить",
                "payload": {"prompt": understanding.follow_up_question},
            })
        else:
            base.append({"action_kind": "save_task_without_date", "title": "Сохранить без даты", "payload": {}})
        return base

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

    def _list_label(self, understanding: StructuredUnderstanding) -> str:
        count = len(understanding.list_items)
        if count:
            return f"Сохранить список ({count})"
        return "Сохранить как список"
