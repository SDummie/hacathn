import os
import cv2
import base64
import eventlet
import logging
from datetime import datetime
from flask import Flask, Response, jsonify, request, abort
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from ultralytics import YOLO

eventlet.monkey_patch()
load_dotenv()
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

app.config["MONGO_URI"] = os.getenv("MONGODB_URI")
mongo = PyMongo(app)
alerts = mongo.db.alerts

MODEL_PATH = os.getenv("MODEL_PATH", 'yolov8n.pt')
model = YOLO(MODEL_PATH)

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.8))

def generate_frames(url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        logger.error(f"Failed to open video stream: {url}")
        abort(500, description="Failed to open video stream")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            logger.warning("Failed to read frame from video stream")
            break

        try:
            results = model(frame, verbose=False)
            for result in results:
                for box in result.boxes:
                    if model.names[int(box.cls)] == 'gun' and box.conf > CONFIDENCE_THRESHOLD:
                        alerts.insert_one({
                            "timestamp": datetime.now(),
                            "confidence": float(box.conf),
                            "image": base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
                        })
                        logger.info(f"Alert triggered with confidence: {box.conf}")

            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            break

    cap.release()

@app.route('/video_feed')
@limiter.limit("10 per minute")
def video_feed():
    url = request.args.get('url')
    if not url:
        abort(400, description="URL parameter is required")
    return Response(generate_frames(url), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alerts')
@limiter.limit("30 per minute")
def get_alerts():
    try:
        alerts_list = list(alerts.find({}, {'_id': 0}).sort("timestamp", -1).limit(10))
        return jsonify(alerts_list)
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        abort(500, description="Internal server error")

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
