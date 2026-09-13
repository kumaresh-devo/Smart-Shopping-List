# Smart Shopping List – Full-Stack Web Application

A modern, clean, and full-featured Smart Shopping List web application built using **Python Flask**, **Flask-SQLAlchemy**, **Flask-Login**, and **MySQL**, styled with an emerald **green and white theme** (HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons, Chart.js).

---

## 🚀 Key Features & Pages

### Exactly 5 Main Application Pages:
1. **Dashboard (`/` or `/dashboard`)**:
   - Real-time statistics: Total Shopping Lists, Total Items, Pending Items, Completed Items, Estimated Expense, Actual Expense.
   - **Frequently Bought Items** section: Automatically computed from purchase history with instant **Quick Add** into any shopping list.
   - Active Shopping Lists progress overview and Recent Purchases feed.

2. **My Shopping List (`/lists`)**:
   - Multiple separate shopping lists (e.g. *Monthly Grocery*, *Medical Essentials*, *Home Improvement*).
   - Create, rename, and delete shopping lists.
   - Inside each list: Add items, edit items, delete items.
   - **Purchase flow**: Mark as purchased & enter the **Actual Price** paid, which immediately logs into Shopping History.
   - Live real-time search, category filter, and status filter (All, Pending, Completed).

3. **Add New Item (`/items/add`)**:
   - Form to add items to any chosen shopping list.
   - Fields: Shopping List, Item Name, Category, Quantity, Unit, Estimated Price, Notes.
   - Non-negative validation and sensible defaults.

4. **Expense Reports (`/reports`)**:
   - Total Estimated Expense vs Total Actual Expense vs Difference (Savings/Overspent badge).
   - Category-wise Spending Breakdown with interactive **Chart.js Donut Chart** and summary table.
   - Monthly Spending Timeline with **Chart.js Bar Chart**.
   - Period filtering (All Time, This Month, Last 30 Days, Last 7 Days) and list filtering.

5. **Shopping History (`/history`)**:
   - Records created automatically when items are marked purchased with actual prices.
   - Displays Item Name, Shopping List Title, Category, Quantity, Actual Price, Total Cost, Purchase Date.
   - Search by item name, filter by category, date range (From / To), and shopping list.
   - Delete history record with interactive confirmation modal.

### Dedicated Authentication Pages:
- **Login (`/login`)**: Email & password authentication with "Remember Me" option.
- **Sign Up (`/signup`)**: Full name, email, and password registration with secure Werkzeug hashing.
- **Forgot Password (`/forgot-password`)**: Generates timed URL-safe tokens using `itsdangerous`.
- **Reset Password (`/reset-password/<token>`)**: Validates token and resets account password.
- **Logout (`/logout`)**: Clears user session.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Chart.js 4.4.4.
- **Backend**: Python 3.13, Flask 3.1.0, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3, itsdangerous, Werkzeug.
- **Database**: MySQL 8.0 with PyMySQL driver and SQLAlchemy ORM.
- **Security**: Strong password hashing (`generate_password_hash`), CSRF/SQL injection protection via ORM parameterization, strict multi-tenant data isolation by `user_id`.

---

## 🗄️ Database Schema

### 1. `users`
- `id` (INT, PK, AUTO_INCREMENT)
- `name` (VARCHAR(150), NOT NULL)
- `email` (VARCHAR(150), UNIQUE, NOT NULL, INDEX)
- `password_hash` (VARCHAR(255), NOT NULL)
- `created_at` (DATETIME, NOT NULL)

### 2. `shopping_lists`
- `id` (INT, PK, AUTO_INCREMENT)
- `user_id` (INT, FK -> `users.id` ON DELETE CASCADE)
- `title` (VARCHAR(150), NOT NULL)
- `created_at` (DATETIME, NOT NULL)
- `updated_at` (DATETIME, NOT NULL)

### 3. `shopping_items`
- `id` (INT, PK, AUTO_INCREMENT)
- `list_id` (INT, FK -> `shopping_lists.id` ON DELETE CASCADE)
- `user_id` (INT, FK -> `users.id` ON DELETE CASCADE)
- `item_name` (VARCHAR(150), NOT NULL)
- `category` (VARCHAR(100), NOT NULL)
- `quantity` (FLOAT, NOT NULL, DEFAULT 1.0)
- `unit` (VARCHAR(50), NOT NULL, DEFAULT 'pcs')
- `estimated_price` (DECIMAL(10, 2), NOT NULL, DEFAULT 0.00)
- `actual_price` (DECIMAL(10, 2), NULL)
- `notes` (TEXT, NULL)
- `completed` (BOOLEAN, NOT NULL, DEFAULT FALSE)
- `created_at` (DATETIME, NOT NULL)
- `updated_at` (DATETIME, NOT NULL)

### 4. `shopping_history`
- `id` (INT, PK, AUTO_INCREMENT)
- `user_id` (INT, FK -> `users.id` ON DELETE CASCADE)
- `list_id` (INT, FK -> `shopping_lists.id` ON DELETE SET NULL, NULL)
- `item_name` (VARCHAR(150), NOT NULL)
- `category` (VARCHAR(100), NOT NULL)
- `quantity` (FLOAT, NOT NULL, DEFAULT 1.0)
- `actual_price` (DECIMAL(10, 2), NOT NULL)
- `purchase_date` (DATETIME, NOT NULL, INDEX)

---

## ⚙️ Installation & Setup Instructions

### 1. Prerequisites
- Python 3.10+
- MySQL Server 8.0+ running on `localhost:3306`

### 2. Install Dependencies
```bash
cd C:\Users\R.Kumaresh\.gemini\antigravity\scratch\smart_shopping_list
python -m pip install -r requirements.txt
```

### 3. Configure `.env`
Ensure `.env` contains your MySQL credentials:
```env
SECRET_KEY=smart-shopping-list-super-secret-key-2026
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=kumaresh@23
MYSQL_DB=smart_shopping_list
```

### 4. Initialize the Database
Run the database creation script:
```bash
python init_db.py
```

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests
Run the test suite with pytest:
```bash
python -m pytest tests/test_app.py -v
```
All tests verify authentication, user data isolation, list/item lifecycle, purchase logging to history, and expense computations.
