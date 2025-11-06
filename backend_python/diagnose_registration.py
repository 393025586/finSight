#!/usr/bin/env python
"""诊断注册问题"""

import sys
from database.db_manager import DatabaseManager
from user_management.auth import AuthManager

def test_new_user_registration():
    """测试注册新用户"""
    print("=" * 60)
    print("finSight 注册功能诊断")
    print("=" * 60)

    db = DatabaseManager()
    auth_manager = AuthManager(db)

    # 使用唯一的测试数据
    import random
    random_id = random.randint(1000, 9999)
    test_email = f"newuser{random_id}@example.com"
    test_username = f"newuser{random_id}"
    test_password = "mypassword123"

    print(f"\n📝 测试数据：")
    print(f"  邮箱: {test_email}")
    print(f"  用户名: {test_username}")
    print(f"  密码: {test_password}")

    # 步骤1：检查数据库连接
    print(f"\n1️⃣ 检查数据库连接...")
    try:
        with db.get_session() as session:
            print("  ✅ 数据库连接成功")
    except Exception as e:
        print(f"  ❌ 数据库连接失败: {e}")
        return False

    # 步骤2：检查现有用户
    print(f"\n2️⃣ 检查现有用户...")
    existing_user = db.get_user_by_email(test_email)
    if existing_user:
        print(f"  ⚠️  邮箱已存在")
    else:
        print(f"  ✅ 邮箱可用")

    # 步骤3：测试注册
    print(f"\n3️⃣ 尝试注册新用户...")
    try:
        result = auth_manager.register_user(
            email=test_email,
            username=test_username,
            password=test_password
        )

        print(f"  ✅ 注册成功！")
        print(f"\n📊 注册结果：")
        print(f"  用户ID: {result['user']['id']}")
        print(f"  用户名: {result['user']['username']}")
        print(f"  邮箱: {result['user']['email']}")
        print(f"  Token: {result['access_token'][:50]}...")

        # 步骤4：验证用户已创建
        print(f"\n4️⃣ 验证用户已创建...")
        created_user = db.get_user_by_username(test_username)
        if created_user:
            print(f"  ✅ 用户在数据库中找到")
            print(f"     ID: {created_user.id}")
            print(f"     用户名: {created_user.username}")
            print(f"     邮箱: {created_user.email}")
        else:
            print(f"  ❌ 用户在数据库中未找到")
            return False

        # 步骤5：测试登录
        print(f"\n5️⃣ 测试用新账号登录...")
        login_result = auth_manager.login(
            identifier=test_username,
            password=test_password
        )
        print(f"  ✅ 登录成功！")
        print(f"  Token: {login_result['access_token'][:50]}...")

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！注册功能正常工作")
        print("=" * 60)

        return True

    except ValueError as e:
        print(f"  ❌ 注册失败（业务逻辑错误）")
        print(f"  错误信息: {str(e)}")

        # 详细诊断
        print(f"\n🔍 详细诊断：")
        if "Email already registered" in str(e):
            print(f"  - 问题：邮箱已被注册")
            print(f"  - 建议：使用不同的邮箱地址")
        elif "Username already taken" in str(e):
            print(f"  - 问题：用户名已被占用")
            print(f"  - 建议：使用不同的用户名")
        elif "Password" in str(e):
            print(f"  - 问题：密码格式错误")
            print(f"  - 建议：密码至少6个字符")
        else:
            print(f"  - 未知错误")

        return False

    except Exception as e:
        print(f"  ❌ 注册失败（系统错误）")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")

        print(f"\n🔍 堆栈跟踪：")
        import traceback
        traceback.print_exc()

        return False


def check_existing_users():
    """查看现有用户"""
    print("\n" + "=" * 60)
    print("查看数据库中现有用户")
    print("=" * 60)

    db = DatabaseManager()

    try:
        with db.get_session() as session:
            from database.models import User
            users = session.query(User).all()

            if not users:
                print("\n  数据库中没有用户")
            else:
                print(f"\n  找到 {len(users)} 个用户：")
                for user in users:
                    print(f"\n  用户 #{user.id}")
                    print(f"    用户名: {user.username}")
                    print(f"    邮箱: {user.email}")
                    print(f"    创建时间: {user.created_at}")
                    print(f"    状态: {'活跃' if user.is_active else '未激活'}")
    except Exception as e:
        print(f"\n  ❌ 查询失败: {e}")


if __name__ == "__main__":
    print("\n🚀 开始诊断...")

    # 先查看现有用户
    check_existing_users()

    # 然后测试注册
    success = test_new_user_registration()

    if success:
        print("\n✅ 注册功能工作正常！")
        print("\n💡 如果前端注册失败，可能的原因：")
        print("   1. 前端API地址配置错误")
        print("   2. CORS配置问题")
        print("   3. 服务器未启动")
        print("   4. 邮箱或用户名已存在")
        sys.exit(0)
    else:
        print("\n❌ 注册功能有问题，请查看上面的错误信息")
        sys.exit(1)
