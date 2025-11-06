#!/usr/bin/env python
"""Initialize database"""

from database.db_manager import DatabaseManager

if __name__ == "__main__":
    print("正在初始化数据库...")
    db = DatabaseManager()
    db.create_all_tables()
    print("✅ 数据库初始化成功！")
