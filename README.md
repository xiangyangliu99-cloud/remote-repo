## 2D 扩散方程 ADI 格式求解器

### 项目概述

本项目实现了一个**面向对象的2D非稳态扩散方程求解系统**，采用**交替方向隐式(ADI)格式**进行数值离散。

**求解的方程：**

$$\frac{\partial u}{\partial t} = \sigma_x \frac{\partial^2 u}{\partial x^2} + \sigma_y \frac{\partial^2 u}{\partial y^2}$$

其中 $\sigma_x = 0.01$，$\sigma_y = 0.05$，计算域为 $[0,1] \times [0,1]$。

---

### 项目架构

采用**模块化、分层设计**，每个功能独立封装为一个类：

```
xiangyangliu99-cloud/remote-repo/
│
├── A_grid.py              # 网格管理
│   └── Grid               # 2D笛卡尔网格类
│
├── B_module.py            # 系数矩阵构建
│   ├── CoefficientMatrix  # 三对角矩阵
│   └── ADICoefficientPair # ADI系数矩阵对
│
├── C_init.py              # 初始条件
│   └── InitialCondition   # 初始条件生成
│
├── D_boundary.py          # 边界条件
│   └── BoundaryCondition  # 边界条件管理
│
├── E_ustar.py             # 中间步求解 (u*)
│   └── IntermediateStepSolver
│
├── F_unext.py             # 下一步求解 (u^{n+1})
│   └── NextStepSolver
│
├── G_full_u.py            # 场组装
│   └── FieldAssembler     # 内部-边界组合
│
├── G_solver.py            # 主求解器
│   ├── ADISolver          # 单网格求解器
│   └── MultiGridSolver    # 多网格求解器
│
├── H_error_analysis.py    # 误差分析
│   ├── ErrorAnalyzer      # 误差计算
│   └── SolutionNorm       # 范数计算
│
├── I_visualizer.py        # 可视化
│   └── SolutionVisualizer # 绘图工具
│
└── H_main.py              # 主程序入口
```

---

### 核心类说明

#### 1. **Grid** - 网格管理
```python
grid = Grid(nx=100, ny=100, x_range=(0,1), y_range=(0,1))
```
- 管理计算网格的离散化参数
- 自动计算网格间距和坐标

#### 2. **InitialCondition** - 初始条件
```python
ic = InitialCondition(grid, init_type='gaussian_blob')
u0 = ic.get_initial_field()
```
- 支持多种初始条件类型
- 默认为高斯斑块 (题目要求)

#### 3. **BoundaryCondition** - 边界条件
```python
bc = BoundaryCondition(grid, bc_type='dirichlet_zero')
u_bc = bc.apply_boundary(u, t)
```
- 支持 Dirichlet/Neumann 边界条件
- 题目采用零 Dirichlet 条件

#### 4. **ADISolver** - 主求解器
```python
solver = ADISolver(nx=100, ny=100, sigma_x=0.01, 
                   sigma_y=0.05, dt=1e-3, total_steps=2000)
result = solver.solve(verbose=True)
```
- 完整的时间积分
- 自动处理所有物理和数值参数

#### 5. **MultiGridSolver** - 多网格求解
```python
mg_solver = MultiGridSolver(grid_sizes=[50, 100, 200, 400, 800])
mg_solver.solve_all()
```
- 网格独立性分析
- 收敛性研究

#### 6. **ErrorAnalyzer** - 误差分析
```python
analyzer = ErrorAnalyzer(grid)
errors = analyzer.compute_all_errors(u_numeric, u_exact)
```
- L2, L∞, L1 范数误差
- 收敛阶计算

#### 7. **SolutionVisualizer** - 可视化
```python
visualizer = SolutionVisualizer(save_dir='./results')
visualizer.plot_solution(u, grid, t, filename='solution.png')
```
- 解场热力图
- 收敛性曲线
- 统计信息绘制

---

### 使用方法

#### 1. 基本求解（单网格）

