from fastapi import FastAPI, Depends, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, update, func, cast, String, delete, text, distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import models
import schemas
from time_utils import get_current_time, set_time_offset, is_mock_enabled, set_mock_enabled
from database import engine, get_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    # Seed default package rules and config if empty
    await seed_default_packages()
    await seed_default_config()
    
    # Setup background task
    scheduler = AsyncIOScheduler()
    scheduler.add_job(purge_old_members, 'interval', days=1)
    scheduler.add_job(mark_expired_members, 'interval', minutes=1)
    scheduler.add_job(process_monthly_salaries, 'interval', days=1)
    scheduler.start()

async def seed_default_packages():
    """Seed the package_rules table with defaults if empty."""
    from database import SessionLocal
    async with SessionLocal() as db:
        result = await db.execute(select(func.count(models.PackageRule.id)))
        count = result.scalar()
        if count == 0:
            defaults = [
                models.PackageRule(name='1-Month Access', price=50, duration_days=30, sessions=None),
                models.PackageRule(name='3-Month Access', price=135, duration_days=90, sessions=None),
                models.PackageRule(name='1-Year Access', price=480, duration_days=365, sessions=None),
                models.PackageRule(name='10-Session Pass', price=80, duration_days=90, sessions=10),
                models.PackageRule(name='24-Session Pass', price=160, duration_days=180, sessions=24),
                models.PackageRule(name='Sauna Add-on', price=20, duration_days=30, sessions=None),
                models.PackageRule(name='Treadmill Only', price=30, duration_days=30, sessions=None),
            ]
            db.add_all(defaults)
            await db.commit()

async def seed_default_receptionist():
    """Seed a default receptionist if none exists."""
    from database import SessionLocal
    async with SessionLocal() as db:
        result = await db.execute(select(func.count(models.Receptionist.id)))
        count = result.scalar()
        if count == 0:
            db.add(models.Receptionist(name='Admin'))
            await db.commit()

async def seed_default_config():
    """Seed default app configuration."""
    from database import SessionLocal
    async with SessionLocal() as db:
        result = await db.execute(select(models.AppConfig).where(models.AppConfig.key == "admin_password"))
        if not result.scalars().first():
            db.add(models.AppConfig(key="admin_password", value="1111"))
            await db.commit()

async def mark_expired_members():
    from database import SessionLocal
    async with SessionLocal() as db:
        now = get_current_time()
        query = select(models.Member).options(selectinload(models.Member.subscriptions)).where(
            models.Member.status.in_(["Active", "Owed Money", "Frozen"])
        )
        result = await db.execute(query)
        members = result.scalars().unique().all()
        updated = False
        for member in members:
            if member.status == "Frozen":
                if member.freeze_end_date and now >= member.freeze_end_date.replace(tzinfo=timezone.utc):
                    # Unfreeze automatically
                    days_frozen = (member.freeze_end_date.replace(tzinfo=timezone.utc) - member.frozen_at.replace(tzinfo=timezone.utc)).days
                    if member.subscriptions:
                        latest_sub = member.subscriptions[-1]
                        latest_sub.end_date = latest_sub.end_date + timedelta(days=days_frozen)
                        
                        if latest_sub.end_date.replace(tzinfo=timezone.utc) < now:
                            member.status = "Expired"
                            member.expired_at = now
                        elif latest_sub.amount_owed > 0:
                            member.status = "Owed Money"
                        else:
                            member.status = "Active"
                    else:
                        member.status = "Active"
                        
                    member.frozen_at = None
                    member.freeze_end_date = None
                    updated = True
                continue

            if not member.subscriptions:
                continue
            latest_sub = member.subscriptions[-1]
            expired_by_date = latest_sub.end_date.replace(tzinfo=timezone.utc) < now
            expired_by_sessions = latest_sub.total_sessions is not None and latest_sub.attended_sessions >= latest_sub.total_sessions
            if expired_by_date or expired_by_sessions:
                member.status = "Expired"
                if expired_by_date:
                    member.expired_at = latest_sub.end_date.replace(tzinfo=timezone.utc)
                else:
                    member.expired_at = now
                updated = True
        if updated:
            await db.commit()

async def purge_old_members():
    async with engine.begin() as conn:
        from database import SessionLocal
        async with SessionLocal() as db:
            ninety_days_ago = get_current_time() - timedelta(days=90)
            
            query = select(models.Member).where(models.Member.status == 'Expired', models.Member.expired_at <= ninety_days_ago)
            result = await db.execute(query)
            members_to_delete = result.scalars().all()
            
            for member in members_to_delete:
                await db.execute(delete(models.AttendanceLog).where(models.AttendanceLog.member_id == member.id))
                await db.execute(delete(models.Subscription).where(models.Subscription.member_id == member.id))
                await db.delete(member)
            await db.commit()

