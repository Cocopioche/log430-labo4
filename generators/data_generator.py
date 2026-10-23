"""
Data generator for load testing
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import random
import json
import os
from datetime import datetime, timedelta

# Dataset size and location configurations
NUM_USERS = 1000
NUM_PRODUCTS = 10_000
NUM_ORDERS = 80_000
MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 5
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "db-init")
REDIS_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "redis_mock_data")

class DataGenerator:
    def __init__(self):
        """Initialize output directories"""
        os.makedirs(SQL_OUTPUT_DIR, exist_ok=True)
        os.makedirs(REDIS_OUTPUT_DIR, exist_ok=True)
        print(f"✓ Output directories created:")
        print(f"  - {SQL_OUTPUT_DIR}/")
        print(f"  - {REDIS_OUTPUT_DIR}/")
        
        # Store generated data for consistency
        self.users = {}
        self.products = {}
        self.orders = {}
    
    def escape_sql_string(self, s):
        """Escape single quotes for SQL"""
        if s is None:
            return ""
        return str(s).replace("'", "\\'")
    
    def escape_redis_string(self, s):
        """Escape single quotes for Redis"""
        if s is None:
            return ""
        return str(s).replace("'", "\\'")
    
    def generate_users(self):
        """Generate user data"""
        print(f"\nGenerating {NUM_USERS:,} users...")
        
        for i in range(NUM_USERS):
            user_id = i + 1
            self.users[user_id] = {
                'id': user_id,
                'name': f"User {user_id}",
                'email': f"user{user_id}@example.com",
            }
        
        print(f"✓ Generated {NUM_USERS:,} users")
    
    def generate_products(self):
        """Generate product data"""
        print(f"\nGenerating {NUM_PRODUCTS:,} products...")
        
        product_adjectives = ["Premium", "Professional", "Deluxe", "Compact", "Advanced", 
                              "Smart", "Ultra", "Pro", "Elite", "Standard"]
        product_categories = ["Laptop", "Monitor", "Keyboard", "Mouse", "Headphone", 
                              "Cable", "Hub", "Stand", "Dock", "Adapter"]
        
        for i in range(NUM_PRODUCTS):
            product_id = i + 1
            adjective = random.choice(product_adjectives)
            category = random.choice(product_categories)
            
            self.products[product_id] = {
                'id': product_id,
                'name': f"{adjective} {category} {product_id}",
                'sku': f"SKU{product_id:06d}",
                'price': round(random.uniform(5.00, 2000.00), 2),
                'stock': random.randint(10, 1000)
            }
        
        print(f"✓ Generated {NUM_PRODUCTS:,} products with stock")
    
    def generate_orders(self):
        """Generate order data"""
        print(f"\nGenerating {NUM_ORDERS:,} orders...")
        
        product_ids = list(self.products.keys())
        
        for order_num in range(NUM_ORDERS):
            order_id = order_num + 1
            user_id = random.randint(1, NUM_USERS)
            num_items = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)
            selected_products = random.sample(product_ids, min(num_items, len(product_ids)))
            
            total_amount = 0
            items = []
            
            for product_id in selected_products:
                quantity = random.randint(1, 3)
                unit_price = self.products[product_id]['price']
                total_amount += unit_price * quantity
                
                items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price
                })
            
            days_ago = random.randint(0, 730)
            created_at = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
            self.orders[order_id] = {
                'id': order_id,
                'user_id': user_id,
                'total_amount': round(total_amount, 2),
                'items': items,
                'created_at': created_at
            }
            
            if (order_num + 1) % 100000 == 0:
                print(f"  Generated {order_num + 1:,} orders")
        
        print(f"✓ Generated {NUM_ORDERS:,} orders with items")
    
    def write_sql_users(self):
        """Write users to SQL file"""
        filename = os.path.join(SQL_OUTPUT_DIR, "01_insert_users.sql")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("-- Users Table\n")
            f.write("DELETE FROM users;\n\n")
            f.write("INSERT INTO users (id, name, email) VALUES\n")
            
            user_list = list(self.users.items())
            for i, (user_id, user) in enumerate(user_list):
                f.write(f"({user_id}, '{self.escape_sql_string(user['name'])}', '{self.escape_sql_string(user['email'])}')")
                if i < len(user_list) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
    
    def write_sql_products(self):
        """Write products to SQL file"""
        filename = os.path.join(SQL_OUTPUT_DIR, "02_insert_products.sql")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("-- Products Table\n")
            f.write("DELETE FROM products;\n\n")
            f.write("INSERT INTO products (id, name, sku, price) VALUES\n")
            
            product_list = list(self.products.items())
            for i, (product_id, product) in enumerate(product_list):
                f.write(f"({product_id}, '{self.escape_sql_string(product['name'])}', '{product['sku']}', {product['price']})")
                if i < len(product_list) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
    
    def write_sql_stocks(self):
        """Write stocks to SQL file"""
        filename = os.path.join(SQL_OUTPUT_DIR, "03_insert_stocks.sql")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("-- Stocks Table\n")
            f.write("DELETE FROM stocks;\n\n")
            f.write("INSERT INTO stocks (product_id, quantity) VALUES\n")
            
            product_list = list(self.products.items())
            for i, (product_id, product) in enumerate(product_list):
                f.write(f"({product_id}, {product['stock']})")
                if i < len(product_list) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
    
    def write_sql_orders(self):
        """Write orders to SQL files (chunked)"""
        chunk_size = 100_000
        chunk_num = 0
        orders_batch = []
        order_items_batch = []
        
        print(f"\nWriting SQL order files (chunked)...")
        
        order_list = list(self.orders.items())
        
        for order_idx, (order_id, order) in enumerate(order_list):
            orders_batch.append(f"({order_id}, {order['user_id']}, {order['total_amount']}, '{order['created_at']}')")
            
            for item in order['items']:
                order_items_batch.append(
                    f"({order_id}, {item['product_id']}, {item['quantity']}, {item['unit_price']})"
                )
            
            if (order_idx + 1) % chunk_size == 0 or order_idx == len(order_list) - 1:
                chunk_num += 1
                self._write_sql_orders_chunk(chunk_num, orders_batch, order_items_batch)
                print(f"  Wrote orders chunk {chunk_num}")
                orders_batch = []
                order_items_batch = []
    
    def _write_sql_orders_chunk(self, chunk_num, orders_batch, order_items_batch):
        """Write a chunk of orders"""
        # Write orders
        orders_file = os.path.join(SQL_OUTPUT_DIR, f"04_insert_orders_part{chunk_num:02d}.sql")
        
        with open(orders_file, 'w', encoding='utf-8') as f:
            if chunk_num == 1:
                f.write("-- Orders Table (may be split across multiple files)\n")
                f.write("DELETE FROM orders;\n\n")
            
            f.write("INSERT INTO orders (id, user_id, total_amount, created_at) VALUES\n")
            
            for i, order_row in enumerate(orders_batch):
                f.write(order_row)
                if i < len(orders_batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
        
        # Write order items
        order_items_file = os.path.join(SQL_OUTPUT_DIR, f"05_insert_order_items_part{chunk_num:02d}.sql")
        
        with open(order_items_file, 'w', encoding='utf-8') as f:
            if chunk_num == 1:
                f.write("-- Order Items Table (may be split across multiple files)\n")
                f.write("DELETE FROM order_items;\n\n")
            
            f.write("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES\n")
            
            for i, item_row in enumerate(order_items_batch):
                f.write(item_row)
                if i < len(order_items_batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
    
    def write_redis_users(self):
        """Write users to Redis file"""
        filename = os.path.join(REDIS_OUTPUT_DIR, "01_populate_users.redis")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Redis Users\n")
            f.write("# Data structure: user:{id} -> Hash {name, email}\n\n")
            
            for user_id, user in self.users.items():
                f.write(f"HSET user:{user_id} name '{self.escape_redis_string(user['name'])}' ")
                f.write(f"email '{self.escape_redis_string(user['email'])}'\n")
    
    def write_redis_products(self):
        """Write products to Redis file"""
        filename = os.path.join(REDIS_OUTPUT_DIR, "02_populate_products.redis")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Redis Products (reference)\n")
            f.write("# Data structure: product:{id} -> Hash {name, sku, price}\n\n")
            
            for product_id, product in self.products.items():
                f.write(f"HSET product:{product_id} name '{self.escape_redis_string(product['name'])}' ")
                f.write(f"sku '{product['sku']}' price {product['price']}\n")
    
    def write_redis_stocks(self):
        """Write stocks to Redis file"""
        filename = os.path.join(REDIS_OUTPUT_DIR, "03_populate_stocks.redis")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Redis Stock\n")
            f.write("# Data structure: stock:{product_id} -> Hash {product_name, product_sku, product_unit_price, quantity}\n\n")
            
            for product_id, product in self.products.items():
                f.write(f"HSET stock:{product_id} product_name '{self.escape_redis_string(product['name'])}' ")
                f.write(f"product_sku '{product['sku']}' product_unit_price {product['price']} ")
                f.write(f"quantity {product['stock']}\n")
    
    def write_redis_orders(self):
        """Write orders to Redis files (chunked)"""
        chunk_size = 100_000
        chunk_num = 0
        orders_batch = []
        
        print(f"\nWriting Redis order files (chunked)...")
        
        order_list = list(self.orders.items())
        
        for order_idx, (order_id, order) in enumerate(order_list):
            orders_batch.append(order)
            
            if (order_idx + 1) % chunk_size == 0 or order_idx == len(order_list) - 1:
                chunk_num += 1
                self._write_redis_orders_chunk(chunk_num, orders_batch)
                print(f"  Wrote Redis orders chunk {chunk_num}")
                orders_batch = []
    
    def _write_redis_orders_chunk(self, chunk_num, orders_batch):
        """Write a chunk of Redis orders"""
        filename = os.path.join(REDIS_OUTPUT_DIR, f"04_populate_orders_part{chunk_num:02d}.redis")
        
        with open(filename, 'w', encoding='utf-8') as f:
            if chunk_num == 1:
                f.write("# Redis Orders\n")
                f.write("# Data structure: order:{id} -> Hash {user_id, total_amount, items}\n")
                f.write("# items is a JSON string containing the order items array\n\n")
            
            for order in orders_batch:
                order_id = order['id']
                user_id = order['user_id']
                total_amount = order['total_amount']
                items_json = json.dumps(order['items'])
                
                f.write(f"HSET order:{order_id} user_id {user_id} ")
                f.write(f"total_amount {total_amount} ")
                f.write(f"items '{self.escape_redis_string(items_json)}'\n")
    
    def write_cleanup_scripts(self):
        """Write cleanup scripts"""
        # SQL cleanup
        sql_cleanup = os.path.join(SQL_OUTPUT_DIR, "00_post_init.sql")
        with open(sql_cleanup, 'w', encoding='utf-8') as f:
            f.write("-- SQL Cleanup and Setup\n\n")
            f.write("SET FOREIGN_KEY_CHECKS=0;\n")
            f.write("SET autocommit=0;\n\n")
            f.write("ALTER TABLE orders DISABLE KEYS;\n")
            f.write("ALTER TABLE order_items DISABLE KEYS;\n")
        
        # SQL finalize
        sql_finalize = os.path.join(SQL_OUTPUT_DIR, "06_finalize.sql")
        with open(sql_finalize, 'w', encoding='utf-8') as f:
            f.write("-- SQL Finalize\n\n")
            f.write("ALTER TABLE orders ENABLE KEYS;\n")
            f.write("ALTER TABLE order_items ENABLE KEYS;\n\n")
            f.write("SET FOREIGN_KEY_CHECKS=1;\n")
            f.write("SET autocommit=1;\n")
            f.write("COMMIT;\n\n")
            f.write("OPTIMIZE TABLE users;\n")
            f.write("OPTIMIZE TABLE products;\n")
            f.write("OPTIMIZE TABLE orders;\n")
            f.write("OPTIMIZE TABLE order_items;\n")
            f.write("OPTIMIZE TABLE stocks;\n\n")
            f.write("ANALYZE TABLE users;\n")
            f.write("ANALYZE TABLE products;\n")
            f.write("ANALYZE TABLE orders;\n")
            f.write("ANALYZE TABLE order_items;\n")
            f.write("ANALYZE TABLE stocks;\n")
    
    def generate_all(self):
        """Generate all SQL and Redis files"""
        print("="*70)
        print("MySQL & Redis Data Generator")
        print("="*70)
        print(f"\nConfiguration:")
        print(f"  Users: {NUM_USERS:,}")
        print(f"  Products: {NUM_PRODUCTS:,}")
        print(f"  Orders: {NUM_ORDERS:,}")
        print(f"  Items per order: {MIN_ITEMS_PER_ORDER}-{MAX_ITEMS_PER_ORDER}")
        print("\nAll data will be IDENTICAL and COHERENT across MySQL and Redis!")
        print("="*70)
        
        # Generate data in memory first
        self.generate_users()
        self.generate_products()
        self.generate_orders()
        
        # Write SQL files
        print("\nWriting SQL files...")
        self.write_cleanup_scripts()
        self.write_sql_users()
        self.write_sql_products()
        self.write_sql_stocks()
        self.write_sql_orders()
        print("✓ SQL files written")
        
        # Write Redis files
        print("\nWriting Redis files...")
        self.write_redis_users()
        self.write_redis_products()
        self.write_redis_stocks()
        self.write_redis_orders()
        print("✓ Redis files written")
        
        self.print_summary()
    
    def print_summary(self):
        """Print summary"""
        print("\n" + "="*70)
        print("✓ Generation complete!")
        print("="*70)
        
        sql_files = sorted([f for f in os.listdir(SQL_OUTPUT_DIR) if f.endswith('.sql')])
        redis_files = sorted([f for f in os.listdir(REDIS_OUTPUT_DIR) if f.endswith('.redis')])
        
        print(f"\nSQL Files ({len(sql_files)}):")
        for filename in sql_files:
            filepath = os.path.join(SQL_OUTPUT_DIR, filename)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  {filename:<40} ({size_kb:>10,.1f} KB)")
        
        print(f"\nRedis Files ({len(redis_files)}):")
        for filename in redis_files:
            filepath = os.path.join(REDIS_OUTPUT_DIR, filename)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  {filename:<40} ({size_kb:>10,.1f} KB)")
        
        print("NEXT STEPS: see README.md")

if __name__ == "__main__":
    generator = DataGenerator()
    generator.generate_all()