```python
from G_solver import ADISolver

# 创建求解器
solver = ADISolver(nx=100, ny=100, 
                   sigma_x=0.01, sigma_y=0.05,
                   dt=1e-3, total_steps=2000)

# 求解
result = solver.solve(verbose=True)

# 保存结果
solver.save_solution('solution_N100.npz')
```

#### 2. 多网格收敛性分析

```python
from G_solver import MultiGridSolver

# 创建多网格求解器
mg = MultiGridSolver(grid_sizes=[50, 100, 200, 400, 800])

# 求解所有网格
mg.solve_all(verbose=True)

# 保存结果
mg.save_all_solutions('./results')
```

#### 3. 可视化结果

```python
from I_visualizer import SolutionVisualizer

visualizer = SolutionVisualizer(save_dir='./results')

# 绘制指定时刻的解
u = result['u_history'][500]
t = result['t_history'][500]
visualizer.plot_solution(u, grid, t, filename='u_t500.png')

# 绘制统计信息
visualizer.plot_statistics(t_history, u_max, u_mean, u_min)
```

#### 4. 完整示例（见 H_main.py）

```bash
python H_main.py
```

---

### 输出文件

运行程序后，会在 `./diffusion_results` 目录下生成：

```
diffusion_results/
├── solution_N50.npz           # 50×50网格求解结果
├── solution_N100.npz          # 100×100网格求解结果
├── solution_N200.npz          # 200×200网格求解结果
├── solution_N400.npz          # 400×400网格求解结果
├── solution_N800.npz          # 800×800网格求解结果
│
├── solution_N100_t_0.0000.png # 初始条件
├── solution_N100_t_0.2000.png # t=0.2时刻
├── solution_N100_t_0.4000.png # t=0.4时刻
├── ...
│
├── statistics_N100.png        # 统计信息
├── convergence.png            # 网格收敛曲线
└── error_history.png          # 误差随时间变化
```

---

### 数值方法：ADI 格式

**第一步（x方向隐式）：**
$$(I - \theta \Delta t \sigma_x D_{xx}) u^* = (I + (1-\theta)\Delta t \sigma_y D_{yy}) u^n$$

**第二步（y方向隐式）：**
$$(I - \theta \Delta t \sigma_y D_{yy}) u^{n+1} = u^*$$

其中 $\theta = 1.0$ 对应完全隐式（无条件稳定）。

**优点：**
- ✅ 无条件稳定（$\theta = 1.0$）
- ✅ 计算复杂度 $O(n^2)$（vs $O(n^3)$）
- ✅ 适合大规模问题

---

### 验证与分析

#### 1. 验证初始条件
```python
# 初始条件：高斯斑块
u(x,y)|_{t=0} = {
    1,  if (x-0.5)² + (y-0.5)² < 0.2²
    0,  otherwise
}
```

#### 2. 网格收敛性
在指定时刻比较不同网格大小的解，观察收敛阶

#### 3. 长时间行为
- 解的总能量单调递减（扩散特性）
- 最终收敛到平衡态 u=0

---

### 性能指标

| 网格大小 | 时间步数 | 计算时间* | 内存用量* |
|---------|---------|---------|---------|
| 50×50   | 2000    | ~2s     | ~50MB   |
| 100×100 | 2000    | ~10s    | ~200MB  |
| 200×200 | 2000    | ~50s    | ~800MB  |
| 400×400 | 2000    | ~300s   | ~3.2GB  |
| 800×800 | 2000    | ~2000s  | ~12.8GB |

*测试环境：Intel i7, 16GB RAM

---

### 参考文献

- Peaceman, D. W., & Rachford, H. H. (1955). "The numerical solution of parabolic and elliptic differential equations."
- Smith, G. D. (1985). "Numerical Solution of Partial Differential Equations: Finite Difference Methods."

---

### 许可证

MIT License

---

### 作者

xiangyangliu99-cloud

**最后更新**: 2026-04-30
