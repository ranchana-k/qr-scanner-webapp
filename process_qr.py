import cv2
from pyzbar.pyzbar import decode
import sys

def find_and_decode_qr(image_path: str):
    """
    อ่านและถอดรหัส QR Code จากไฟล์รูปภาพ
    รองรับหลาย QR ต่อรูป
    """
    print(f"กำลังอ่านไฟล์รูปภาพจาก: {image_path}")
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"ไม่สามารถอ่านไฟล์รูปภาพได้จาก path '{image_path}'")
        return []

    # ลดขนาดรูปถ้ารูปใหญ่เกินไป (เพื่อเร่งความเร็ว)
    max_dim = 800
    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        image = cv2.resize(image, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
        print(f"ย่อรูปภาพเหลือ {image.shape[1]}x{image.shape[0]} เพื่อความเร็ว")

    # ถอดรหัส QR Code
    decoded_objects = decode(image)
    if not decoded_objects:
        print("ไม่พบ QR Code ในรูปภาพนี้")
        return []

    decoded_data_list = []
    for obj in decoded_objects:
        data = obj.data.decode("utf-8")
        decoded_data_list.append(data)
        print(f"พบ QR Code: {data}")
    
    return decoded_data_list

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("กรุณาระบุ Path ของไฟล์รูปภาพ")
        sys.exit(1)

    image_file_path = sys.argv[1]
    decoded_data = find_and_decode_qr(image_file_path)
    
    if decoded_data:
        print("-" * 30)
        print("ข้อมูลทั้งหมดที่ถอดรหัสได้:")
        for d in decoded_data:
            print(d)
        print("-" * 30)