async def process_monthly_salaries():
    async with engine.begin() as conn:
        from database import SessionLocal
        async with SessionLocal() as db:
            now = get_current_time()
            query = select(models.Staff)
            result = await db.execute(query)
            staff_members = result.scalars().all()
            
            for staff in staff_members:
                last_paid = staff.last_paid_date.replace(tzinfo=timezone.utc) if staff.last_paid_date.tzinfo is None else staff.last_paid_date
                
                # Pay date for the current month
                try:
                    pay_date_this_month = datetime(now.year, now.month, staff.pay_day, tzinfo=timezone.utc)
                except ValueError:
                    # In case pay_day is 31 and month has 30 days
                    import calendar
                    last_day = calendar.monthrange(now.year, now.month)[1]
                    pay_date_this_month = datetime(now.year, now.month, min(staff.pay_day, last_day), tzinfo=timezone.utc)
                
                should_pay = False
                if now >= pay_date_this_month and last_paid < pay_date_this_month:
                    should_pay = True

                if should_pay:
                    amount_to_pay = max(0.0, staff.base_salary + staff.pending_bonus - staff.pending_deduction)
                    payment = models.StaffPayment(
                        staff_id=staff.id,
                        amount=amount_to_pay,
                        bonus=staff.pending_bonus,
                        deduction=staff.pending_deduction,
                        payment_date=now
                    )
                    db.add(payment)
                    staff.pending_bonus = 0
                    staff.pending_deduction = 0
                    staff.last_paid_date = now
            
            await db.commit()

async def get_package_rules(db: AsyncSession):
    """Load package rules from database into a dict keyed by name."""
    result = await db.execute(select(models.PackageRule))
    rules = result.scalars().all()
    return {r.name: {'price': r.price, 'duration_days': r.duration_days, 'sessions': r.sessions, 'is_addon': r.is_addon} for r in rules}

async def get_next_available_id(db: AsyncSession) -> int:
    """Find the lowest available member ID (reuses gaps from deleted members)."""
    result = await db.execute(select(models.Member.id).order_by(models.Member.id))
    existing_ids = [row[0] for row in result.fetchall()]
    
    if not existing_ids:
        return 1
    
    # Find the first gap
    for expected_id, actual_id in enumerate(existing_ids, start=1):
        if expected_id != actual_id:
            return expected_id
    
    # No gap found, use next after max
    return existing_ids[-1] + 1

# ─── List All Members (with optional search) ────────────────────────────────

ARABIC_DIGITS_MAP = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

@app.get("/members/", response_model=List[schemas.Member])
async def list_members(q: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(models.Member).options(
        selectinload(models.Member.subscriptions),
        selectinload(models.Member.attendance_logs)
    ).where(models.Member.status != "Deleted")
    
    if q and q.strip():
        search_term = q.strip()
        normalized_term = search_term.translate(ARABIC_DIGITS_MAP)
        conditions = [
            cast(models.Member.id, String).like(f"%{search_term}%"),
            models.Member.name.ilike(f"%{search_term}%"),
            models.Member.phone.ilike(f"%{search_term}%"),
        ]
        if normalized_term != search_term:
            conditions.append(cast(models.Member.id, String).like(f"%{normalized_term}%"))
            conditions.append(models.Member.phone.ilike(f"%{normalized_term}%"))
            
        digits = ''.join(c for c in normalized_term if c.isdigit())
        if digits and digits not in (search_term, normalized_term):
            conditions.append(models.Member.phone.ilike(f"%{digits}%"))

        query = query.where(or_(*conditions))
    
    query = query.order_by(models.Member.id)
    result = await db.execute(query)
    return result.scalars().unique().all()

# ─── Search Members (legacy endpoint used by Reception) ──────────────────────

@app.get("/members/search", response_model=List[schemas.Member])
async def search_members(q: str, db: AsyncSession = Depends(get_db)):
    query = select(models.Member).options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
    query = query.where(models.Member.status != "Deleted")
    if q.isdigit():
        query = query.where(models.Member.id == int(q))
    else:
        query = query.where(models.Member.name.ilike(f"%{q}%"))
        
    result = await db.execute(query)
    return result.scalars().unique().all()

# ─── Get Single Member Detail ────────────────────────────────────────────────

@app.get("/members/{member_id}", response_model=schemas.Member)
async def get_member(member_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

# ─── Create Member ───────────────────────────────────────────────────────────


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

@app.post("/members/", response_model=schemas.Member)
async def create_member(member: schemas.MemberCreate, db: AsyncSession = Depends(get_db)):
    # Load package rules from DB
    PACKAGE_RULES = await get_package_rules(db)
    
    # 1. Intercept array of packages and calculate predefined rules
    total_price = 0
    max_duration = 0
    total_sessions = 0
    has_sessions = False
    addons_usage = {}
    
    for pkg_name in member.subscription.packages:
        rule = PACKAGE_RULES.get(pkg_name, {'price': 0, 'duration_days': 0, 'sessions': None, 'is_addon': False})
        total_price += rule['price']
        if rule['duration_days'] > max_duration:
            max_duration = rule['duration_days']
        
        if rule.get('is_addon'):
            addons_usage[pkg_name] = {
                "total": rule.get('sessions'),
                "used": 0
            }
        else:
            if rule.get('sessions') is not None:
                has_sessions = True
                total_sessions += rule.get('sessions')
            
    if not has_sessions:
        total_sessions = None
    
    # Apply discount: reduce the effective price the member needs to pay
    discount = max(0.0, member.subscription.discount or 0)
    effective_price = max(0.0, total_price - discount)
    
    # Amount owed is based on the discounted price
    amount_owed = max(0.0, effective_price - member.subscription.amount_paid)
    
    # Get the lowest available ID
    next_id = await get_next_available_id(db)
    
    db_member = models.Member(id=next_id, name=member.name, phone=member.phone, gender=member.gender, status="Active")
    if amount_owed > 0:
        db_member.status = "Owed Money"
        
    db.add(db_member)
    await db.commit()
    await db.refresh(db_member)
    
    if member.subscription.start_date:
        start_date = member.subscription.start_date
    else:
        start_date = get_current_time()
    
    end_date = start_date + timedelta(days=max_duration)
    
    db_sub = models.Subscription(
        member_id=db_member.id,
        package_name=member.subscription.packages,
        total_price=total_price,
        discount=discount,
        amount_paid=member.subscription.amount_paid,
        amount_owed=amount_owed,
        total_sessions=total_sessions,
        attended_sessions=0,
        addons_usage=addons_usage,
        start_date=start_date,
        end_date=end_date
    )
    db.add(db_sub)
    await db.commit()
    await db.refresh(db_sub)
    
    # Reload with relations
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == db_member.id)
    )
    return result.scalars().first()

