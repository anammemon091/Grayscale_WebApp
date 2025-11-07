import cv2
import numpy as np

# ---------- FILTER FUNCTIONS ----------
def convert_grayscale(img):
    """Convert image to grayscale"""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def convert_binary(img, threshold=127):
    """Convert image to binary (black & white)"""
    gray = convert_grayscale(img)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary

def convert_negative(img):
    """Convert image to negative"""
    return 255 - img

def convert_sepia(img):
    """Apply sepia filter"""
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    sepia = cv2.transform(img, sepia_filter)
    sepia = np.clip(sepia, 0, 255)
    return sepia.astype(np.uint8)

def convert_cartoon(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

# ---------- Helper: Add title text ----------
def add_title(img, title):
    """Add label text to the image"""
    return cv2.putText(img.copy(), title, (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                       (255, 255, 255), 2, cv2.LINE_AA)

# ---------- IMAGE MODE ----------
def process_image(img_path):
    img = cv2.imread(img_path)
    if img is None:
        print("Image not found!")
        return

    # Apply filters
    gray = convert_grayscale(img)
    binary = convert_binary(img)
    negative = convert_negative(img)
    sepia = convert_sepia(img)
    cartoon = convert_cartoon(img)

    # Convert grayscale/binary to 3 channels for stacking
    gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    binary_3ch = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    # Resize all to same size
    img = cv2.resize(img, (320, 240))
    gray_3ch = cv2.resize(gray_3ch, (320, 240))
    binary_3ch = cv2.resize(binary_3ch, (320, 240))
    negative = cv2.resize(negative, (320, 240))
    sepia = cv2.resize(sepia, (320, 240))
    cartoon = cv2.resize(cartoon, (320, 240))

    # Add titles to each image
    def add_label(image, text):
        labeled = image.copy()
        cv2.rectangle(labeled, (0, 0), (320, 30), (0, 0, 0), -1)  # black bar
        cv2.putText(labeled, text, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return labeled

    img = add_label(img, "Original")
    gray_3ch = add_label(gray_3ch, "Grayscale")
    binary_3ch = add_label(binary_3ch, "Binary")
    negative = add_label(negative, "Negative")
    sepia = add_label(sepia, "Sepia")
    cartoon = add_label(cartoon, "Cartoon")

    # Combine in grid layout (2 rows × 3 columns)
    top_row = np.hstack((img, gray_3ch, binary_3ch))
    bottom_row = np.hstack((negative, sepia, cartoon))
    combined = np.vstack((top_row, bottom_row))

    # Optional: enlarge display
    display = cv2.resize(combined, (960, 720))

    cv2.imshow("Image Filters (Press any key to close)", display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ---------- WEBCAM MODE ----------
def process_webcam():
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    if not cap.isOpened():
        print("Cannot open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip horizontally to fix mirror effect
        frame = cv2.flip(frame, 1)

        # Apply filters
        gray = convert_grayscale(frame)
        binary = convert_binary(frame)
        negative = convert_negative(frame)
        sepia = convert_sepia(frame)
        cartoon = convert_cartoon(frame)

        # Convert grayscale/binary to 3 channels for stacking
        gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        binary_3ch = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

        # Resize all to same size
        frame = cv2.resize(frame, (320, 240))
        gray_3ch = cv2.resize(gray_3ch, (320, 240))
        binary_3ch = cv2.resize(binary_3ch, (320, 240))
        negative = cv2.resize(negative, (320, 240))
        sepia = cv2.resize(sepia, (320, 240))
        cartoon = cv2.resize(cartoon, (320, 240))

        # ---------- Add labels ----------
        def add_label(image, text):
            labeled = image.copy()
            cv2.rectangle(labeled, (0, 0), (320, 30), (0, 0, 0), -1)  # black bar
            cv2.putText(labeled, text, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            return labeled

        frame = add_label(frame, "Original")
        gray_3ch = add_label(gray_3ch, "Grayscale")
        binary_3ch = add_label(binary_3ch, "Binary")
        negative = add_label(negative, "Negative")
        sepia = add_label(sepia, "Sepia")
        cartoon = add_label(cartoon, "Cartoon")

        # Combine in grid layout (2 rows × 3 columns)
        top_row = np.hstack((frame, gray_3ch, binary_3ch))
        bottom_row = np.hstack((negative, sepia, cartoon))
        combined = np.vstack((top_row, bottom_row))

        # Optional: enlarge display
        display = cv2.resize(combined, (960, 720))

        # Show combined window
        cv2.imshow("Webcam Filters (Press Q to Quit)", display)

        # Press 'q' to quit
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# ---------- MAIN ----------
if __name__ == "__main__":
    print("Choose Mode:")
    print("1. Image Mode")
    print("2. Webcam Mode")
    choice = input("Enter 1 or 2: ")

    if choice == "1":
        img_path = input("Enter image path (e.g., images/test.jpg): ")
        process_image(img_path)
    elif choice == "2":
        process_webcam()
    else:
        print("Invalid choice!")
