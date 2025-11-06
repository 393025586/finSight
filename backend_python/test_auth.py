#!/usr/bin/env python
"""测试用户认证功能"""

from database.db_manager import DatabaseManager
from user_management.auth import AuthManager

def test_register():
    print("=" * 50)
    print("测试用户注册功能")
    print("=" * 50)

    db = DatabaseManager()
    auth_manager = AuthManager(db)

    # 测试数据
    test_email = "test@example.com"
    test_username = "testuser"
    test_password = "password123"

    try:
        # 尝试注册
        print(f"\n注册用户: {test_username}")
        print(f"邮箱: {test_email}")

        result = auth_manager.register_user(
            email=test_email,
            username=test_username,
            password=test_password
        )

        print("\n✅ 注册成功！")
        print(f"用户ID: {result['user']['id']}")
        print(f"用户名: {result['user']['username']}")
        print(f"Token: {result['access_token'][:50]}...")

        # 测试登录
        print("\n" + "=" * 50)
        print("测试用户登录功能")
        print("=" * 50)

        login_result = auth_manager.login(
            identifier=test_username,
            password=test_password
        )

        print("\n✅ 登录成功！")
        print(f"用户ID: {login_result['user']['id']}")
        print(f"Token: {login_result['access_token'][:50]}...")

    except ValueError as e:
        print(f"\n❌ 错误: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ 未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_register()
    if success:
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ 测试失败")
        print("=" * 50)
