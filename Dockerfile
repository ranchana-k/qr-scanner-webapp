# ใช้ Python 3.9 เป็น Base Image
FROM python:3.9-slim-buster

# ตั้งค่า Working Directory
WORKDIR /app

# คัดลอกและติดตั้ง Dependencies
COPY requirements.txt .
# [เพิ่ม] ติดตั้ง zbar-tools ซึ่งเป็น dependency ของ pyzbar บน Debian (buster)
RUN apt-get update && apt-get install -y libzbar0 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกไฟล์แอปพลิเคชันทั้งหมด
COPY . .

# Cloud Run จะส่ง Traffic ไปที่ Port 8080
ENV PORT 8080

# รันแอปพลิเคชันด้วย functions-framework
# --target=scan หมายถึงให้รันฟังก์ชันชื่อ 'scan' ที่อยู่ในไฟล์
CMD ["functions-framework", "--target=scan", "--host=0.0.0.0", "--port=$(PORT)"]
