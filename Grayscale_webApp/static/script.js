// === Webcam Setup ===
const video = document.getElementById("webcam");
const captureBtn = document.querySelector("#capture-btn");
const uploadBtn = document.querySelector("#upload-btn");
const uploadInput = document.querySelector("#upload-input");
const clearBtn = document.querySelector("#clear-btn");

video.width = 320;
video.height = 240;

// === Request webcam access ===
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(err => {
    alert("⚠️ Error accessing camera: " + err.message + "\nPlease allow camera access in browser settings.");
  });


// === Function to send image to Flask backend ===
function sendImageToServer(imageData) {
  fetch("/process_image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageData }),
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert("⚠️ Server error: " + data.error);
        return;
      }

      // Update preview images
      document.querySelector("#original").src = data.original;
      document.querySelector("#grayscale").src = data.grayscale;
      document.querySelector("#binary").src = data.binary;
      document.querySelector("#negative").src = data.negative;
      document.querySelector("#sepia").src = data.sepia;
      document.querySelector("#cartoon").src = data.cartoon;
    })
    .catch(err => {
      console.error("Error sending image:", err);
      alert("❌ Something went wrong while sending the image to the server.");
    });
}


// === Capture Image from Webcam ===
captureBtn.addEventListener("click", () => {
  if (video.readyState < 2) {
    alert("📷 Camera not ready yet! Please wait a few seconds.");
    return;
  }

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth || 320;
  canvas.height = video.videoHeight || 240;
  const ctx = canvas.getContext("2d");

  // Fix mirror effect
  ctx.translate(canvas.width, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  ctx.setTransform(1, 0, 0, 1, 0, 0);

  const imageData = canvas.toDataURL("image/jpeg");

  if (!imageData || imageData.length < 1000) {
    alert("⚠️ Failed to capture image. Please try again.");
    return;
  }

  sendImageToServer(imageData);
});


// === Upload Image from File ===
uploadBtn.addEventListener("click", () => {
  uploadInput.click(); // trigger file selector
});

uploadInput.addEventListener("change", () => {
  const file = uploadInput.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    const imageData = e.target.result;
    sendImageToServer(imageData);
  };
  reader.readAsDataURL(file);
});


// === Clear All Images ===
clearBtn.addEventListener("click", () => {
  const imgs = document.querySelectorAll(".img-card img");
  imgs.forEach(img => (img.src = ""));
  uploadInput.value = "";
  alert("🧹 All images cleared!");
});
