import streamlit as st
import tempfile
import json
from model_loader import load_model

with open("food_items.json", "r") as f:
    FOOD_ITEMS = json.load(f)


def detect_foods(model, video_path):
    """
    Run YOLO on video and return unique detected food items.
    """
    detected = []

    results = model.predict(
        source=video_path,
        conf=0.5,
        stream=True,
        device="cpu"
    )

    for r in results:
        if r.boxes is None:
            continue

        for cls in r.boxes.cls:
            class_name = r.names[int(cls)].lower()
            if class_name in FOOD_ITEMS:
                detected.append(class_name)

    # keep order, remove duplicates
    return list(dict.fromkeys(detected))


def app():
    st.title("Food Recognition & Macro Calculator")

    model = load_model()

    file = st.file_uploader("Upload a video file", type=("mp4",))

    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(file.read())
            video_path = tmp.name

        st.success("Video uploaded successfully")

        if st.button("🔍 Detect Food Items"):
            with st.spinner("Running food detection..."):
                foods = detect_foods(model, video_path)

            if not foods:
                st.warning("No food items detected.")
                return

            st.session_state["detected_foods"] = foods
            st.success(f"Detected {len(foods)} food items")

    foods = st.session_state.get("detected_foods", [])
    if not foods:
        return

    st.subheader("Enter weights for detected food items (in g):")

    for food in foods:
        st.number_input(
            f"{food.capitalize()} (g)",
            min_value=0,
            step=1,
            key=f"w_{food}"
        )

    if st.button("📊 Calculate Macros"):
        total_protein = total_carbs = total_fat = total_calories = 0.0

        for food in foods:
            weight = st.session_state.get(f"w_{food}", 0)
            if weight <= 0:
                continue

            data = FOOD_ITEMS[food]
            total_protein += data["protein"] * weight / 100
            total_carbs += data["carbs"] * weight / 100
            total_fat += data["fat"] * weight / 100
            total_calories += data["calories"] * weight / 100

        st.subheader("📊 Macro Breakdown")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Protein", f"{total_protein:.2f} g")
        c2.metric("Carbs", f"{total_carbs:.2f} g")
        c3.metric("Fat", f"{total_fat:.2f} g")
        c4.metric("Calories", f"{total_calories:.0f} kcal")
