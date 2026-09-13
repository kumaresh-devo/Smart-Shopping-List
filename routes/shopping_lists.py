from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.shopping_list import ShoppingList
from models.shopping_item import ShoppingItem
from models.shopping_history import ShoppingHistory

shopping_lists_bp = Blueprint('shopping_lists', __name__)

STANDARD_CATEGORIES = [
    'Produce & Fruits', 'Dairy & Eggs', 'Bakery', 'Pantry & Grains',
    'Meat & Seafood', 'Beverages', 'Snacks', 'Household & Cleaning',
    'Personal Care', 'Medical & Health', 'Masala', 'Other'
]

STANDARD_UNITS = [
    'pcs', 'kg', 'g', 'l', 'ml', 'pack', 'box', 'bottle', 'can', 'bag', 'dozen'
]

@shopping_lists_bp.route('/lists')
@shopping_lists_bp.route('/lists/<int:list_id>')
@login_required
def view_list(list_id=None):
    all_lists = ShoppingList.query.filter_by(
        user_id=current_user.id
    ).order_by(ShoppingList.updated_at.desc()).all()

    active_list = None
    if list_id:
        active_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user.id).first()
        if not active_list:
            flash('Selected shopping list not found.', 'warning')
            if all_lists:
                return redirect(url_for('shopping_lists.view_list', list_id=all_lists[0].id))
            return redirect(url_for('shopping_lists.view_list'))
    elif all_lists:
        active_list = all_lists[0]

    items = []
    category_list = []
    if active_list:
        items = active_list.items.order_by(ShoppingItem.completed.asc(), ShoppingItem.created_at.desc()).all()
        # Collect unique categories present in this list
        category_list = sorted(list(set(item.category for item in items)))

    return render_template(
        'shopping_list.html',
        all_lists=all_lists,
        active_list=active_list,
        items=items,
        category_list=category_list,
        standard_categories=STANDARD_CATEGORIES,
        standard_units=STANDARD_UNITS
    )

@shopping_lists_bp.route('/lists/create', methods=['POST'])
@login_required
def create_list():
    title = request.form.get('title', '').strip()
    if not title:
        flash('List name cannot be empty.', 'warning')
        return redirect(url_for('shopping_lists.view_list'))

    new_list = ShoppingList(user_id=current_user.id, title=title)
    db.session.add(new_list)
    db.session.commit()

    flash(f"Shopping list '{title}' created successfully!", 'success')
    return redirect(url_for('shopping_lists.view_list', list_id=new_list.id))

@shopping_lists_bp.route('/lists/<int:list_id>/edit', methods=['POST'])
@login_required
def edit_list(list_id):
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    title = request.form.get('title', '').strip()

    if not title:
        flash('List name cannot be empty.', 'warning')
        return redirect(url_for('shopping_lists.view_list', list_id=list_id))

    old_title = shopping_list.title
    shopping_list.title = title
    shopping_list.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    flash(f"Shopping list renamed from '{old_title}' to '{title}'.", 'success')
    return redirect(url_for('shopping_lists.view_list', list_id=list_id))

@shopping_lists_bp.route('/lists/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_list(list_id):
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    title = shopping_list.title

    db.session.delete(shopping_list)
    db.session.commit()

    flash(f"Shopping list '{title}' and all its items have been deleted.", 'info')
    return redirect(url_for('shopping_lists.view_list'))

@shopping_lists_bp.route('/lists/<int:list_id>/items/add', methods=['POST'])
@login_required
def add_item_to_list(list_id):
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()

    item_name = request.form.get('item_name', '').strip()
    category = request.form.get('category', '').strip() or 'Other'
    quantity = request.form.get('quantity', 1.0, type=float)
    unit = request.form.get('unit', 'pcs').strip() or 'pcs'
    estimated_price = request.form.get('estimated_price', 0.0, type=float)
    notes = request.form.get('notes', '').strip()

    if not item_name:
        flash('Item name is required.', 'warning')
        return redirect(url_for('shopping_lists.view_list', list_id=list_id))

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
        notes=notes,
        completed=False
    )

    shopping_list.updated_at = datetime.now(timezone.utc)
    db.session.add(new_item)
    db.session.commit()

    flash(f"Item '{item_name}' added to '{shopping_list.title}'.", 'success')
    return redirect(url_for('shopping_lists.view_list', list_id=list_id))

@shopping_lists_bp.route('/items/<int:item_id>/edit', methods=['POST'])
@login_required
def edit_item(item_id):
    item = ShoppingItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()

    item_name = request.form.get('item_name', '').strip()
    category = request.form.get('category', '').strip() or 'Other'
    quantity = request.form.get('quantity', 1.0, type=float)
    unit = request.form.get('unit', 'pcs').strip() or 'pcs'
    estimated_price = request.form.get('estimated_price', 0.0, type=float)
    notes = request.form.get('notes', '').strip()

    if not item_name:
        flash('Item name cannot be empty.', 'warning')
        return redirect(url_for('shopping_lists.view_list', list_id=item.list_id))

    if quantity <= 0:
        quantity = 1.0
    if estimated_price < 0:
        estimated_price = 0.0

    item.item_name = item_name
    item.category = category
    item.quantity = quantity
    item.unit = unit
    item.estimated_price = estimated_price
    item.notes = notes
    item.updated_at = datetime.now(timezone.utc)
    if item.shopping_list:
        item.shopping_list.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    flash(f"Item '{item.item_name}' updated successfully.", 'success')
    return redirect(url_for('shopping_lists.view_list', list_id=item.list_id))

@shopping_lists_bp.route('/items/<int:item_id>/purchase', methods=['POST'])
@login_required
def mark_purchased(item_id):
    item = ShoppingItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    actual_price = request.form.get('actual_price', type=float)

    if actual_price is None or actual_price < 0:
        flash('Please enter a valid non-negative actual price.', 'warning')
        return redirect(url_for('shopping_lists.view_list', list_id=item.list_id))

    item.completed = True
    item.actual_price = actual_price
    item.updated_at = datetime.now(timezone.utc)
    if item.shopping_list:
        item.shopping_list.updated_at = datetime.now(timezone.utc)

    # Automatically record in Shopping History!
    history_entry = ShoppingHistory(
        user_id=current_user.id,
        list_id=item.list_id,
        item_name=item.item_name,
        category=item.category,
        quantity=item.quantity,
        actual_price=actual_price,
        purchase_date=datetime.now(timezone.utc)
    )
    db.session.add(history_entry)
    db.session.commit()

    flash(f"'{item.item_name}' marked as purchased (Actual Price: ₹{actual_price:.2f}) and recorded in Shopping History!", 'success')
    return redirect(url_for('shopping_lists.view_list', list_id=item.list_id))

@shopping_lists_bp.route('/items/<int:item_id>/toggle-status', methods=['POST'])
@login_required
def toggle_item_status(item_id):
    item = ShoppingItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    item.completed = not item.completed
    if not item.completed:
        item.actual_price = None
    item.updated_at = datetime.now(timezone.utc)
    if item.shopping_list:
        item.shopping_list.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    status_text = 'completed' if item.completed else 'pending'
    flash(f"Item '{item.item_name}' marked as {status_text}.", 'info')
    return redirect(url_for('shopping_lists.view_list', list_id=item.list_id))

@shopping_lists_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = ShoppingItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    list_id = item.list_id
    item_name = item.item_name

    db.session.delete(item)
    db.session.commit()

    flash(f"Item '{item_name}' deleted.", 'info')
    return redirect(url_for('shopping_lists.view_list', list_id=list_id))
