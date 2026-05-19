import base64
from flask import Blueprint, Flask, render_template, url_for, request, flash, redirect
import json
from kafka import KafkaProducer
import requests
import os

app = Flask(__name__)

bp = Blueprint("image", __name__)

ALLOWED_EXTENSIONS = {'png'}

def allowed_file(filename: str) -> bool:
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/")
def index():
    r = requests.get('http://db_handler:5000')

    if r.status_code != 200:
        flash(f"Error occurred in database: {r.status_code}", "error")

        return render_template("image/gallery.html")

    images = []

    images_raw = json.loads(r.content)

    for image_raw in images_raw:
        if 'image_proc' in image_raw:
            cache_path = f'/app/frontend/static/images/{image_raw["id"]}.png'

            # TODO: Ezt nem mindig kéne elküldeni
            if not os.path.exists(cache_path):
                image = base64.b64decode(image_raw['image_proc'])

                with open(cache_path, 'wb') as image_file:
                    image_file.write(image)

        if image_raw['processed'] == 1:
            images.append({'src': f'{image_raw["id"]}.png',
                           'caption': image_raw['caption_user']})
        else:
            images.append({'src': f'empty',
                           'caption': image_raw['caption_user'],
                           'id': image_raw['id']})

    return render_template(
        "image/gallery.html",
        images=images
    )

@bp.route("/upload", methods=['GET'])
def upload():
    return render_template(
        "image/upload.html", 
    )

@bp.route("/upload-image", methods=['POST'])
def handle_upload():
    redirect_url = url_for('image.upload')

    if 'image-file' not in request.files:
        flash("File part missing from the request.", "error")
        return redirect(redirect_url)
    
    file = request.files['image-file']

    if not file or file.filename == '':
        flash("No file selected. Please choose a file to upload.", "error")
        return redirect(redirect_url)

    if not allowed_file(file.filename):
        flash("File type not allowed. Only .png files are accepted.", "error")
        return redirect(redirect_url)
    
    image_string = base64.b64encode(file.read())
    caption = request.form.get("caption", "").strip()
    json_obj = {"image": image_string.decode('utf-8'), "caption": caption}

    r = requests.post('http://db_handler:5000/upload', json=json_obj)
    
    if r.status_code != 200:
        flash(f"Error occurred in database: {r.status_code}", "error")
        return redirect(redirect_url)

    content = json.loads(r.content)

    producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    resp = {"id": content['id']}
    producer.send('image-uploaded', resp)
    
    flash(f"File uploaded successfully!", "success")
    
    return redirect(redirect_url)

@bp.route('/refresh/<int:image_id>')
def refresh(image_id):
    redirect_url = url_for('index')

    producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    resp = {"id": image_id}
    producer.send('image-uploaded', resp)

    return redirect(redirect_url)