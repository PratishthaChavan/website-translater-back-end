from transformers import pipeline
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="japan",
    device="cpu",
    enable_mkldnn=False
)
img_path = "images/image.png"
translator = pipeline(
    task="translation",
    model="facebook/nllb-200-distilled-600M",
    src_lang="jpn_Jpan",  # Source language (English)
    tgt_lang="eng_Latn"   # Target language (French)
)
result = ocr.predict(img_path)

for res in result:
    texts = res["rec_texts"]
    print(texts)
    translated = translator(texts)
    print("Translated text:",translated)

text = "United Nations Chief says there is no military solution in Syria."


print(translated[0]['translation_text'])