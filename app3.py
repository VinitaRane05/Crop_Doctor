import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image, ImageOps
from remedies3 import get_remedy, get_plant_info
import os
import tensorflow as tf

MODEL_PATH = os.path.join(os.path.dirname(__file__), "keras_model.h5")

try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
except Exception as e:
    st.error(f"Could not load model: {e}")
    st.stop()

# Load your trained model (make sure the .h5 file is in your repo)
MODEL_PATH = "keras_model.h5"

# Replace these with your expanded dataset class names
CLASSES = [
    "Tomato___Late_blight",
    "Tomato___Leaf_Spot",
    "Potato___Early_blight",
    "Corn___Rust",
    "Wheat___Mildew",
    "Cucumber___Downy_mildew",
    "Rice___Blast"
]

def predict_image(image):
    """Preprocess image and make prediction."""
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    img = np.asarray(image) / 255.0
    img = np.expand_dims(img, axis=0)
    prediction = model.predict(img)
    index = np.argmax(prediction)
    confidence = float(np.max(prediction)) * 100
    label = CLASSES[index]
    return label, confidence

# Streamlit UI
st.set_page_config(page_title="Crop Disease Detector", page_icon="🌾", layout="centered")

st.title("🌿 Crop Doctor — Disease Detection & Remedies")
st.markdown("Upload a leaf image to identify disease and get trusted treatment advice.")

uploaded = st.file_uploader("Upload a plant leaf image", type=["jpg", "jpeg", "png"])

if uploaded is not None:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Analyzing the image..."):
        label, confidence = predict_image(image)

    # Parse plant and disease
    plant, disease = label.split("___")
    st.success(f"Detected: **{plant}** with **{disease}**")
    st.metric("Prediction Confidence", f"{confidence:.2f}%")

    # Fetch trusted info
    st.subheader("🪴 Plant Information")
    st.write(get_plant_info(plant))

    st.subheader("🧫 Disease Remedy")
    st.write(get_remedy(disease))

    st.caption("All information sourced from curated databases and Wikipedia.")
else:
    st.info("Upload an image of a crop leaf to begin detection.")

st.markdown("---")
st.caption("Built with ❤️ and a serious dislike for unreliable scraping.")
