export interface User {
  id: number;
  email: string;
  username: string;
}

export interface Asset {
  id: number;
  userId: number;
  symbol: string;
  name: string;
  type: string;
  notes?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  token: string;
}

export interface AssetsResponse {
  assets: Asset[];
}