# ─── Update Member (name / phone) ───────────────────────────────────────────

@app.put("/members/{member_id}", response_model=schemas.Member)
async def update_member(member_id: int, updates: schemas.MemberUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if updates.name is not None:
        member.name = updates.name
    if updates.phone is not None:
        member.phone = updates.phone
    
    await db.commit()
    await db.refresh(member)
    
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    return result.scalars().first()

# ─── Delete Expired Members ──────────────────────────────────────────────────

@app.delete("/members/expired/all")
async def delete_all_expired_members(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Member).where(models.Member.status == "Expired"))
    members = result.scalars().all()
    count = 0
    for m in members:
        await db.execute(update(models.AttendanceLog).where(models.AttendanceLog.member_id == m.id).values(member_id=None))
        await db.execute(update(models.Subscription).where(models.Subscription.member_id == m.id).values(member_id=None))
        await db.delete(m)
        count += 1
    await db.commit()
    return {"detail": f"Deleted {count} expired members. Their IDs are now available."}

# ─── Delete Member ───────────────────────────────────────────────────────────

@app.delete("/members/{member_id}")
async def delete_member(member_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Member).where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    await db.execute(update(models.AttendanceLog).where(models.AttendanceLog.member_id == member_id).values(member_id=None))
    await db.execute(update(models.Subscription).where(models.Subscription.member_id == member_id).values(member_id=None))
    await db.delete(member)
    await db.commit()
    return {"detail": f"Member {member_id} deleted successfully. Their ID is now available."}

# ─── Pay Debt ────────────────────────────────────────────────────────────────

