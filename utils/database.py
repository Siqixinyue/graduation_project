#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智农云平台 - 数据库操作模块

本文件实现了智农云平台的所有数据库操作功能，使用SQLite作为后端数据库。
提供了用户管理、农场管理、作物规划、农资库存、市场交易、病虫害识别记录等数据操作。

主要功能模块：
- 用户认证和管理
- 农场信息管理
- 作物种植规划
- 农资库存管理
- 农产品市场交易
- 病虫害识别历史
- 自动检测提醒
- 数据统计和分析

数据库设计：
- users: 用户表
- farms: 农场表
- crop_plans: 作物规划表
- inventory: 农资库存表
- market_listings: 市场商品表
- orders: 订单表
- diagnosis_history: 识别历史表
- auto_alerts: 自动提醒表

作者：智农云平台开发团队
版本：1.0.0
更新日期：2026-03-30
"""

import hashlib
import os
import sqlite3
from datetime import datetime, timezone, timedelta

# 时区处理 - 兼容不同Python版本
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

# 数据库文件路径
DB_PATH = "data.db"

# 北京时区设置
if ZoneInfo is not None:
    BEIJING_TZ = ZoneInfo("Asia/Shanghai")
else:
    BEIJING_TZ = None

# 获取北京时间字符串的工具函数
def beijing_now_str():
    """
    获取当前北京时间的字符串表示

    使用zoneinfo模块（Python 3.9+）或手动计算UTC+8来获取北京时间。

    返回：
    - str: 北京时间字符串，格式为"YYYY-MM-DD HH:MM:SS"
    """
    if BEIJING_TZ is not None:
        return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")
    # 兼容性：未安装 zoneinfo 时按北京时间（UTC+8）
    return (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

# 密码哈希函数
def hash_password(password):
    """
    对密码进行SHA256哈希处理

    使用SHA256算法对密码进行单向哈希，确保密码安全存储。

    参数：
    - password: 原始密码字符串

    返回：
    - str: 哈希后的密码字符串（十六进制表示）
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# 数据库操作主类
class Database:
    """
    智农云平台数据库操作类

    封装了所有数据库操作方法，提供统一的数据库访问接口。
    使用SQLite作为底层数据库，支持事务处理和外键约束。

    主要功能：
    - 用户管理（注册、登录、信息查询）
    - 农场管理（增删改查）
    - 作物规划管理
    - 农资库存管理
    - 市场交易管理
    - 病虫害识别记录管理
    - 数据统计和分析
    """

    def __init__(self):
        """
        初始化数据库连接

        创建数据库目录（如果不存在），并初始化所有数据表。
        """
        db_dir = os.path.dirname(DB_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.create_tables()

    def get_connection(self):
        """
        获取数据库连接

        创建SQLite数据库连接，设置行工厂为字典模式，
        并启用外键约束支持。

        返回：
        - sqlite3.Connection: 配置好的数据库连接对象
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 返回字典式结果
        conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
        return conn

    def get_user_columns(self):
        """
        获取用户表的列信息

        查询users表的结构信息，用于数据库迁移和兼容性检查。

        返回：
        - list: 用户表的所有列名列表
        """
        with self.get_connection() as conn:
            cols = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
        return cols

    def create_tables(self):
        """
        创建所有数据表

        初始化智农云平台所需的所有数据库表结构，
        包括用户表、农场表、作物规划表等。
        支持数据库迁移和向后兼容。
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 创建用户表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    phone TEXT,
                    role TEXT DEFAULT 'farmer',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # 兼容旧版 users 表旧字段 password
            cols = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
            if "password" in cols and "password_hash" not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
                cursor.execute("UPDATE users SET password_hash = password")
            if "password_hash" in cols and "password" not in cols:
                # 旧版本可能没有 password 字段，保留兼容性不强制创建
                pass

            # 创建农场表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS farms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    area_mu REAL NOT NULL,
                    soil_type TEXT,
                    irrigation_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
                )
                """
            )

            # 创建作物规划表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS crop_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER NOT NULL,
                    crop_name TEXT NOT NULL,
                    season TEXT,
                    sowing_date DATE,
                    expected_harvest DATE,
                    growth_stage TEXT DEFAULT '育苗期',
                    status TEXT DEFAULT '进行中',
                    FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                )
                """
            )

            # 创建农场任务表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS farm_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    due_date DATE,
                    priority TEXT DEFAULT '中',
                    status TEXT DEFAULT '待处理',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                )
                """
            )

            # 创建病虫害识别历史表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS diagnosis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    image_name TEXT,
                    class_id INTEGER NOT NULL,
                    class_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    diagnosis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
                """
            )

            # 创建自动提醒表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS auto_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    image_name TEXT,
                    class_id INTEGER NOT NULL,
                    class_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT '未处理',
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
                """
            )

            # 创建农资库存表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    warning_level REAL DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
                """
            )

            # 创建市场商品表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS market_listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    quality_level TEXT DEFAULT '标准',
                    status TEXT DEFAULT 'on_sale',
                    source TEXT DEFAULT 'local',
                    source_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (seller_id) REFERENCES users (id) ON DELETE CASCADE
                )
                """
            )

            # 创建订单表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id INTEGER NOT NULL,
                    buyer_id INTEGER NOT NULL,
                    seller_id INTEGER NOT NULL,
                    quantity REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT '待发货',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (listing_id) REFERENCES market_listings (id),
                    FOREIGN KEY (buyer_id) REFERENCES users (id),
                    FOREIGN KEY (seller_id) REFERENCES users (id)
                )
                """
            )

            # ===== 新病虫害学习中心相关表 =====
            # 创建学习任务表 - 用户提交新病害学习请求
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    requester_id INTEGER NOT NULL,
                    crop_type TEXT NOT NULL,
                    disease_name TEXT NOT NULL,
                    description TEXT,
                    symptoms TEXT,
                    prevention TEXT,
                    treatment TEXT,
                    status TEXT NOT NULL DEFAULT 'pending', -- pending/approved/rejected
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_at TIMESTAMP,
                    FOREIGN KEY (requester_id) REFERENCES users (id) ON DELETE CASCADE
                )
                """
            )

            # 创建学习图片表 - 存储用户上传的学习样本图片
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    file_name TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES learning_tasks (id) ON DELETE CASCADE
                )
                """
            )

            # 创建模型版本表 - 记录AI模型的版本信息
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS model_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    model_path TEXT,
                    status TEXT DEFAULT 'prepared', -- prepared/active/failed
                    notes TEXT
                )
                """
            )

            # 创建训练作业表 - 记录模型训练任务
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS train_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    finished_at TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'queued', -- queued/running/succeeded/failed
                    log_path TEXT,
                    message TEXT,
                    FOREIGN KEY (task_id) REFERENCES learning_tasks (id) ON DELETE CASCADE
                )
                """
            )

            # 创建学习任务类别映射表 - 将学习任务映射到模型类别
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_task_class_map (
                    task_id INTEGER PRIMARY KEY,
                    class_id INTEGER NOT NULL,
                    class_name TEXT NOT NULL,
                    model_version_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES learning_tasks (id) ON DELETE CASCADE
                )
                """
            )

            # ===== 农场管理扩展 =====
            # 创建农场工人表 - 管理农场工人信息
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS farm_workers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    phone TEXT,
                    hire_date DATE,
                    salary REAL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS farm_equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    model TEXT,
                    purchase_date DATE,
                    purchase_price REAL,
                    status TEXT DEFAULT '正常',
                    maintenance_schedule TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS farm_finances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER NOT NULL,
                    type TEXT NOT NULL, -- 'income' or 'expense'
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    transaction_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS crop_yields (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_plan_id INTEGER NOT NULL,
                    harvest_date DATE NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    quality_grade TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (crop_plan_id) REFERENCES crop_plans (id) ON DELETE CASCADE
                )
                """
            )

            # 修复已存在的 crop_yields 表外键约束（如果没有 ON DELETE CASCADE）
            try:
                # 检查外键约束是否存在且正确
                conn.execute("PRAGMA foreign_key_check")
            except sqlite3.IntegrityError:
                pass

            # 对于已存在的数据库，需要重建表来修复外键约束
            # 检查 crop_yields 表是否存在且需要修复
            crop_yields_exists = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='crop_yields'"
            ).fetchone()

            if crop_yields_exists:
                # 检查当前外键约束定义
                fk_info = cursor.execute("PRAGMA foreign_key_list(crop_yields)").fetchall()
                needs_rebuild = False

                for fk in fk_info:
                    # fk 结构: (id, seq, table, from, to, on_update, on_delete, match)
                    if fk[2] == 'crop_plans' and fk[6] != 'CASCADE':  # on_delete 不是 CASCADE
                        needs_rebuild = True
                        break

                if needs_rebuild:
                    # 重建表以修复外键约束
                    cursor.execute("""
                        CREATE TABLE crop_yields_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            crop_plan_id INTEGER NOT NULL,
                            harvest_date DATE NOT NULL,
                            quantity REAL NOT NULL,
                            unit TEXT NOT NULL,
                            quality_grade TEXT,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (crop_plan_id) REFERENCES crop_plans (id) ON DELETE CASCADE
                        )
                    """)
                    cursor.execute("""
                        INSERT INTO crop_yields_new (id, crop_plan_id, harvest_date, quantity, unit, quality_grade, notes, created_at)
                        SELECT id, crop_plan_id, harvest_date, quantity, unit, quality_grade, notes, created_at FROM crop_yields
                    """)
                    cursor.execute("DROP TABLE crop_yields")
                    cursor.execute("ALTER TABLE crop_yields_new RENAME TO crop_yields")
                    conn.commit()

            # ===== 农资库存扩展 =====
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory_suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory_batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventory_item_id INTEGER NOT NULL,
                    supplier_id INTEGER,
                    batch_number TEXT,
                    quantity REAL NOT NULL,
                    unit_cost REAL,
                    expiry_date DATE,
                    purchase_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (inventory_item_id) REFERENCES inventory (id) ON DELETE CASCADE,
                    FOREIGN KEY (supplier_id) REFERENCES inventory_suppliers (id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventory_item_id INTEGER NOT NULL,
                    type TEXT NOT NULL, -- 'in' or 'out'
                    quantity REAL NOT NULL,
                    reason TEXT,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (inventory_item_id) REFERENCES inventory (id) ON DELETE CASCADE
                )
                """
            )

            # ===== 交易市场扩展 =====
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS market_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    reviewer_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL, -- 1-5
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (reviewer_id) REFERENCES users (id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    location TEXT,
                    notes TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
                )
                """
            )

            conn.commit()
            self._migrate_legacy_users(conn)
            self._migrate_legacy_farms(conn)
            self._fix_foreign_key_constraints(conn)

    def _fix_foreign_key_constraints(self, conn):
        """修复所有表的外键约束，确保都有 ON DELETE CASCADE"""
        cursor = conn.cursor()

        # 临时关闭外键约束检查
        cursor.execute("PRAGMA foreign_keys = OFF")

        # 定义需要修复的表及其外键约束
        tables_to_fix = {
            'crop_plans': {
                'ref_table': 'farms',
                'ref_column': 'id',
                'fk_column': 'farm_id',
                'schema': '''
                    CREATE TABLE crop_plans_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        farm_id INTEGER NOT NULL,
                        crop_name TEXT NOT NULL,
                        season TEXT,
                        sowing_date DATE,
                        expected_harvest DATE,
                        growth_stage TEXT DEFAULT '育苗期',
                        status TEXT DEFAULT '进行中',
                        FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                    )
                '''
            },
            'farm_tasks': {
                'ref_table': 'farms',
                'ref_column': 'id',
                'fk_column': 'farm_id',
                'schema': '''
                    CREATE TABLE farm_tasks_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        farm_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        due_date DATE,
                        priority TEXT DEFAULT '中',
                        status TEXT DEFAULT '待处理',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                    )
                '''
            },
            'farm_workers': {
                'ref_table': 'farms',
                'ref_column': 'id',
                'fk_column': 'farm_id',
                'schema': '''
                    CREATE TABLE farm_workers_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        farm_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        phone TEXT,
                        hire_date DATE,
                        salary REAL,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                    )
                '''
            },
            'farm_equipment': {
                'ref_table': 'farms',
                'ref_column': 'id',
                'fk_column': 'farm_id',
                'schema': '''
                    CREATE TABLE farm_equipment_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        farm_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        model TEXT,
                        purchase_date DATE,
                        purchase_price REAL,
                        status TEXT DEFAULT '正常',
                        maintenance_schedule TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                    )
                '''
            },
            'farm_finances': {
                'ref_table': 'farms',
                'ref_column': 'id',
                'fk_column': 'farm_id',
                'schema': '''
                    CREATE TABLE farm_finances_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        farm_id INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        category TEXT NOT NULL,
                        amount REAL NOT NULL,
                        description TEXT,
                        transaction_date DATE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                    )
                '''
            },
            'crop_yields': {
                'ref_table': 'crop_plans',
                'ref_column': 'id',
                'fk_column': 'crop_plan_id',
                'schema': '''
                    CREATE TABLE crop_yields_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        crop_plan_id INTEGER NOT NULL,
                        harvest_date DATE NOT NULL,
                        quantity REAL NOT NULL,
                        unit TEXT NOT NULL,
                        quality_grade TEXT,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (crop_plan_id) REFERENCES crop_plans (id) ON DELETE CASCADE
                    )
                '''
            },
        }

        for table_name, table_info in tables_to_fix.items():
            # 检查表是否存在
            table_exists = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            ).fetchone()

            if not table_exists:
                continue

            # 检查外键约束
            fk_list = cursor.execute(f"PRAGMA foreign_key_list({table_name})").fetchall()

            needs_rebuild = False
            for fk in fk_list:
                # fk: (id, seq, table, from, to, on_update, on_delete, match)
                if fk[2] == table_info['ref_table'] and fk[6] != 'CASCADE':
                    needs_rebuild = True
                    break

            if needs_rebuild:
                # 获取表的列信息
                columns_info = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
                column_names = [col[1] for col in columns_info]

                # 创建新表
                cursor.execute(table_info['schema'])

                # 复制数据
                cols_str = ', '.join(column_names)
                cursor.execute(f'''
                    INSERT INTO {table_name}_new ({cols_str})
                    SELECT {cols_str} FROM {table_name}
                ''')

                # 删除旧表，重命名新表
                cursor.execute(f"DROP TABLE {table_name}")
                cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
                conn.commit()

        # 重新启用外键约束检查
        cursor.execute("PRAGMA foreign_keys = ON")

    def _migrate_legacy_users(self, conn):
        cursor = conn.cursor()
        columns = {
            row["name"] for row in cursor.execute("PRAGMA table_info(users)").fetchall()
        }
        if "password" in columns:
            if "password_hash" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            if "full_name" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            if "phone" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")

            users = cursor.execute("SELECT id, password FROM users").fetchall()
            for row in users:
                cursor.execute(
                    """
                    UPDATE users
                    SET password_hash = ?
                    WHERE id = ? AND (password_hash IS NULL OR password_hash = '')
                    """,
                    (
                        hash_password(row["password"]),
                        row["id"],
                    ),
                )
            conn.commit()

    def _migrate_legacy_farms(self, conn):
        cursor = conn.cursor()
        table_exists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='farms'"
        ).fetchone()
        if not table_exists:
            return

        columns = {
            row["name"] for row in cursor.execute("PRAGMA table_info(farms)").fetchall()
        }
        changed = False

        if "owner_id" not in columns:
            cursor.execute("ALTER TABLE farms ADD COLUMN owner_id INTEGER")
            changed = True
        if "area_mu" not in columns:
            cursor.execute("ALTER TABLE farms ADD COLUMN area_mu REAL")
            changed = True
        if "irrigation_type" not in columns:
            cursor.execute("ALTER TABLE farms ADD COLUMN irrigation_type TEXT")
            changed = True

        if "user_id" in columns:
            cursor.execute(
                """
                UPDATE farms
                SET owner_id = user_id
                WHERE owner_id IS NULL
                """
            )
            changed = True

        if "area" in columns:
            cursor.execute(
                """
                UPDATE farms
                SET area_mu = area
                WHERE area_mu IS NULL
                """
            )
            changed = True

        # market_listings 新字段兼容
        market_columns = {
            row["name"] for row in cursor.execute("PRAGMA table_info(market_listings)").fetchall()
        }
        if "source" not in market_columns:
            cursor.execute("ALTER TABLE market_listings ADD COLUMN source TEXT DEFAULT 'local'")
            changed = True
        if "source_url" not in market_columns:
            cursor.execute("ALTER TABLE market_listings ADD COLUMN source_url TEXT")
            changed = True

        cursor.execute(
            """
            UPDATE farms
            SET irrigation_type = '自然降雨为主'
            WHERE irrigation_type IS NULL OR irrigation_type = ''
            """
        )
        changed = True

        if changed:
            conn.commit()

    def register_user(self, username, password, email, full_name="", phone=""):
        password_hash = hash_password(password)
        with self.get_connection() as conn:
            if conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
                return False, "用户名已存在，请换一个"
            if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
                return False, "邮箱已存在，请换一个"

            cols = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
            if "password_hash" in cols and "password" in cols:
                conn.execute(
                    """
                    INSERT INTO users (username, password_hash, password, email, full_name, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (username, password_hash, password_hash, email, full_name, phone),
                )
            elif "password_hash" in cols:
                conn.execute(
                    """
                    INSERT INTO users (username, password_hash, email, full_name, phone)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (username, password_hash, email, full_name, phone),
                )
            elif "password" in cols:
                conn.execute(
                    """
                    INSERT INTO users (username, password, email, full_name, phone)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (username, password_hash, email, full_name, phone),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO users (username, password_hash, email, full_name, phone)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (username, password_hash, email, full_name, phone),
                )
        return True, "注册成功"

    def login_user(self, username, password):
        password_hash = hash_password(password)
        with self.get_connection() as conn:
            cols = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
            row = None
            if "password_hash" in cols and "password" in cols:
                row = conn.execute(
                    "SELECT * FROM users WHERE username = ? AND (password_hash = ? OR password = ?)",
                    (username, password_hash, password_hash),
                ).fetchone()
            elif "password_hash" in cols:
                row = conn.execute(
                    "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                    (username, password_hash),
                ).fetchone()
            elif "password" in cols:
                row = conn.execute(
                    "SELECT * FROM users WHERE username = ? AND password = ?",
                    (username, password_hash),
                ).fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id):
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

    def get_user_by_username(self, username):
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None

    def get_or_create_external_seller(self):
        seller = self.get_user_by_username('cnhnb_official')
        if seller:
            return seller['id']

        username = 'cnhnb_official'
        password = 'cnhnb_official_pwd'
        email = 'support@cnhnb.com'
        full_name = '惠农网官方'
        phone = ''

        # 插入时可能抛 (if exists), so使用 try-except
        try:
            self.register_user(username, password, email, full_name, phone)
        except Exception:
            pass

        seller = self.get_user_by_username('cnhnb_official')
        return seller['id'] if seller else 0

    def add_farm(self, user_id, name, location, area_mu, soil_type, irrigation_type):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO farms (user_id, owner_id, name, location, area_mu, soil_type, irrigation_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, user_id, name, location, area_mu, soil_type, irrigation_type, created_at),
            )
            return cursor.lastrowid

    def get_farms(self, user_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM farms WHERE owner_id = ? ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_crop_plan(
        self, farm_id, crop_name, season, sowing_date, expected_harvest, growth_stage
    ):
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO crop_plans (farm_id, crop_name, season, sowing_date, expected_harvest, growth_stage)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (farm_id, crop_name, season, sowing_date, expected_harvest, growth_stage),
            )

    def get_crop_plans(self, farm_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM crop_plans WHERE farm_id = ? ORDER BY id DESC", (farm_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def add_task(self, farm_id, title, due_date, priority, notes):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO farm_tasks (farm_id, title, due_date, priority, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (farm_id, title, due_date, priority, notes, created_at),
            )

    def update_task_status(self, task_id, status):
        with self.get_connection() as conn:
            conn.execute("UPDATE farm_tasks SET status = ? WHERE id = ?", (status, task_id))

    def update_task(self, task_id, title, due_date, priority, notes, status):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE farm_tasks SET title = ?, due_date = ?, priority = ?, notes = ?, status = ? WHERE id = ?",
                (title, due_date, priority, notes, status, task_id),
            )

    def delete_task(self, task_id, farm_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM farm_tasks WHERE id = ? AND farm_id = ?", (task_id, farm_id))

    def get_tasks(self, farm_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM farm_tasks
                WHERE farm_id = ?
                ORDER BY
                    CASE status
                        WHEN '待处理' THEN 1
                        WHEN '进行中' THEN 2
                        ELSE 3
                    END,
                    due_date ASC
                """,
                (farm_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_task(self, task_id, farm_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM farm_tasks WHERE id = ? AND farm_id = ?",
                (task_id, farm_id),
            ).fetchone()
        return dict(row) if row else None

    def get_farm(self, farm_id):
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM farms WHERE id = ?", (farm_id,)).fetchone()
        return dict(row) if row else None

    def update_farm(self, farm_id, name, location, area_mu, soil_type, irrigation_type):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE farms SET name = ?, location = ?, area_mu = ?, soil_type = ?, irrigation_type = ? WHERE id = ?",
                (name, location, area_mu, soil_type, irrigation_type, farm_id),
            )

    def delete_farm(self, farm_id, owner_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            # 临时关闭外键约束，以便处理可能的孤立数据
            cursor.execute("PRAGMA foreign_keys = OFF")

            # 先删除产量记录 (crop_yields) - 引用 crop_plans
            cursor.execute(
                """
                DELETE FROM crop_yields
                WHERE crop_plan_id IN (
                    SELECT id FROM crop_plans WHERE farm_id = ?
                )
                """,
                (farm_id,),
            )
            # 删除种植计划 (crop_plans)
            cursor.execute("DELETE FROM crop_plans WHERE farm_id = ?", (farm_id,))
            # 删除农事任务 (farm_tasks)
            cursor.execute("DELETE FROM farm_tasks WHERE farm_id = ?", (farm_id,))
            # 删除农场工人 (farm_workers)
            cursor.execute("DELETE FROM farm_workers WHERE farm_id = ?", (farm_id,))
            # 删除农场设备 (farm_equipment)
            cursor.execute("DELETE FROM farm_equipment WHERE farm_id = ?", (farm_id,))
            # 删除农场财务记录 (farm_finances)
            cursor.execute("DELETE FROM farm_finances WHERE farm_id = ?", (farm_id,))
            # 最后删除农场
            cursor.execute(
                "DELETE FROM farms WHERE id = ? AND owner_id = ?",
                (farm_id, owner_id),
            )
            conn.commit()
        finally:
            conn.close()

    def get_crop_plan(self, plan_id):
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM crop_plans WHERE id = ?", (plan_id,)).fetchone()
        return dict(row) if row else None

    def update_crop_plan(self, plan_id, crop_name, season, sowing_date, expected_harvest, growth_stage, status):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE crop_plans SET crop_name = ?, season = ?, sowing_date = ?, expected_harvest = ?, growth_stage = ?, status = ? WHERE id = ?",
                (crop_name, season, sowing_date, expected_harvest, growth_stage, status, plan_id),
            )

    def delete_crop_plan(self, plan_id, farm_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM crop_plans WHERE id = ? AND farm_id = ?", (plan_id, farm_id))

    def add_diagnosis_history(self, user_id, image_name, class_id, class_name, confidence):
        diagnosis_date = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO diagnosis_history (user_id, image_name, class_id, class_name, confidence, diagnosis_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, image_name, class_id, class_name, confidence, diagnosis_date),
            )

    def get_diagnosis_history(self, user_id, limit=100):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM diagnosis_history
                WHERE user_id = ?
                ORDER BY diagnosis_date DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_auto_alert(self, user_id, image_name, class_id, class_name, confidence, status='未处理'):
        detected_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO auto_alerts (user_id, image_name, class_id, class_name, confidence, status, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, image_name, class_id, class_name, confidence, status, detected_at),
            )

    def get_auto_alerts(self, user_id, limit=50):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM auto_alerts
                WHERE user_id = ?
                ORDER BY detected_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def clear_auto_alerts(self, user_id):
        """清除指定用户的所有自动检测预警"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM auto_alerts WHERE user_id = ?", (user_id,))
            return conn.total_changes

    def clear_single_auto_alert(self, alert_id, user_id):
        """清除指定的单个预警（确保用户权限）"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM auto_alerts WHERE id = ? AND user_id = ?", (alert_id, user_id))
            return conn.total_changes

    def add_inventory_item(self, user_id, item_name, category, quantity, unit, warning_level):
        updated_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO inventory (user_id, item_name, category, quantity, unit, warning_level, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, item_name, category, quantity, unit, warning_level, updated_at),
            )

    def get_inventory(self, user_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM inventory WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_inventory_item(self, item_id, user_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM inventory WHERE id = ? AND user_id = ?",
                (item_id, user_id),
            ).fetchone()
        return dict(row) if row else None

    def update_inventory_item(self, item_id, user_id, item_name, category, quantity, unit, warning_level):
        updated_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE inventory SET item_name = ?, category = ?, quantity = ?, unit = ?, warning_level = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                (item_name, category, quantity, unit, warning_level, updated_at, item_id, user_id),
            )

    def delete_inventory_item(self, item_id, user_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM inventory WHERE id = ? AND user_id = ?", (item_id, user_id))

    def add_listing(
        self, seller_id, title, category, description, price, quantity, unit, quality_level,
        status='on_sale', source='local', source_url=None
    ):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO market_listings (seller_id, title, category, description, price, quantity, unit, quality_level, status, source, source_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    seller_id,
                    title,
                    category,
                    description,
                    price,
                    quantity,
                    unit,
                    quality_level,
                    status,
                    source,
                    source_url,
                    created_at,
                ),
            )

    def add_or_update_external_listing(
        self, title, category, description, price, quantity, unit, quality_level, source_url,
        status='on_sale', source='cnhnb'
    ):
        seller_id = self.get_or_create_external_seller() or 1
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM market_listings WHERE source = ? AND source_url = ?",
                (source, source_url),
            ).fetchone()
            if row:
                conn.execute(
                    """
                    UPDATE market_listings
                    SET title = ?, category = ?, description = ?, price = ?, quantity = ?, unit = ?, quality_level = ?, status = ?, source = ?, source_url = ?
                    WHERE id = ?
                    """,
                    (title, category, description, price, quantity, unit, quality_level, status, source, source_url, row[0]),
                )
                return row[0]
            else:
                conn.execute(
                    """
                    INSERT INTO market_listings (seller_id, title, category, description, price, quantity, unit, quality_level, status, source, source_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        seller_id,
                        title,
                        category,
                        description,
                        price,
                        quantity,
                        unit,
                        quality_level,
                        status,
                        source,
                        source_url,
                        beijing_now_str(),
                    ),
                )
                return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    def delete_cnhnb_listings(self):
        with self.get_connection() as conn:
            # 获取要删除的惠农网商品ID列表
            cnhnb_listing_ids = [row[0] for row in conn.execute("SELECT id FROM market_listings WHERE source = 'cnhnb'").fetchall()]

            if cnhnb_listing_ids:
                # 将ID列表转换为SQL IN子句的参数
                placeholders = ','.join('?' for _ in cnhnb_listing_ids)

                # 先删除相关的评价记录
                conn.execute(f"DELETE FROM market_reviews WHERE order_id IN (SELECT id FROM orders WHERE listing_id IN ({placeholders}))", cnhnb_listing_ids)

                # 再删除相关的订单记录（orders_tracking会自动删除，因为有CASCADE约束）
                conn.execute(f"DELETE FROM orders WHERE listing_id IN ({placeholders})", cnhnb_listing_ids)

                # 最后删除惠农网商品记录
                conn.execute("DELETE FROM market_listings WHERE source = 'cnhnb'")

    def get_cnhnb_listing_count(self):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) as c FROM market_listings WHERE source = 'cnhnb'"
            ).fetchone()
            return row[0] if row else 0

    def get_market_listings(self, user_id=None):
        query = """
            SELECT l.*, u.username AS seller_name
            FROM market_listings l
            JOIN users u ON u.id = l.seller_id
            WHERE l.status = 'on_sale'
        """
        params = []
        if user_id is not None:
            query += " AND l.seller_id != ?"
            params.append(user_id)
        query += " ORDER BY l.created_at DESC"
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_user_listings(self, user_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM market_listings WHERE seller_id = ? ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_listing(self, listing_id, seller_id=None):
        with self.get_connection() as conn:
            if seller_id is not None:
                row = conn.execute(
                    "SELECT * FROM market_listings WHERE id = ? AND seller_id = ?",
                    (listing_id, seller_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM market_listings WHERE id = ?",
                    (listing_id,),
                ).fetchone()
        return dict(row) if row else None

    def update_listing(self, listing_id, seller_id, title, category, description, price, quantity, unit, quality_level, status):
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE market_listings
                SET title = ?, category = ?, description = ?, price = ?, quantity = ?, unit = ?, quality_level = ?, status = ?
                WHERE id = ? AND seller_id = ?
                """,
                (title, category, description, price, quantity, unit, quality_level, status, listing_id, seller_id),
            )

    def delete_listing(self, listing_id, seller_id):
        with self.get_connection() as conn:
            # 先删除相关的评价记录
            conn.execute(
                "DELETE FROM market_reviews WHERE order_id IN (SELECT id FROM orders WHERE listing_id = ?)",
                (listing_id,),
            )
            # 再删除相关的订单记录（orders_tracking会自动删除，因为有CASCADE约束）
            conn.execute(
                "DELETE FROM orders WHERE listing_id = ?",
                (listing_id,),
            )
            # 最后删除商品记录
            conn.execute(
                "DELETE FROM market_listings WHERE id = ? AND seller_id = ?",
                (listing_id, seller_id),
            )

    def create_order(self, listing_id, buyer_id, quantity):
        with self.get_connection() as conn:
            listing = conn.execute(
                "SELECT * FROM market_listings WHERE id = ? AND status = 'on_sale'",
                (listing_id,),
            ).fetchone()
            if not listing:
                return False, "商品不存在或已下架"
            if listing["seller_id"] == buyer_id:
                return False, "不能购买自己的商品"
            if quantity <= 0 or quantity > listing["quantity"]:
                return False, "购买数量不合法"

            total = float(quantity) * float(listing["price"])
            order_time = beijing_now_str()
            conn.execute(
                """
                INSERT INTO orders (listing_id, buyer_id, seller_id, quantity, total_amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (listing_id, buyer_id, listing["seller_id"], quantity, total, order_time),
            )
            remain = float(listing["quantity"]) - float(quantity)
            if remain <= 0:
                conn.execute(
                    "UPDATE market_listings SET quantity = 0, status = 'sold_out' WHERE id = ?",
                    (listing_id,),
                )
            else:
                conn.execute(
                    "UPDATE market_listings SET quantity = ? WHERE id = ?",
                    (remain, listing_id),
                )
            return True, f"下单成功，订单金额 {total:.2f} 元"

    def get_orders(self, user_id, limit=None):
        with self.get_connection() as conn:
            query = """
            SELECT o.*, l.title
            FROM orders o
            JOIN market_listings l ON l.id = o.listing_id
            WHERE o.buyer_id = ? OR o.seller_id = ?
            ORDER BY o.created_at DESC
            """
            params = [user_id, user_id]
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def update_order_status(self, order_id, user_id, status):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE orders SET status = ? WHERE id = ? AND (buyer_id = ? OR seller_id = ?)",
                (status, order_id, user_id, user_id),
            )

    def delete_order(self, order_id, user_id):
        with self.get_connection() as conn:
            conn.execute(
                "DELETE FROM orders WHERE id = ? AND (buyer_id = ? OR seller_id = ?)",
                (order_id, user_id, user_id),
            )

    def get_dashboard_stats(self, user_id):
        with self.get_connection() as conn:
            def safe_count(query, params=()):
                result = conn.execute(query, params).fetchone()
                return result[0] if result else 0
            
            stats = {
                "farm_count": safe_count("SELECT COUNT(*) FROM farms WHERE owner_id = ?", (user_id,)),
                "task_pending": safe_count(
                    """
                    SELECT COUNT(*)
                    FROM farm_tasks t
                    JOIN farms f ON f.id = t.farm_id
                    WHERE f.owner_id = ? AND t.status != '已完成'
                    """,
                    (user_id,),
                ),
                "listing_on_sale": safe_count(
                    """
                    SELECT COUNT(*)
                    FROM market_listings
                    WHERE seller_id = ? AND status = 'on_sale'
                    """,
                    (user_id,),
                ),
                "diagnosis_count": safe_count(
                    "SELECT COUNT(*) FROM diagnosis_history WHERE user_id = ?", (user_id,)
                ),
            }
        return stats

    # ===== 农场管理扩展方法 =====
    def add_farm_worker(self, farm_id, name, role, phone, hire_date, salary):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO farm_workers (farm_id, name, role, phone, hire_date, salary, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (farm_id, name, role, phone, hire_date, salary, created_at),
            )

    def get_farm_workers(self, farm_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM farm_workers WHERE farm_id = ? ORDER BY hire_date DESC",
                (farm_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_farm_worker(self, worker_id, farm_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM farm_workers WHERE id = ? AND farm_id = ?",
                (worker_id, farm_id),
            ).fetchone()
        return dict(row) if row else None

    def update_farm_worker(self, worker_id, farm_id, name, role, phone, hire_date, salary, status):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE farm_workers SET name = ?, role = ?, phone = ?, hire_date = ?, salary = ?, status = ? WHERE id = ? AND farm_id = ?",
                (name, role, phone, hire_date, salary, status, worker_id, farm_id),
            )

    def delete_farm_worker(self, worker_id, farm_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM farm_workers WHERE id = ? AND farm_id = ?", (worker_id, farm_id))

    def add_farm_equipment(self, farm_id, name, category, model, purchase_date, purchase_price, maintenance_schedule):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO farm_equipment (farm_id, name, category, model, purchase_date, purchase_price, maintenance_schedule, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (farm_id, name, category, model, purchase_date, purchase_price, maintenance_schedule, created_at),
            )

    def get_farm_equipment(self, farm_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM farm_equipment WHERE farm_id = ? ORDER BY purchase_date DESC",
                (farm_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_farm_equipment_item(self, equipment_id, farm_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM farm_equipment WHERE id = ? AND farm_id = ?",
                (equipment_id, farm_id),
            ).fetchone()
        return dict(row) if row else None

    def update_farm_equipment(self, equipment_id, farm_id, name, category, model, purchase_date, purchase_price, status, maintenance_schedule):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE farm_equipment SET name = ?, category = ?, model = ?, purchase_date = ?, purchase_price = ?, status = ?, maintenance_schedule = ? WHERE id = ? AND farm_id = ?",
                (name, category, model, purchase_date, purchase_price, status, maintenance_schedule, equipment_id, farm_id),
            )

    def delete_farm_equipment(self, equipment_id, farm_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM farm_equipment WHERE id = ? AND farm_id = ?", (equipment_id, farm_id))

    def add_farm_finance(self, farm_id, type_, category, amount, description, transaction_date):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO farm_finances (farm_id, type, category, amount, description, transaction_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (farm_id, type_, category, amount, description, transaction_date, created_at),
            )

    def get_farm_finances(self, farm_id, type_=None):
        with self.get_connection() as conn:
            if type_:
                rows = conn.execute(
                    "SELECT * FROM farm_finances WHERE farm_id = ? AND type = ? ORDER BY transaction_date DESC",
                    (farm_id, type_),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM farm_finances WHERE farm_id = ? ORDER BY transaction_date DESC",
                    (farm_id,),
                ).fetchall()
        return [dict(row) for row in rows]

    def get_farm_finance(self, finance_id, farm_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM farm_finances WHERE id = ? AND farm_id = ?",
                (finance_id, farm_id),
            ).fetchone()
        return dict(row) if row else None

    def update_farm_finance(self, finance_id, farm_id, type_, category, amount, description, transaction_date):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE farm_finances SET type = ?, category = ?, amount = ?, description = ?, transaction_date = ? WHERE id = ? AND farm_id = ?",
                (type_, category, amount, description, transaction_date, finance_id, farm_id),
            )

    def delete_farm_finance(self, finance_id, farm_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM farm_finances WHERE id = ? AND farm_id = ?", (finance_id, farm_id))

    def add_crop_yield(self, crop_plan_id, harvest_date, quantity, unit, quality_grade, notes):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO crop_yields (crop_plan_id, harvest_date, quantity, unit, quality_grade, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (crop_plan_id, harvest_date, quantity, unit, quality_grade, notes, created_at),
            )

    def get_crop_yields(self, crop_plan_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM crop_yields WHERE crop_plan_id = ? ORDER BY harvest_date DESC",
                (crop_plan_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_crop_yield(self, yield_id, crop_plan_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM crop_yields WHERE id = ? AND crop_plan_id = ?",
                (yield_id, crop_plan_id),
            ).fetchone()
        return dict(row) if row else None

    def update_crop_yield(self, yield_id, crop_plan_id, harvest_date, quantity, unit, quality_grade, notes):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE crop_yields SET harvest_date = ?, quantity = ?, unit = ?, quality_grade = ?, notes = ? WHERE id = ? AND crop_plan_id = ?",
                (harvest_date, quantity, unit, quality_grade, notes, yield_id, crop_plan_id),
            )

    def delete_crop_yield(self, yield_id, crop_plan_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM crop_yields WHERE id = ? AND crop_plan_id = ?", (yield_id, crop_plan_id))

    # ===== 农资库存扩展方法 =====
    def add_inventory_supplier(self, name, contact_person, phone, email, address):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO inventory_suppliers (name, contact_person, phone, email, address, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, contact_person, phone, email, address, created_at),
            )

    def get_inventory_suppliers(self):
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM inventory_suppliers ORDER BY name").fetchall()
        return [dict(row) for row in rows]

    def get_inventory_supplier(self, supplier_id):
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM inventory_suppliers WHERE id = ?", (supplier_id,)).fetchone()
        return dict(row) if row else None

    def update_inventory_supplier(self, supplier_id, name, contact_person, phone, email, address):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE inventory_suppliers SET name = ?, contact_person = ?, phone = ?, email = ?, address = ? WHERE id = ?",
                (name, contact_person, phone, email, address, supplier_id),
            )

    def delete_inventory_supplier(self, supplier_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM inventory_suppliers WHERE id = ?", (supplier_id,))

    def add_inventory_batch(self, inventory_item_id, supplier_id, batch_number, quantity, unit_cost, expiry_date, purchase_date):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO inventory_batches (inventory_item_id, supplier_id, batch_number, quantity, unit_cost, expiry_date, purchase_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (inventory_item_id, supplier_id, batch_number, quantity, unit_cost, expiry_date, purchase_date, created_at),
            )

    def get_inventory_batches(self, inventory_item_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT b.*, s.name as supplier_name FROM inventory_batches b LEFT JOIN inventory_suppliers s ON b.supplier_id = s.id WHERE b.inventory_item_id = ? ORDER BY b.purchase_date DESC",
                (inventory_item_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_inventory_batch(self, batch_id):
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM inventory_batches WHERE id = ?", (batch_id,)).fetchone()
        return dict(row) if row else None

    def update_inventory_batch(self, batch_id, inventory_item_id, supplier_id, batch_number, quantity, unit_cost, expiry_date, purchase_date):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE inventory_batches SET inventory_item_id = ?, supplier_id = ?, batch_number = ?, quantity = ?, unit_cost = ?, expiry_date = ?, purchase_date = ? WHERE id = ?",
                (inventory_item_id, supplier_id, batch_number, quantity, unit_cost, expiry_date, purchase_date, batch_id),
            )

    def delete_inventory_batch(self, batch_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM inventory_batches WHERE id = ?", (batch_id,))

    def add_inventory_transaction(self, inventory_item_id, type_, quantity, reason):
        transaction_date = beijing_now_str()
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO inventory_transactions (inventory_item_id, type, quantity, reason, transaction_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (inventory_item_id, type_, quantity, reason, transaction_date, created_at),
            )
            # Update inventory quantity
            if type_ == 'in':
                conn.execute(
                    "UPDATE inventory SET quantity = quantity + ?, updated_at = ? WHERE id = ?",
                    (quantity, created_at, inventory_item_id),
                )
            elif type_ == 'out':
                conn.execute(
                    "UPDATE inventory SET quantity = quantity - ?, updated_at = ? WHERE id = ?",
                    (quantity, created_at, inventory_item_id),
                )

    def get_inventory_transactions(self, inventory_item_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM inventory_transactions WHERE inventory_item_id = ? ORDER BY transaction_date DESC",
                (inventory_item_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_inventory_transaction(self, transaction_id, inventory_item_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM inventory_transactions WHERE id = ? AND inventory_item_id = ?",
                (transaction_id, inventory_item_id),
            ).fetchone()
        return dict(row) if row else None

    def delete_inventory_transaction(self, transaction_id, inventory_item_id):
        with self.get_connection() as conn:
            conn.execute(
                "DELETE FROM inventory_transactions WHERE id = ? AND inventory_item_id = ?",
                (transaction_id, inventory_item_id),
            )

    # ===== 交易市场扩展方法 =====
    def add_market_review(self, order_id, reviewer_id, rating, comment):
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO market_reviews (order_id, reviewer_id, rating, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (order_id, reviewer_id, rating, comment, created_at),
            )

    def get_market_review(self, review_id, reviewer_id=None, seller_id=None):
        with self.get_connection() as conn:
            if reviewer_id is not None:
                row = conn.execute("SELECT * FROM market_reviews WHERE id = ? AND reviewer_id = ?", (review_id, reviewer_id)).fetchone()
            elif seller_id is not None:
                row = conn.execute(
                    "SELECT mr.* FROM market_reviews mr JOIN orders o ON mr.order_id = o.id WHERE mr.id = ? AND o.seller_id = ?",
                    (review_id, seller_id),
                ).fetchone()
            else:
                row = conn.execute("SELECT * FROM market_reviews WHERE id = ?", (review_id,)).fetchone()
        return dict(row) if row else None

    def update_market_review(self, review_id, reviewer_id, rating, comment):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE market_reviews SET rating = ?, comment = ? WHERE id = ? AND reviewer_id = ?",
                (rating, comment, review_id, reviewer_id),
            )

    def delete_market_review(self, review_id, reviewer_id=None, seller_id=None):
        with self.get_connection() as conn:
            if reviewer_id is not None:
                conn.execute("DELETE FROM market_reviews WHERE id = ? AND reviewer_id = ?", (review_id, reviewer_id))
            elif seller_id is not None:
                conn.execute(
                    "DELETE FROM market_reviews WHERE id IN (SELECT mr.id FROM market_reviews mr JOIN orders o ON mr.order_id = o.id WHERE mr.id = ? AND o.seller_id = ?)",
                    (review_id, seller_id),
                )
            else:
                conn.execute("DELETE FROM market_reviews WHERE id = ?", (review_id,))

    def get_market_reviews(self, listing_id=None, seller_id=None):
        with self.get_connection() as conn:
            if listing_id:
                rows = conn.execute(
                    """
                    SELECT r.*, u.username as reviewer_name, o.quantity, l.title as item_title
                    FROM market_reviews r
                    JOIN orders o ON r.order_id = o.id
                    JOIN market_listings l ON o.listing_id = l.id
                    JOIN users u ON r.reviewer_id = u.id
                    WHERE l.id = ?
                    ORDER BY r.created_at DESC
                    """,
                    (listing_id,),
                ).fetchall()
            elif seller_id:
                rows = conn.execute(
                    """
                    SELECT r.*, u.username as reviewer_name, o.quantity, l.title as item_title
                    FROM market_reviews r
                    JOIN orders o ON r.order_id = o.id
                    JOIN market_listings l ON o.listing_id = l.id
                    JOIN users u ON r.reviewer_id = u.id
                    WHERE l.seller_id = ?
                    ORDER BY r.created_at DESC
                    """,
                    (seller_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT r.*, u.username as reviewer_name, o.quantity, l.title as item_title
                    FROM market_reviews r
                    JOIN orders o ON r.order_id = o.id
                    JOIN market_listings l ON o.listing_id = l.id
                    JOIN users u ON r.reviewer_id = u.id
                    ORDER BY r.created_at DESC
                    """,
                ).fetchall()
        return [dict(row) for row in rows]

    def add_order_tracking(self, order_id, status, location, notes):
        updated_at = beijing_now_str()
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO orders_tracking (order_id, status, location, notes, updated_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (order_id, status, location, notes, updated_at, created_at),
            )

    def get_order_tracking(self, order_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM orders_tracking WHERE order_id = ? ORDER BY updated_at DESC",
                (order_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_order_tracking(self, order_id, status, location, notes):
        updated_at = beijing_now_str()
        created_at = beijing_now_str()
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO orders_tracking (order_id, status, location, notes, updated_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (order_id, status, location, notes, updated_at, created_at),
            )

    def update_order_tracking(self, track_id, order_id, status, location, notes):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE orders_tracking SET status = ?, location = ?, notes = ?, updated_at = ? WHERE id = ? AND order_id = ?",
                (status, location, notes, beijing_now_str(), track_id, order_id),
            )

    def delete_order_tracking(self, track_id, order_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM orders_tracking WHERE id = ? AND order_id = ?", (track_id, order_id))

    # ===== 新病虫害学习中心：任务/图片/审核/作业 =====

    def create_learning_task(
        self,
        requester_id,
        crop_type,
        disease_name,
        description="",
        symptoms="",
        prevention="",
        treatment="",
    ):
        with self.get_connection() as conn:
            created_at = beijing_now_str()
            cur = conn.execute(
                """
                INSERT INTO learning_tasks (
                    requester_id, crop_type, disease_name, description,
                    symptoms, prevention, treatment, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
                """,
                (
                    requester_id,
                    crop_type,
                    disease_name,
                    description,
                    symptoms,
                    prevention,
                    treatment,
                    created_at,
                ),
            )
            return cur.lastrowid

    def add_learning_image(self, task_id, file_name, storage_path):
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO learning_images (task_id, file_name, storage_path)
                VALUES (?, ?, ?)
                """,
                (task_id, file_name, storage_path),
            )

    def get_learning_task(self, task_id):
        with self.get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM learning_tasks WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_learning_tasks_by_requester(self, requester_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT t.*,
                       (SELECT COUNT(*) FROM learning_images i WHERE i.task_id = t.id) AS image_count,
                       u.username AS requester_name
                FROM learning_tasks t
                JOIN users u ON u.id = t.requester_id
                WHERE t.requester_id = ?
                ORDER BY t.created_at DESC
                """,
                (requester_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_pending_learning_tasks(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT t.*,
                       (SELECT COUNT(*) FROM learning_images i WHERE i.task_id = t.id) AS image_count,
                       u.username AS requester_name
                FROM learning_tasks t
                JOIN users u ON u.id = t.requester_id
                WHERE t.status = 'pending'
                ORDER BY t.created_at ASC
                """,
            ).fetchall()
        return [dict(r) for r in rows]

    def get_approved_learning_tasks(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT t.*,
                       (SELECT COUNT(*) FROM learning_images i WHERE i.task_id = t.id) AS image_count,
                       u.username AS requester_name
                FROM learning_tasks t
                JOIN users u ON u.id = t.requester_id
                WHERE t.status = 'approved'
                ORDER BY t.approved_at DESC
                """,
            ).fetchall()
        return [dict(r) for r in rows]

    def review_learning_task(
        self,
        task_id,
        new_status,
        reason="",
        symptoms=None,
        prevention=None,
        treatment=None,
    ):
        assert new_status in ("approved", "rejected")
        with self.get_connection() as conn:
            if new_status == "approved":
                conn.execute(
                    """
                    UPDATE learning_tasks
                    SET status = 'approved',
                        approved_at = CURRENT_TIMESTAMP,
                        reason = ?
                    WHERE id = ?
                    """,
                    (reason, task_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE learning_tasks
                    SET status = 'rejected',
                        approved_at = NULL,
                        reason = ?
                    WHERE id = ?
                    """,
                    (reason, task_id),
                )

            # 可选：管理员可补/改知识字段
            if any(v is not None for v in (symptoms, prevention, treatment)):
                conn.execute(
                    """
                    UPDATE learning_tasks
                    SET symptoms = COALESCE(?, symptoms),
                        prevention = COALESCE(?, prevention),
                        treatment = COALESCE(?, treatment)
                    WHERE id = ?
                    """,
                    (symptoms, prevention, treatment, task_id),
                )

    def get_approved_custom_crops(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT crop_type
                FROM learning_tasks
                WHERE status = 'approved'
                ORDER BY crop_type
                """,
            ).fetchall()
        return [r["crop_type"] for r in rows]

    def get_approved_custom_diseases(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, crop_type, disease_name, symptoms, prevention, treatment, description, created_at
                FROM learning_tasks
                WHERE status = 'approved'
                ORDER BY created_at DESC
                """,
            ).fetchall()
        return [dict(r) for r in rows]

    def get_learning_images(self, task_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, file_name, storage_path, created_at
                FROM learning_images
                WHERE task_id = ?
                ORDER BY created_at ASC
                """,
                (task_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def create_train_job(self, task_id):
        with self.get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO train_jobs (task_id, status)
                VALUES (?, 'queued')
                """,
                (task_id,),
            )
            return cur.lastrowid

    def set_train_job_status(self, job_id, status, message="", log_path=None):
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE train_jobs
                SET status = ?,
                    message = ?,
                    log_path = ?,
                    started_at = CASE WHEN ? IN ('running', 'succeeded', 'failed') AND started_at IS NULL
                                      THEN CURRENT_TIMESTAMP
                                      ELSE started_at
                                 END,
                    finished_at = CASE WHEN ? IN ('succeeded', 'failed')
                                         THEN CURRENT_TIMESTAMP
                                         ELSE finished_at
                                    END
                WHERE id = ?
                """,
                (status, message, log_path, status, status, job_id),
            )

    def get_train_job(self, job_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM train_jobs WHERE id = ?", (job_id,)
            ).fetchone()
        return dict(row) if row else None

    def get_learning_task_class_map(self, task_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM learning_task_class_map WHERE task_id = ?",
                (task_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_learning_task_by_class_id(self, class_id):
        with self.get_connection() as conn:
            row = conn.execute(
                """
                SELECT t.*, m.class_id
                FROM learning_task_class_map m
                JOIN learning_tasks t ON t.id = m.task_id
                WHERE m.class_id = ?
                """,
                (int(class_id),),
            ).fetchone()
        return dict(row) if row else None

    def get_trained_learning_task_class_maps(self, exclude_task_id=None):
        query = """
            SELECT m.*, t.disease_name
            FROM learning_task_class_map m
            JOIN learning_tasks t ON t.id = m.task_id
            WHERE t.status = 'approved'
        """
        params = []
        if exclude_task_id is not None:
            query += " AND m.task_id != ?"
            params.append(exclude_task_id)
        query += " ORDER BY m.created_at ASC"
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def assign_learning_task_class(
        self,
        task_id,
        class_id,
        class_name,
        model_version_id=None,
    ):
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO learning_task_class_map (task_id, class_id, class_name, model_version_id)
                VALUES (?, ?, ?, ?)
                """,
                (task_id, class_id, class_name, model_version_id),
            )


db = Database()


def init_default_admin():
    # 仅用于本地毕设/演示：若数据库中没有 admin，则创建一个默认管理员账号
    with db.get_connection() as conn:
        row = conn.execute("SELECT id FROM users WHERE username = 'admin' LIMIT 1").fetchone()
        if row:
            # 尽量补齐 role
            conn.execute(
                "UPDATE users SET role = 'admin' WHERE username = 'admin'"
            )
            return

        conn.execute(
            """
            INSERT INTO users (username, password_hash, email, full_name, phone, role)
            VALUES (?, ?, ?, ?, ?, 'admin')
            """,
            (
                "admin",
                hash_password("admin123"),
                "admin@example.com",
                "管理员",
                "",
            ),
        )


init_default_admin()
