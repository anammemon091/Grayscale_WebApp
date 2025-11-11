from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
PROCESSED_FOLDER = "static/processed"

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        data = request.get_json()
        image_data = data['image'].split(',')[1]  # remove "data:image/jpeg;base64,"
        img_bytes = base64.b64decode(image_data)

        # Save uploaded image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_path = os.path.join(UPLOAD_FOLDER, f"captured_{timestamp}.jpg")
        with open(input_path, "wb") as f:
            f.write(img_bytes)

        # Read image with OpenCV
        npimg = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        # Create filters
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
        negative = cv2.bitwise_not(img)
        sepia = cv2.transform(img, np.matrix([[0.272, 0.534, 0.131],
                                              [0.349, 0.686, 0.168],
                                              [0.393, 0.769, 0.189]]))
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)
        cartoon = cv2.stylization(img, sigma_s=150, sigma_r=0.25)

        # Save processed images
        gray_path = os.path.join(PROCESSED_FOLDER, f"gray_{timestamp}.jpg")
        binary_path = os.path.join(PROCESSED_FOLDER, f"binary_{timestamp}.jpg")
        neg_path = os.path.join(PROCESSED_FOLDER, f"neg_{timestamp}.jpg")
        sepia_path = os.path.join(PROCESSED_FOLDER, f"sepia_{timestamp}.jpg")
        cartoon_path = os.path.join(PROCESSED_FOLDER, f"cartoon_{timestamp}.jpg")

        cv2.imwrite(gray_path, gray)
        cv2.imwrite(binary_path, binary)
        cv2.imwrite(neg_path, negative)
        cv2.imwrite(sepia_path, sepia)
        cv2.imwrite(cartoon_path, cartoon)

        # Return file URLs to display
        return jsonify({
            "original": "/" + input_path,
            "grayscale": "/" + gray_path,
            "binary": "/" + binary_path,
            "negative": "/" + neg_path,
            "sepia": "/" + sepia_path,
            "cartoon": "/" + cartoon_path
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