@app.post("/members/{member_id}/pay-debt", response_model=schemas.Member)
async def pay_debt(member_id: int, payment: schemas.PaymentCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Apply payment to the latest subscription
    if not member.subscriptions:
        raise HTTPException(status_code=400, detail="No subscription found")
    
    sub = member.subscriptions[-1]  # latest subscription
    sub.amount_paid += payment.amount
    sub.amount_owed = max(0.0, sub.total_price - sub.discount - sub.amount_paid)
    
    # Update member status if debt cleared
    if sub.amount_owed <= 0:
        # Check if subscription is still valid
        if sub.end_date.replace(tzinfo=timezone.utc) >= get_current_time():
            member.status = "Active"
        else:
            member.status = "Expired"
            member.expired_at = get_current_time()
    
    await db.commit()
    
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    return result.scalars().first()

# ─── Update Subscription (modify packages — adds cost to debt) ──────────────

@app.put("/members/{member_id}/subscription", response_model=schemas.Member)
async def update_subscription(member_id: int, sub_update: schemas.SubscriptionUpdate, db: AsyncSession = Depends(get_db)):
    # Load package rules from DB
    PACKAGE_RULES = await get_package_rules(db)
    
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Calculate new subscription costs
    total_price = 0
    max_duration = 0
    total_sessions = 0
    has_sessions = False
    addons_usage = {}
    
    for pkg_name in sub_update.packages:
        rule = PACKAGE_RULES.get(pkg_name, {'price': 0, 'duration_days': 0, 'sessions': None, 'is_addon': False})
        total_price += rule['price']
        if rule['duration_days'] > max_duration:
            max_duration = rule['duration_days']
        
        if rule.get('is_addon'):
            addons_usage[pkg_name] = {
                "total": rule.get('sessions'),
                "used": 0
            }
        else:
            if rule.get('sessions') is not None:
                has_sessions = True
                total_sessions += rule.get('sessions')
    
    if not has_sessions:
        total_sessions = None
    
    # Apply discount
    discount = max(0.0, sub_update.discount or 0)
    effective_price = max(0.0, total_price - discount)
    amount_owed = max(0.0, effective_price - sub_update.amount_paid)
    
    start_date = get_current_time()
    end_date = start_date + timedelta(days=max_duration)
    
    # Create a new subscription record (keeps history)
    db_sub = models.Subscription(
        member_id=member_id,
        package_name=sub_update.packages,
        total_price=total_price,
        discount=discount,
        amount_paid=sub_update.amount_paid,
        amount_owed=amount_owed,
        total_sessions=total_sessions,
        attended_sessions=0,
        addons_usage=addons_usage,
        start_date=start_date,
        end_date=end_date
    )
    db.add(db_sub)
    
    # Update member status
    if amount_owed > 0:
        member.status = "Owed Money"
    else:
        member.status = "Active"
    
    await db.commit()
    
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    return result.scalars().first()

# ─── Consume Addon ───────────────────────────────────────────────────────────

@app.post("/members/{member_id}/consume-addon", response_model=schemas.Member)
async def consume_addon(member_id: int, payload: dict, db: AsyncSession = Depends(get_db)):
    addon_name = payload.get("addon_name")
    if not addon_name:
        raise HTTPException(status_code=400, detail="Addon name is required")

    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    result = await db.execute(
        select(models.Subscription)
        .where(models.Subscription.member_id == member_id)
        .order_by(models.Subscription.end_date.desc())
    )
    sub = result.scalars().first()
    if not sub:
        raise HTTPException(status_code=400, detail="No active subscription found")
        
    if sub.addons_usage is None:
        sub.addons_usage = {}
    elif isinstance(sub.addons_usage, list):
        # Migrate from list to dict if needed
        sub.addons_usage = {}

    PACKAGE_RULES = await get_package_rules(db)
    addon_rule = PACKAGE_RULES.get(addon_name)
    if not addon_rule or not addon_rule.get('is_addon'):
        raise HTTPException(status_code=400, detail="Invalid addon")

    # The addons_usage dictionary stores usage state like {"total": 5, "used": 2} or just the used count if not initialized properly
    usage_info = sub.addons_usage.get(addon_name, {"total": addon_rule.get('sessions'), "used": 0})
    if isinstance(usage_info, int):
        usage_info = {"total": addon_rule.get('sessions'), "used": usage_info}

    if usage_info.get("total") is not None and usage_info.get("used", 0) >= usage_info.get("total"):
        raise HTTPException(status_code=400, detail=f"No {addon_name} sessions remaining")

    usage_info["used"] = usage_info.get("used", 0) + 1
    
    # Needs to be a new dict so SQLAlchemy detects mutation
    new_addons_usage = dict(sub.addons_usage)
    new_addons_usage[addon_name] = usage_info
    sub.addons_usage = new_addons_usage
    flag_modified(sub, "addons_usage")

    # Add attendance log with tag (first 3 chars)
    tag = addon_name[:3] if addon_name else "ADD"
    new_log = models.AttendanceLog(member_id=member_id, addon_tag=tag)
    db.add(new_log)

    await db.commit()
    
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    return result.scalars().first()

# ─── Check-in Member ─────────────────────────────────────────────────────────

@app.post("/members/{member_id}/checkin", response_model=schemas.Member)
async def checkin_member(member_id: int, db: AsyncSession = Depends(get_db)):
    # Find member
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    # Find active subscription (for simplicity, we assume one active)
    result = await db.execute(
        select(models.Subscription)
        .where(models.Subscription.member_id == member_id)
        .order_by(models.Subscription.end_date.desc())
    )
    sub = result.scalars().first()
    
    if not sub:
        raise HTTPException(status_code=400, detail="No active subscription found")
        
    # Check if expired
    if sub.end_date.replace(tzinfo=timezone.utc) < get_current_time():
        member.status = "Expired"
        member.expired_at = get_current_time()
        await db.commit()
        raise HTTPException(status_code=400, detail="Subscription expired")
        
    if sub.total_sessions and sub.attended_sessions >= sub.total_sessions:
        if member.status != "Expired":
            member.status = "Expired"
            member.expired_at = get_current_time()
            await db.commit()
        raise HTTPException(status_code=400, detail="No sessions remaining")

    # Update attended sessions
    sub.attended_sessions += 1
    
    # Add attendance log
    new_log = models.AttendanceLog(member_id=member_id)
    db.add(new_log)
    
    await db.commit()
    
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    return result.scalars().first()




# ─── Freeze / Unfreeze Member ────────────────────────────────────────────────

@app.post("/members/{member_id}/freeze", response_model=schemas.Member)
async def freeze_member(member_id: int, req: schemas.FreezeRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    if member.status == "Frozen":
        raise HTTPException(status_code=400, detail="Member is already frozen")
        
    # Mark as frozen
    now = get_current_time()
    member.status = "Frozen"
    member.frozen_at = now
    member.freeze_end_date = now + timedelta(weeks=req.duration_weeks)
    await db.commit()
    await db.refresh(member)
    
    return member

@app.post("/members/{member_id}/unfreeze", response_model=schemas.Member)
async def unfreeze_member(member_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Member)
        .options(selectinload(models.Member.subscriptions), selectinload(models.Member.attendance_logs))
        .where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    if member.status != "Frozen":
        raise HTTPException(status_code=400, detail="Member is not frozen")
        
    if member.frozen_at:
        now = get_current_time()
        days_frozen = (now - member.frozen_at.replace(tzinfo=timezone.utc)).days
        
        if member.subscriptions:
            latest_sub = member.subscriptions[-1]
            latest_sub.end_date = latest_sub.end_date + timedelta(days=days_frozen)
            
            if latest_sub.end_date.replace(tzinfo=timezone.utc) < now:
                member.status = "Expired"
                member.expired_at = now
            elif latest_sub.amount_owed > 0:
                member.status = "Owed Money"
            else:
                member.status = "Active"
        else:
            member.status = "Active"
            
        member.frozen_at = None
        member.freeze_end_date = None
        
    await db.commit()
    await db.refresh(member)
    
    return member


# ─── Single Sessions ─────────────────────────────────────────────────────────

class SingleSessionCreate(BaseModel):
    name: str
    amount: float

@app.post("/single-sessions")
async def create_single_session(req: SingleSessionCreate, db: AsyncSession = Depends(get_db)):
    now = get_current_time()
    session = models.SingleSession(name=req.name, amount=req.amount, timestamp=now)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"detail": "Single session recorded", "id": session.id}

@app.get("/config/single-session-price")
async def get_single_session_price(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.AppConfig).where(models.AppConfig.key == "single_session_price"))
    config = result.scalars().first()
    return {"price": float(config.value) if config else 30.0}

