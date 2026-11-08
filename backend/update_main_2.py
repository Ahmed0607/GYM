import re

filepath = 'C:/Users/DELL/Desktop/GYM/backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update process_monthly_salaries logic to use pay_day
new_salaries_logic = """async def process_monthly_salaries():
    async with engine.begin() as conn:
        from database import SessionLocal
        async with SessionLocal() as db:
            now = get_current_time()
            query = select(models.Staff)
            result = await db.execute(query)
            staff_members = result.scalars().all()
            
            for staff in staff_members:
                # If current day is >= pay_day and we haven't paid this month yet
                last_paid = staff.last_paid_date.replace(tzinfo=timezone.utc) if staff.last_paid_date.tzinfo is None else staff.last_paid_date
                
                # Check if we should pay today:
                # 1. We are at or past the pay_day in the current month
                # 2. We haven't paid them this exact month & year yet
                should_pay = False
                if now.day >= staff.pay_day:
                    if last_paid.month != now.month or last_paid.year != now.year:
                        should_pay = True
                else:
                    # If current day is < pay_day, we should have paid them last month.
                    # This handles if the script was offline on the 1st, and today is the 2nd, etc.
                    pass
                
                # simplified robust logic: if today >= pay_day and we haven't paid this month, pay them.
                if now.day >= staff.pay_day and (last_paid.year < now.year or (last_paid.year == now.year and last_paid.month < now.month)):
                    should_pay = True

                if should_pay:
                    amount_to_pay = max(0.0, staff.base_salary + staff.pending_bonus - staff.pending_deduction)
                    
                    # Create payment record
                    payment = models.StaffPayment(
                        staff_id=staff.id,
                        amount=amount_to_pay,
                        bonus=staff.pending_bonus,
                        deduction=staff.pending_deduction,
                        payment_date=now
                    )
                    db.add(payment)
                    
                    # Reset pending bonus/deduction and update last_paid_date
                    staff.pending_bonus = 0
                    staff.pending_deduction = 0
                    staff.last_paid_date = now
            
            await db.commit()"""

# Replace old process_monthly_salaries
content = re.sub(r'async def process_monthly_salaries\(\):[\s\S]*?await db\.commit\(\)', new_salaries_logic, content)

# 2. Add /admin/finances/filter endpoint
new_endpoint = """
@app.get("/admin/finances/filter")
async def get_finances_filtered(start_date: str, end_date: str, db: AsyncSession = Depends(get_db)):
    try:
        from dateutil.parser import parse
        start = parse(start_date).replace(tzinfo=timezone.utc) if parse(start_date).tzinfo is None else parse(start_date)
        # For end date, we want to include the whole day, so we might want to push it to the end of the day if time isn't provided
        end = parse(end_date).replace(tzinfo=timezone.utc) if parse(end_date).tzinfo is None else parse(end_date)
        
        # Subscriptions
        subs_query = select(models.Subscription).where(
            models.Subscription.start_date >= start,
            models.Subscription.start_date <= end
        )
        subs = await db.execute(subs_query)
        revenue = sum(s.amount_paid for s in subs.scalars().all())
        
        # Expenses
        exp_query = select(models.Expense).where(
            models.Expense.date >= start,
            models.Expense.date <= end
        )
        expenses_list = (await db.execute(exp_query)).scalars().all()
        maintenance_cost = sum(e.amount for e in expenses_list if e.category == "Maintenance")
        bills_cost = sum(e.amount for e in expenses_list if e.category == "Bill")
        
        # Salaries
        staff_query = select(models.StaffPayment).where(
            models.StaffPayment.payment_date >= start,
            models.StaffPayment.payment_date <= end
        )
        staff_list = (await db.execute(staff_query)).scalars().all()
        salaries_cost = sum(p.amount for p in staff_list)
        
        net_revenue = revenue - (maintenance_cost + bills_cost + salaries_cost)
        
        return {
            "revenue": revenue,
            "net_revenue": net_revenue,
            "total_maintenance": maintenance_cost,
            "total_bills": bills_cost,
            "total_salaries": salaries_cost
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
"""

content = content + new_endpoint

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated main.py successfully")
