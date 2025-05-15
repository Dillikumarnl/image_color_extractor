from flask import Flask, render_template, request
import os
from PIL import Image
import numpy as np
from collections import Counter

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

default_num_colors = 10
default_delta = 16

def get_first_file(directory):
    files = sorted(os.listdir(directory))  # Sort to ensure order
    return files[0] if files else None  # Return first file if available


def adjust_brightness(rgb, factor=0.8):
    return tuple(min(255, int(c * factor)) for c in rgb)

def quantize_color(rgb, delta=24):
    adjust_brightness(rgb)
    return tuple(int(round(c / delta) * delta) for c in rgb)


def get_dominant_colors(image_path, num_colors, delta, reduce_gradients,
                        brightness_factor, resize=(150, 150),):
    """Extracts dominant colors from an image using quantization and brightness adjustments."""
    image = Image.open(image_path).resize(resize).convert("RGB")
    pixels = np.array(image).reshape(-1, 3)

    # Apply brightness adjustment if needed
    if brightness_factor != 1.0:
        pixels = [adjust_brightness(pixel, brightness_factor) for pixel in pixels]

    # Apply quantization
    quantized_pixels = [quantize_color(pixel, delta) for pixel in pixels]

    # Apply gradient reduction
    if reduce_gradients:
        quantized_pixels = [(c[0] // 2 * 2, c[1] // 2 * 2, c[2] // 2 * 2) for c in quantized_pixels]

    # Count dominant colors
    colors = Counter(quantized_pixels)
    return colors.most_common(num_colors)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["imgFile"]
        num_colors = int(request.form.get("num_colors"))
        delta = int(request.form.get("delta"))
        brightness_factor = float(request.form.get("brightness_factor", 1.0))
        reduce_gradients = bool(request.form.get("reduce_gradients"))
        if file:
            filename = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filename)
            colors = get_dominant_colors(filename, num_colors, delta, brightness_factor, reduce_gradients)
            return render_template("index.html", colors=colors, image_path=filename, colors_num=len(colors), num_colors=num_colors, delta=delta)
    return render_template("index.html", colors=None, num_colors=default_num_colors, delta=default_delta)


if __name__ == "__main__":
    app.run(debug=True)
