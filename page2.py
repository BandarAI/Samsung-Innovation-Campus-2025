import streamlit as st
import cv2
import tempfile
import json
from model_loader import load_model

with open('food_items.json', 'r') as f:
    FOOD_ITEMS = json.load(f)

def text_detection(model, input_file, output_file):
    """Detect foods in video and save output video."""
    cap = cv2.VideoCapture(input_file)
    w, h, fps = (int(cap.get(x)) for x in (
        cv2.CAP_PROP_FRAME_WIDTH,
        cv2.CAP_PROP_FRAME_HEIGHT,
        cv2.CAP_PROP_FPS
    ))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, fps if fps > 0 else 25, (w, h))

    all_detections = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        res = model.predict(frame, conf=0.5, save=False)
        res_plotted = res[0].plot()[:, :, ::-1]
        out.write(res_plotted)

        class_names = res[0].names
        for box in res[0].boxes:
            class_id = int(box.cls[0])
            class_name = class_names[class_id].lower()
            all_detections.append(class_name)

    cap.release()
    out.release()

    detected_foods = [d for d in all_detections if d in FOOD_ITEMS]
    unique_foods = list(dict.fromkeys(detected_foods))

    return {
        'unique_foods': unique_foods,
        'output_path': output_file
    }


def app():
    st.title("Food Recognition & Macro Calculator")

    model = load_model()

    file = st.file_uploader("Upload a video file", type=("mp4",))

    preview_placeholder = None
    temp_file_path = None

    if 'page2_temp_file' in st.session_state:
        temp_file_path = st.session_state['page2_temp_file']

    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name
            st.session_state['page2_temp_file'] = temp_file_path

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            preview_placeholder = st.empty()
            preview_placeholder.video(file)

    button = st.sidebar.button("🎥 Detect and Calculate")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        output_path = tmp.name

    if button:
        if temp_file_path is not None:
            if preview_placeholder is not None:
                preview_placeholder.empty()
            res = text_detection(model, temp_file_path, output_path)
            if not res or not res.get('unique_foods'):
                st.warning("No food items detected in the video.")
            else:
                st.session_state['page2_unique_foods'] = res['unique_foods']
                st.session_state['page2_output_path'] = res['output_path']
                st.session_state['page2_processed'] = True
        else:
            st.error("Please upload a video file first")

    if st.session_state.get('page2_processed'):
        out_path = st.session_state.get('page2_output_path', output_path)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.video(out_path)

        unique_foods = st.session_state.get('page2_unique_foods', [])

        if not unique_foods:
            st.warning("No food items detected in the video.")
            return

        st.success(f"Detected {len(unique_foods)} food items")

        st.subheader("Enter weights for detected food items (in g):")
        for food in unique_foods:
            key = f"vid_w_{food}"
            if key not in st.session_state:
                st.session_state[key] = 0
            st.number_input(f"Weight of {food.capitalize()} (g):", min_value=0, step=1, key=key)

        if st.button("Calculate Macros", key="page2_calc"):
            total_protein = total_carbs = total_fat = total_calories = 0.0
            for food in unique_foods:
                weight_g = st.session_state.get(f"vid_w_{food}", 0)
                if weight_g <= 0:
                    continue
                food_data = FOOD_ITEMS[food]
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
