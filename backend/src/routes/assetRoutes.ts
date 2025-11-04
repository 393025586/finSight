import { Router } from 'express';
import {
  getAssets,
  addAsset,
  updateAsset,
  deleteAsset,
} from '../controllers/assetController';
import { authMiddleware } from '../middleware/auth';

const router = Router();

// 所有资产路由都需要认证
router.use(authMiddleware);

// GET /api/assets - 获取用户资产列表
router.get('/', getAssets);

// POST /api/assets - 添加资产
router.post('/', addAsset);

// PUT /api/assets/:id - 更新资产
router.put('/:id', updateAsset);

// DELETE /api/assets/:id - 删除资产
router.delete('/:id', deleteAsset);

export default router;
