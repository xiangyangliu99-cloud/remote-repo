"""
误差分析模块
计算数值解与精确解之间的误差
"""

import numpy as np


class SolutionNorm:
    """
    解的范数计算类
    """
    
    @staticmethod
    def l2_norm(u, dx, dy):
        """
        计算L2范数
        ||u||_2 = sqrt(sum(u²) * dx * dy)
        
        Args:
            u (ndarray): 解场
            dx (float): x方向步长
            dy (float): y方向步长
            
        Returns:
            float: L2范数值
        """
        return np.sqrt(np.sum(u ** 2) * dx * dy)
    
    @staticmethod
    def l_inf_norm(u):
        """
        计算L∞范数
        ||u||_∞ = max(|u|)
        
        Args:
            u (ndarray): 解场
            
        Returns:
            float: L∞范数值
        """
        return np.max(np.abs(u))
    
    @staticmethod
    def l1_norm(u, dx, dy):
        """
        计算L1范数
        ||u||_1 = sum(|u|) * dx * dy
        
        Args:
            u (ndarray): 解场
            dx (float): x方向步长
            dy (float): y方向步长
            
        Returns:
            float: L1范数值
        """
        return np.sum(np.abs(u)) * dx * dy


class ErrorAnalyzer:
    """
    误差分析器
    计算数值误差和收敛性
    """
    
    def __init__(self, grid):
        """
        初始化误差分析器
        
        Args:
            grid (Grid): 网格对象
        """
        self.grid = grid
        self.dx = grid.dx
        self.dy = grid.dy
    
    def compute_l2_error(self, u_numeric, u_exact):
        """
        计算L2误差
        e_2 = ||u_numeric - u_exact||_2
        
        Args:
            u_numeric (ndarray): 数值解
            u_exact (ndarray): 精确解
            
        Returns:
            float: L2误差
        """
        error = u_numeric - u_exact
        return SolutionNorm.l2_norm(error, self.dx, self.dy)
    
    def compute_l_inf_error(self, u_numeric, u_exact):
        """
        计算L∞误差
        e_∞ = ||u_numeric - u_exact||_∞
        
        Args:
            u_numeric (ndarray): 数值解
            u_exact (ndarray): 精确解
            
        Returns:
            float: L∞误差
        """
        error = u_numeric - u_exact
        return SolutionNorm.l_inf_norm(error)
    
    def compute_l1_error(self, u_numeric, u_exact):
        """
        计算L1误差
        e_1 = ||u_numeric - u_exact||_1
        
        Args:
            u_numeric (ndarray): 数值解
            u_exact (ndarray): 精确解
            
        Returns:
            float: L1误差
        """
        error = u_numeric - u_exact
        return SolutionNorm.l1_norm(error, self.dx, self.dy)
    
    def compute_relative_error(self, u_numeric, u_exact):
        """
        计算相对误差
        e_rel = ||u_numeric - u_exact||_2 / ||u_exact||_2
        
        Args:
            u_numeric (ndarray): 数值解
            u_exact (ndarray): 精确解
            
        Returns:
            float: 相对误差
        """
        u_exact_norm = SolutionNorm.l2_norm(u_exact, self.dx, self.dy)
        
        if u_exact_norm < 1e-15:
            return 0.0
        
        error = self.compute_l2_error(u_numeric, u_exact)
        return error / u_exact_norm
    
    def compute_all_errors(self, u_numeric, u_exact):
        """
        计算所有误差类型
        
        Args:
            u_numeric (ndarray): 数值解
            u_exact (ndarray): 精确解
            
        Returns:
            dict: 包含各种误差的字典
        """
        return {
            'l2': self.compute_l2_error(u_numeric, u_exact),
            'l_inf': self.compute_l_inf_error(u_numeric, u_exact),
            'l1': self.compute_l1_error(u_numeric, u_exact),
            'relative': self.compute_relative_error(u_numeric, u_exact)
        }
    
    def compute_convergence_order(self, errors_fine, errors_coarse):
        """
        计算收敛阶
        p = log(e_coarse / e_fine) / log(2)
        
        Args:
            errors_fine (ndarray): 细网格误差
            errors_coarse (ndarray): 粗网格误差
            
        Returns:
            ndarray: 收敛阶
        """
        # 避免除以零
        valid_idx = errors_fine > 1e-15
        
        convergence_order = np.zeros_like(errors_fine)
        convergence_order[valid_idx] = np.log(errors_coarse[valid_idx] / errors_fine[valid_idx]) / np.log(2)
        
        return convergence_order
    
    def analyze_grid_convergence(self, results_dict):
        """
        分析网格收敛性
        
        Args:
            results_dict (dict): 不同网格大小的求解结果字典
                                 key: 网格大小, value: 结果字典
            
        Returns:
            dict: 包含收敛性分析的字典
        """
        grid_sizes = sorted(results_dict.keys())
        
        convergence_data = {}
        
        for i, nx in enumerate(grid_sizes):
            result = results_dict[nx]
            u_final = result['final_solution']
            
            convergence_data[nx] = {
                'u_final': u_final,
                'u_max': np.max(u_final),
                'u_mean': np.mean(u_final),
                'u_energy': np.sum(u_final ** 2)
            }
        
        return convergence_data
    
    def __str__(self):
        return f"ErrorAnalyzer: {self.grid.nx}×{self.grid.ny}"
