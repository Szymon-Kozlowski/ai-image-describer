import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(page_title="AI Vision Assistant (Free)")
st.title("Image Expert (Powered by Gemini)")

mode = st.sidebar.selectbox("Choose AI Personality", ["General Expert"])

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    if st.button("Analyze Image"):
        with st.spinner("Gemini is looking at your photo..."):
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompts = {
                "General Expert": "Describe this image in detail.",
                "Chef": "Identify ingredients in this image and suggest a recipe.",
                "Interior Designer": "Critique the design of this space and suggest improvements.",
                "Dungeon Master": "Describe this scene as if it is a room in a fantasy RPG dungeon."
            }

            response = model.generate_content([prompts[mode], image])
            
            st.markdown("### Analysis:")
            st.write(response.text)