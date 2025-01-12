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