@app.post("/config/single-session-price")
async def update_single_session_price(price: float = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.AppConfig).where(models.AppConfig.key == "single_session_price"))
    config = result.scalars().first()
    if config:
        config.value = str(price)
    else:
        db.add(models.AppConfig(key="single_session_price", value=str(price)))
    await db.commit()
    return {"detail": "Price updated"}

# ─── Admin Dashboard ─────────────────────────────────────────────────────────


@app.get("/admin/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    now = get_current_time()
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    ninety_mins_ago = now - timedelta(minutes=90)
    
    # Live Occupancy (Checkins in last 90 mins)
    occupancy_query = select(func.count(distinct(models.AttendanceLog.member_id))).where(models.AttendanceLog.timestamp >= ninety_mins_ago)
    live_occupancy = (await db.execute(occupancy_query)).scalar() or 0
    ss_occ_query = select(func.count(models.SingleSession.id)).where(models.SingleSession.timestamp >= ninety_mins_ago)
    live_occupancy += (await db.execute(ss_occ_query)).scalar() or 0
    
    # Today's checkins count
    checkins_query = select(func.count(models.AttendanceLog.id)).where(models.AttendanceLog.timestamp >= today_start)
    today_checkins = (await db.execute(checkins_query)).scalar() or 0
    ss_today_query = select(func.count(models.SingleSession.id)).where(models.SingleSession.timestamp >= today_start)
    today_checkins += (await db.execute(ss_today_query)).scalar() or 0
    
    # Today's checkin details (with member info) — reverse chronological
    checkin_details_query = (
        select(models.AttendanceLog, models.Member.name, models.Member.id.label("mid"))
        .join(models.Member, models.AttendanceLog.member_id == models.Member.id)
        .where(models.AttendanceLog.timestamp >= today_start)
    )
    checkin_rows = (await db.execute(checkin_details_query)).all()
    today_checkin_list = [
        {
            "member_id": row.mid,
            "member_name": row.name,
            "timestamp": row.AttendanceLog.timestamp.isoformat() if row.AttendanceLog.timestamp else None,
            "type": "Member"
        }
        for row in checkin_rows
    ]
    ss_today_details_query = select(models.SingleSession).where(models.SingleSession.timestamp >= today_start)
    ss_rows = (await db.execute(ss_today_details_query)).scalars().all()
    today_checkin_list.extend([
        {
            "member_id": "G",
            "member_name": f"{row.name} (Walk-in)",
            "timestamp": row.timestamp.isoformat(),
            "type": "Walk-in"
        }
        for row in ss_rows
    ])
    today_checkin_list.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Total active members
    active_query = select(func.count(models.Member.id)).where(models.Member.status == "Active")
    active_result = await db.execute(active_query)
    active_members = active_result.scalar() or 0
    
    # Total money owed
    owed_query = select(func.sum(models.Subscription.amount_owed))
    owed_result = await db.execute(owed_query)
    total_owed = owed_result.scalar() or 0
    
    # Revenue today 
    rev_query = select(func.sum(models.Subscription.amount_paid)).where(models.Subscription.start_date >= today_start)
    revenue_today = (await db.execute(rev_query)).scalar() or 0
    ss_rev_today_query = select(func.sum(models.SingleSession.amount)).where(models.SingleSession.timestamp >= today_start)
    revenue_today += (await db.execute(ss_rev_today_query)).scalar() or 0
    
    # All time finances for dashboard
    all_rev_query = select(func.sum(models.Subscription.amount_paid))
    all_revenue = (await db.execute(all_rev_query)).scalar() or 0
    ss_all_rev_query = select(func.sum(models.SingleSession.amount))
    all_revenue += (await db.execute(ss_all_rev_query)).scalar() or 0
    
    all_exp = (await db.execute(select(models.Expense))).scalars().all()
    total_maintenance = sum(e.amount for e in all_exp if e.category == "Maintenance")
    total_bills = sum(e.amount for e in all_exp if e.category == "Bill")
    total_other = sum(e.amount for e in all_exp if e.category == "Other")
    
    all_salaries_query = select(models.StaffPayment).options(selectinload(models.StaffPayment.staff))
    all_salaries_records = (await db.execute(all_salaries_query)).scalars().all()
    total_salaries = sum(p.amount for p in all_salaries_records)
    
    net_revenue = all_revenue - (total_maintenance + total_bills + total_salaries + total_other)
    
    # Finances History
    finance_history = []
    for exp in all_exp:
        finance_history.append({
            "type": exp.category,
            "amount": exp.amount,
            "description": exp.description,
            "date": exp.date.isoformat()
        })
    for sal in all_salaries_records:
        finance_history.append({
            "type": "Salary",
            "amount": sal.amount,
            "description": f"Paid {sal.staff.name} ({sal.staff.role})",
            "date": sal.payment_date.isoformat()
        })
    all_ss = (await db.execute(select(models.SingleSession))).scalars().all()
    for ss in all_ss:
        finance_history.append({
            "type": "Income",
            "amount": -ss.amount,  # make it negative so the UI sees it as a positive addition if we want, or handle in UI
            "description": f"Walk-in Session: {ss.name}",
            "date": ss.timestamp.isoformat()
        })
    finance_history.sort(key=lambda x: x["date"], reverse=True)
    finance_history = finance_history[:20] # Top 20 recent
    
    # Members owing money
    members_owing_query = select(models.Member).options(selectinload(models.Member.subscriptions)).join(models.Subscription).where(
        models.Subscription.amount_owed > 0,
        models.Member.status != "Deleted"
    )
    members_owing = (await db.execute(members_owing_query)).scalars().unique().all()
    
    # Expiring within 7 days
    seven_days = now + timedelta(days=7)
    expiring_query = select(models.Member).options(selectinload(models.Member.subscriptions)).join(models.Subscription).where(
        models.Subscription.end_date >= now,
        models.Subscription.end_date <= seven_days,
        models.Member.status != "Deleted"
    )
    expiring_members = (await db.execute(expiring_query)).scalars().unique().all()
    
    # Recent subscriptions (last 10)
    recent_subs_query = (
        select(models.Subscription, models.Member.name, models.Member.id.label("mid"))
        .join(models.Member, models.Subscription.member_id == models.Member.id)
        .order_by(models.Subscription.start_date.desc())
        .limit(10)
    )
    recent_subs_rows = (await db.execute(recent_subs_query)).all()
    recent_subscriptions = [
        {
            "member_id": str(row.mid),
            "member_name": row.name,
            "packages": row.Subscription.package_name,
            "amount_paid": row.Subscription.amount_paid,
            "start_date": row.Subscription.start_date.isoformat() if row.Subscription.start_date else None
        }
        for row in recent_subs_rows
    ]
    
    recent_ss_query = (
        select(models.SingleSession)
        .order_by(models.SingleSession.timestamp.desc())
        .limit(10)
    )
    recent_ss_rows = (await db.execute(recent_ss_query)).scalars().all()
    
    for row in recent_ss_rows:
        recent_subscriptions.append({
            "member_id": f"G{row.id}",
            "member_name": row.name,
            "packages": ["1-Session"],
            "amount_paid": row.amount,
            "start_date": row.timestamp.isoformat() if row.timestamp else None
        })
        
    recent_subscriptions.sort(key=lambda x: x["start_date"] or "", reverse=True)
    recent_subscriptions = recent_subscriptions[:10]
    
    return {
        "net_revenue": net_revenue,
        "total_salaries": total_salaries,
        "total_maintenance": total_maintenance,
        "total_bills": total_bills,
        "total_other": total_other,
        "finance_history": finance_history,
        "kpis": {
            "today_checkins": today_checkins,
            "total_active_members": active_members,
            "total_money_owed": total_owed,
            "revenue_today": revenue_today,
            "live_occupancy": live_occupancy
        },
        "today_checkin_list": today_checkin_list,
        "members_owing_money": members_owing,
        "expiring_soon": expiring_members,
        "recent_subscriptions": recent_subscriptions
    }

# ─── Package Rules CRUD ─────────────────────────────────────────────────────

@app.get("/admin/packages", response_model=List[schemas.PackageRule])
async def list_packages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.PackageRule).order_by(models.PackageRule.id))
    return result.scalars().all()

