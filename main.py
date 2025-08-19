# --------------------------------------------------------------------------
# 1. Import Libraries
# --------------------------------------------------------------------------
import functions_framework
import cv2
from pyzbar.pyzbar import decode
from flask import jsonify
import os
import tempfile
import uuid  # For creating safe, unique filenames
import logging # For better logging in a production environment

# --------------------------------------------------------------------------
# 2. Configure Logging
# --------------------------------------------------------------------------
# Set up basic logging to show INFO level messages and above.
# In Cloud Run, these logs will automatically appear in Google Cloud Logging.
logging.basicConfig(level=logging.INFO)

# --------------------------------------------------------------------------
# 3. Core QR Code Processing Function
# --------------------------------------------------------------------------
def find_and_decode_qr(image_path: str):
    """
    Reads an image file, resizes it for safety, and decodes any QR codes found.
    Args:
        image_path: The full path to the temporary image file.
    Returns:
        A list of decoded strings from the QR codes.
    """
    logging.info(f"Starting to process image from: {image_path}")

    # Read the image from the specified path
    image = cv2.imread(image_path)
    if image is None:
        logging.error(f"Could not read the image file from path: '{image_path}'")
        return []

    # [Safety Net] Resize the image on the backend if it's too large.
    # This protects against direct API calls that bypass frontend compression.
    max_dim = 1200  # A reasonable max dimension for backend processing
    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        logging.info(f"Backend resized image to {image.shape[1]}x{image.shape[0]} for safety.")

    # Decode the QR codes from the (potentially resized) image
    decoded_objects = decode(image)

    if not decoded_objects:
        logging.info("No QR codes were found in the provided image.")
        return []

    # Extract and decode the data from each found object
    decoded_data_list = [obj.data.decode("utf-8") for obj in decoded_objects]
    logging.info(f"Successfully found {len(decoded_data_list)} QR Code(s).")
    return decoded_data_list

# --------------------------------------------------------------------------
# 4. Main HTTP Cloud Function (The API Endpoint)
# --------------------------------------------------------------------------
@functions_framework.http
def scan(request):
    """
    The main HTTP Cloud Function that handles file uploads and orchestrates
    the QR code scanning process.
    """
    # --- CORS Preflight Handling ---
    # This block is essential for allowing browsers from other domains
    # (like your Firebase Hosting URL) to make requests to this API.
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # --- Standard CORS Header for all other responses ---
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    # --- Input Validation ---
    if request.method != 'POST':
        return (jsonify({'error': 'Method not allowed. Please use POST.'}), 405, headers)

    if 'image' not in request.files:
        return (jsonify({'error': 'No image file provided in the request.'}), 400, headers)

    file = request.files['image']

    if file.filename == '':
        return (jsonify({'error': 'No file was selected for upload.'}), 400, headers)

    # --- Secure File Handling ---
    # Create a safe, unique filename to prevent security issues.
    _, extension = os.path.splitext(file.filename)
    safe_filename = f"{uuid.uuid4()}{extension}"

    # Use a temporary directory that cleans itself up automatically
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, safe_filename)
        
        logging.info(f"Saving uploaded file temporarily to: {filepath}")
        file.save(filepath)

        # --- Execute Core Logic and Handle Responses ---
        try:
            decoded_results = find_and_decode_qr(filepath)

            if decoded_results:
                # Success case: QR code(s) found
                return (jsonify({'results': decoded_results}), 200, headers)
            else:
                # Success case: No QR code found
                return (jsonify({'results': [], 'message': 'No QR code found in the image.'}), 200, headers)

        except Exception as e:
            # Error case: Something went wrong during processing
            logging.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
            # Return a generic error message to the user for security
            return (jsonify({'error': 'An internal server error occurred while processing the image.'}), 500, headers)

