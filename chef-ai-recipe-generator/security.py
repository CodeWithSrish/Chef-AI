def is_allowed_file(filename: str) -> bool:
    return filename.endswith('.txt') or filename.endswith('.json')

def sanitize_text(text: str) -> str:
    import re
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove basic script tags and content
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE)
    return text.strip()

def validate_ingredient_list(items: list[str]) -> tuple[bool, str]:
    if not items:
        return False, "Ingredient list is empty. Please provide at least 1 ingredient."
    if len(items) > 30:
        return False, "Too many ingredients. Maximum allowed is 30."
    for item in items:
        if not item or not isinstance(item, str) or not item.strip():
            return False, "Invalid ingredient found. Every ingredient must be a non-empty string."
    return True, ""
