import requests


REMEDY_DB = {
    "late blight": "Remove infected leaves immediately, apply copper fungicide, avoid overhead watering.",
    "early blight": "Prune affected leaves, rotate crops yearly, use sulfur-based spray.",
    "powdery mildew": "Spray neem oil or potassium bicarbonate, ensure good airflow.",
    "leaf spot": "Remove infected leaves, apply chlorothalonil spray, reduce moisture.",
    "rust": "Use sulfur fungicides, remove infected leaves, avoid overcrowding.",
    # add more as needed...
}


def get_wiki_summary(name):
    # try several reasonable search terms
    search_terms = [
        name,
        name + " disease",
        name.replace(" leaf spot", "") + " leaf spot",
        name.split()[0]
    ]

    for term in search_terms:
        if not term or term.strip() == "":
            continue
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + term.replace(" ", "_")
        try:
            r = requests.get(url, timeout=6)
            if r.status_code == 200:
                data = r.json()
                extract = data.get("extract", "")
                if extract and extract.strip():
                    return extract
        except Exception:
            pass

    return ""


def remedy_lookup(name):
    name = (name or "").lower().strip()

    # exact match
    if name in REMEDY_DB:
        return REMEDY_DB[name]

    # partial match
    for key in REMEDY_DB:
        if key in name:
            return REMEDY_DB[key]

    # broad categories fallback
    if "fungi" in name or "fungal" in name:
        return "Use broad-spectrum fungicides (copper or sulfur), remove infected leaves, improve airflow."
    if "bacteria" in name or "bacterial" in name:
        return "Use antibacterial copper spray, disinfect tools, improve drainage and airflow."
    if "insect" in name or "insecta" in name or "aphid" in name or "moth" in name:
        return "Inspect and remove pests manually; use neem oil or appropriate insecticidal soap."

    return "No curated remedy available yet."
