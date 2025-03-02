import os
import cv2
import base64
import eventlet
from datetime import datetime
from flask import Flask, Response, jsonify, request
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from ultralytics import YOLO

# Initialize
eventlet.monkey_patch()
load_dotenv()
app = Flask(__name__)

# MongoDB Setup
app.config["MONGO_URI"] = os.getenv("MONGODB_URI")
mongo = PyMongo(app)
alerts = mongo.db.alerts

# Load AI Model
model = YOLO('yolov8n.pt')

def generate_frames(url):
    cap = cv2.VideoCapture(url)
    while cap.isOpened():
        success, frame = cap.read()
        if not success: break
        
        results = model(frame, verbose=False)
        for result in results:
            for box in result.boxes:
                if model.names[int(box.cls)] == 'gun' and box.conf > 0.8:
                    alerts.insert_one({
                        "timestamp": datetime.now(),
                        "confidence": float(box.conf),
                        "image": base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
                    })
        
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    url = request.args.get('url')
    return Response(generate_frames(url), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alerts')
def get_alerts():
    return jsonify(list(alerts.find({}, {'_id': 0}).sort("timestamp", -1).limit(10)))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)