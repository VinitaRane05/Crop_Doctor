import streamlit as st
import requests
import base64
from pathlib import Path
from remedies3 import REMEDY_DB, get_wiki_summary

def set_bg(image_file):
    img_bytes = Path(image_file).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/jpg;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background
set_bg("bgimage.jpg")

# --- Global text styles ---
st.markdown(
    """
    <style>
    .stApp, .stMarkdown, .css-18e3th9, .css-10trblm { color: #064e3b; }
    h1, h2, h3, h4, h5, h6 { color: #064e3b !important; }

    .stFileUploader label { color: #064e3b !important; font-weight: 700; }
    .stFileUploader button { color: #f5f5dc !important; background-color: #064e3b !important; font-weight: 700; }
    .stButton > button { color: #ffffff !important; background-color: #064e3b !important; font-weight: 700; border: none; }
    .stButton > button:hover { background-color: #046c4e !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- API Setup ---
# YOU add your key in .streamlit/secrets.toml, like this:
# [plantid]
# api_key="YOUR_KEY_HERE"

API_KEY = st.secrets["plantid"]["api_key"]
API_URL = "https://api.plant.id/v3/health_assessment"

st.title("🌱 Smart Crop Doctor")
st.write("Upload a leaf image and I'll check its health & explain the disease with trusted sources.")

uploaded_file = st.file_uploader("Choose a leaf image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Leaf", use_container_width=True)
    
    if st.button("Analyze"):
        files = {"images": uploaded_file.getvalue()}
        headers = {"Api-Key": API_KEY}
        
        response = requests.post(API_URL, headers=headers, files=files)
        
        if response.status_code == 201:
            result = response.json().get("result", {})
            health_info = result.get("is_healthy", {})
            prob = health_info.get("probability", 0) * 100
            
            # --- HEALTHY ---
            if prob >= 75:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #14532d;
                        color: #d1fae5;
                        padding: 15px;
                        border-radius: 10px;
                        font-weight: bold;
                        font-size: 18px;
                        text-align: center;
                    ">
                    🌿 Healthy: YES ({prob:.1f}%) – No remedies needed!
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # --- UNHEALTHY ---
            else:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #7f1d1d;
                        color: #fee2e2;
                        padding: 15px;
                        border-radius: 10px;
                        font-weight: bold;
                        font-size: 18px;
                        text-align: center;
                    ">
                    ⚠️ Healthy: NO ({prob:.1f}%)
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                disease_info = result.get("disease", {})
                suggestions = disease_info.get("suggestions", [])

                if suggestions:
                    st.subheader("🦠 Possible Issues & Remedies (Trusted Sources)")
                    for s in suggestions[:3]:
                        disease_name = s["name"]
                        probability = s["probability"] * 100
                        
                        st.markdown(f"### {disease_name} ({probability:.1f}%)")

                        # Wikipedia summary
                        summary = get_wiki_summary(disease_name)
                        st.write(summary)

                        # Remedy (trusted curated DB)
                        remedy = REMEDY_DB.get(disease_name.lower(), "No curated remedy available yet.")
                        st.markdown(
                            f"""
                            <div style="background:#fff7ed; border-left:4px solid #c2410c; padding:10px; border-radius:8px;">
                            <b>✔ Remedy:</b> {remedy}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.write("")

                else:
                    st.write("No disease detected.")
        else:
            st.error(f"❌ Error: {response.status_code}")
            st.write("Response text:", response.text)
