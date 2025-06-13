import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_date TEXT,
                is_blocked INTEGER DEFAULT 0,
                last_activity TEXT
            )
        ''')
        
        # Admins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                added_by INTEGER,
                added_date TEXT
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                name TEXT,
                features TEXT,
                price TEXT,
                description TEXT,
                created_date TEXT
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_name TEXT,
                amount TEXT,
                status TEXT,
                order_date TEXT,
                screenshot_file_id TEXT
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = None):
        """Add or update user information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, joined_date, last_activity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, 
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def update_user_activity(self, user_id: int):
        """Update user's last activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET last_activity = ? WHERE user_id = ?
        ''', (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
    
    def add_admin(self, user_id: int, username: str, added_by: int):
        """Add admin user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO admins (user_id, username, added_by, added_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, added_by, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def remove_admin(self, user_id: int):
        """Remove admin user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, first_name, last_name, joined_date, last_activity
            FROM users WHERE is_blocked = 0
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'joined_date': row[4],
                'last_activity': row[5]
            })
        
        conn.close()
        return users
    
    def add_product(self, category: str, name: str, features: str, price: str, description: str):
        """Add new product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (category, name, features, price, description, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (category, name, features, price, description, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get products by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, features, price, description FROM products WHERE category = ?
        ''', (category,))
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'id': row[0],
                'name': row[1],
                'features': row[2],
                'price': row[3],
                'description': row[4]
            })
        
        conn.close()
        return products
    
    def get_all_products(self) -> List[Dict]:
        """Get all products"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, category, name, features, price, description FROM products
        ''')
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'id': row[0],
                'category': row[1],
                'name': row[2],
                'features': row[3],
                'price': row[4],
                'description': row[5]
            })
        
        conn.close()
        return products
    
    def delete_product(self, product_id: int):
        """Delete product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        
        conn.commit()
        conn.close()
    
    def add_order(self, user_id: int, product_name: str, amount: str, screenshot_file_id: str = None):
        """Add new order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (user_id, product_name, amount, status, order_date, screenshot_file_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, product_name, amount, 'pending', datetime.now().isoformat(), screenshot_file_id))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Get setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else default
    
    def set_setting(self, key: str, value: str):
        """Set setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_user_count(self) -> int:
        """Get total user count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_blocked = 0')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
