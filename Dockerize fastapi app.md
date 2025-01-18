https://www.youtube.com/watch?v=ED6PRjmXgBA
https://www.youtube.com/watch?v=0c96PQd3nA8

#  FastAPI 和 Docker 建立 ML 應用程式

- 此專案是 支援`中文`與`英文`對圖片做提問，不需付任何API token的費用
- 使用Docker 快速Build 啟用

Hugging Face 模型連結 :
https://huggingface.co/dandelin/vilt-b32-finetuned-vqa
這是一個 Transformer 影像及文字轉換器(可處理兩個圖像和文字)
- 對圖像發送訊息
- 接著詢問 : 舉例 : `動物再做甚麼? 他是甚麼動物 等等 `

![](https://i.imgur.com/VaFTG01.png)

使用[[Ulysses/成長筆記本/資料工程師/程式語言/Python/UV 虛擬環境 new|UV 虛擬環境 new]]

```bash
uv init fastapi_docker
uv add fastapi[standard]>=0.110.3
googletrans==4.0.0rc1
jupyter>=1.1.1
pillow>=11.1.0
python-multipart>=0.0.20
torch>=2.5.1
transformers>=4.48.0
uvicorn>=0.34.0
```

模型檔名取名為 `model.py` 
```python
from transformers import ViltProcessor, ViltForQuestionAnswering
import requests
from PIL import Image

# prepare image + question
url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)
text = "How many cats are there?"

processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")

# prepare inputs
encoding = processor(image, text, return_tensors="pt")

# forward pass
outputs = model(**encoding)
logits = outputs.logits
idx = logits.argmax(-1).item()
print("Predicted answer:", model.config.id2label[idx])

```

接著進行改寫 `model.py` 
- model_pipeline 為 圖片與文字的問答模型 (給fastAPI做函式使用)
```python
from transformers import ViltProcessor, ViltForQuestionAnswering
from PIL import Image
from googletrans import Translator  # google translate

processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
translator = Translator()  # google translate


# model_pipeline 為 圖片與文字的問答模型
def model_pipeline(text: str, image: Image):
    # 判斷是否有中文，若有則翻譯成英文
    if any("\u4e00" <= char <= "\u9fff" for char in text):
        translated_text = translator.translate(text, src="zh-tw", dest="en")
        text = translated_text.text

    encoding = processor(image, text, return_tensors="pt")
    outputs = model(**encoding)
    logits = outputs.logits
    idx = logits.argmax(-1).item()
    return model.config.id2label[idx]  # 回傳預測答案

```

- main.py
```python
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

```

index.html
```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ML Application</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css">
    <style>
        body {
            padding: 20px;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
        }

        .result {
            margin-top: 20px;
            padding: 10px;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>請上傳動物圖片進行提問！</h1>
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="row">
                <div class="six columns">
                    <label for="image">Upload Image</label>
                    <input class="u-full-width" type="file" id="image" name="image" accept="image/*" required>
                </div>
                <div class="six columns">
                    <label for="question">Enter Question</label>
                    <input class="u-full-width" type="text" id="question" name="question" required>
                </div>
            </div>
            <input class="button-primary" type="submit" value="Submit">
        </form>
        <div id="result" class="result" style="display: none;"></div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function (event) {
            event.preventDefault();
            const formData = new FormData(this);
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            document.getElementById('result').style.display = 'block';
            document.getElementById('result').innerText = `預測結果: ${result.result}`;
        });
    </script>
</body>

</html>
```

# 使用 Docker 打包
https://jumping-code.com/2024/08/23/uv-pip-docker-image/

初始化
```bash
docker init
```


![](https://i.imgur.com/OaJRhfU.png)


![](https://i.imgur.com/Ahmn0JP.png)


```bash
docker compose up --build
```