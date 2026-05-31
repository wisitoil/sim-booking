from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

app = FastAPI(title="สูตรซิ่ง Sim Racing & PS5 Booking System")

# 1. จำลองฐานข้อมูลเครื่องเล่นในร้าน (Sim 4 เครื่อง, PS5 4 เครื่อง)
CONSOLES_DB = {
    "SIM-01": {"zone": "Simulator", "price_per_hr": 400, "status": "Available"},
    "SIM-02": {"zone": "Simulator", "price_per_hr": 400, "status": "Available"},
    "SIM-03": {"zone": "Simulator", "price_per_hr": 400, "status": "Available"},
    "SIM-04": {"zone": "Simulator", "price_per_hr": 400, "status": "Available"},
    "PS5-01": {"zone": "PS5_Standard", "price_per_hr": 150, "status": "Available"},
    "PS5-02": {"zone": "PS5_Standard", "price_per_hr": 150, "status": "Available"},
    "PS5-03": {"zone": "PS5_Standard", "price_per_hr": 150, "status": "Available"},
    "PS5-04": {"zone": "PS5_Standard", "price_per_hr": 150, "status": "Available"},
}

# จำลองฐานข้อมูลการจอง
BOOKINGS_DB = {}

# โครงสร้างข้อมูลที่รับจากลูกค้า
class BookingRequest(BaseModel):
    line_user_id: str
    customer_name: str
    console_id: str
    hours: int

# 2. API สำหรับดูสถานะเครื่องทั้งหมดในร้าน (ฝั่งพนักงาน/ลูกค้าดูออนไลน์)
@app.get("/consoles", summary="ดูสถานะเครื่องทั้งหมดในร้าน")
def get_all_consoles():
    return CONSOLES_DB

# 3. API สำหรับกดจองเครื่องผ่านระบบ
@app.post("/book", summary="ระบบกดจองเครื่องและคำนวณเงิน")
def book_console(request: BookingRequest):
    console_id = request.console_id.upper()
    
    # เช็กว่ามีเครื่องนี้อยู่ในร้านไหม
    if console_id not in CONSOLES_DB:
        raise HTTPException(status_code=404, detail="ไม่พบเครื่องเล่นที่ระบุ")
    
    # เช็กว่าเครื่องว่างอยู่ไหม
    if CONSOLES_DB[console_id]["status"] != "Available":
        raise HTTPException(status_code=400, detail=f"เครื่อง {console_id} ถูกจองแล้วในขณะนี้")
    
    # คำนวณราคาค่าบริการ
    price_per_hr = CONSOLES_DB[console_id]["price_per_hr"]
    total_price = price_per_hr * request.hours
    
    # บันทึกข้อมูลการจอง
    booking_id = f"BK-{int(datetime.now().timestamp())}"
    BOOKINGS_DB[booking_id] = {
        "booking_id": booking_id,
        "line_user_id": request.line_user_id,
        "customer_name": request.customer_name,
        "console_id": console_id,
        "hours": request.hours,
        "total_price": total_price,
        "status": "Confirmed (Paid Deposit)"
    }
    
    # เปลี่ยนสถานะเครื่องเป็น "ถูกจอง"
    CONSOLES_DB[console_id]["status"] = "Booked"
    
    return {
        "message": "จองคิวสำเร็จ!",
        "booking_details": BOOKINGS_DB[booking_id]
    }

# 4. API สำหรับพนักงานเคลียร์เครื่องเมื่อลูกค้าเล่นเสร็จกลับบ้าน
@app.post("/release/{console_id}", summary="พนักงานเคลียร์เครื่องให้กลับมาว่าง")
def release_console(console_id: str):
    console_id = console_id.upper()
    if console_id in CONSOLES_DB:
        CONSOLES_DB[console_id]["status"] = "Available"
        return {"message": f"เครื่อง {console_id} พร้อมให้บริการลูกค้าท่านต่อไปแล้ว"}
    raise HTTPException(status_code=404, detail="ไม่พบเครื่องเล่นที่ระบุ")
