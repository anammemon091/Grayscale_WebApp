from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import os
from datetime import datetime

app = Flask(__name__)

# === Folder Setup ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "static", "processed")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# === Home Route ===
@app.route('/')
def index():
    return render_template('index.html')


# === Image Processing Route ===
@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        data = request.get_json()
        image_data = data.get('image', '').split(',')[1]  # remove data:image/jpeg;base64,
        img_bytes = base64.b64decode(image_data)

        # Save original image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_filename = f"captured_{timestamp}.jpg"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)

        with open(input_path, "wb") as f:
            f.write(img_bytes)

        # Convert bytes to OpenCV image
        npimg = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Invalid image data"}), 400

        # === Apply Filters ===
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
        negative = cv2.bitwise_not(img)
        sepia = cv2.transform(img, np.matrix([[0.272, 0.534, 0.131],
                                              [0.349, 0.686, 0.168],
                                              [0.393, 0.769, 0.189]]))
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)
        cartoon = cv2.stylization(img, sigma_s=150, sigma_r=0.25)

        # === Save Processed Images ===
        paths = {
            "original": os.path.join(UPLOAD_FOLDER, input_filename),
            "grayscale": os.path.join(PROCESSED_FOLDER, f"gray_{timestamp}.jpg"),
            "binary": os.path.join(PROCESSED_FOLDER, f"binary_{timestamp}.jpg"),
            "negative": os.path.join(PROCESSED_FOLDER, f"neg_{timestamp}.jpg"),
            "sepia": os.path.join(PROCESSED_FOLDER, f"sepia_{timestamp}.jpg"),
            "cartoon": os.path.join(PROCESSED_FOLDER, f"cartoon_{timestamp}.jpg")
        }

        cv2.imwrite(paths["grayscale"], gray)
        cv2.imwrite(paths["binary"], binary)
        cv2.imwrite(paths["negative"], negative)
        cv2.imwrite(paths["sepia"], sepia)
        cv2.imwrite(paths["cartoon"], cartoon)

        # === Return URLs ===
        for key in paths:
            paths[key] = "/" + os.path.relpath(paths[key], BASE_DIR).replace("\\", "/")

        return jsonify(paths)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
