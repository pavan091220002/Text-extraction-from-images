from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
import numpy as np
import cv2
import pytesseract
import string
import random
import os
from io import BytesIO

app = FastAPI()

UPLOAD_DIRECTORY = 'uploads'
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIRECTORY), name="uploads")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_image(request, image_upload: UploadFile = File(...)):
    try:
        image = Image.open(BytesIO(await image_upload.read()))

        # Converting image to array
        image_arr = np.array(image.convert('RGB'))
        # Converting image to grayscale
        gray_img_arr = cv2.cvtColor(image_arr, cv2.COLOR_BGR2GRAY)
        # Converting image back to RGB for saving
        image = Image.fromarray(gray_img_arr).convert('RGB')

        # Generating unique image name for dynamic image display
        letters = string.ascii_lowercase
        name = ''.join(random.choice(letters) for i in range(10)) + '.png'
        full_filename = os.path.join(UPLOAD_DIRECTORY, name)

        # Extracting text from image
        custom_config = r'-l eng --oem 3 --psm 6'
        text = pytesseract.image_to_string(gray_img_arr, config=custom_config)

        # Remove symbols if any
        characters_to_remove = "!()@—*“>+-/,'|£#%$&^_~"
        new_string = text
        for character in characters_to_remove:
            new_string = new_string.replace(character, "")

        new_string = new_string.split("\n")

        image.save(full_filename)

        return templates.TemplateResponse("result.html", {"request": request, "full_filename": f"/uploads/{name}", "text": new_string})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
