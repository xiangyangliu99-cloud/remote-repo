"""
主程序：2D扩散方程ADI格式求解完整示例
"""

import numpy as np
import os
from G_solver import ADISolver, MultiGridSolver
from I_visualizer import SolutionVisualizer
from H_error_analysis import ErrorAnalyzer


def main_single_grid():
    """
    单网格求解示例
    """
    print("="*70)
    print("Single Grid ADI Solver")
    print("="*70)
    
    # 创建求解器
    solver = ADISolver(nx=100, ny=100, 
                       sigma_x=0.01, sigma_y=0.05,
                       dt=1e-3, total_steps=2000,
                       init_type='gaussian_blob')
    
    # 求解
    result = solver.solve(verbose=True, save_interval=10)
    
    # 保存结果
    os.makedirs('./diffusion_results', exist_ok=True)
    solver.save_solution('./diffusion_results/solution_N100.npz')
    
    # 可视化
    visualizer = SolutionVisualizer(save_dir='./diffusion_results')
    
    # 绘制解序列
    visualizer.plot_solution_series(
        result['u_history'], result['t_history'], solver.grid,
        filename='solution_N100_series.png'
    )
    
    # 绘制统计信息
    visualizer.plot_statistics(
        result['t_history'],
        result['statistics']['u_max'],
        result['statistics']['u_min'],
        result['statistics']['u_mean'],
        filename='statistics_N100.png'
    )
    
    # 绘制能量衰减
    visualizer.plot_energy_decay(
        result['t_history'],
        result['statistics']['u_energy'],
        filename='energy_decay_N100.png'
    )
    
    # 保存指定时刻的解
    time_steps = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 1999]
    for n in time_steps:
        if n < len(result['u_history']):
            visualizer.plot_solution(
                result['u_history'][n],
                solver.grid,
                result['t_history'][n],
                filename=f"solution_N100_step_{n:04d}.png"
            )
    
    print("\nSingle grid solving completed!")


def main_multi_grid():
    """
    多网格收敛性分析示例
    """
    print("\n" + "="*70)
    print("Multi-Grid Convergence Analysis")
    print("="*70)
    
    # 创建多网格求解器
    grid_sizes = [50, 100, 200, 400, 800]
    mg_solver = MultiGridSolver(grid_sizes=grid_sizes,
                                sigma_x=0.01, sigma_y=0.05,
                                dt=1e-3, total_steps=2000)
    
    # 求解所有网格
    mg_solver.solve_all(verbose=True)
    
    # 保存所有结果
    mg_solver.save_all_solutions('./diffusion_results')
    
    # 绘制收敛性分析
    visualizer = SolutionVisualizer(save_dir='./diffusion_results')
    
    u_final_dict = {}
    for nx in grid_sizes:
        if nx in mg_solver.results:
            u_final_dict[nx] = mg_solver.results[nx]['final_solution']
    
    visualizer.plot_convergence(grid_sizes, u_final_dict,
                               filename='convergence_analysis.png')
    
    # 打印收敛性信息
    print("\nConvergence Analysis:")
    print(f"{'Grid Size':<15} {'u_max':<15} {'u_mean':<15} {'Energy':<15}")
    print("-" * 60)
    
    for nx in grid_sizes:
        if nx in mg_solver.results:
            result = mg_solver.results[nx]
            u_final = result['final_solution']
            print(f"{nx:<15} {np.max(u_final):<15.6f} "
                  f"{np.mean(u_final):<15.6f} "
                  f"{np.sum(u_final**2):<15.6f}")
    
    print("\nMulti-grid solving completed!")


def main_specified_times():
    """
    在指定时刻进行求解和分析
    """
    print("\n" + "="*70)
    print("Solving at Specified Times")
    print("="*70)
    
    # 求解
    solver = ADISolver(nx=100, ny=100,
                       sigma_x=0.01, sigma_y=0.05,
                       dt=1e-3, total_steps=2000)
    
    result = solver.solve(verbose=False, save_interval=1)
    
    visualizer = SolutionVisualizer(save_dir='./diffusion_results')
    
    # 指定时刻：t = 0.2, 0.4, 0.6, 0.8, 1.2, 1.6
    specified_times = [0.2, 0.4, 0.6, 0.8, 1.2, 1.6]
    
    print("\nSaving solutions at specified times:")
    print(f"{'Time':<10} {'Step':<10} {'u_max':<15} {'u_mean':<15}")
    print("-" * 50)
    
    for target_t in specified_times:
        # 找到最接近的时间步
        t_array = np.array(result['t_history'])
        idx = np.argmin(np.abs(t_array - target_t))
        actual_t = result['t_history'][idx]
        u = result['u_history'][idx]
        
        print(f"{target_t:<10.2f} {idx:<10} {np.max(u):<15.6f} "
              f"{np.mean(u):<15.6f}")
        
        # 保存图片
        visualizer.plot_solution(
            u, solver.grid, actual_t,
            filename=f"solution_t_{target_t:.1f}.png",
            title=f"Solution at t = {actual_t:.4f}"
        )
    
    print("\nSolutions at specified times saved!")


def main_complete():
    """
    完整的综合示例
    """
    print("="*70)
    print("Complete 2D Diffusion Equation Solver - ADI Format")
    print("="*70)
    
    # 问题参数
    print("\nProblem Setup:")
    print("  Equation: ∂u/∂t = σ_x*∂²u/∂x² + σ_y*∂²u/∂y²")
    print("  Domain: [0,1] × [0,1]")
    print("  σ_x = 0.01, σ_y = 0.05")
    print("  Initial condition: Gaussian blob at (0.5, 0.5) with radius 0.2")
    print("  Boundary condition: Dirichlet u = 0")
    print("  dt = 1e-3, total_steps = 2000\n")
    
    # 1. 单网格求解
    main_single_grid()
    
    # 2. 多网格分析
    main_multi_grid()
    
    # 3. 指定时刻求解
    main_specified_times()
    
    print("\n" + "="*70)
    print("All computations completed successfully!")
    print("Results saved in: ./diffusion_results/")
    print("="*70)


if __name__ == '__main__':
    main_complete()
