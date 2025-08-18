import functions_framework
import cv2
from pyzbar.pyzbar import decode
from flask import jsonify # ยังคงใช้ jsonify จาก Flask ที่แถมมากับ Framework ได้
import os
import tempfile

# ไม่ต้อง import process_qr.py แล้ว เพราะเราจะย้ายโค้ดมาไว้ที่นี่เลย

def find_and_decode_qr(image_path: str):
    """
    อ่านและถอดรหัส QR Code จากไฟล์รูปภาพ
    (โค้ดนี้มาจาก process_qr.py ของคุณ)
    """
    print(f"กำลังอ่านไฟล์รูปภาพจาก: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print(f"ไม่สามารถอ่านไฟล์รูปภาพได้จาก path '{image_path}'")
        return []

    # # ลดขนาดรูปถ้ารูปใหญ่เกินไป (เพื่อเร่งความเร็ว)
    # max_dim = 800
    # h, w = image.shape[:2]
    # if max(h, w) > max_dim:
    #     scale = max_dim / max(h, w)
    #     image = cv2.resize(image, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    #     print(f"ย่อรูปภาพเหลือ {image.shape[1]}x{image.shape[0]} เพื่อความเร็ว")
    
    decoded_objects = decode(image)

    if not decoded_objects:
        print("ไม่พบ QR Code ในรูปภาพนี้")
        return []

    decoded_data_list = [obj.data.decode("utf-8") for obj in decoded_objects]
    print(f"พบ QR Codes: {decoded_data_list}")
    return decoded_data_list


@functions_framework.http
def scan(request):
    """
    HTTP Cloud Function ที่จะถูกเรียกโดย Cloud Run/Functions
    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`.
    """
    # --- จัดการ CORS Headers เพื่อให้ Frontend เรียกใช้ได้ ---
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    # ----------------------------------------------------

    if request.method != 'POST':
        return (jsonify({'error': 'Method not allowed'}), 405, headers)

    if 'image' not in request.files:
        return (jsonify({'error': 'No image file provided'}), 400, headers)
    
    file = request.files['image']

    if file.filename == '':
        return (jsonify({'error': 'No image selected'}), 400, headers)

    # ใช้ Temporary Directory ที่ปลอดภัยและจัดการตัวเองอัตโนมัติ
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, file.filename)
        file.save(filepath)
        
        try:
            decoded_results = find_and_decode_qr(filepath)
            
            if decoded_results:
                return (jsonify({'results': decoded_results}), 200, headers)
            else:
                return (jsonify({'results': [], 'message': 'No QR code found in the image.'}), 200, headers)
        except Exception as e:
            return (jsonify({'error': f'An error occurred: {str(e)}'}), 500, headers)

