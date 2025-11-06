"""
finSight - Minimal API for Testing Authentication
只包含认证功能的最小化版本，用于快速测试
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import modules
from database.db_manager import DatabaseManager
from user_management.auth import AuthManager

# Initialize FastAPI app
app = FastAPI(
    title="finSight API - Minimal",
    description="Authentication Testing Version",
    version="2.0.0-minimal"
)

# CORS configuration - 允许所有来源（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
db = DatabaseManager()
auth_manager = AuthManager(db)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    db.create_all_tables()
    print("✅ finSight Minimal API started successfully")
    print("📝 只包含认证功能")
    print("🌐 CORS: 允许所有来源")
    print("📍 Server: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")


# ==================== Pydantic Models ====================

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    identifier: str  # email or username
    password: str


# ==================== Auth Dependency ====================

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current user from token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        token = authorization.replace("Bearer ", "")
        user = auth_manager.validate_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# ==================== Authentication Routes ====================

@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        print(f"📝 注册请求: {user_data.username} ({user_data.email})")
        result = auth_manager.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password
        )
        print(f"✅ 注册成功: 用户ID {result['user']['id']}")
        return result
    except ValueError as e:
        print(f"❌ 注册失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ 系统错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    try:
        print(f"🔐 登录请求: {credentials.identifier}")
        result = auth_manager.login(
            identifier=credentials.identifier,
            password=credentials.password
        )
        print(f"✅ 登录成功: 用户ID {result['user']['id']}")
        return result
    except ValueError as e:
        print(f"❌ 登录失败: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        print(f"❌ 系统错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/auth/me")
async def get_me(current_user=Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-minimal",
        "message": "Authentication API is running"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "finSight API - Minimal Version",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "me": "GET /api/auth/me"
        }
    }


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    print("\n" + "="*60)
    print("🚀 Starting finSight Minimal API")
    print("="*60)
    print(f"📍 Server: http://{host}:{port}")
    print(f"📖 API Docs: http://localhost:{port}/docs")
    print(f"🔧 Features: Authentication Only")
    print(f"🌐 CORS: All origins allowed")
    print("="*60 + "\n")

    uvicorn.run(
        "main_minimal:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
