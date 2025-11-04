import { Router } from 'express';
import { register, login } from '../controllers/authController';

const router = Router();

// POST /api/auth/register - 用户注册
router.post('/register', register);

// POST /api/auth/login - 用户登录
router.post('/login', login);

export default router;
