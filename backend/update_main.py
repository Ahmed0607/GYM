with open('C:/Users/DELL/Desktop/GYM/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix scheduler
content = content.replace("scheduler.add_job(mark_expired_members, 'interval', minutes=1)", "scheduler.add_job(mark_expired_members, 'interval', minutes=1)\n    scheduler.add_job(process_monthly_salaries, 'interval', days=1)")

# Fix get_dashboard
old_dashboard = """    today_subs = await db.execute(select(models.Subscription).where(models.Subscription.start_date >= today_start))
    today_revenue = sum(s.amount_paid for s in today_subs.scalars().all())

    all_subs = await db.execute(select(models.Subscription))
    all_revenue = sum(s.amount_paid for s in all_subs.scalars().all())

    return {
        "active_members": active_members,
        "members_owed": members_owed,
        "today_checkins": today_checkins,
        "current_active": current_active,
        "today_revenue": today_revenue,
        "total_revenue": all_revenue,
    }"""

new_dashboard = """    today_subs = await db.execute(select(models.Subscription).where(models.Subscription.start_date >= today_start))
    today_revenue = sum(s.amount_paid for s in today_subs.scalars().all())

    all_subs = await db.execute(select(models.Subscription))
    all_revenue = sum(s.amount_paid for s in all_subs.scalars().all())
    
    # Finance calculations
    all_expenses = await db.execute(select(models.Expense))
    expenses_list = all_expenses.scalars().all()
    maintenance_cost = sum(e.amount for e in expenses_list if e.category == "Maintenance")
    bills_cost = sum(e.amount for e in expenses_list if e.category == "Bill")
    
    all_staff_payments = await db.execute(select(models.StaffPayment))
    salaries_cost = sum(p.amount for p in all_staff_payments.scalars().all())
    
    net_revenue = all_revenue - (maintenance_cost + bills_cost + salaries_cost)

    return {
        "active_members": active_members,
        "members_owed": members_owed,
        "today_checkins": today_checkins,
        "current_active": current_active,
        "today_revenue": today_revenue,
        "net_revenue": net_revenue,
        "total_maintenance": maintenance_cost,
        "total_bills": bills_cost,
        "total_salaries": salaries_cost
    }"""
content = content.replace(old_dashboard, new_dashboard)

with open('C:/Users/DELL/Desktop/GYM/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
