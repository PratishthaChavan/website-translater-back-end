import requests
from PIL import Image,ImageDraw,ImageFont
from paddleocr import PaddleOCR

img_path = 'images/download.jpg'
# img_path = 'output/sized.jpg'
ocr = PaddleOCR(
    lang="en"
)
font = ImageFont.load_default()
image = Image.open(img_path)
draw = ImageDraw.Draw(image)

draw.text((10, 10), "", fill="black")

print(image.size)
print(image.mode)

result = ocr.predict(img_path)
for res in result:
    texts = res['rec_texts']
    boxes = res['rec_polys']
    print(texts)
    for text, box in zip(texts, boxes):
        points = [
        (int(point[0]), int(point[1]))
        for point in box
        ]

        print("TEXT:", text)
        print("BOX:", points)


        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        left = min(xs)
        top = min(ys)
        right = max(xs)
        bottom = max(ys)
        draw.rectangle(
            (left, top, right, bottom),
            fill="white"
        )

image.save("output/draw_text_font.jpg")
image.show()
