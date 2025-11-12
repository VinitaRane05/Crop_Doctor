import requests

# Curated fallback data
REMEDIES = {
    "Powdery mildew": "Ensure proper air circulation, avoid overwatering, and apply sulfur-based fungicides.",
    "Late blight": "Use certified disease-free seeds, apply copper fungicide, and destroy infected plants.",
    "Rust": "Remove infected leaves and apply sulfur or copper fungicides.",
    "Leaf_Spot": "Prune infected leaves, avoid wetting foliage, and use preventive fungicides.",
    "Downy_mildew": "Reduce humidity, ensure good drainage, and spray with appropriate fungicides.",
    "Early_blight": "Rotate crops yearly, remove plant debris, and use fungicides like chlorothalonil or mancozeb.",
    "Blast": "Avoid excess nitrogen, maintain good drainage, and apply tricyclazole if necessary."
}

PLANT_INFO = {
    "Tomato": "Tomatoes are a warm-season crop rich in vitamin C and lycopene. Commonly affected by blight and leaf spot.",
    "Potato": "A major tuber crop, rich in carbohydrates. Often affected by blight and scab diseases.",
    "Corn": "Also known as maize, it’s a cereal crop affected by rust and leaf blight.",
    "Wheat": "A staple grain, commonly affected by rusts and mildews.",
    "Cucumber": "A vining plant grown for its refreshing fruits, often attacked by downy or powdery mildew.",
    "Rice": "A staple crop for half the world, prone to blast and sheath blight."
}

def get_remedy(disease):
    if disease in REMEDIES:
        return REMEDIES[disease]
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{disease.replace(' ', '_')}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("extract", "Information unavailable.")
    except Exception:
        pass
    return "No trusted remedy information available."

def get_plant_info(plant):
    if plant in PLANT_INFO:
        return PLANT_INFO[plant]
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{plant.replace(' ', '_')}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("extract", "No description found.")
    except Exception:
        pass
    return "No trusted information found for this plant."
