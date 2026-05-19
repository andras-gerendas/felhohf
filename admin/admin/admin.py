import base64
from flask import Blueprint, Flask, render_template, url_for, request, flash, redirect, session
import json
import requests

app = Flask(__name__)

bp = Blueprint("image", __name__)

@bp.route("/")
def index():
    images = []
    is_subscribed = False
    subscription_id = None

    if 'subscription_id' in session.keys():
        r = requests.get(f"http://notifier:5000/subscription/{session['subscription_id']}")

        if r.status_code == 200:
            is_subscribed = True
            subscription_id = session["subscription_id"]

            r = requests.get(f"http://db_handler:5000/captions")

            if r.status_code != 200:
                flash(f"Error occurred in database: {r.status_code}", "error")

                return render_template("image/list.html")

            images_raw = json.loads(r.content)

            for image_raw in images_raw:
                images.append({'caption_user': image_raw['caption_user'], 'caption_gen': image_raw['caption_gen']})

        elif r.status_code == 401:
            # Removing entry as session does not exist in the database
            session.pop('subscription_id', default=None)

    return render_template(
        "image/list.html",
        images=images,
        is_subscribed=is_subscribed,
        subscription_id=subscription_id
    )

@bp.route("/subscribe")
def subscribe():
    redirect_url = url_for('index')

    r = requests.get('http://notifier:5000/subscribe')

    if r.status_code != 200:
        flash(f"Error occurred in database: {r.status_code}", "error")
    
        return redirect(redirect_url)
    
    subscription = json.loads(r.content)

    session["subscription_id"] = subscription["id"]

    return redirect(redirect_url)