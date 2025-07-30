from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from PIL import Image
import requests
import os
import tempfile
import google.generativeai as genai

# Initialize FastAPI app
app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set API keys
GOOGLE_API_KEY = "GOOGLE_API_KEY"
SERPAPI_KEY = "SERPAPI_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

# Models
class Suggestion(BaseModel):
    action: str
    item: str
    location: List[int]

class Product(BaseModel):
    title: str
    price: str
    thumbnail: str
    link: str

class AnalyzeResponse(BaseModel):
    suggestions: List[Suggestion]
    layout: Dict[str, Any]
    vibe_tags: List[str]
    gemini_design_ideas: str
    products: List[Product]

# Dummy logic for layout/suggestions
def analyze_image(image_path: str) -> Dict[str, Any]:
    return {
        "walls": 4,
        "objects": ["sofa", "table", "lamp"]
    }

def generate_suggestions(layout: Dict[str, Any], vibe: str) -> List[Dict[str, Any]]:
    return [
        {"action": "add", "item": "floor lamp", "location": [100, 200]},
        {"action": "hang", "item": "framed art", "location": [300, 150]}
    ]

def get_gemini_suggestions(image_path: str, vibe: str) -> str:
    model = genai.GenerativeModel("gemini-2.5-flash")
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()
    response = model.generate_content([
        "Give me interior design suggestions for a room based on this vibe: " + vibe,
        Image.open(image_path)
    ])
    return response.text if hasattr(response, "text") else str(response)

def fetch_products_from_google(item: str) -> List[Product]:
    params = {
        "engine": "google_shopping",
        "location": "Chennai, India",
        "gl": "in",
        "hl": "en",
        "q": item,
        "api_key": SERPAPI_KEY
    }
    response = requests.get("https://serpapi.com/search", params=params)
    if response.status_code == 200:
        results = response.json().get("shopping_results", [])
        return [
            Product(
                title=p.get("title", ""),
                price=p.get("price", ""),
                thumbnail=p.get("thumbnail", ""),
                link=p.get("link", "")
            ) for p in results[:3]
        ]
    return []

@app.post("/analyze-room", response_model=AnalyzeResponse)
async def analyze_room(image: UploadFile, vibe: str = Form(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await image.read())
        image_path = tmp.name

    layout_data = analyze_image(image_path)
    suggestions = generate_suggestions(layout_data, vibe)
    gemini_response = get_gemini_suggestions(image_path, vibe)

    all_products = []
    for s in suggestions:
        products = fetch_products_from_google(s["item"])
        all_products.extend(products)

    return {
        "suggestions": suggestions,
        "layout": layout_data,
        "vibe_tags": [vibe],
        "gemini_design_ideas": gemini_response,
        "products": all_products
    }
