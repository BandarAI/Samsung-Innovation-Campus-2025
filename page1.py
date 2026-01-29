import streamlit as st
import PIL
import json
from model_loader import load_model

with open('food_items.json', 'r') as f:
    FOOD_ITEMS = json.load(f)

def text_detection(model, file):
    uploaded_image = PIL.Image.open(file)
    res = model.predict(uploaded_image, conf=0.5)

    class_names = res[0].names
    boxes = res[0].boxes
    detections = []

    for box in boxes:
        class_id = int(box.cls[0])
        class_name = class_names[class_id].lower()
        detections.append(class_name)

    res_plotted = res[0].plot()[:, :, ::-1]

    detected_foods = [d for d in detections if d in FOOD_ITEMS]
    unique_foods = list(dict.fromkeys(detected_foods)) 

    return {
        'unique_foods': unique_foods,
        'res_plotted': res_plotted
    }


def app():
    st.title("Food Recognition & Macro Calculator")  # ONLY this one

    model = load_model()

    file = st.file_uploader("Upload an image", type=("jpg", "jpeg", "png"))

    image_placeholder = None

    if file is not None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            image_placeholder = st.empty()
            image_placeholder.image(file, caption='Selected Image', width=700)

    button = st.sidebar.button("🔍 Detect and Calculate")
    if button:
        if file is not None:
            if image_placeholder is not None:
                image_placeholder.empty()
            res = text_detection(model, file)
            if not res or not res.get('unique_foods'):
                st.warning("No food items detected in the image.")
            else:
                st.session_state['page1_unique_foods'] = res.get('unique_foods', [])
                st.session_state['page1_res_plotted'] = res.get('res_plotted')
                st.session_state['page1_processed'] = True
        else:
            st.error("Please upload an image first")

    if st.session_state.get('page1_processed'):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(st.session_state.get('page1_res_plotted'), caption='Detection Results', width=700)

        unique_foods = st.session_state.get('page1_unique_foods', [])
        if not unique_foods:
            st.warning("No food items detected in the image.")
            return

        st.success(f"Detected {len(unique_foods)} food items")

        st.subheader("Enter weights for detected food items (in g):")
        for food in unique_foods:
            key = f"img_w_{food}"
            if key not in st.session_state:
                st.session_state[key] = 0
            st.number_input(f"Weight of {food.capitalize()} (g):", min_value=0, step=1, key=key)

        if st.button("Calculate Macros", key="page1_calc"):
            total_protein = total_carbs = total_fat = total_calories = 0.0
            for food in unique_foods:
                weight_g = st.session_state.get(f"img_w_{food}", 0)
                if weight_g <= 0:
                    continue
                food_data = FOOD_ITEMS.get(food)
                if not food_data:
                    continue
                total_protein += (food_data['protein'] * weight_g) / 100.0
                total_carbs += (food_data['carbs'] * weight_g) / 100.0
                total_fat += (food_data['fat'] * weight_g) / 100.0
                total_calories += (food_data['calories'] * weight_g) / 100.0

            st.subheader("📊 Macro Breakdown:")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Protein", f"{total_protein:.2f} g")
            with col2:
                st.metric("Carbs", f"{total_carbs:.2f} g")
            with col3:
                st.metric("Fat", f"{total_fat:.2f} g")
            with col4:
                st.metric("Calories", f"{total_calories:.0f} kcal")
