import re
import pymysql
from config import Config

def parse_qty_unit(val):
    if not val:
        return 1.0, 'pcs'
    val = str(val).strip()
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)', val)
    qty = float(match.group(1)) if match else 1.0
    
    val_lower = val.lower()
    if 'packet' in val_lower or 'pack' in val_lower:
        unit = 'pack'
    elif 'ltr' in val_lower or 'liter' in val_lower or ' l' in val_lower:
        unit = 'l'
    elif 'kg' in val_lower or 'kilo' in val_lower:
        unit = 'kg'
    elif ' g' in val_lower or 'gram' in val_lower:
        unit = 'g'
    elif 'ml' in val_lower:
        unit = 'ml'
    elif 'box' in val_lower:
        unit = 'box'
    elif 'bottle' in val_lower:
        unit = 'bottle'
    else:
        unit = 'pcs'
    return qty, unit

def upgrade_schema():
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=int(Config.MYSQL_PORT),
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    with conn.cursor() as cur:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # 1. users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # 2. shopping_lists table
        cur.execute("SHOW COLUMNS FROM `shopping_lists` LIKE 'name';")
        has_name = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM `shopping_lists` LIKE 'title';")
        has_title = cur.fetchone()
        
        if has_name and not has_title:
            print("Renaming shopping_lists.name to title...")
            cur.execute("ALTER TABLE `shopping_lists` CHANGE COLUMN `name` `title` VARCHAR(150) NOT NULL;")

        cur.execute("SHOW COLUMNS FROM `shopping_lists` LIKE 'updated_at';")
        if not cur.fetchone():
            print("Adding shopping_lists.updated_at...")
            cur.execute("ALTER TABLE `shopping_lists` ADD COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;")

        # 3. shopping_items table
        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'name';")
        has_item_name_old = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'item_name';")
        has_item_name_new = cur.fetchone()

        if has_item_name_old and not has_item_name_new:
            print("Renaming shopping_items.name to item_name...")
            cur.execute("ALTER TABLE `shopping_items` CHANGE COLUMN `name` `item_name` VARCHAR(150) NOT NULL;")

        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'user_id';")
        if not cur.fetchone():
            print("Adding shopping_items.user_id...")
            cur.execute("ALTER TABLE `shopping_items` ADD COLUMN `user_id` INT NOT NULL DEFAULT 1 AFTER `list_id`;")
            cur.execute("UPDATE `shopping_items` si JOIN `shopping_lists` sl ON si.list_id = sl.id SET si.user_id = sl.user_id;")

        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'category';")
        if not cur.fetchone():
            print("Adding shopping_items.category...")
            cur.execute("ALTER TABLE `shopping_items` ADD COLUMN `category` VARCHAR(100) NOT NULL DEFAULT 'Other' AFTER `item_name`;")

        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'unit';")
        if not cur.fetchone():
            print("Adding shopping_items.unit...")
            cur.execute("ALTER TABLE `shopping_items` ADD COLUMN `unit` VARCHAR(50) NOT NULL DEFAULT 'pcs' AFTER `quantity`;")

        # Clean existing quantity text data
        cur.execute("SELECT id, quantity FROM `shopping_items`;")
        rows = cur.fetchall()
        for r_id, r_qty in rows:
            clean_qty, clean_unit = parse_qty_unit(r_qty)
            cur.execute("UPDATE `shopping_items` SET `quantity` = %s, `unit` = %s WHERE id = %s;", (str(clean_qty), clean_unit, r_id))

        cur.execute("ALTER TABLE `shopping_items` MODIFY COLUMN `quantity` FLOAT NOT NULL DEFAULT 1.0;")

        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'actual_price';")
        if not cur.fetchone():
            print("Adding shopping_items.actual_price...")
            cur.execute("ALTER TABLE `shopping_items` ADD COLUMN `actual_price` DECIMAL(10, 2) NULL AFTER `estimated_price`;")

        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'notes';")
        if not cur.fetchone():
            print("Adding shopping_items.notes...")
            cur.execute("ALTER TABLE `shopping_items` ADD COLUMN `notes` TEXT NULL AFTER `actual_price`;")

        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'is_completed';")
        has_is_completed = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'completed';")
        has_completed = cur.fetchone()

        if has_is_completed and not has_completed:
            print("Renaming shopping_items.is_completed to completed...")
            cur.execute("ALTER TABLE `shopping_items` CHANGE COLUMN `is_completed` `completed` TINYINT(1) NOT NULL DEFAULT 0;")

        cur.execute("SHOW COLUMNS FROM `shopping_items` LIKE 'updated_at';")
        if not cur.fetchone():
            print("Adding shopping_items.updated_at...")
            cur.execute("ALTER TABLE `shopping_items` ADD COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;")

        # 4. shopping_history table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shopping_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                list_id INT NULL,
                item_name VARCHAR(150) NOT NULL,
                category VARCHAR(100) NOT NULL,
                quantity FLOAT NOT NULL DEFAULT 1.0,
                actual_price DECIMAL(10, 2) NOT NULL,
                purchase_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_list_id (list_id),
                INDEX idx_purchase_date (purchase_date),
                CONSTRAINT fk_history_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_history_list FOREIGN KEY (list_id) REFERENCES shopping_lists(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # Clean unused tables
        for old_tbl in ['budgets', 'expenses']:
            cur.execute(f"DROP TABLE IF EXISTS `{old_tbl}`;")

        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("Schema successfully aligned with exact specification!")

    conn.close()

if __name__ == '__main__':
    upgrade_schema()
