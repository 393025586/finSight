import { Request, Response } from 'express';
import prisma from '../config/database';
import { hashPassword, comparePassword } from '../utils/password';
import { generateToken } from '../utils/jwt';

// 用户注册
export const register = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, username, password } = req.body;

    // 验证必填字段
    if (!email || !username || !password) {
      res.status(400).json({ error: '邮箱、用户名和密码都是必填项' });
      return;
    }

    // 验证密码强度
    if (password.length < 6) {
      res.status(400).json({ error: '密码长度至少为 6 位' });
      return;
    }

    // 检查用户是否已存在
    const existingUser = await prisma.user.findFirst({
      where: {
        OR: [{ email }, { username }],
      },
    });

    if (existingUser) {
      if (existingUser.email === email) {
        res.status(400).json({ error: '该邮箱已被注册' });
        return;
      }
      if (existingUser.username === username) {
        res.status(400).json({ error: '该用户名已被使用' });
        return;
      }
    }

    // 加密密码
    const hashedPassword = await hashPassword(password);

    // 创建用户
    const user = await prisma.user.create({
      data: {
        email,
        username,
        password: hashedPassword,
      },
      select: {
        id: true,
        email: true,
        username: true,
        createdAt: true,
      },
    });

    // 生成 JWT token
    const token = generateToken({
      userId: user.id,
      email: user.email,
      username: user.username,
    });

    res.status(201).json({
      message: '注册成功',
      user,
      token,
    });
  } catch (error) {
    console.error('注册错误:', error);
    res.status(500).json({ error: '服务器错误' });
  }
};

// 用户登录
export const login = async (req: Request, res: Response): Promise<void> => {
  try {
    const { emailOrUsername, password } = req.body;

    // 验证必填字段
    if (!emailOrUsername || !password) {
      res.status(400).json({ error: '邮箱/用户名和密码都是必填项' });
      return;
    }

    // 查找用户（通过邮箱或用户名）
    const user = await prisma.user.findFirst({
      where: {
        OR: [{ email: emailOrUsername }, { username: emailOrUsername }],
      },
    });

    if (!user) {
      res.status(401).json({ error: '用户名/邮箱或密码错误' });
      return;
    }

    // 验证密码
    const isPasswordValid = await comparePassword(password, user.password);

    if (!isPasswordValid) {
      res.status(401).json({ error: '用户名/邮箱或密码错误' });
      return;
    }

    // 生成 JWT token
    const token = generateToken({
      userId: user.id,
      email: user.email,
      username: user.username,
    });

    res.json({
      message: '登录成功',
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
      },
      token,
    });
  } catch (error) {
    console.error('登录错误:', error);
    res.status(500).json({ error: '服务器错误' });
  }
};
