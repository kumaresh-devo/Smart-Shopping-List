from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.shopping_history import ShoppingHistory
from models.shopping_list import ShoppingList

history_bp = Blueprint('history', __name__)

STANDARD_CATEGORIES = [
    'Produce & Fruits', 'Dairy & Eggs', 'Bakery', 'Pantry & Grains',
    'Meat & Seafood', 'Beverages', 'Snacks', 'Household & Cleaning',
    'Personal Care', 'Medical & Health', 'Masala', 'Other'
]

@history_bp.route('/history')
@login_required
def shopping_history_view():
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()
    list_id = request.args.get('list_id', type=int)

    query = ShoppingHistory.query.filter_by(user_id=current_user.id)

    # Filter: Search keyword
    if search_query:
        query = query.filter(ShoppingHistory.item_name.ilike(f'%{search_query}%'))

    # Filter: Category
    if category_filter:
        query = query.filter(ShoppingHistory.category == category_filter)

    # Filter: Shopping List
    if list_id:
        query = query.filter(ShoppingHistory.list_id == list_id)

    # Filter: Date range
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(ShoppingHistory.purchase_date >= start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            # include the whole end day
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(ShoppingHistory.purchase_date <= end_date)
        except ValueError:
            pass

    history_records = query.order_by(ShoppingHistory.purchase_date.desc()).all()

    total_spent = sum(
        float(r.actual_price or 0.0)
        for r in history_records
    )

    user_lists = ShoppingList.query.filter_by(user_id=current_user.id).order_by(ShoppingList.title.asc()).all()

    return render_template(
        'shopping_history.html',
        records=history_records,
        total_spent=round(total_spent, 2),
        total_count=len(history_records),
        categories=STANDARD_CATEGORIES,
        user_lists=user_lists,
        search_query=search_query,
        category_filter=category_filter,
        start_date=start_date_str,
        end_date=end_date_str,
        selected_list_id=list_id
    )

@history_bp.route('/history/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_history_record(record_id):
    record = ShoppingHistory.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
    item_name = record.item_name

    db.session.delete(record)
    db.session.commit()

    flash(f"Purchase history record for '{item_name}' was deleted successfully.", 'info')
    return redirect(url_for('history.shopping_history_view'))
