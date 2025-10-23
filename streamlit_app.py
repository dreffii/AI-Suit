import streamlit as st
from PIL import Image
import io
from your_gemini_module import analyze_image, generate_image_with_flash

st.title("🏛️ Architectural Visualization Creator")

uploaded_file = st.file_uploader("Upload a sketch, render, or concept", type=["png", "jpg", "jpeg"])
prompt = st.text_area("Smart prompt will appear here", height=120)
generate_prompt_btn = st.button("Generate Smart Prompt")
generate_image_btn = st.button("Generate Rendering")

if generate_prompt_btn and uploaded_file:
    with st.spinner("Analyzing image to generate prompt..."):
        prompt_text = analyze_image(uploaded_file, instruction="Your detailed architectural prompt instruction")
        prompt = prompt_text
        st.success("Smart prompt generated!")

if generate_image_btn and prompt:
    with st.spinner("Generating rendering..."):
        result_image = generate_image_with_flash(prompt)
        st.image(result_image, caption="Final Rendering", use_column_width=True)
