from pydantic import BaseModel, Field
from typing import List, Optional

class MissingInfoDetection(BaseModel):
    has_missing_or_conflict: bool = Field(description="True if there are missing essential details or conflicting requirements")
    clarifying_question: Optional[str] = Field(description="The question to ask the user if there are missing details or conflicts", default=None)

class StepInstruction(BaseModel):
    description: str = Field(description="Detailed instruction for this step")
    estimated_time_minutes: int = Field(description="Estimated time in minutes to complete this step")

class Recipe(BaseModel):
    id: str = Field(description="Unique identifier for this recipe option")
    title: str = Field(description="Creative title for the recipe")
    ingredients: List[str] = Field(description="List of ingredients needed")
    steps: List[StepInstruction] = Field(description="Step by step cooking instructions")
    total_time_minutes: int = Field(description="Total estimated cooking time")

class RecipeOptions(BaseModel):
    recipes: List[Recipe] = Field(description="A list of 2-3 recipe options")

class EvaluationScore(BaseModel):
    recipe_id: str = Field(description="ID of the recipe being evaluated")
    nutrition_score: int = Field(description="Score out of 10 for nutritional value")
    feasibility_score: int = Field(description="Score out of 10 for how feasible it is given constraints")
    availability_score: int = Field(description="Score out of 10 for ingredient availability/commonness")
    complexity_score: int = Field(description="Score out of 10 (higher means easier/better complexity match)")
    originality_score: int = Field(description="Score out of 10 for uniqueness and originality")
    total_score: int = Field(description="Sum of all scores")

class EvaluationResult(BaseModel):
    evaluations: List[EvaluationScore] = Field(description="Evaluations for all generated recipes")
    best_recipe_id: str = Field(description="The ID of the recipe with the highest total score")

class NutritionalInfo(BaseModel):
    calories: int = Field(description="Calories per serving")
    protein_g: int = Field(description="Grams of protein per serving")
    carbohydrates_g: int = Field(description="Grams of carbohydrates per serving")
    fat_g: int = Field(description="Grams of fat per serving")
    fiber_g: int = Field(description="Grams of fiber per serving")

class Pairings(BaseModel):
    side_dishes: List[str] = Field(description="Suggested side dishes")
    beverages: List[str] = Field(description="Suggested beverages")
    desserts: List[str] = Field(description="Suggested desserts")

class ShoppingCategory(BaseModel):
    category_name: str = Field(description="Name of the category (e.g., Produce, Dairy)")
    items: List[str] = Field(description="Items in this category")

class ShoppingList(BaseModel):
    categories: List[ShoppingCategory] = Field(description="Shopping list grouped by category")

class RefinedRecipe(BaseModel):
    title: str = Field(description="Final refined title")
    ingredients: List[str] = Field(description="Refined ingredient list with measurements")
    substitutions: List[str] = Field(description="Suggested allergy-safe or common substitutions")
    steps: List[StepInstruction] = Field(description="Detailed, refined step-by-step instructions")
    total_time_minutes: int = Field(description="Total estimated cooking time")
    servings: int = Field(description="Number of servings")
    cost_per_serving_usd: float = Field(description="Approximate cost per serving in USD")
    leftover_storage: str = Field(description="Instructions for storing leftovers")
    reheating_instructions: str = Field(description="Instructions for reheating")
    beginner_tips: List[str] = Field(description="Tips for beginners and common mistakes to avoid")

class QualityReview(BaseModel):
    passed: bool = Field(description="True if the recipe passes all quality, logical timing, and safety checks")
    feedback: str = Field(description="Feedback or corrections if it failed, or a success message if it passed")

class FinalOutput(BaseModel):
    recipe: RefinedRecipe
    nutrition: NutritionalInfo
    pairings: Pairings
    shopping_list: ShoppingList
    review: QualityReview
