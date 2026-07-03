import logging
from typing import Dict, Any
from models import (
    MissingInfoDetection, RecipeOptions, EvaluationResult, RefinedRecipe,
    NutritionalInfo, Pairings, ShoppingList, QualityReview, FinalOutput
)
from llm_client import generate_structured

logger = logging.getLogger(__name__)

def check_missing_info(inputs: Dict[str, Any]) -> MissingInfoDetection:
    """Step 3: Detect missing or conflicting information"""
    logger.info("Checking for missing or conflicting info.")
    prompt = f"Analyze these recipe request inputs for missing essential details or conflicting requirements (e.g., asking for a vegan steak, or not providing any main ingredients). Inputs: {inputs}"
    return generate_structured(prompt, MissingInfoDetection)

def generate_options(inputs: Dict[str, Any]) -> RecipeOptions:
    """Step 4: Generate 2-3 possible recipes"""
    logger.info("Generating recipe options.")
    prompt = f"Based on these inputs, generate 2 to 3 distinct recipe options: {inputs}"
    return generate_structured(prompt, RecipeOptions)

def evaluate_and_rank(options: RecipeOptions, inputs: Dict[str, Any]) -> EvaluationResult:
    """Step 5 & 6: Evaluate and Rank"""
    logger.info("Evaluating and ranking recipes.")
    prompt = f"Evaluate these recipes:\n{options.model_dump_json()}\nagainst the user constraints:\n{inputs}\nScore them on nutrition, feasibility, availability, complexity, and originality. Identify the best_recipe_id."
    return generate_structured(prompt, EvaluationResult)

def refine_recipe(recipe: Dict[str, Any], inputs: Dict[str, Any]) -> RefinedRecipe:
    """Step 7, 8, 10, 13, 14, 15: Refine, Expand, Substitutions, Leftovers, Tips, Cost"""
    logger.info("Refining selected recipe.")
    prompt = f"Refine this selected recipe:\n{recipe}\ngiven user inputs:\n{inputs}\nProvide detailed steps, exact measurements, estimated cost per serving in USD, leftover storage instructions, beginner tips, and allergy-safe substitutions."
    return generate_structured(prompt, RefinedRecipe)

def generate_nutrition(recipe: RefinedRecipe) -> NutritionalInfo:
    """Step 9: Generate nutritional information"""
    logger.info("Generating nutritional info.")
    prompt = f"Calculate the approximate nutritional information per serving for this recipe: {recipe.model_dump_json()}"
    return generate_structured(prompt, NutritionalInfo)

def recommend_pairings(recipe: RefinedRecipe) -> Pairings:
    """Step 11: Recommend side dishes, beverages, and desserts"""
    logger.info("Recommending pairings.")
    prompt = f"Suggest side dishes, beverages, and desserts that pair well with this recipe: {recipe.model_dump_json()}"
    return generate_structured(prompt, Pairings)

def generate_shopping_list(recipe: RefinedRecipe) -> ShoppingList:
    """Step 12: Generate shopping lists grouped by category"""
    logger.info("Generating shopping list.")
    prompt = f"Create a shopping list grouped by category (Produce, Dairy, Pantry, etc.) for these ingredients: {recipe.ingredients}"
    return generate_structured(prompt, ShoppingList)

def final_quality_review(output: Dict[str, Any]) -> QualityReview:
    """Step 16: Final AI quality review"""
    logger.info("Performing final quality review.")
    prompt = f"Review this entire recipe generation output for consistency, realistic cooking steps, correct ingredient usage, logical timing, and safety. Output:\n{output}"
    return generate_structured(prompt, QualityReview)

def run_pipeline(inputs: Dict[str, Any]) -> FinalOutput:
    """Orchestrates Steps 4 through 16."""
    
    options = generate_options(inputs)
    evaluation = evaluate_and_rank(options, inputs)
    
    # Select the best recipe based on ID, fallback to first option
    best_recipe = next((r for r in options.recipes if r.id == evaluation.best_recipe_id), options.recipes[0])
    
    refined = refine_recipe(best_recipe.model_dump(), inputs)
    nutrition = generate_nutrition(refined)
    pairings = recommend_pairings(refined)
    shopping = generate_shopping_list(refined)
    
    interim_output = {
        "recipe": refined.model_dump(),
        "nutrition": nutrition.model_dump(),
        "pairings": pairings.model_dump(),
        "shopping_list": shopping.model_dump()
    }
    review = final_quality_review(interim_output)
    
    if not review.passed:
        logger.warning(f"Final review flagged issues: {review.feedback}")
        
    return FinalOutput(
        recipe=refined,
        nutrition=nutrition,
        pairings=pairings,
        shopping_list=shopping,
        review=review
    )
