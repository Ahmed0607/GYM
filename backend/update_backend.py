import re

filepath = 'C:/Users/DELL/Desktop/GYM/backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update process_monthly_salaries logic
new_salaries_logic = """async def process_monthly_salaries():
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
            
            await db.commit()"""

content = re.sub(r'async def process_monthly_salaries\(\):[\s\S]*?await db\.commit\(\)', new_salaries_logic, content)

# 2. Update get_dashboard to include finances
dashboard_pattern = r'# Total money owed\n    owed_query = select\(func\.sum\(models\.Subscription\.amount_owed\)\)[\s\S]*?return \{'
new_dashboard_finances = """# Total money owed
    owed_query = select(func.sum(models.Subscription.amount_owed))
    owed_result = await db.execute(owed_query)
    total_owed = owed_result.scalar() or 0
    
    # Revenue today 
    rev_query = select(func.sum(models.Subscription.amount_paid)).where(models.Subscription.start_date >= today_start)
    rev_result = await db.execute(rev_query)
    revenue_today = rev_result.scalar() or 0
    
    # All time finances for dashboard
    all_rev_query = select(func.sum(models.Subscription.amount_paid))
    all_revenue = (await db.execute(all_rev_query)).scalar() or 0
    
    all_exp = (await db.execute(select(models.Expense))).scalars().all()
    total_maintenance = sum(e.amount for e in all_exp if e.category == "Maintenance")
    total_bills = sum(e.amount for e in all_exp if e.category == "Bill")
    
    all_salaries_query = select(models.StaffPayment).options(selectinload(models.StaffPayment.staff))
    all_salaries_records = (await db.execute(all_salaries_query)).scalars().all()
    total_salaries = sum(p.amount for p in all_salaries_records)
    
    net_revenue = all_revenue - (total_maintenance + total_bills + total_salaries)
    
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
            "member_id": row.mid,
            "member_name": row.name,
            "packages": row.Subscription.package_name,
            "amount_paid": row.Subscription.amount_paid,
            "start_date": row.Subscription.start_date.isoformat() if row.Subscription.start_date else None
        }
        for row in recent_subs_rows
    ]
    
    return {"""
content = re.sub(dashboard_pattern, new_dashboard_finances, content)

# 3. Add to return object
return_pattern = r'return \{\n        "kpis": \{[\s\S]*?\},'
new_return = """return {
        "net_revenue": net_revenue,
        "total_salaries": total_salaries,
        "total_maintenance": total_maintenance,
        "total_bills": total_bills,
        "finance_history": finance_history,
        "kpis": {"""
content = re.sub(return_pattern, new_return, content)

# 4. Filter Finances Endpoint also needs to return history
filter_pattern = r'net_revenue = revenue - \(maintenance_cost \+ bills_cost \+ salaries_cost\)[\s\S]*?return \{'
new_filter = """net_revenue = revenue - (maintenance_cost + bills_cost + salaries_cost)
        
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
        finance_history.sort(key=lambda x: x["date"], reverse=True)

        return {"""
content = re.sub(filter_pattern, new_filter, content)

# update return for filter
filter_return_pattern = r'return \{\n            "revenue": revenue,\n            "net_revenue": net_revenue,\n            "total_maintenance": maintenance_cost,\n            "total_bills": bills_cost,\n            "total_salaries": salaries_cost\n        \}'
new_filter_return = """return {
            "revenue": revenue,
            "net_revenue": net_revenue,
            "total_maintenance": maintenance_cost,
            "total_bills": bills_cost,
            "total_salaries": salaries_cost,
            "finance_history": finance_history
        }"""
content = re.sub(filter_return_pattern, new_filter_return, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated backend successfully")
