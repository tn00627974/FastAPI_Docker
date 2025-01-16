from fastapi import FastAPI, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from typing import Union
from model import model_pipeline
from PIL import Image
from io import BytesIO
import os

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse("index.html")


@app.post("/predict", response_class=JSONResponse)
async def predict(request: Request):
    form = await request.form()
    question = form["question"]
    image = Image.open(form["image"].file)
    result = model_pipeline(question, image)
    return {"result": result}  # 返回 JSON 格式的預測結果


# 新增健康檢查路由
@app.get("/health", response_class=JSONResponse)
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
