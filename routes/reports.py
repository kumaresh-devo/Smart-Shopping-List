from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db
from models.shopping_list import ShoppingList
from models.shopping_item import ShoppingItem
from models.shopping_history import ShoppingHistory

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def expense_reports_view():
    user_id = current_user.id
    time_filter = request.args.get('period', 'all')  # all, 30days, this_month, 7days
    list_filter = request.args.get('list_id', type=int)

    # Base query for history
    history_query = ShoppingHistory.query.filter_by(user_id=user_id)
    items_query = ShoppingItem.query.filter_by(user_id=user_id)

    # Time filtering
    now = datetime.now(timezone.utc)
    if time_filter == '7days':
        start_date = now - timedelta(days=7)
        history_query = history_query.filter(ShoppingHistory.purchase_date >= start_date)
    elif time_filter == '30days':
        start_date = now - timedelta(days=30)
        history_query = history_query.filter(ShoppingHistory.purchase_date >= start_date)
    elif time_filter == 'this_month':
        start_date = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        history_query = history_query.filter(ShoppingHistory.purchase_date >= start_date)

    if list_filter:
        history_query = history_query.filter_by(list_id=list_filter)
        items_query = items_query.filter_by(list_id=list_filter)

    history_records = history_query.all()
    all_items = items_query.all()

    # 1. Total Estimated vs Actual
    total_estimated = sum(
        float(item.estimated_price or 0.0)
        for item in all_items
    )
    total_actual = sum(
        float(h.actual_price or 0.0)
        for h in history_records
    )
    difference = total_actual - total_estimated
    diff_status = 'over' if difference > 0 else 'under'

    # 2. Category-wise Spending Breakdown from History
    cat_spending = {}
    for h in history_records:
        cat = h.category or 'Other'
        cat_spending[cat] = cat_spending.get(cat, 0.0) + float(h.actual_price or 0.0)

    category_data = [
        {'category': cat, 'amount': round(amt, 2), 'percentage': round((amt / total_actual * 100) if total_actual > 0 else 0, 1)}
        for cat, amt in sorted(cat_spending.items(), key=lambda x: x[1], reverse=True)
    ]

    # 3. Monthly Spending Timeline (last 6 months)
    monthly_data = {}
    for h in history_records:
        if h.purchase_date:
            month_key = h.purchase_date.strftime('%b %Y')
            monthly_data[month_key] = monthly_data.get(month_key, 0.0) + float(h.actual_price or 0.0)

    user_lists = ShoppingList.query.filter_by(user_id=user_id).order_by(ShoppingList.title.asc()).all()

    return render_template(
        'expense_reports.html',
        total_estimated=round(total_estimated, 2),
        total_actual=round(total_actual, 2),
        difference=round(abs(difference), 2),
        diff_status=diff_status,
        raw_difference=round(difference, 2),
        category_data=category_data,
        monthly_data=monthly_data,
        total_purchases_count=len(history_records),
        user_lists=user_lists,
        current_period=time_filter,
        current_list_id=list_filter
    )
