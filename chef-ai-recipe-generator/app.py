import streamlit as st
import json
import logging
from security import is_allowed_file, sanitize_text
from ingredient_parser import parse_ingredients
from pipeline import check_missing_info, run_pipeline

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Chef AI – Pro Recipe Generator", page_icon="🍳", layout="wide")

if "step" not in st.session_state:
    st.session_state.step = "collecting"
if "inputs" not in st.session_state:
    st.session_state.inputs = {}
if "clarification_question" not in st.session_state:
    st.session_state.clarification_question = ""
if "final_output" not in st.session_state:
    st.session_state.final_output = None

# Floating food emoji effect
st.markdown("""
<style>
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}
.floating-emoji {
    animation: float 3s ease-in-out infinite;
    font-size: 2rem;
    text-align: center;
    margin-bottom: 10px;
}
</style>
<div class="floating-emoji">🍔 🍕 🥗 🌮 🍣</div>
""", unsafe_allow_html=True)

st.title("Chef AI – Advanced Recipe Pipeline")
st.write("Turn your ingredients and constraints into a masterpiece!")

if st.session_state.step == "collecting":
    with st.form("recipe_form"):
        st.subheader("1. Ingredients")
        input_method = st.radio("Choose input method:", ["Text Input", "File Upload"])
        
        raw_text = ""
        uploaded_file = st.file_uploader("Upload an ingredients file (.txt or .json)", type=["txt", "json"])
        
        text_area_content = st.text_area("Or enter ingredients (comma or newline separated):", height=100)
        
        st.subheader("2. Preferences & Constraints")
        col1, col2 = st.columns(2)
        with col1:
            cuisine = st.text_input("Cuisine (e.g., Italian, Mexican, Fusion)", "")
            dietary = st.text_input("Dietary Restrictions (e.g., Vegan, Keto)", "")
            allergies = st.text_input("Allergies (e.g., Peanuts, Shellfish)", "")
        with col2:
            servings = st.number_input("Servings", min_value=1, value=2)
            cooking_time = st.number_input("Max Cooking Time (minutes)", min_value=5, value=30, step=5)
            appliances = st.text_input("Available Appliances (e.g., Oven, Air Fryer, Blender)", "Stove, Oven")
            
        submitted = st.form_submit_button("Start Recipe Pipeline")
        
        if submitted:
            # Process ingredients
            if input_method == "File Upload" and uploaded_file is not None:
                if is_allowed_file(uploaded_file.name):
                    stringio = uploaded_file.getvalue().decode("utf-8")
                    if uploaded_file.name.endswith('.json'):
                        try:
                            data = json.loads(stringio)
                            if isinstance(data, list):
                                raw_text = ", ".join(str(item) for item in data)
                            elif isinstance(data, dict) and 'ingredients' in data:
                                raw_text = ", ".join(str(item) for item in data['ingredients'])
                        except:
                            st.error("Invalid JSON format.")
                    else:
                        raw_text = stringio
            else:
                raw_text = text_area_content
                
            ingredients_list = parse_ingredients(sanitize_text(raw_text))
            
            st.session_state.inputs = {
                "ingredients": ingredients_list,
                "cuisine": sanitize_text(cuisine),
                "dietary_restrictions": sanitize_text(dietary),
                "allergies": sanitize_text(allergies),
                "servings": servings,
                "max_cooking_time_minutes": cooking_time,
                "appliances": sanitize_text(appliances),
                "additional_context": ""
            }
            
            with st.spinner("Analyzing inputs for missing information..."):
                try:
                    check_result = check_missing_info(st.session_state.inputs)
                    if check_result.has_missing_or_conflict and check_result.clarifying_question:
                        st.session_state.clarification_question = check_result.clarifying_question
                        st.session_state.step = "clarifying"
                        st.rerun()
                    else:
                        st.session_state.step = "generating"
                        st.rerun()
                except Exception as e:
                    st.error(f"Error checking inputs: {e}")

elif st.session_state.step == "clarifying":
    st.warning("Wait, I need a bit more clarification!")
    st.write(f"**Chef AI asks:** {st.session_state.clarification_question}")
    
    with st.form("clarification_form"):
        answer = st.text_input("Your answer:")
        submitted = st.form_submit_button("Continue")
        if submitted:
            st.session_state.inputs["additional_context"] = answer
            st.session_state.step = "generating"
            st.rerun()

elif st.session_state.step == "generating":
    with st.spinner("Executing 16-Step AI Pipeline... this may take a minute!"):
        try:
            output = run_pipeline(st.session_state.inputs)
            st.session_state.final_output = output
            st.session_state.step = "done"
            st.rerun()
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            if st.button("Start Over"):
                st.session_state.step = "collecting"
                st.rerun()

elif st.session_state.step == "done":
    st.success("Pipeline completed!")
    if st.button("Generate Another Recipe"):
        st.session_state.step = "collecting"
        st.session_state.inputs = {}
        st.session_state.final_output = None
        st.rerun()
        
    output = st.session_state.final_output
    recipe = output.recipe
    
    st.header(f"🍳 {recipe.title}")
    
    # AI Review Banner
    if output.review.passed:
        st.info(f"✅ AI Quality Check Passed: {output.review.feedback}")
    else:
        st.warning(f"⚠️ AI Quality Check Flagged: {output.review.feedback}")
        
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Servings", recipe.servings)
    col2.metric("Prep/Cook Time", f"{recipe.total_time_minutes} min")
    col3.metric("Est. Cost/Serving", f"${recipe.cost_per_serving_usd:.2f}")
    col4.metric("Calories", f"{output.nutrition.calories} kcal")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Recipe", "Nutrition", "Pairings & Tips", "Shopping List", "Leftovers"])
    
    with tab1:
        st.subheader("Ingredients")
        for item in recipe.ingredients:
            st.markdown(f"- {item}")
            
        st.subheader("Instructions")
        for i, step in enumerate(recipe.steps, 1):
            st.markdown(f"**Step {i} ({step.estimated_time_minutes} min):** {step.description}")
            
        if recipe.substitutions:
            st.subheader("Allergy-Safe / Common Substitutions")
            for sub in recipe.substitutions:
                st.markdown(f"- {sub}")
                
    with tab2:
        st.subheader("Nutritional Information (per serving)")
        st.write(f"- Calories: {output.nutrition.calories}")
        st.write(f"- Protein: {output.nutrition.protein_g}g")
        st.write(f"- Carbohydrates: {output.nutrition.carbohydrates_g}g")
        st.write(f"- Fat: {output.nutrition.fat_g}g")
        st.write(f"- Fiber: {output.nutrition.fiber_g}g")
        
    with tab3:
        st.subheader("Pairings")
        st.write("**Sides:**", ", ".join(output.pairings.side_dishes))
        st.write("**Beverages:**", ", ".join(output.pairings.beverages))
        st.write("**Desserts:**", ", ".join(output.pairings.desserts))
        
        st.subheader("Beginner Tips")
        for tip in recipe.beginner_tips:
            st.markdown(f"- 💡 {tip}")
            
    with tab4:
        st.subheader("Shopping List")
        for cat in output.shopping_list.categories:
            st.markdown(f"**{cat.category_name}**")
            for item in cat.items:
                st.markdown(f"- [ ] {item}")
                
    with tab5:
        st.subheader("Leftovers & Storage")
        st.write("**Storage:**", recipe.leftover_storage)
        st.write("**Reheating:**", recipe.reheating_instructions)
