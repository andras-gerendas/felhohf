import base64
from io import BytesIO
from flask import Flask, copy_current_request_context, request
import json
import pytesseract
from PIL import Image, ImageDraw
import io
import requests

app = Flask(__name__)

def process_image(image_buffer, id):
    image = Image.open(io.BytesIO(image_buffer))
    boxes = pytesseract.image_to_boxes(image)
    text = pytesseract.image_to_string(image)
    h = image.height

    draw = ImageDraw.Draw(image)

    for box in boxes.splitlines():
        b = box.split()
        char, x1, y1, x2, y2 = b[0], int(b[1]), int(b[2]), int(b[3]), int(b[4])
        draw.rectangle(((x1, h - y2), (x2, h - y1)), outline="black")
    
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    json_obj = {"image": img_str.decode('utf-8'), "caption": text, "id": id}

    r = requests.post('http://db_handler:5000/upload', json=json_obj)

    return json.dumps(json_obj)

@app.route("/", methods=['POST'])
def add_to_queue():
    content = request.json

    if 'image' not in content or 'id' not in content:
        resp = {"status": f'missing image or id parameter'}
        return app.response_class(response=json.dumps(resp), status=402, mimetype='application/json')

    resp = {"status": "ok"}
    response = app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    @response.call_on_close
    @copy_current_request_context
    def post_processing():
        content = request.json

        image = base64.b64decode(content['image'])

        process_image(image, content['id'])
    return response