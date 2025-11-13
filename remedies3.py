import requests

# --- Curated Remedies Database (edit anytime) ---
REMEDY_DB = {
    "late blight": "Remove infected leaves immediately, use copper-based fungicide, avoid overhead watering.",
    "early blight": "Prune affected leaves, apply sulfur or copper spray, rotate crops yearly.",
    "powdery mildew": "Spray neem oil or potassium bicarbonate, improve airflow.",
    "leaf spot": "Remove infected leaves, use chlorothalonil spray, avoid wetting leaves.",
    "rust": "Use sulfur fungicides, remove infected plant parts, avoid overcrowding."
}

# --- Wikipedia Summary Fetch ---
def get_wiki_summary(query):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")

    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            return data.get("extract", "No summary available.")
        else:
            return "No Wikipedia data found."
    except:
        return "Wikipedia lookup failed."
