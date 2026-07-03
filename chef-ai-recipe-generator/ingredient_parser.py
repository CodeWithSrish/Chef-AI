import re

def parse_ingredients(raw_text: str) -> list[str]:
    # Split by commas and new lines
    raw_items = re.split(r'[,\n]', raw_text)
    
    parsed = []
    seen = set()
    
    plurals_map = {
        'tomatoes': 'tomato',
        'potatoes': 'potato',
        'onions': 'onion',
        'carrots': 'carrot'
    }
    
    for item in raw_items:
        clean_item = item.strip().lower()
        if not clean_item:
            continue
            
        # Normalize simple plurals
        if clean_item in plurals_map:
            clean_item = plurals_map[clean_item]
            
        # Remove duplicates but preserve order
        if clean_item not in seen:
            seen.add(clean_item)
            parsed.append(clean_item)
            
    return parsed
