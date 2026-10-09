import base64, requests, cv2

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
MODEL_NAME = "gemma3:12b"

def gemma_read_crop(image, box, pad=6, scale=4):
    x1, y1, x2, y2 = box
    h, w = image.shape[:2]
    crop = image[max(0, y1 - pad):min(h, y2 + pad),
                 max(0, x1 - pad):min(w, x2 + pad)]
    crop = cv2.resize(crop, None, fx=scale, fy=scale,
                      interpolation=cv2.INTER_CUBIC)
    crop = cv2.copyMakeBorder(crop, 60, 60, 60, 60,
                              cv2.BORDER_CONSTANT, value=(255, 255, 255))

    ok, buf = cv2.imencode(".png", crop)
    b64 = base64.b64encode(buf.tobytes()).decode()

    prompt = (
        "This image is a vertical column of small Japanese hiragana (furigana). "
        "Read it top to bottom. Output ONLY the hiragana, nothing else. "
        "Check each character for dakuten marks (゛), for example こ vs ご."
    )

    r = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "temperature": 0,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ]}],
    }, timeout=300)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

# test on your furigana box
img = cv2.imread("images/deimon101.png")
print(gemma_read_crop(img, [1815, 708, 1856, 797]))