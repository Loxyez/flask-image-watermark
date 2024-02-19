from flask import Flask, request, send_file, render_template
from PIL import Image, ImageDraw, ImageFont
import os
import zipfile

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
WATERMARK_FILE = 'static/img/watermark_pst.png'

# Define route for the root URL ("/"), which serves as the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Define route for uploading files
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return 'No file part'
    
    files = request.files.getlist('files[]')
    if not files:
        return 'No file selected'
    
    # Create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # List to store file paths of processed images
    processed_files = []
    
    # Process each uploaded file
    for file in files:
        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Add watermark
            watermark_image(filepath)
            
            processed_files.append(filepath)
    
    # Create a zip file containing all processed images
    zip_filepath = 'processed_images.zip'
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for file in processed_files:
            zipf.write(file, os.path.basename(file))
    
    # Send the zip file to the client
    return send_file(zip_filepath, as_attachment=True)

# Function to add watermark to images
def watermark_image(filepath):
    image = Image.open(filepath)
    watermark = Image.open(WATERMARK_FILE)
    
    # Resize watermark to match the dimensions of the input image
    image = image.resize(image.size, Image.LANCZOS)
    
    # Position the watermark at the bottom right corner of the image
    x_offset = image.width - watermark.width
    y_offset = image.height - watermark.height
    
    image.paste(watermark, (x_offset, y_offset), watermark)
    
    # Save the image with watermark
    image.save(filepath)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
