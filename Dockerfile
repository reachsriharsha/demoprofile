# Use an official Python runtime as a parent image
FROM python:3.12-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by the application's Python packages
# - tesseract-ocr: for pytesseract (OCR)
# - poppler-utils: for pdf2image (PDF to image conversion)
# - ffmpeg: for pydub (audio processing)
# - ghostscript: for camelot-py (PDF table extraction)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    ffmpeg \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install Python packages, using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY demo_app.py .

# Copy the SSL certificates.
# IMPORTANT: For production, consider using a reverse proxy (like Nginx) for SSL
# termination or mounting certificates as secrets, rather than building them in.
COPY certificates/ ./certificates/

# Make port 7860 available to the world outside this container for the Gradio app
EXPOSE 7860

# Run demo_app.py when the container launches
CMD ["python", "demo_app.py"]