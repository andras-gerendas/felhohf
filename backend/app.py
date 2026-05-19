import base64
from io import BytesIO
import json
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import pytesseract
from PIL import Image, ImageDraw
import io
import logging
import requests
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger = logging.getLogger('kafka')
logger.setLevel(logging.ERROR)

def create_consumer(topic, group_id):
    while True:
        try:
            consumer = KafkaConsumer(topic,
                                     group_id=group_id,
                                     bootstrap_servers="kafka:9092",
                                     value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                                     enable_auto_commit=False)

            logging.info('backend connected to kafka')
            
            return consumer
        except NoBrokersAvailable:
            time.sleep(5)

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

    return r.status_code

if __name__ == "__main__":
    while True:
        try:
            consumer = create_consumer('image-uploaded', 'backend-group')

            for message in consumer:
                logging.info(f'message received: {message.value}, partition: {message.partition}')
                event = message.value['id']

                r = requests.get(f"http://db_handler:5000/image/raw/{event}")

                if r.status_code == 401:
                    consumer.commit()
                    continue

                if r.status_code == 402:
                    # Database error, no commit
                    continue

                content = json.loads(r.content)

                if content['processed'] == 1:
                    consumer.commit()
                    continue

                image = base64.b64decode(content['image'])

                resp = process_image(image, content['id'])

                if resp == 200:
                    logging.info(f'backend finished processing {content['id']}')
                    consumer.commit()
        except Exception as e:
            logging.info(f'Error during image processing: {e}')
            time.sleep(5)