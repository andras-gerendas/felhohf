from flask import Flask, g, Blueprint
import json
import logging
import sqlite3

DATABASE = '/app/notifications.db'

app = Flask(__name__)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

bp = Blueprint("notification", __name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row

        with app.open_resource("/app/schema.sql", "r") as f:
            db.executescript(f.read())
    return db

@bp.route("/subscription/<int:user_id>")
def subscription(user_id):
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM subscriptions where id = ?", (int(user_id),))

        rows = cur.fetchall()

        if len(rows) == 0:
            resp = {"status": f'content with this id does not exist'}
            return app.response_class(response=json.dumps(resp), status=401, mimetype='application/json')
        
        resp = {"status": f'ok'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=200, mimetype='application/json')

    except Exception as e:
        resp = {"status": f'database error has occurred: {str(e)}'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=402, mimetype='application/json')

@bp.route("/subscribe")
def subscribe():
    inserted_id = -1
    
    try:
        db = get_db()

        with db:
            result = db.execute("INSERT INTO subscriptions VALUES (NULL)")

            inserted_id = result.lastrowid
    except Exception as e:
        resp = {"status": f'database error has occurred: {str(e)}'}
        app.logger.info(resp)
        return app.response_class(response=json.dumps(resp), status=402, mimetype='application/json')

    resp = {"status": "ok", "id": inserted_id}
    app.logger.info(resp)
    return app.response_class(response=json.dumps(resp), status=200, mimetype='application/json')