import streamlit as st
import requests
from PIL import Image
REMEDIES = {
    "Late blight": "Remove infected leaves, apply copper fungicide.",
    "Early blight": "Prune infected leaves, rotate crops, apply sulfur spray.",
    "Powdery mildew": "Spray neem oil or potassium bicarbonate.",
    "Leaf spot": "Remove affected leaves, improve airflow.",
    "Rust": "Use sulfur spray, avoid overhead watering.",
    "Healthy": "Plant is fine! Maintain good soil and watering."
}


st.set_page_config(page_title="Crop Doctor", layout="centered")

# --- Your Plant.id API Key ---
API_KEY = st.secrets["plantid"]["api_key"] if "plantid" in st.secrets else "YOUR_FALLBACK_API_KEY"
DETECTION_API_URL = "https://perenual.com/user/developer"

# --- Wikipedia API for plant info ---
def get_wikipedia_summary(plant_name):
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


# --- Streamlit UI ---
st.title("🌿 Crop Disease Detector")
st.write("Upload a leaf image to detect possible plant diseases using Plant.id API.")

uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Leaf", use_container_width=True)

    if st.button("🔍 Analyze Leaf"):
        with st.spinner("Analyzing leaf..."):
            try:
                # Send image to Plant.id API
                files = [("images", uploaded_file.getvalue())]
                headers = {"Api-Key": API_KEY}

                response = requests.post(DETECTION_API_URL, headers=headers, files=files)
                data = response.json()

                # Debug view (optional)
                # st.write(data)

                # Extract details safely
                suggestions = data.get("result", {}).get("disease", [])
                if not suggestions:
                    st.error("No disease detected. Try another image.")
                else:
                    # Grab top prediction
                    disease_info = suggestions[0]
                    plant_name = data.get("result", {}).get("is_plant", {}).get("suggestions", [{}])[0].get("plant_name", "Unknown")
                    disease_name = disease_info.get("name", "Unknown Disease")
                    confidence = round(disease_info.get("probability", 0) * 100, 2)

                    st.subheader(f"🌱 {plant_name} — {disease_name}")
                    st.write(f"**Confidence:** {confidence}%")

                    # Wikipedia info
                    wiki = get_wikipedia_summary(plant_name)
                    if wiki:
                        st.markdown(f"**About {wiki['title']}:** {wiki['extract']}")
                        st.markdown(f"[Read more on Wikipedia]({wiki['url']})")

                    # Remedies
                    remedy = REMEDIES.get(disease_name) or REMEDIES.get(plant_name)
                    if remedy:
                        st.markdown("### 💊 Suggested Remedy")
                        st.write(remedy)
                    else:
                        st.info("No remedy found. Consult local agricultural experts.")

            except Exception as e:
                st.error(f"Error: {e}")

