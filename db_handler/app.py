import sqlite3
import logging
from flask import Flask, g, request
from kafka import KafkaProducer
import json

DATABASE = '/app/data/images.db'

app = Flask(__name__)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row

        with app.open_resource("./schema.sql", "r") as f:
            db.executescript(f.read())
    return db

@app.route("/")
def index():
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM images")

        rows = cur.fetchall()

        result = []

        for row in rows:
            if row["processed"] == 0:
                result.append({"id": row['id'], "processed": 0, "caption_user": row["caption_user"]})
            else:
                result.append({"id": row['id'], "processed": 1, "image_proc": row["image_proc"], "caption_user": row["caption_user"], "caption_gen": row["caption_gen"]})
        
        return app.response_class(response=json.dumps(result), status=200, mimetype='application/json')
    except Exception as e:
        resp = {"status": f'database error has occurred: {str(e)}'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=402, mimetype='application/json')

@app.route("/image/<int:image_id>")
def image(image_id):
    id = request.view_args['image_id']

    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM images where id = ?", (int(id),))

        rows = cur.fetchall()

        if len(rows) == 0:
            resp = {"status": f'content with this id does not exist'}
            app.logger.info(resp)
            return app.response_class(response=json.dumps(resp), status=401, mimetype='application/json')
        
        row = rows[0]

        if row["processed"] == 0:
            result = {"id": row['id'], "processed": 0, "caption_user": row["caption_user"]}
        else:
            result = {"id": row['id'], "processed": 1, "image_proc": row["image_proc"], "caption_user": row["caption_user"], "caption_gen": row["caption_gen"]}
        
        return app.response_class(response=json.dumps(result), status=200, mimetype='application/json')
    except Exception as e:
        resp = {"status": f'database error has occurred: {str(e)}'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=402, mimetype='application/json')

@app.route("/image/raw/<int:image_id>")
def raw_image(image_id):
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM images where id = ?", (int(image_id),))

        rows = cur.fetchall()

        if len(rows) == 0:
            resp = {"status": f'content with this id does not exist'}
            app.logger.info(resp)
            return app.response_class(response=json.dumps(resp), status=401, mimetype='application/json')
        
        row = rows[0]

        if row["processed"] == 0:
            result = {"id": row['id'], "processed": 0, "image": row["image_normal"]}
        else:
            result = {"id": row['id'], "processed": 1}
        
        return app.response_class(response=json.dumps(result), status=200, mimetype='application/json')
    except Exception as e:
        resp = {"status": f'database error has occurred: {str(e)}'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=402, mimetype='application/json')

def create_new(content):
    if 'image' not in content or 'caption' not in content:
        resp = {'status': 'image or caption parameters are missing'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=404, mimetype='application/json')

    inserted_id = -1
    
    try:
        db = get_db()

        with db:
            result = db.execute(
                "INSERT INTO images (image_normal, caption_user, processed) VALUES (?, ?, ?)",
                (content['image'], content['caption'], 0)
            )

            inserted_id = result.lastrowid
    except Exception as e:
        resp = {"status": f'database error has occurred: {str(e)}'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=402, mimetype='application/json')

    resp = {"status": "ok", "id": inserted_id}
    app.logger.info(resp)
    return app.response_class(response=json.dumps(resp), status=200, mimetype='application/json')


def update_existing(content):
    if 'image' not in content or 'caption' not in content:
        resp = {'status': 'generated image or caption parameters are missing'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=404, mimetype='application/json')
    
    try:
        db = get_db()

        with db:
            cur = db.cursor()
            cur.execute("SELECT * FROM images WHERE id = ?", (int(content['id']),))

            rows = cur.fetchall()

            if len(rows) == 0:
                cur.close()
                resp = {"status": f'content with this id does not exist'}
                app.logger.info(resp)
                return app.response_class(response=json.dumps(resp), status=401, mimetype='application/json')
            
            cur.close()
            
            db.execute("UPDATE images set image_proc=?,caption_gen=?,processed=1 where id = ?", (content["image"], content["caption"], int(content["id"])))

            producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            resp = {'caption_user': rows[0]['caption_user'], 'caption_gen': content['caption']}
            app.logger.info(resp)
            producer.send('ocr-completed', resp)
    except Exception as e:
        resp = {"status": f'database error has occurred: {str(e)}'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=402, mimetype='application/json')

    resp = {"status": "ok"}
    app.logger.info(resp)
    return app.response_class(response=json.dumps(resp), status=200, mimetype='application/json')

@app.route("/upload", methods=['POST'])
def upload():
    content = request.json

    if 'id' in content:
        return update_existing(content)
    
    return create_new(content)

@app.route("/captions")
def captions():
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM images")

        rows = cur.fetchall()

        result = []

        for row in rows:
            if row["processed"] == 1:
                result.append({"id": row['id'], "caption_user": row["caption_user"], "caption_gen": row["caption_gen"]})
        
        return app.response_class(response=json.dumps(result), status=200, mimetype='application/json')
    except Exception as e:
        resp = {"status": f'database error has occurred: {str(e)}'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=402, mimetype='application/json')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)

    if db is not None:
        db.close()