import streamlit as st
import requests
import base64
from pathlib import Path
from remedies3 import REMEDY_DB, get_wiki_summary, remedy_lookup

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

# --- Custom styling for links + green boxes ---
st.markdown("""
<style>
a.wikipedia-link {
    color: #8B0000 !important;
    font-weight: 600;
    text-decoration: none;
}
a.wikipedia-link:hover {
    text-decoration: underline;
}

.desc-box {
    background-color: #e8f5e9;
    padding: 12px;
    border-radius: 10px;
    border-left: 4px solid #2e7d32;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# Identify Plant (Name + Scientific Name)
def identify_plant(image_bytes, api_key):
    url = "https://api.plant.id/v3/identification"
    headers = {"Api-Key": api_key}
    files = {"images": image_bytes}

    r = requests.post(url, headers=headers, files=files)
    if r.status_code == 201:
        data = r.json().get("result", {})
        suggestions = data.get("classification", {}).get("suggestions", [])
        if not suggestions:
            return None
        
        best = suggestions[0]
        return {
            "name": best["name"],
            "scientific": best["details"].get("scientific_name", best["name"]),
            "probability": best["probability"]
        }
    return None

API_KEY = st.secrets["plantid"]["api_key"]
API_URL = "https://api.plant.id/v3/health_assessment"

st.title("🌱 Smart Crop Doctor")
st.write("Upload a leaf image and I'll check its health & explain the disease with trusted sources.")

uploaded_file = st.file_uploader("Choose a leaf image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Leaf", use_container_width=True)

    if st.button("Analyze"):
        image_bytes = uploaded_file.getvalue()
        files = {"images": image_bytes}
        headers = {"Api-Key": API_KEY}

        # -----------------------------------------------------------
        # PLANT IDENTIFICATION
        # -----------------------------------------------------------
        plant = identify_plant(image_bytes, API_KEY)

        if plant:
            st.subheader("🌿 Plant Identified")
            st.write(f"**Common Name:** {plant['name']}")
            st.write(f"**Scientific Name:** *{plant['scientific']}*")
            st.write(f"**Confidence:** {plant['probability'] * 100:.1f}%")

            # Wikipedia summary in green box
            plant_summary = get_wiki_summary(plant["scientific"])
            st.markdown(f'<div class="desc-box">{plant_summary}</div>', unsafe_allow_html=True)

            # Wikipedia link
            plant_wiki_link = f"https://en.wikipedia.org/wiki/{plant['scientific'].replace(' ', '_')}"
            st.markdown(
                f'<a href="{plant_wiki_link}" class="wikipedia-link" target="_blank">🔗 More about this plant on Wikipedia</a>',
                unsafe_allow_html=True
            )

            st.write("---")
        else:
            st.subheader("🌿 Plant Identification Failed")
            st.write("The system could not identify the plant species.")
            st.write("---")

        # -----------------------------------------------------------
        # HEALTH ASSESSMENT (DISEASE CHECK)
        # -----------------------------------------------------------
        response = requests.post(API_URL, headers=headers, files=files)

        if response.status_code == 201:
            result = response.json().get("result", {})
            health_info = result.get("is_healthy", {})
            prob = health_info.get("probability", 0) * 100

            # HEALTHY BLOCK
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

            # UNHEALTHY BLOCK
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

                        # Wikipedia summary in green box
                        summary = get_wiki_summary(disease_name)
                        st.markdown(f'<div class="desc-box">{summary}</div>', unsafe_allow_html=True)

                        # Wikipedia link
                        disease_wiki = f"https://en.wikipedia.org/wiki/{disease_name.replace(' ', '_')}"
                        st.markdown(
                            f'<a href="{disease_wiki}" class="wikipedia-link" target="_blank">🔗 More about {disease_name} on Wikipedia</a>',
                            unsafe_allow_html=True
                        )

                        # Remedy box
                        remedy = remedy_lookup(disease_name)
                        st.markdown(
                            f"""
                            <div style="background:#fff7ed; border-left:4px solid #c2410c; padding:10px; border-radius:8px; margin-top:10px;">
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
