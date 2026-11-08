import re

filepath = 'C:/Users/DELL/Desktop/GYM/backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Single Session endpoint
new_endpoints = """
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
"""
content = content.replace('# ─── Admin Dashboard ─────────────────────────────────────────────────────────', new_endpoints)

# 2. Update get_dashboard to include SingleSessions
# We need to find `occupancy_query = select(func.count(distinct(models.AttendanceLog.member_id))).where(models.AttendanceLog.timestamp >= ninety_mins_ago)`
dash_pattern = r'# Live Occupancy \(Checkins in last 90 mins\)[\s\S]*?checkins_result = await db\.execute\(checkins_query\)\n    today_checkins = checkins_result\.scalar\(\) or 0'
new_dash_checkins = """# Live Occupancy (Checkins in last 90 mins)
    occupancy_query = select(func.count(distinct(models.AttendanceLog.member_id))).where(models.AttendanceLog.timestamp >= ninety_mins_ago)
    live_occupancy = (await db.execute(occupancy_query)).scalar() or 0
    ss_occ_query = select(func.count(models.SingleSession.id)).where(models.SingleSession.timestamp >= ninety_mins_ago)
    live_occupancy += (await db.execute(ss_occ_query)).scalar() or 0
    
    # Today's checkins count
    checkins_query = select(func.count(models.AttendanceLog.id)).where(models.AttendanceLog.timestamp >= today_start)
    today_checkins = (await db.execute(checkins_query)).scalar() or 0
    ss_today_query = select(func.count(models.SingleSession.id)).where(models.SingleSession.timestamp >= today_start)
    today_checkins += (await db.execute(ss_today_query)).scalar() or 0"""
content = re.sub(dash_pattern, new_dash_checkins, content)

# 3. Update checkin_list in get_dashboard
checkin_list_pattern = r'# Today\'s checkin details \(with member info\) — reverse chronological[\s\S]*?for row in checkin_rows\n    \]'
new_checkin_list = """# Today's checkin details (with member info) — reverse chronological
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
            "member_id": f"SS-{row.id}",
            "member_name": f"{row.name} (Walk-in)",
            "timestamp": row.timestamp.isoformat(),
            "type": "Walk-in"
        }
        for row in ss_rows
    ])
    today_checkin_list.sort(key=lambda x: x["timestamp"], reverse=True)"""
content = re.sub(checkin_list_pattern, new_checkin_list, content)

# 4. Update get_dashboard revenue calculation
revenue_today_pattern = r'# Revenue today \n    rev_query = select\(func\.sum\(models\.Subscription\.amount_paid\)\)\.where\(models\.Subscription\.start_date >= today_start\)\n    rev_result = await db\.execute\(rev_query\)\n    revenue_today = rev_result\.scalar\(\) or 0\n    \n    # All time finances for dashboard\n    all_rev_query = select\(func\.sum\(models\.Subscription\.amount_paid\)\)\n    all_revenue = \(await db\.execute\(all_rev_query\)\)\.scalar\(\) or 0'
new_revenue_calc = """# Revenue today 
    rev_query = select(func.sum(models.Subscription.amount_paid)).where(models.Subscription.start_date >= today_start)
    revenue_today = (await db.execute(rev_query)).scalar() or 0
    ss_rev_today_query = select(func.sum(models.SingleSession.amount)).where(models.SingleSession.timestamp >= today_start)
    revenue_today += (await db.execute(ss_rev_today_query)).scalar() or 0
    
    # All time finances for dashboard
    all_rev_query = select(func.sum(models.Subscription.amount_paid))
    all_revenue = (await db.execute(all_rev_query)).scalar() or 0
    ss_all_rev_query = select(func.sum(models.SingleSession.amount))
    all_revenue += (await db.execute(ss_all_rev_query)).scalar() or 0"""
content = re.sub(revenue_today_pattern, new_revenue_calc, content)

# 5. Update Finance History in get_dashboard
history_pattern = r'for sal in all_salaries_records:\n        finance_history\.append\(\{\n            "type": "Salary",\n            "amount": sal\.amount,\n            "description": f"Paid \{sal\.staff\.name\} \(\{sal\.staff\.role\}\)",\n            "date": sal\.payment_date\.isoformat\(\)\n        \}\)\n    finance_history\.sort\(key=lambda x: x\["date"\], reverse=True\)'
new_history = """for sal in all_salaries_records:
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
    finance_history.sort(key=lambda x: x["date"], reverse=True)"""
content = re.sub(history_pattern, new_history, content)

# 6. Update get_finances_filtered revenue
filter_rev_pattern = r'# Subscriptions\n        subs_query = select\(models\.Subscription\)\.where\(\n            models\.Subscription\.start_date >= start,\n            models\.Subscription\.start_date <= end\n        \)\n        subs = await db\.execute\(subs_query\)\n        revenue = sum\(s\.amount_paid for s in subs\.scalars\(\)\.all\(\)\)'
new_filter_rev = """# Subscriptions
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
        revenue += sum(s.amount for s in ss_filter_list)"""
content = re.sub(filter_rev_pattern, new_filter_rev, content)

# 7. Update get_finances_filtered history
filter_history_pattern = r'for sal in staff_list_filter:\n            finance_history\.append\(\{\n                "type": "Salary",\n                "amount": sal\.amount,\n                "description": f"Paid \{sal\.staff\.name\} \(\{sal\.staff\.role\}\)",\n                "date": sal\.payment_date\.isoformat\(\)\n            \}\)\n        finance_history\.sort\(key=lambda x: x\["date"\], reverse=True\)'
new_filter_history = """for sal in staff_list_filter:
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
        finance_history.sort(key=lambda x: x["date"], reverse=True)"""
content = re.sub(filter_history_pattern, new_filter_history, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated main.py successfully")
