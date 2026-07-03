# Chef AI – Ingredient to Recipe

## Features
- Enter ingredients manually or upload a `.txt` or `.json` file
- Generates a fun, simple recipe based on provided ingredients
- Floating emoji animations and clean Streamlit UI

## File Structure
```
chef-ai-recipe-generator/
  ├── app.py
  ├── security.py
  ├── ingredient_parser.py
  ├── recipe_generator.py
  ├── narrator.py
  ├── mcp_server.py
  ├── requirements.txt
  ├── README.md
  └── sample_ingredients.txt
```

## How to install
```bash
pip install -r requirements.txt
```

## How to run
```bash
streamlit run app.py
```

## Sample Input
You can use the provided `sample_ingredients.txt` file or input something like:
```text
tomato
onion
pasta
garlic
olive oil
```

## Architecture
**Streamlit UI** -> **security** (sanitizes and validates) -> **parser** (cleans and formats ingredients) -> **generator** (applies rule-based logic to create a recipe) -> **narrator** (adds emojis and fun text)
