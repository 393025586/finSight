import { Request, Response } from 'express';
import prisma from '../config/database';

// 获取用户的资产列表
export const getAssets = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = req.user?.userId;

    if (!userId) {
      res.status(401).json({ error: '未授权' });
      return;
    }

    const assets = await prisma.asset.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });

    res.json({ assets });
  } catch (error) {
    console.error('获取资产列表错误:', error);
    res.status(500).json({ error: '服务器错误' });
  }
};

// 添加资产
export const addAsset = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = req.user?.userId;

    if (!userId) {
      res.status(401).json({ error: '未授权' });
      return;
    }

    const { symbol, name, type, notes } = req.body;

    // 验证必填字段
    if (!symbol || !name || !type) {
      res.status(400).json({ error: '资产代码、名称和类型都是必填项' });
      return;
    }

    // 检查是否已存在相同的资产
    const existingAsset = await prisma.asset.findUnique({
      where: {
        userId_symbol: {
          userId,
          symbol: symbol.toUpperCase(),
        },
      },
    });

    if (existingAsset) {
      res.status(400).json({ error: '该资产已在您的列表中' });
      return;
    }

    // 创建资产
    const asset = await prisma.asset.create({
      data: {
        userId,
        symbol: symbol.toUpperCase(),
        name,
        type,
        notes: notes || null,
      },
    });

    res.status(201).json({
      message: '资产添加成功',
      asset,
    });
  } catch (error) {
    console.error('添加资产错误:', error);
    res.status(500).json({ error: '服务器错误' });
  }
};

// 更新资产
export const updateAsset = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = req.user?.userId;
    const assetId = parseInt(req.params.id);

    if (!userId) {
      res.status(401).json({ error: '未授权' });
      return;
    }

    const { name, type, notes } = req.body;

    // 检查资产是否存在且属于当前用户
    const asset = await prisma.asset.findUnique({
      where: { id: assetId },
    });

    if (!asset || asset.userId !== userId) {
      res.status(404).json({ error: '资产不存在' });
      return;
    }

    // 更新资产
    const updatedAsset = await prisma.asset.update({
      where: { id: assetId },
      data: {
        name: name || asset.name,
        type: type || asset.type,
        notes: notes !== undefined ? notes : asset.notes,
      },
    });

    res.json({
      message: '资产更新成功',
      asset: updatedAsset,
    });
  } catch (error) {
    console.error('更新资产错误:', error);
    res.status(500).json({ error: '服务器错误' });
  }
};

// 删除资产
export const deleteAsset = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = req.user?.userId;
    const assetId = parseInt(req.params.id);

    if (!userId) {
      res.status(401).json({ error: '未授权' });
      return;
    }

    // 检查资产是否存在且属于当前用户
    const asset = await prisma.asset.findUnique({
      where: { id: assetId },
    });

    if (!asset || asset.userId !== userId) {
      res.status(404).json({ error: '资产不存在' });
      return;
    }

    // 删除资产
    await prisma.asset.delete({
      where: { id: assetId },
    });

    res.json({ message: '资产删除成功' });
  } catch (error) {
    console.error('删除资产错误:', error);
    res.status(500).json({ error: '服务器错误' });
  }
};