@app.post("/admin/packages", response_model=schemas.PackageRule)
async def create_package(pkg: schemas.PackageRuleCreate, db: AsyncSession = Depends(get_db)):
    # Check for duplicate name
    existing = await db.execute(select(models.PackageRule).where(models.PackageRule.name == pkg.name))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="A package with this name already exists.")
    
    db_pkg = models.PackageRule(
        name=pkg.name,
        price=pkg.price,
        duration_days=pkg.duration_days,
        sessions=pkg.sessions,
        is_addon=pkg.is_addon
    )
    db.add(db_pkg)
    await db.commit()
    await db.refresh(db_pkg)
    return db_pkg

@app.put("/admin/packages/{pkg_id}", response_model=schemas.PackageRule)
async def update_package(pkg_id: int, updates: schemas.PackageRuleUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.PackageRule).where(models.PackageRule.id == pkg_id))
    pkg = result.scalars().first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")
    
    if updates.name is not None:
        # Check name uniqueness
        existing = await db.execute(
            select(models.PackageRule).where(models.PackageRule.name == updates.name, models.PackageRule.id != pkg_id)
        )
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="A package with this name already exists.")
        pkg.name = updates.name
    if updates.price is not None:
        pkg.price = updates.price
    if updates.duration_days is not None:
        pkg.duration_days = updates.duration_days
    if updates.sessions is not None:
        pkg.sessions = updates.sessions
    # Allow explicitly setting sessions to null (unlimited)
    if 'sessions' in (updates.model_dump(exclude_unset=True)):
        pkg.sessions = updates.sessions
    if updates.is_addon is not None:
        pkg.is_addon = updates.is_addon
    
    await db.commit()
    await db.refresh(pkg)
    return pkg

