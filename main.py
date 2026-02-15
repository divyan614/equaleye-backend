from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from deepface import DeepFace
import numpy as np
from PIL import Image
import io

app = FastAPI(title="EqualEye API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "EqualEye backend is running"}


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    img_array = np.array(image)

    try:
        results = DeepFace.analyze(
            img_array,
            actions=["gender"],
            enforce_detection=False
        )
    except Exception as e:
        return {"error": str(e)}

    if not isinstance(results, list):
        results = [results]

    male = 0
    female = 0
    unknown = 0

    for face in results:
        gender = face.get("dominant_gender", "").lower()
        if gender == "man":
            male += 1
        elif gender == "woman":
            female += 1
        else:
            unknown += 1

    total = male + female + unknown
    if total == 0:
        equity_score = 0
    else:
        equity_score = int(100 - abs(male - female) * 100 / total)

    status = "Balanced" if equity_score > 80 else "Imbalanced"

    return {
        "total": total,
        "male": male,
        "female": female,
        "unknown": unknown,
        "equity_score": equity_score,
        "status": status,
    }
