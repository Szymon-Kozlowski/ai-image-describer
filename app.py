import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

st.set_page_config(
    page_title="AI Image Describer", 
    page_icon="✍️", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

st.html("""
<style>     
        
section[data-testid="stSidebar"] {
    width: 240px !important;
}

section[data-testid="stSidebar"] > div {
    width: 240px !important;
}


[data-testid="stSidebar"] button {
    white-space: nowrap !important;
    overflow: hidden;
    text-overflow: ellipsis;

    padding: 0.35rem 0.6rem !important;
    font-size: 0.85rem !important;
    min-height: 2.2rem !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] button[kind="secondary"] {
    background-color: #0D0B0B !important; 
    border: 1px solid #444c56 !important; 
    color: #ffffff !important; 
}

[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background-color: #3b424a !important;
    border: 1px solid #768390 !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #2ea043 !important;
    border: 1px solid #2ea043 !important;
    color: white !important;
}

[data-testid="stSidebar"] button[kind="primary"]:hover {
    background-color: #3fb950 !important;
    border: 1px solid #3fb950 !important;
    color: white !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

</style>
""")

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None

def change_agent(new_agent):
    st.session_state.mode = new_agent
    st.session_state.analysis_result = None

personalities = {
    "General Expert": {
        "path": "assets/GeneralExpert.png",
        "desc": "General describer.",
        "system": "You are a professional, highly observant image analyst. Provide objective, deeply detailed descriptions. Plan your analysis to fit completely within 3 to 4 concise paragraphs and wrap up cleanly.",
        "prompt": "Provide a professional description of this image.",
        "temperature": 0.4,
        "top_p": 0.9,
        "max_tokens": 4096 
    },
    "Meme Expert": {
        "path": "assets/MemeExpert.png",
        "desc": "Meme identification. ",
        "system": (
            "You are expert in online culture, memes, and pop culture. "
            "You have access to Google Search to verify exact meme titles. "
            "CRITICAL RULE FOR URLs: You are strictly forbidden from guessing, formulating, or constructing URLs. "
            "You may ONLY provide a link if you can extract the exact, real URL directly from your Google Search results. "
            "If you cannot find the actual working Know Your Meme URL in your search results, you must state 'I couldn't find the exact page' instead of guessing."
        ),
        "prompt": (
            "1. Analyze this image and identify the underlying meme format or internet trope. Try to find at least 3 possible option to increase chance that one of them will be right one.\n"
            "2. Trigger your Google Search tool immediately to find this memes' official page on Know Your Meme."
            "Search for 'site:knowyourmeme.com [meme name]'." 
            "3. Provide the definitive origin and meaning." 
            "4. Provide a markdown link to the Know Your Meme page ONLY by copying the exact URL from your search results. Do not make one up."
        ),
        "temperature": 0.2,
        "top_p": 0.6,
        "max_tokens": 4096
    },
    "Chef": {
        "path": "assets/Chef.png",
        "desc": "Recipe creator.",
        "system": "You are a world-class chef. Provide a clear list of ingredients and a simple step-by-step recipe. Keep it streamlined so the recipe finishes cleanly without getting cut off.",
        "prompt": "Identify dish and it's ingredients then suggest a recipe.",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 4096
    },
    "Dungeon Master": {
        "path": "assets/DungeonMaster.png",
        "desc": "Fantasy world-building.",
        "system": "You are a creative D&D Dungeon Master. Write an atmospheric scene description. You must pace your narrative beautifully so that it naturally concludes with a dramatic closing thought within 4 paragraphs total. Do not ramble indefinitely.",
        "prompt": "Describe this image as a fantasy D&D location.",
        "temperature": 1.1,
        "top_p": 1.0,
        "max_tokens": 4096 
    },
    "Hoshimi Miyabi": {
        "path": "assets/HoshimiMiyabi.png",
        "desc": "Chief of Hollow Special Operations Section 6. ",
        "system": "You are Hoshimi Miyabi, Chief of Hollow Special Operations Section 6 from Zenless Zone Zero. You are an elite martial artist of the prestigious Hoshimi lineage—disciplined, principled, and intensely focused on your duty to eliminate Hollow anomalies, upholding justice and any forms of traning. Your speech is elegant and calm. You speak with absolute certainty and zero hesitation. You despise bureaucratic fluff and administrative details, leaving those matters entirely to your vice-chief, Yanagi. Maintain a cold, dignified, yet polite demeanor.",
        "prompt": "Analyze this image with the sharp focus. Structure your report into exactly two short, high-level tactical sections: 'Threat Assessment' and 'Eradication Strategy'. Start your response exactly with: \"I am Hoshimi Miyabi, Chief of Section 6. Here is my reconnaissance report:\" and end your response exactly with: \" At least that's what Yanagi would say.\"",
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 4096
}
}

st.sidebar.header("Select your Agent")

for name, details in personalities.items():
    is_active = st.session_state.mode == name

    cols = st.sidebar.columns(
        [1, 4],
        gap="small",
        vertical_alignment="center"
    )

    with cols[0]:
        try:
            st.image(details["path"], width=100)
        except Exception:
            st.write("🖼️")

    with cols[1]:
        st.button(
            name,
            key=f"btn_{name}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
            on_click=change_agent,
            args=(name,)
        )

mode = st.session_state.mode

active_agent = personalities.get(mode)

st.sidebar.markdown("---")

st.sidebar.markdown(f"**Current Agent:** `{mode if mode else 'None selected'}`")
if active_agent:
    st.sidebar.info(active_agent["desc"])
else:
    st.sidebar.info("👆 Please select an agent to begin.")

st.title("Image Describer")
st.markdown("Upload an image and let your chosen agent analyze it.")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

if uploaded_file and uploaded_file.name != st.session_state.last_uploaded_file:
    st.session_state.analysis_result = None
    st.session_state.last_uploaded_file = uploaded_file.name

if uploaded_file:
    image = Image.open(uploaded_file)
    with st.expander("View Uploaded Image", expanded=True):
        st.image(image, use_container_width=True)
    
    if not active_agent:
        st.warning("👈 Please select an agent from the sidebar before analyzing.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            analyze_btn = st.button("Describe Image", use_container_width=True, type="primary")
        with col2:
            refresh_btn = st.button("Try Again", use_container_width=True)

        if analyze_btn or refresh_btn:
            st.session_state.analysis_result = None 
            
            try:
                model = genai.GenerativeModel(
                    model_name='gemini-2.5-flash-lite',
                    system_instruction=active_agent["system"],
                    tools=[{'google_search': {}}] 
                )
            except Exception:
                model = genai.GenerativeModel(
                    model_name='gemini-2.5-flash-lite',
                    system_instruction=active_agent["system"]
                )

            final_prompt = active_agent["prompt"]
            if refresh_btn:
                final_prompt += " Dig deeper. Notice details you missed the first time and provide a fresh perspective."

            st.markdown("---")
            with st.chat_message("assistant", avatar=active_agent.get("path", None)):
                st.write(f"**{mode} is examining the image...**")
                
                try:
                    gen_config = {
                        "temperature": active_agent["temperature"],
                        "top_p": active_agent["top_p"],
                        "max_output_tokens": active_agent["max_tokens"]
                    }
                    
                    response = model.generate_content(
                        [final_prompt, image], 
                        stream=True,
                        generation_config=gen_config
                    )
                    
                    def stream_text():
                        for chunk in response:
                            yield chunk.text
                            
                    full_response = st.write_stream(stream_text())
                    st.session_state.analysis_result = full_response
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")

        elif st.session_state.analysis_result:
            st.markdown("---")
            with st.chat_message("assistant", avatar=active_agent.get("path", None)):
                st.markdown(st.session_state.analysis_result)