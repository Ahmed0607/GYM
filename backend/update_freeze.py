import re

filepath = 'C:/Users/DELL/Desktop/GYM/backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update mark_expired_members
mark_expired_pattern = r'if member\.status == "Frozen":[\s\S]*?continue'
new_mark_expired = """if member.status == "Frozen":
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
                continue"""
content = re.sub(mark_expired_pattern, new_mark_expired, content)

# 2. Update freeze_member
freeze_pattern = r'@app\.post\("/members/\{member_id\}/freeze", response_model=schemas\.Member\)\nasync def freeze_member\(member_id: int, db: AsyncSession = Depends\(get_db\)\):[\s\S]*?return member'
new_freeze = """@app.post("/members/{member_id}/freeze", response_model=schemas.Member)
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
    
    return member"""
content = re.sub(freeze_pattern, new_freeze, content)

# 3. Update unfreeze_member
unfreeze_pattern = r'@app\.post\("/members/\{member_id\}/unfreeze", response_model=schemas\.Member\)\nasync def unfreeze_member\(member_id: int, db: AsyncSession = Depends\(get_db\)\):[\s\S]*?return member'
new_unfreeze = """@app.post("/members/{member_id}/unfreeze", response_model=schemas.Member)
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
    
    return member"""
content = re.sub(unfreeze_pattern, new_unfreeze, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated backend freeze logic successfully")
