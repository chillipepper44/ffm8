# 🛫 Cargo Manifest to FFM/8 Web App

แอปพลิเคชันบนเว็บที่แปลงไฟล์ **Cargo Manifest (PDF)** ให้อยู่ในรูปแบบข้อความ **FFM/8** พร้อมแยกข้อมูล ULD และ BULK โดยอัตโนมัติ

> สร้างโดยเพื่อช่วยงานด้านโลจิสติกส์เท่านั้น โดยไม่มีวัตถุประสงค์ทางพาณิชย์

## 🔧 ฟีเจอร์
- อัปโหลด PDF ของ Cargo Manifest
- แยกข้อมูลออกเป็นรูปแบบมาตรฐาน FFM/8
- จัดกลุ่ม BULK ขึ้นก่อน และ ULD แยกตามหมายเลข
- สามารถ Copy หรือ Download ผลลัพธ์ได้ทันที

---

## 🚀 วิธีใช้งาน
### 1. คลิก “Choose File” แล้วอัปโหลดไฟล์ Cargo Manifest (`.pdf`)
### 2. กดปุ่ม “Convert”
### 3. ผลลัพธ์จะแสดงในรูปแบบข้อความ
- สามารถ Copy หรือ Download เป็น `.txt` ได้เลย

---

## 🌐 วิธี Deploy ขึ้น Render.com
### ✅ ต้องมี
- บัญชี [GitHub](https://github.com)
- บัญชี [Render](https://render.com)

### 📦 ขั้นตอน
1. สร้าง GitHub Repository ใหม่ แล้วอัปโหลดไฟล์ทั้งหมดของโปรเจกต์นี้
2. เข้าเว็บไซต์ [https://render.com](https://render.com)
3. กด `New` → `Web Service`
4. Connect กับ GitHub และเลือก repo ที่อัปโหลดไว้
5. ตั้งค่า:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
6. รอ Render deploy อัตโนมัติ และจะได้ลิงก์ใช้งานทันที

---

## 📁 โครงสร้างโปรเจกต์
```
├── app.py
├── ffm_parser.py
├── requirements.txt
├── README.md
├── static/
│   └── styles.css
├── templates/
│   └── index.html
```

---

## 📄 License
Licensed under the MIT License.  
Copyright (c) 2025 Chilli Pepper
