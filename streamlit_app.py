import streamlit as st
from google import genai
from PIL import Image
import io

# --- App Config ---
st.set_page_config(page_title="🎨 Google Banana (Gemini 2.5 Flash Image)", layout="wide")
st.title("🍌 Google Banana Image-to-Image Generator")

st.markdown("""
This app uses **Google Gemini 2.5 Flash Image (Banana)** model for image-to-image generation.  
Users can log in to [Google AI Studio](https://aistudio.google.com/) → copy their **API key**,  
and use it here to generate or edit images.
""")

# --- Sidebar: API Key Input ---
st.sidebar.header("🔑 Google Gemini API Key")
api_key = st.sidebar.text_input("Enter your Gemini API key", type="password")

if not api_key:
    st.sidebar.warning("Please enter your API key to continue.")
    st.stop()

# --- Main Controls ---
uploaded_file = st.file_uploader("📤 Upload an image to edit / enhance", type=["png", "jpg", "jpeg"])
prompt = st.text_area("📝 Describe the desired transformation", 
                      placeholder="Example: Turn this building into a nighttime scene with neon lights and reflections.")

generate_btn = st.button("🚀 Generate Image")

# --- Image Generation ---
if generate_btn:
    if not uploaded_file:
        st.error("Please upload an image first.")
        st.stop()
    if not prompt.strip():
        st.error("Please enter a prompt.")
        st.stop()

    try:
        image_bytes = uploaded_file.read()

        # Initialize Google Client with user key
        client = genai.Client(api_key=api_key)

        with st.spinner("Generating image... please wait ⏳"):
            response = client.models.generate_images(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt, image_bytes]
            )

        # Extract first candidate
        image_data = response.candidates[0].content.parts[0].inline_data.data
        generated_image = Image.open(io.BytesIO(image_data))

        st.success("✅ Image generated successfully!")
        st.image(generated_image, caption="Generated Result", use_column_width=True)

        # Download button
        img_bytes = io.BytesIO()
        generated_image.save(img_bytes, format="PNG")
        st.download_button(
            label="💾 Download Image",
            data=img_bytes.getvalue(),
            file_name="generated_image.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
