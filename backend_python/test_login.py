#!/usr/bin/env python
"""测试登录功能"""

from database.db_manager import DatabaseManager
from user_management.auth import AuthManager

def test_login():
    print("=" * 50)
    print("测试用户登录功能")
    print("=" * 50)

    db = DatabaseManager()
    auth_manager = AuthManager(db)

    # 使用已存在的测试用户
    test_username = "testuser"
    test_password = "password123"

    try:
        print(f"\n登录用户: {test_username}")

        result = auth_manager.login(
            identifier=test_username,
            password=test_password
        )

        print("\n✅ 登录成功！")
        print(f"用户ID: {result['user']['id']}")
        print(f"用户名: {result['user']['username']}")
        print(f"邮箱: {result['user']['email']}")
        print(f"\nToken (前50字符): {result['access_token'][:50]}...")
        print(f"Token类型: {result['token_type']}")

        return True

    except ValueError as e:
        print(f"\n❌ 错误: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ 未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_login():
        print("\n" + "=" * 50)
        print("✅ 登录测试通过！")
        print("=" * 50)
