import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime, timezone, timedelta
from app import create_app
from models import db
from models.user import User
from models.shopping_list import ShoppingList
from models.shopping_item import ShoppingItem
from models.shopping_history import ShoppingHistory

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_user(app):
    with app.app_context():
        test_email = f"test_{int(datetime.now(timezone.utc).timestamp())}_{os.getpid()}@example.com"
        user = User(name="Test User", email=test_email)
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        yield {'id': user_id, 'email': test_email, 'password': 'secret123', 'name': 'Test User'}
        
        u = db.session.get(User, user_id)
        if u:
            db.session.delete(u)
            db.session.commit()

def test_user_registration_and_login(client, app):
    email = f"newuser_{int(datetime.now(timezone.utc).timestamp())}_{os.getpid()}@example.com"
    # 1. Sign up
    res = client.post('/signup', data={
        'name': 'New Tester',
        'email': email,
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Your account has been created successfully" in res.data or b"Please log in" in res.data

    # 2. Login
    res_login = client.post('/login', data={
        'email': email,
        'password': 'password123'
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b"Dashboard Overview" in res_login.data

    # 3. Logout
    res_logout = client.get('/logout', follow_redirects=True)
    assert res_logout.status_code == 200
    assert b"logged out successfully" in res_logout.data

    # Cleanup
    with app.app_context():
        u = User.query.filter_by(email=email).first()
        if u:
            db.session.delete(u)
            db.session.commit()

def test_password_reset_flow(client, app):
    with app.app_context():
        email = f"reset_{int(datetime.now(timezone.utc).timestamp())}_{os.getpid()}@example.com"
        user = User(name="Reset Tester", email=email)
        user.set_password("oldpass123")
        db.session.add(user)
        db.session.commit()
        u_id = user.id

    # 1. Request reset link
    res_req = client.post('/forgot-password', data={'email': email}, follow_redirects=True)
    assert res_req.status_code == 200
    assert b"Password reset link generated" in res_req.data

    with app.app_context():
        u = db.session.get(User, u_id)
        token = u.get_reset_token()

    # 2. Perform reset
    res_reset = client.post(f'/reset-password/{token}', data={
        'password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert res_reset.status_code == 200
    assert b"Your password has been reset successfully" in res_reset.data

    # 3. Login with new password
    res_login = client.post('/login', data={
        'email': email,
        'password': 'newpassword123'
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b"Dashboard Overview" in res_login.data

    with app.app_context():
        u = db.session.get(User, u_id)
        if u:
            db.session.delete(u)
            db.session.commit()

def test_shopping_list_and_items_lifecycle(client, auth_user, app):
    # Log in
    client.post('/login', data={
        'email': auth_user['email'],
        'password': auth_user['password']
    }, follow_redirects=True)

    # 1. Create a shopping list
    res = client.post('/lists/create', data={'title': 'Monthly Grocery'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Monthly Grocery" in res.data

    with app.app_context():
        sl = ShoppingList.query.filter_by(user_id=auth_user['id'], title='Monthly Grocery').first()
        assert sl is not None
        list_id = sl.id

    # 2. Add an item to the list via Add New Item page (/items/add)
    res_add_page = client.post('/items/add', data={
        'list_id': list_id,
        'item_name': 'Brown Basmati Rice',
        'category': 'Pantry & Grains',
        'quantity': 5,
        'unit': 'kg',
        'estimated_price': 85.00,
        'notes': '5kg bag'
    }, follow_redirects=True)
    assert res_add_page.status_code == 200
    assert b"Brown Basmati Rice" in res_add_page.data

    with app.app_context():
        item = ShoppingItem.query.filter_by(list_id=list_id, item_name='Brown Basmati Rice').first()
        assert item is not None
        assert item.completed is False
        assert float(item.estimated_price) == 85.00
        item_id = item.id

    # 3. Edit item
    res_edit = client.post(f'/items/{item_id}/edit', data={
        'item_name': 'Royal Basmati Rice',
        'category': 'Pantry & Grains',
        'quantity': 5,
        'unit': 'kg',
        'estimated_price': 90.00,
        'notes': 'Premium pack'
    }, follow_redirects=True)
    assert res_edit.status_code == 200

    with app.app_context():
        item = db.session.get(ShoppingItem, item_id)
        assert item.item_name == 'Royal Basmati Rice'
        assert float(item.estimated_price) == 90.00

    # 4. Mark item as purchased
    res_purchase = client.post(f'/items/{item_id}/purchase', data={
        'actual_price': 88.00
    }, follow_redirects=True)
    assert res_purchase.status_code == 200

    with app.app_context():
        item = db.session.get(ShoppingItem, item_id)
        assert item.completed is True
        assert float(item.actual_price) == 88.00

        # Verify ShoppingHistory record
        history_record = ShoppingHistory.query.filter_by(user_id=auth_user['id'], item_name='Royal Basmati Rice').first()
        assert history_record is not None
        assert float(history_record.actual_price) == 88.00
        assert history_record.category == 'Pantry & Grains'

    # 5. Dashboard Frequently Bought quick-add test
    res_quick_add = client.post('/dashboard/quick-add', data={
        'list_id': list_id,
        'item_name': 'Royal Basmati Rice',
        'category': 'Pantry & Grains',
        'quantity': 2,
        'unit': 'kg',
        'estimated_price': 88.00
    }, follow_redirects=True)
    assert res_quick_add.status_code == 200

    with app.app_context():
        items_count = ShoppingItem.query.filter_by(list_id=list_id, item_name='Royal Basmati Rice').count()
        assert items_count >= 2

    # 6. View Expense Reports
    res_rep = client.get('/reports')
    assert res_rep.status_code == 200
    assert b"Pantry &amp; Grains" in res_rep.data or b"Pantry & Grains" in res_rep.data

    # 7. View Shopping History & Delete record
    res_hist = client.get('/history')
    assert res_hist.status_code == 200
    assert b"Royal Basmati Rice" in res_hist.data

    with app.app_context():
        hist = ShoppingHistory.query.filter_by(user_id=auth_user['id']).first()
        hist_id = hist.id
    
    res_del_hist = client.post(f'/history/{hist_id}/delete', follow_redirects=True)
    assert res_del_hist.status_code == 200
    with app.app_context():
        assert db.session.get(ShoppingHistory, hist_id) is None

    # 8. Delete Shopping List
    res_del = client.post(f'/lists/{list_id}/delete', follow_redirects=True)
    assert res_del.status_code == 200
    with app.app_context():
        assert db.session.get(ShoppingList, list_id) is None
        assert ShoppingItem.query.filter_by(list_id=list_id).count() == 0

def test_user_data_isolation(client, app):
    with app.app_context():
        u1_email = f"u1_{int(datetime.now(timezone.utc).timestamp())}_{os.getpid()}@example.com"
        u2_email = f"u2_{int(datetime.now(timezone.utc).timestamp())}_{os.getpid()}@example.com"
        u1 = User(name="User One", email=u1_email)
        u1.set_password("pass123")
        u2 = User(name="User Two", email=u2_email)
        u2.set_password("pass123")
        db.session.add_all([u1, u2])
        db.session.commit()
        u1_id = u1.id
        u2_id = u2.id

        # Create list for user 1
        l1 = ShoppingList(user_id=u1.id, title="User One Private List")
        db.session.add(l1)
        db.session.commit()
        l1_id = l1.id

    # Log in as user 2
    client.post('/login', data={'email': u2_email, 'password': 'pass123'}, follow_redirects=True)

    # User 2 tries to access user 1's list view
    res = client.get(f'/lists/{l1_id}')
    assert b"User One Private List" not in res.data

    # User 2 tries to delete user 1's list
    res_del = client.post(f'/lists/{l1_id}/delete')
    assert res_del.status_code == 404

    # Cleanup
    with app.app_context():
        user1 = db.session.get(User, u1_id)
        user2 = db.session.get(User, u2_id)
        if user1: db.session.delete(user1)
        if user2: db.session.delete(user2)
        db.session.commit()
