"""
网格管理模块
负责定义计算网格的离散化参数和坐标生成
"""

import numpy as np


class Grid:
    """
    2D笛卡尔网格类
    
    用于管理计算域的离散化，包括网格点数、坐标、间距等
    """
    
    def __init__(self, nx, ny=None, x_range=(0, 1), y_range=(0, 1)):
        """
        初始化网格
        
        Args:
            nx (int): x方向网格点数
            ny (int): y方向网格点数，默认等于nx（正方形网格）
            x_range (tuple): x方向范围 (x_min, x_max)
            y_range (tuple): y方向范围 (y_min, y_max)
        """
        self.nx = nx
        self.ny = ny if ny is not None else nx
        self.x_min, self.x_max = x_range
        self.y_min, self.y_max = y_range
        
        # 计算网格间距
        self.dx = (self.x_max - self.x_min) / (self.nx - 1)
        self.dy = (self.y_max - self.y_min) / (self.ny - 1)
        
        # 生成网格坐标
        self.x = np.linspace(self.x_min, self.x_max, self.nx)
        self.y = np.linspace(self.y_min, self.y_max, self.ny)
        
        # 2D网格矩阵
        self.X, self.Y = np.meshgrid(self.x, self.y, indexing='ij')
        
        # 网格点总数
        self.total_points = self.nx * self.ny
        
    def get_interior_indices(self):
        """获取内部点的索引（不含边界）"""
        indices = np.arange(1, self.nx - 1)
        return indices
    
    def get_boundary_indices(self):
        """获取边界点的索引"""
        boundary_x = np.concatenate([np.zeros(self.ny, dtype=int), 
                                     np.full(self.ny, self.nx - 1, dtype=int)])
        boundary_y = np.concatenate([np.arange(self.ny), np.arange(self.ny)])
        return boundary_x, boundary_y
    
    def __str__(self):
        return (f"Grid: {self.nx}×{self.ny}\n"
                f"Domain: [{self.x_min}, {self.x_max}] × [{self.y_min}, {self.y_max}]\n"
                f"Spacing: dx={self.dx:.6f}, dy={self.dy:.6f}")
