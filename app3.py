import streamlit as st
import requests
import json
from PIL import Image
REMEDIES = {
    "Late blight": "Remove infected leaves and apply copper fungicide.",
    "Early blight": "Prune affected areas, rotate crops, use sulfur spray.",
    "Powdery mildew": "Spray neem oil weekly.",
    "Leaf spot": "Remove infected leaves, keep soil clean, use fungicide.",
    "Rust": "Use sulfur-based spray and remove infected leaves.",
    "Healthy": "Looks good! Maintain balanced soil and watering."
}


# --- Config ---
st.set_page_config(page_title="Crop Disease Detector", layout="centered")
DETECTION_API_URL = "https://your-model-api.com/predict"  # Replace with your actual endpoint


# --- Wikipedia summary fetch ---
def get_wikipedia_summary(plant_name):
    """Fetch short plant summary from Wikipedia REST API."""
    if not plant_name:
        return None
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{plant_name.replace(' ', '_')}"
    try:
        r = requests.get(url, timeout=6, headers={"User-Agent": "CropDoctor/1.0"})
        if r.status_code == 200:
            data = r.json()
            return {
                "title": data.get("title"),
                "extract": data.get("extract"),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page")
            }
    except Exception as e:
        print("Wikipedia error:", e)
    return None


# --- UI ---
st.title("🌾 Crop Disease Detector")
st.write("Upload a plant leaf image to identify its health status and get quick remedies.")

uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Leaf", use_container_width=True)

    if st.button("🔍 Analyze Leaf"):
        with st.spinner("Detecting..."):
            try:
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(DETECTION_API_URL, files=files)
                data = response.json()

                # Expected API JSON: { "plant": "Tomato", "disease": "Late blight", "confidence": 0.96 }
                plant = data.get("plant", "Unknown").strip()
                disease = data.get("disease", "Unknown").strip()
                confidence = round(float(data.get("confidence", 0)) * 100, 2)

                st.subheader(f"🌱 {plant} - {disease}")
                st.write(f"**Confidence:** {confidence}%")

                # Fetch plant info from Wikipedia
                wiki = get_wikipedia_summary(plant)
                if wiki:
                    st.markdown(f"**About {wiki['title']}:** {wiki['extract']}")
                    st.markdown(f"[Read more on Wikipedia]({wiki['url']})")

                # Remedies
                remedy = REMEDIES.get(disease) or REMEDIES.get(plant)
                if remedy:
                    st.markdown("### 💊 Suggested Remedy")
                    st.write(remedy)
                else:
                    st.info("No specific remedy found. Consult an agricultural extension service.")

            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("👆 Upload an image to begin analysis.")
