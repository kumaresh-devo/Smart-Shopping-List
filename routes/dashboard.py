from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from models import db
from models.shopping_list import ShoppingList
from models.shopping_item import ShoppingItem
from models.shopping_history import ShoppingHistory

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard_view():
    # 1. Total Shopping Lists
    total_lists = ShoppingList.query.filter_by(user_id=current_user.id).count()

    # 2. Items counts
    items = ShoppingItem.query.filter_by(user_id=current_user.id).all()
    total_items = len(items)
    pending_items = sum(1 for item in items if not item.completed)
    completed_items = sum(1 for item in items if item.completed)

    # 3. Estimated Expense (Sum of estimated_price across all items)
    estimated_expense = sum(
        float(item.estimated_price or 0.0)
        for item in items
    )

    # 4. Actual Expense (Sum of actual_price from ShoppingHistory)
    history_records = ShoppingHistory.query.filter_by(user_id=current_user.id).all()
    actual_expense = sum(
        float(h.actual_price or 0.0)
        for h in history_records
    )

    # 5. Frequently Bought Items (Grouped by item_name and category from ShoppingHistory)
    # Query: Count occurrences, avg price, last purchase date
    frequent_query = db.session.query(
        ShoppingHistory.item_name,
        ShoppingHistory.category,
        func.count(ShoppingHistory.id).label('purchase_count'),
        func.avg(ShoppingHistory.actual_price).label('avg_price'),
        func.max(ShoppingHistory.purchase_date).label('last_purchased')
    ).filter(
        ShoppingHistory.user_id == current_user.id
    ).group_by(
        ShoppingHistory.item_name,
        ShoppingHistory.category
    ).order_by(
        desc('purchase_count'),
        desc('last_purchased')
    ).limit(8).all()

    frequently_bought = []
    for item in frequent_query:
        frequently_bought.append({
            'item_name': item.item_name,
            'category': item.category,
            'purchase_count': item.purchase_count,
            'avg_price': round(float(item.avg_price or 0.0), 2),
            'last_purchased': item.last_purchased.strftime('%b %d, %Y') if item.last_purchased else 'N/A'
        })

    # 6. User's active shopping lists (for quick display and quick-add modal)
    user_lists = ShoppingList.query.filter_by(user_id=current_user.id).order_by(ShoppingList.updated_at.desc()).all()

    # 7. Recent 5 Purchases from history
    recent_purchases = ShoppingHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ShoppingHistory.purchase_date.desc()
    ).limit(5).all()

    return render_template(
        'dashboard.html',
        total_lists=total_lists,
        total_items=total_items,
        pending_items=pending_items,
        completed_items=completed_items,
        estimated_expense=round(estimated_expense, 2),
        actual_expense=round(actual_expense, 2),
        frequently_bought=frequently_bought,
        user_lists=user_lists,
        recent_purchases=recent_purchases
    )

@dashboard_bp.route('/dashboard/quick-add', methods=['POST'])
@login_required
def quick_add_frequent():
    list_id = request.form.get('list_id', type=int)
    item_name = request.form.get('item_name', '').strip()
    category = request.form.get('category', '').strip() or 'Other'
    quantity = request.form.get('quantity', 1.0, type=float)
    unit = request.form.get('unit', 'pcs').strip() or 'pcs'
    estimated_price = request.form.get('estimated_price', 0.0, type=float)

    if not list_id or not item_name:
        flash('Please select a valid shopping list and item.', 'warning')
        return redirect(url_for('dashboard.dashboard_view'))

    # Verify list ownership
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user.id).first()
    if not shopping_list:
        flash('Target shopping list not found.', 'danger')
        return redirect(url_for('dashboard.dashboard_view'))

    if quantity <= 0:
        quantity = 1.0
    if estimated_price < 0:
        estimated_price = 0.0

    new_item = ShoppingItem(
        list_id=shopping_list.id,
        user_id=current_user.id,
        item_name=item_name,
        category=category,
        quantity=quantity,
        unit=unit,
        estimated_price=estimated_price,
        completed=False
    )

    db.session.add(new_item)
    db.session.commit()

    flash(f"'{item_name}' was quickly added to list '{shopping_list.title}'!", 'success')
    return redirect(url_for('shopping_lists.view_list', list_id=shopping_list.id))