@app.delete("/admin/packages/{pkg_id}")
async def delete_package(pkg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.PackageRule).where(models.PackageRule.id == pkg_id))
    pkg = result.scalars().first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")
    
    await db.delete(pkg)
    await db.commit()
    return {"detail": f"Package '{pkg.name}' deleted successfully."}

# ─── Admin Reset (delete all members, subscriptions, attendance logs) ────────

@app.delete("/admin/reset")
async def admin_reset(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(models.AttendanceLog))
    await db.execute(delete(models.Subscription))
    await db.execute(delete(models.Member))
    await db.execute(delete(models.Expense))
    await db.execute(delete(models.StaffPayment))
    await db.execute(delete(models.SingleSession))
    await db.execute(delete(models.Staff))
    await db.execute(delete(models.PackageRule))
    await db.execute(delete(models.Receptionist))
    await db.commit()
    return {"detail": "All members, subscriptions, attendance logs, expenses, staff payments, single sessions, staff members, packages, and receptionists have been reset."}

# ─── Receptionists CRUD ─────────────────────────────────────────────────────

@app.get("/admin/receptionists", response_model=List[schemas.Receptionist])
async def list_receptionists(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Receptionist).order_by(models.Receptionist.id))
    return result.scalars().all()

@app.post("/admin/receptionists", response_model=schemas.Receptionist)
async def create_receptionist(rec: schemas.ReceptionistCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(models.Receptionist).where(models.Receptionist.name == rec.name))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="A receptionist with this name already exists.")
    
    db_rec = models.Receptionist(name=rec.name)
    db.add(db_rec)
    await db.commit()
    await db.refresh(db_rec)
    return db_rec

@app.put("/admin/receptionists/{rec_id}", response_model=schemas.Receptionist)
async def update_receptionist(rec_id: int, updates: schemas.ReceptionistUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Receptionist).where(models.Receptionist.id == rec_id))
    rec = result.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Receptionist not found")
    
    if updates.name is not None:
        existing = await db.execute(
            select(models.Receptionist).where(models.Receptionist.name == updates.name, models.Receptionist.id != rec_id)
        )
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="A receptionist with this name already exists.")
        rec.name = updates.name
    
    await db.commit()
    await db.refresh(rec)
    return rec

@app.delete("/admin/receptionists/{rec_id}")
async def delete_receptionist(rec_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Receptionist).where(models.Receptionist.id == rec_id))
    rec = result.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Receptionist not found")
    
    await db.delete(rec)
    await db.commit()
    return {"detail": f"Receptionist '{rec.name}' deleted successfully."}


# ─── Mock Time endpoints ──────────────────────────────────────────────────────

@app.post("/admin/mock-time")
async def set_mock_time_endpoint(target_date: str):
    from datetime import datetime, timezone
    try:
        target = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        set_time_offset(target)
        # Immediately run background jobs so time-travel takes effect
        await mark_expired_members()
        await purge_old_members()
        await process_monthly_salaries()
        return {"detail": "Time mocked", "current_time": get_current_time(), "mock_enabled": is_mock_enabled()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/mock-time/toggle")
async def toggle_mock_time_endpoint(enabled: bool):
    set_mock_enabled(enabled)
    return {"detail": "Mock time enabled" if enabled else "Mock time disabled", "current_time": get_current_time(), "mock_enabled": is_mock_enabled()}

@app.get("/admin/mock-time")
async def get_mock_time_endpoint():
    return {"current_time": get_current_time(), "mock_enabled": is_mock_enabled()}

# ─── Finances Endpoints ───────────────────────────────────────────────────────

@app.get("/admin/staff", response_model=List[schemas.StaffResponse])
async def list_staff(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Staff))
    return result.scalars().all()

@app.post("/admin/staff", response_model=schemas.StaffResponse)
async def create_staff(staff: schemas.StaffCreate, db: AsyncSession = Depends(get_db)):
    new_staff = models.Staff(**staff.dict(), last_paid_date=get_current_time(), created_at=get_current_time())
    db.add(new_staff)
    await db.commit()
    await db.refresh(new_staff)
    return new_staff

