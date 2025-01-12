from fastapi import FastAPI, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from typing import Union
from model import model_pipeline
from PIL import Image
from io import BytesIO
import os

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse("index.html")


@app.post("/predict", response_class=HTMLResponse)
def predict(question: str = Form(...), image: UploadFile = Form(...)):
    image_data = image.file.read()
    image = Image.open(BytesIO(image_data))
    result = model_pipeline(question, image)
    return result.text


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
