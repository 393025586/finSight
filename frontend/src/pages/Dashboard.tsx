import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { assetAPI } from '../services/api';
import { Asset } from '../types';
import { getUser, clearAuth } from '../utils/auth';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const user = getUser();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    symbol: '',
    name: '',
    type: 'stock',
    notes: '',
  });

  useEffect(() => {
    loadAssets();
  }, []);

  const loadAssets = async () => {
    try {
      setLoading(true);
      const response = await assetAPI.getAssets();
      setAssets(response.assets);
      setError('');
    } catch (err: any) {
      setError('加载资产列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const handleAddAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await assetAPI.addAsset(
        formData.symbol,
        formData.name,
        formData.type,
        formData.notes || undefined
      );
      setFormData({ symbol: '', name: '', type: 'stock', notes: '' });
      setShowAddForm(false);
      loadAssets();
    } catch (err: any) {
      alert(err.response?.data?.error || '添加失败');
    }
  };

  const handleDeleteAsset = async (id: number) => {
    if (!window.confirm('确定要删除这个资产吗？')) return;

    try {
      await assetAPI.deleteAsset(id);
      loadAssets();
    } catch (err: any) {
      alert(err.response?.data?.error || '删除失败');
    }
  };

  const getAssetTypeLabel = (type: string) => {
    const types: { [key: string]: string } = {
      stock: '股票',
      crypto: '加密货币',
      commodity: '商品',
      forex: '外汇',
      other: '其他',
    };
    return types[type] || type;
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>finSight 资产管理</h1>
          <p style={styles.welcome}>欢迎, {user?.username}!</p>
        </div>
        <button onClick={handleLogout} style={styles.logoutButton}>
          退出登录
        </button>
      </div>

      <div style={styles.content}>
        <div style={styles.toolbar}>
          <h2 style={styles.subtitle}>我的资产列表</h2>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            style={styles.addButton}
          >
            {showAddForm ? '取消' : '+ 添加资产'}
          </button>
        </div>

        {showAddForm && (
          <div style={styles.formCard}>
            <h3 style={styles.formTitle}>添加新资产</h3>
            <form onSubmit={handleAddAsset} style={styles.form}>
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>资产代码</label>
                  <input
                    type="text"
                    value={formData.symbol}
                    onChange={(e) =>
                      setFormData({ ...formData, symbol: e.target.value.toUpperCase() })
                    }
                    placeholder="如: AAPL, BTC"
                    style={styles.input}
                    required
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>资产名称</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    placeholder="如: 苹果公司"
                    style={styles.input}
                    required
                  />
                </div>
              </div>
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>资产类型</label>
                  <select
                    value={formData.type}
                    onChange={(e) =>
                      setFormData({ ...formData, type: e.target.value })
                    }
                    style={styles.select}
                  >
                    <option value="stock">股票</option>
                    <option value="crypto">加密货币</option>
                    <option value="commodity">商品</option>
                    <option value="forex">外汇</option>
                    <option value="other">其他</option>
                  </select>
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>备注（可选）</label>
                  <input
                    type="text"
                    value={formData.notes}
                    onChange={(e) =>
                      setFormData({ ...formData, notes: e.target.value })
                    }
                    placeholder="添加备注"
                    style={styles.input}
                  />
                </div>
              </div>
              <button type="submit" style={styles.submitButton}>
                添加
              </button>
            </form>
          </div>
        )}

        {error && <div style={styles.error}>{error}</div>}

        {loading ? (
          <p style={styles.loadingText}>加载中...</p>
        ) : assets.length === 0 ? (
          <div style={styles.emptyState}>
            <p style={styles.emptyText}>还没有添加任何资产</p>
            <p style={styles.emptyHint}>点击上方"添加资产"按钮开始</p>
          </div>
        ) : (
          <div style={styles.assetGrid}>
            {assets.map((asset) => (
              <div key={asset.id} style={styles.assetCard}>
                <div style={styles.assetHeader}>
                  <div>
                    <h3 style={styles.assetSymbol}>{asset.symbol}</h3>
                    <p style={styles.assetName}>{asset.name}</p>
                  </div>
                  <span style={styles.assetType}>
                    {getAssetTypeLabel(asset.type)}
                  </span>
                </div>
                {asset.notes && (
                  <p style={styles.assetNotes}>{asset.notes}</p>
                )}
                <div style={styles.assetFooter}>
                  <span style={styles.assetDate}>
                    添加于: {new Date(asset.createdAt).toLocaleDateString('zh-CN')}
                  </span>
                  <button
                    onClick={() => handleDeleteAsset(asset.id)}
                    style={styles.deleteButton}
                  >
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: 'white',
    padding: '20px 40px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#333',
    margin: 0,
  },
  welcome: {
    fontSize: '14px',
    color: '#666',
    marginTop: '4px',
  },
  logoutButton: {
    padding: '8px 16px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '40px 20px',
  },
  toolbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  subtitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#333',
  },
  addButton: {
    padding: '10px 20px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  },
  formCard: {
    backgroundColor: 'white',
    padding: '24px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    marginBottom: '24px',
  },
  formTitle: {
    fontSize: '18px',
    fontWeight: '600',
    marginBottom: '16px',
    color: '#333',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  formRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#555',
  },
  input: {
    padding: '10px 12px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    outline: 'none',
  },
  select: {
    padding: '10px 12px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    outline: 'none',
    backgroundColor: 'white',
  },
  submitButton: {
    padding: '12px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
  },
  error: {
    backgroundColor: '#fee',
    color: '#c33',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '16px',
  },
  loadingText: {
    textAlign: 'center',
    color: '#666',
    fontSize: '16px',
  },
  emptyState: {
    textAlign: 'center',
    padding: '60px 20px',
    backgroundColor: 'white',
    borderRadius: '8px',
  },
  emptyText: {
    fontSize: '18px',
    color: '#666',
    marginBottom: '8px',
  },
  emptyHint: {
    fontSize: '14px',
    color: '#999',
  },
  assetGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px',
  },
  assetCard: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  assetHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  assetSymbol: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#007bff',
    margin: 0,
  },
  assetName: {
    fontSize: '14px',
    color: '#666',
    marginTop: '4px',
  },
  assetType: {
    padding: '4px 12px',
    backgroundColor: '#e9ecef',
    borderRadius: '12px',
    fontSize: '12px',
    color: '#495057',
    fontWeight: '500',
  },
  assetNotes: {
    fontSize: '14px',
    color: '#555',
    fontStyle: 'italic',
  },
  assetFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: '12px',
    borderTop: '1px solid #eee',
  },
  assetDate: {
    fontSize: '12px',
    color: '#999',
  },
  deleteButton: {
    padding: '6px 12px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
  },
};

export default Dashboard;
