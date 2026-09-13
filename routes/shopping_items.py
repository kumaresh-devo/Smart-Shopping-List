from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.shopping_list import ShoppingList
from models.shopping_item import ShoppingItem

shopping_items_bp = Blueprint('shopping_items', __name__)

STANDARD_CATEGORIES = [
    'Produce & Fruits', 'Dairy & Eggs', 'Bakery', 'Pantry & Grains',
    'Meat & Seafood', 'Beverages', 'Snacks', 'Household & Cleaning',
    'Personal Care', 'Medical & Health', 'Masala', 'Other'
]

STANDARD_UNITS = [
    'pcs', 'kg', 'g', 'l', 'ml', 'pack', 'box', 'bottle', 'can', 'bag', 'dozen'
]

@shopping_items_bp.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item_page():
    user_lists = ShoppingList.query.filter_by(
        user_id=current_user.id
    ).order_by(ShoppingList.updated_at.desc()).all()

    preselected_list_id = request.args.get('list_id', type=int)

    if request.method == 'POST':
        list_id = request.form.get('list_id', type=int)
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip() or 'Other'
        quantity = request.form.get('quantity', 1.0, type=float)
        unit = request.form.get('unit', 'pcs').strip() or 'pcs'
        estimated_price = request.form.get('estimated_price', 0.0, type=float)
        notes = request.form.get('notes', '').strip()

        # Validation
        if not list_id:
            flash('Please select a target shopping list.', 'warning')
            return render_template(
                'add_item.html',
                user_lists=user_lists,
                categories=STANDARD_CATEGORIES,
                units=STANDARD_UNITS,
                selected_list_id=list_id,
                item_name=item_name,
                category=category,
                quantity=quantity,
                unit=unit,
                estimated_price=estimated_price,
                notes=notes
            )

        target_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user.id).first()
        if not target_list:
            flash('Selected shopping list does not exist.', 'danger')
            return redirect(url_for('shopping_items.add_item_page'))

        if not item_name:
            flash('Item name is required.', 'warning')
            return render_template(
                'add_item.html',
                user_lists=user_lists,
                categories=STANDARD_CATEGORIES,
                units=STANDARD_UNITS,
                selected_list_id=list_id,
                item_name=item_name,
                category=category,
                quantity=quantity,
                unit=unit,
                estimated_price=estimated_price,
                notes=notes
            )

        if quantity <= 0:
            quantity = 1.0
        if estimated_price < 0:
            estimated_price = 0.0

        new_item = ShoppingItem(
            list_id=target_list.id,
            user_id=current_user.id,
            item_name=item_name,
            category=category,
            quantity=quantity,
            unit=unit,
            estimated_price=estimated_price,
            notes=notes,
            completed=False
        )

        target_list.updated_at = datetime.now(timezone.utc)
        db.session.add(new_item)
        db.session.commit()

        return render_template(
            'add_item.html',
            user_lists=user_lists,
            categories=STANDARD_CATEGORIES,
            units=STANDARD_UNITS,
            selected_list_id=target_list.id,
            item_name='',
            success_item_name=item_name,
            success_list_name=target_list.title,
            success_list_id=target_list.id
        )

    return render_template(
        'add_item.html',
        user_lists=user_lists,
        categories=STANDARD_CATEGORIES,
        units=STANDARD_UNITS,
        selected_list_id=preselected_list_id
    )
