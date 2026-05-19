from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
import json
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from . import notifier
from threading import Thread
import time

socketio = SocketIO()

connected_users = {}

def initialize_socketio(app, socketio: SocketIO):
    with app.app_context():
        @socketio.on("register")
        def register(subscription_id):
            try:
                cur = notifier.get_db().cursor()
                cur.execute("SELECT * FROM subscriptions where id = ?", (int(subscription_id),))

                rows = cur.fetchall()

                if len(rows) == 0:
                    resp = {"status": f'content with this id does not exist'}
                    app.logger.info(resp)
                    return json.dumps(resp)
            except Exception as e:
                resp = {"status": f'database error has occurred: {str(e)}'}
                app.logger.info(resp)
                return json.dumps(resp)

            connected_users[request.sid] = subscription_id

            app.logger.info(f"User {subscription_id} connected")
            return json.dumps({'status': 'ok'})
        
        @socketio.on('disconnect')
        def disconnect(reason):
            if request.sid in connected_users.keys():
                app.logger.info(f'User {connected_users[request.sid]} disconnected: {reason}')
                del connected_users[request.sid]

def create_consumer(app, topic):
    while True:
        try:
            consumer = KafkaConsumer(topic,
                                     group_id='notification-group',
                                     bootstrap_servers="kafka:9092",
                                     value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                                     enable_auto_commit=False)

            app.logger.info('notifier connected to kafka')
            
            return consumer
        except NoBrokersAvailable:
            time.sleep(5)

def process_message(app, event):
    with app.app_context():
        app.logger.info(connected_users)
        
        for user in connected_users:
            socketio.emit(
                "notification",
                json.dumps({'caption_user': event['caption_user'], 'caption_gen': event['caption_gen']}),
                room=user
            )
        
        app.logger.info('notification stored for users')

def consume_kafka(app):
    while True:
        try:
            consumer = create_consumer(app, 'ocr-completed')

            for message in consumer:
                event = message.value

                try:
                    process_message(app, event)
                    consumer.commit()
                except Exception as e:
                    resp = {"status": f'database error has occurred: {str(e)}'}
                    app.logger.info(resp)
        except Exception as e:
            time.sleep(5)

def create_app():
    app = Flask(__name__)

    with app.app_context():
        cors = CORS(app, resources={r"/*":{"origins":"*"}})
        socketio.init_app(app, cors_allowed_origins="*")
        initialize_socketio(app, socketio)

    app.register_blueprint(notifier.bp)

    thread = Thread(target=consume_kafka, args=(app,))
    thread.daemon = True
    thread.start()

    return app