@app.put("/admin/staff/{staff_id}/pending", response_model=schemas.StaffResponse)
async def update_staff_pending(staff_id: int, update: schemas.StaffUpdate, db: AsyncSession = Depends(get_db)):
    staff = await db.get(models.Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    staff.pending_bonus = update.pending_bonus
    staff.pending_deduction = update.pending_deduction
    await db.commit()
    await db.refresh(staff)
    return staff

@app.delete("/admin/staff/{staff_id}")
async def delete_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    staff = await db.get(models.Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    await db.delete(staff)
    await db.commit()
    return {"detail": "Staff deleted"}

@app.post("/admin/expenses", response_model=schemas.ExpenseResponse)
async def create_expense(expense: schemas.ExpenseCreate, db: AsyncSession = Depends(get_db)):
    new_expense = models.Expense(
        category=expense.category,
        amount=expense.amount,
        description=expense.description,
        date=expense.date if expense.date else get_current_time()
    )
    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)
    return new_expense



@app.get("/admin/finances/filter")
async def get_finances_filtered(start_date: str, end_date: str, db: AsyncSession = Depends(get_db)):
    try:
        from datetime import datetime, timezone
        start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc) if datetime.fromisoformat(start_date).tzinfo is None else datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc) if datetime.fromisoformat(end_date).tzinfo is None else datetime.fromisoformat(end_date)
        if end.hour == 0 and end.minute == 0 and end.second == 0:
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Subscriptions
        subs_query = select(models.Subscription).where(
            models.Subscription.start_date >= start,
            models.Subscription.start_date <= end
        )
        subs = await db.execute(subs_query)
        revenue = sum(s.amount_paid for s in subs.scalars().all())
        
        # Single Sessions
        ss_filter_query = select(models.SingleSession).where(
            models.SingleSession.timestamp >= start,
            models.SingleSession.timestamp <= end
        )
        ss_filter_list = (await db.execute(ss_filter_query)).scalars().all()
        revenue += sum(s.amount for s in ss_filter_list)
        
        # Expenses
        exp_query = select(models.Expense).where(
            models.Expense.date >= start,
            models.Expense.date <= end
        )
        expenses_list = (await db.execute(exp_query)).scalars().all()
        maintenance_cost = sum(e.amount for e in expenses_list if e.category == "Maintenance")
        bills_cost = sum(e.amount for e in expenses_list if e.category == "Bill")
        other_cost = sum(e.amount for e in expenses_list if e.category == "Other")
        
        # Salaries
        staff_query = select(models.StaffPayment).where(
            models.StaffPayment.payment_date >= start,
            models.StaffPayment.payment_date <= end
        )
        staff_list = (await db.execute(staff_query)).scalars().all()
        salaries_cost = sum(p.amount for p in staff_list)
        
        net_revenue = revenue - (maintenance_cost + bills_cost + salaries_cost + other_cost)
        
        finance_history = []
        for exp in expenses_list:
            finance_history.append({
                "type": exp.category,
                "amount": exp.amount,
                "description": exp.description,
                "date": exp.date.isoformat()
            })
        
        # Need staff info for salaries in filter
        staff_query_filter = select(models.StaffPayment).options(selectinload(models.StaffPayment.staff)).where(
            models.StaffPayment.payment_date >= start,
            models.StaffPayment.payment_date <= end
        )
        staff_list_filter = (await db.execute(staff_query_filter)).scalars().all()
        for sal in staff_list_filter:
            finance_history.append({
                "type": "Salary",
                "amount": sal.amount,
                "description": f"Paid {sal.staff.name} ({sal.staff.role})",
                "date": sal.payment_date.isoformat()
            })
        for ss in ss_filter_list:
            finance_history.append({
                "type": "Income",
                "amount": -ss.amount,
                "description": f"Walk-in Session: {ss.name}",
                "date": ss.timestamp.isoformat()
            })
        finance_history.sort(key=lambda x: x["date"], reverse=True)

        return {
            "revenue": revenue,
            "net_revenue": net_revenue,
            "total_maintenance": maintenance_cost,
            "total_bills": bills_cost,
            "total_other": other_cost,
            "total_salaries": salaries_cost,
            "finance_history": finance_history
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class AdminAuth(schemas.BaseModel):
    password: str

@app.post("/verify_admin_password")
async def verify_admin_password(auth: AdminAuth, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.AppConfig).where(models.AppConfig.key == "admin_password"))
    config = result.scalars().first()
    if not config or config.value != auth.password:
        raise HTTPException(status_code=401, detail="كلمة المرور غير صحيحة")
    return {"status": "ok"}

class AdminPasswordUpdate(schemas.BaseModel):
    old_password: str
    new_password: str

@app.put("/admin_password")
async def update_admin_password(payload: AdminPasswordUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.AppConfig).where(models.AppConfig.key == "admin_password"))
    config = result.scalars().first()
    if not config or config.value != payload.old_password:
        raise HTTPException(status_code=401, detail="كلمة المرور الحالية غير صحيحة")
    
    config.value = payload.new_password
    await db.commit()
    return {"status": "ok"}
