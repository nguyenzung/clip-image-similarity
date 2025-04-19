from fastapi import FastAPI, UploadFile
from predictor import SimilarityCalculator
import os
import uuid

app = FastAPI()
similarity_calculator = SimilarityCalculator()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
TEMP_FOLDER = "temp_images"
os.makedirs(TEMP_FOLDER, exist_ok=True)


@app.post("/predict/")
async def predict(files: list[UploadFile]):
    try:
        if len(files) != 2:
            return {"error": "You must upload exactly two image files."}

        file_exts = [os.path.splitext(file.filename)[1].lower() for file in files]

        for ext in file_exts:
            if ext not in ALLOWED_EXTENSIONS:
                return {
                    "error": "Both uploaded files must be in JPG, JPEG, or PNG format."
                }

        image_paths = []

        for i, file in enumerate(files):
            print("Filename:", file.filename)
            destination_path = os.path.join(TEMP_FOLDER, file.filename)
            image_paths.append(file.file.read())

        print("Calcualte image similarity")
        result = similarity_calculator.calculate_similarity(*image_paths)

        return result
    except Exception as e:
        return {"error": str(e)}