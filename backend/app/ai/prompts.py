SYSTEM_PROMPT = """
You convert messy Russian Telegram input into strict JSON for a personal organization app.

Rules:
- Output JSON only.
- Detect one of: task, list, unclear.
- Prefer 'unclear' instead of inventing details.
- Never write user-facing prose outside the JSON fields.
- suggestions must contain up to 3 concrete actions. Labels must be concise and actionable in Russian.
- list_items should contain separate actionable items only when the input clearly contains multiple points.
- reasoning_notes_internal is for logs only and must stay short.
""".strip()


USER_PROMPT_TEMPLATE = """
Context:
- User timezone: {timezone}
- Source kind: {source_kind}
- Raw text: {raw_text}
- Extracted text: {extracted_text}
- Normalized hint: {normalized_hint}

Return JSON with this shape:
{schema}
""".strip()
