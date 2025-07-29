from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

# --- Mocked Service Functions (TO BE REPLACED WITH ACTUAL GEMINI SUGGESTIONS) --- #

def process_image(img_path):
    # Dummy output simulating object detection
    return [
        {"label": "empty wall", "box": [100, 100, 300, 300]},
        {"label": "corner", "box": [400, 400, 500, 500]}
    ]

def parse_vibe(vibe_prompt):
    # Simulate vibe translation
    if "cozy" in vibe_prompt.lower():
        return ["warm lighting", "wood", "plants"]
    elif "minimal" in vibe_prompt.lower():
        return ["neutral tones", "clean lines", "negative space"]
    return ["art", "decor"]

def generate_suggestions(layout_data, vibe_tags):
    suggestions = []
    for obj in layout_data:
        if obj["label"] == "empty wall" and "art" in vibe_tags:
            suggestions.append({
                "action": "hang",
                "item": "framed art",
                "location": obj["box"]
            })
        if obj["label"] == "corner" and "warm lighting" in vibe_tags:
            suggestions.append({
                "action": "place",
                "item": "floor lamp",
                "location": obj["box"]
            })
    return suggestions

# --- FastAPI App Setup --- #

app = FastAPI(title="Kairos API")

# CORS (for Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models --- #

class Suggestion(BaseModel):
    action: str
    item: str
    location: List[int]

class AnalyzeResponse(BaseModel):
    suggestions: List[Suggestion]
    layout: List[dict]
    vibe_tags: List[str]

# --- Routes --- #

@app.post("/analyze-room", response_model=AnalyzeResponse)
async def analyze_room(image: UploadFile, vibe: str = Form(...)):
    os.makedirs("data", exist_ok=True)
    image_path = f"data/{image.filename}"
    with open(image_path, "wb") as f:
        f.write(await image.read())

    layout_data = process_image(image_path)
    vibe_tags = parse_vibe(vibe)
    suggestions = generate_suggestions(layout_data, vibe_tags)

    return AnalyzeResponse(
        suggestions=suggestions,
        layout=layout_data,
        vibe_tags=vibe_tags
    )
