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

set_bg("bgimage.jpg")

st.markdown("""
<style>
.stApp, .stMarkdown { color: #064e3b; }
h1, h2, h3, h4, h5, h6 { color: #064e3b !important; }
.stFileUploader label { color: #064e3b !important; font-weight: 700; }
.stFileUploader button { color: #f5f5dc !important; background-color: #064e3b !important; font-weight: 700; }
.stButton > button { color: #ffffff !important; background-color: #064e3b !important; font-weight: 700; border: none; }
.stButton > button:hover { background-color: #046c4e !important; }
a.wikipedia-link { color: #8B0000 !important; font-weight: 600; text-decoration: none; }
a.wikipedia-link:hover { text-decoration: underline; }
.desc-box {
    background-color: #e8f5e9;
    padding: 12px;
    border-radius: 10px;
    border-left: 4px solid #2e7d32;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

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
st.write("Upload a leaf image and I’ll analyze the plant & detect diseases.")

uploaded_file = st.file_uploader("Choose a leaf image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Leaf", use_container_width=True)

    if st.button("Analyze"):
        image_bytes = uploaded_file.getvalue()
        files = {"images": image_bytes}
        headers = {"Api-Key": API_KEY}

        plant = identify_plant(image_bytes, API_KEY)

        if plant:
            plant_summary = get_wiki_summary(plant["scientific"])
            plant_wiki = f"https://en.wikipedia.org/wiki/{plant['scientific'].replace(' ', '_')}"

            card_html = (
f"""
<div style="background-color:#e8f5e9;padding:18px;border-radius:12px;border-left:5px solid #2e7d32;margin-bottom:22px;">
<h3 style="margin-top:0;color:#064e3b;">🌿 Plant Identified</h3>
<p><b>Common Name:</b> {plant['name']}</p>
<p><b>Scientific Name:</b> <i>{plant['scientific']}</i></p>
<p><b>Confidence:</b> {plant['probability'] * 100:.1f}%</p>
"""
            )

            if plant_summary.strip():
                card_html += (
f"""
<div class="desc-box">{plant_summary}</div>
"""
                )

            card_html += (
f"""
<a href="{plant_wiki}" class="wikipedia-link" target="_blank">🔗 More about this plant on Wikipedia</a>
</div>
"""
            )

            st.markdown(card_html, unsafe_allow_html=True)

        else:
            st.subheader("🌿 Plant Identification Failed")
            st.write("Could not identify the plant species.")
            st.write("---")

        response = requests.post(API_URL, headers=headers, files=files)

        if response.status_code == 201:
            result = response.json().get("result", {})
            prob = result.get("is_healthy", {}).get("probability", 0) * 100

            if prob >= 75:
                st.markdown(
f"""
<div style="background-color:#14532d;color:#d1fae5;padding:15px;border-radius:10px;font-weight:bold;font-size:18px;text-align:center;">
🌿 Healthy: YES ({prob:.1f}%) – No issues found.
</div>
""",
unsafe_allow_html=True,
                )
            else:
                st.markdown(
f"""
<div style="background-color:#7f1d1d;color:#fee2e2;padding:15px;border-radius:10px;font-weight:bold;font-size:18px;text-align:center;">
⚠️ Healthy: NO ({prob:.1f}%)
</div>
""",
unsafe_allow_html=True,
                )

                suggestions = result.get("disease", {}).get("suggestions", [])

                if suggestions:
                    st.subheader("🦠 Possible Issues & Remedies (Trusted Sources)")
                    for s in suggestions[:3]:
                        name = s["name"]
                        probability = s["probability"] * 100
                        st.markdown(f"### {name} ({probability:.1f}%)")

                        summary = get_wiki_summary(name)
                        if summary.strip():
                            st.markdown(f'<div class="desc-box">{summary}</div>', unsafe_allow_html=True)

                        wiki = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
                        st.markdown(
                            f'<a href="{wiki}" class="wikipedia-link" target="_blank">🔗 More about {name} on Wikipedia</a>',
                            unsafe_allow_html=True
                        )

                        remedy = remedy_lookup(name)
                        st.markdown(
f"""
<div style="background:#e8f5e9;padding:10px;border-radius:8px;border-left:4px solid #2e7d32;margin-top:10px;">
<b>✔ Remedy:</b> {remedy}
</div>
""",
unsafe_allow_html=True,
                        )
                else:
                    st.write("No disease suggestions available.")
        else:
            st.error(f"❌ Error: {response.status_code}")
            st.write("Response:", response.text)
