import re

filepath = 'C:/Users/DELL/Desktop/GYM/backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add PIN Endpoints
pin_endpoints = """
from pydantic import BaseModel

class VerifyPinReq(BaseModel):
    pin: str
class UpdatePinReq(BaseModel):
    new_pin: str

@app.post("/auth/verify-pin")
async def verify_pin(req: VerifyPinReq, db: AsyncSession = Depends(get_db)):
    config_query = select(models.AppConfig).where(models.AppConfig.key == "admin_pin")
    res = await db.execute(config_query)
    config = res.scalars().first()
    expected_pin = config.value if config else "1111"
    if req.pin == expected_pin:
        return {"success": True}
    raise HTTPException(status_code=401, detail="Invalid PIN")

@app.put("/admin/pin")
async def update_pin(req: UpdatePinReq, db: AsyncSession = Depends(get_db)):
    config_query = select(models.AppConfig).where(models.AppConfig.key == "admin_pin")
    res = await db.execute(config_query)
    config = res.scalars().first()
    if config:
        config.value = req.new_pin
    else:
        new_config = models.AppConfig(key="admin_pin", value=req.new_pin)
        db.add(new_config)
    await db.commit()
    return {"success": True}
"""
content = content.replace("@app.post(\"/members/\", response_model=schemas.Member)", pin_endpoints + "\n@app.post(\"/members/\", response_model=schemas.Member)")


# 2. Update staff pending to include pay_day, phone, etc
# Find the PUT /admin/staff/{staff_id}/pending
staff_pending_pattern = r"@app\.put\(\"/admin/staff/\{staff_id\}/pending\"\)\nasync def update_staff_pending\(staff_id: int, bonus: float = Body\(0\), deduction: float = Body\(0\), db: AsyncSession = Depends\(get_db\)\):[\s\S]*?return \{\"status\": \"success\"\}\n"

new_staff_update = """class StaffUpdateReq(BaseModel):
    bonus: float = 0
    deduction: float = 0
    pay_day: int = None
    phone: str = None
    base_salary: float = None

@app.put("/admin/staff/{staff_id}/pending")
async def update_staff_pending(staff_id: int, req: StaffUpdateReq, db: AsyncSession = Depends(get_db)):
    query = select(models.Staff).where(models.Staff.id == staff_id)
    result = await db.execute(query)
    staff = result.scalars().first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    staff.pending_bonus = req.bonus
    staff.pending_deduction = req.deduction
    if req.pay_day is not None:
        staff.pay_day = req.pay_day
    if req.phone is not None:
        staff.phone = req.phone
    if req.base_salary is not None:
        staff.base_salary = req.base_salary
    await db.commit()
    return {"status": "success"}
"""
content = re.sub(staff_pending_pattern, new_staff_update, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Backend endpoints updated")
