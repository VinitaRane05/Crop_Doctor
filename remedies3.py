import requests


REMEDY_DB = {
    "late blight": "Remove infected leaves immediately, apply copper fungicide, avoid overhead watering.",
    "early blight": "Prune affected leaves, rotate crops yearly, use sulfur-based spray.",
    "powdery mildew": "Spray neem oil or potassium bicarbonate, ensure good airflow.",
    "leaf spot": "Remove infected leaves, apply chlorothalonil spray, reduce moisture.",
    "rust": "Use sulfur fungicides, remove infected leaves, avoid overcrowding.",
}


def get_wiki_summary(name):
    search_terms = [
        name,
        name + " disease",
        name.replace(" leaf spot", "") + " leaf spot",
        name.split()[0],
    ]

    for term in search_terms:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + term.replace(" ", "_")
        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                extract = data.get("extract")
                if extract:
                    return extract
        except:
            pass

    return "No reliable Wikipedia information available for this disease."


def remedy_lookup(name):
    name = name.lower()

    # Exact match first
    if name in REMEDY_DB:
        return REMEDY_DB[name]

    # Partial match (leaf spot, mildew, rust, etc.)
    for key in REMEDY_DB:
        if key in name:
            return REMEDY_DB[key]

    # Broad AI-returned categories
    if "fungi" in name or "fungal" in name:
        return "Use broad-spectrum fungicides (copper, sulfur), remove infected leaves, improve airflow."

    if "bacteria" in name or "bacterial" in name:
        return "Use antibacterial copper spray, disinfect tools, improve drainage and airflow."

    return "No curated remedy available yet."
