import json
from pathlib import Path

import numpy as np
import tensorflow as tf

from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from api.database import init_db, insert_prediction, get_prediction_history


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE_DIR / "model" / "corn_leaf_mobilenetv2.keras"
CLASS_NAMES_PATH = BASE_DIR / "model" / "class_names.json"

IMG_SIZE = (224, 224)

app = FastAPI(
    title="Corn Leaf Disease Classification API",
    description="REST API untuk klasifikasi penyakit daun jagung menggunakan MobileNetV2.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
class_names = None


@app.on_event("startup")
def startup_event():
    global model, class_names

    init_db()

    model = tf.keras.models.load_model(MODEL_PATH)

    with open(CLASS_NAMES_PATH, "r") as file:
        class_names = json.load(file)


def preprocess_image(image_file):
    image = Image.open(image_file).convert("RGB")
    image = image.resize(IMG_SIZE)

    image_array = tf.keras.utils.img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)
    image_array = preprocess_input(image_array)

    return image_array


@app.get("/")
def root():
    return {
        "message": "Corn Leaf Disease Classification API is running.",
        "classes": class_names
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_array = preprocess_image(file.file)

    prediction = model.predict(image_array, verbose=0)[0]

    predicted_index = int(np.argmax(prediction))
    predicted_class = class_names[predicted_index]
    confidence = float(np.max(prediction))

    insert_prediction(
        filename=file.filename,
        prediction=predicted_class,
        confidence=confidence
    )

    return {
        "filename": file.filename,
        "prediction": predicted_class,
        "confidence": round(confidence, 4)
    }


@app.get("/history")
def history(limit: int = 10):
    return {
        "history": get_prediction_history(limit=limit)
    }