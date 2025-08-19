# ใช้ Python 3.12 บน Debian Bookworm เป็น Base Image
FROM python:3.12-slim-bookworm

# ตั้งค่า Working Directory ภายใน Container
WORKDIR /app

# 1. คัดลอกเฉพาะไฟล์ requirements.txt เข้ามาก่อน
COPY requirements.txt .

# 2. ติดตั้ง System-level dependency (ZBar Engine)
RUN apt-get update && apt-get install -y libzbar0 && rm -rf /var/lib/apt/lists/*

# 3. ติดตั้ง Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 4. เมื่อติดตั้งทุกอย่างเสร็จแล้ว ค่อยคัดลอกซอร์สโค้ดทั้งหมดเข้ามา
COPY . .

# 5. รันแอปพลิเคชัน (เวอร์ชันที่แก้ไขแล้วและแนะนำ)
CMD ["functions-framework", "--target=scan"]
