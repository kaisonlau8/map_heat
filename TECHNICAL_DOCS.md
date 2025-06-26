# 技术文档

## 代码架构详解

### 主程序结构 (map.py)

```
map.py
├── 导入依赖和环境设置
├── 数据读取和预处理
├── 颜色计算函数
├── 渐变层生成函数
├── 地图生成核心函数
├── GIF合成函数
└── 主执行流程
```

### 核心函数详解

#### 1. calculate_color_by_customer_num()
**功能**: 根据客户数量计算颜色值
**输入**: 客户数量、最小值、最大值
**输出**: RGB颜色数组

```python
def calculate_color_by_customer_num(customer_num, min_num, max_num):
    # 数据归一化 [0,1]
    ratio = (customer_num - min_num) / (max_num - min_num)
    
    # 非线性映射增强对比度
    enhanced_ratio = ratio ** 2
    
    # 颜色线性插值
    color = yellow * (1 - enhanced_ratio) + red * enhanced_ratio
    return color
```

**关键技术点**:
- 平方函数非线性映射
- 防止除零异常处理
- RGB颜色空间线性插值

#### 2. create_gradient_layers()
**功能**: 为橙色区域创建透明度渐变层
**输入**: 橙色几何体、蓝色几何体、基础颜色、层数
**输出**: 渐变层几何体列表

```python
def create_gradient_layers(orange_geom, blue_geom, base_color, num_layers=10):
    # 计算最大扩展距离
    max_distance = orange_boundary.distance(blue_boundary)
    
    # 创建多层渐变
    for i in range(num_layers):
        layer_distance = (i + 1) * max_distance / num_layers
        expanded_geom = orange_geom.buffer(layer_distance)
        layer_geom = expanded_geom.intersection(blue_geom)
        
        # 计算透明度
        alpha_ratio = 1 - (i / num_layers)
        final_alpha = 0.8 * alpha_ratio
```

**关键技术点**:
- Shapely缓冲区操作
- 几何体交集和差集运算
- 透明度递减算法

#### 3. create_map_for_year()
**功能**: 为指定年份生成完整地图
**输入**: 年份字符串
**输出**: 验证结果数据

**处理流程**:
1. 读取年份对应的比例和客户数据
2. 计算颜色映射的归一化参数
3. 遍历所有行政区，生成橙色区域
4. 创建渐变层
5. 绘制分层地图
6. 保存PNG文件

#### 4. create_gif_from_images()
**功能**: 将多张PNG图片合成GIF动画
**输入**: 无 (读取全局years变量)
**输出**: 布尔值表示成功与否

```python
def create_gif_from_images():
    # 收集PNG文件
    image_files = [f"{year}.png" for year in sorted(years)]
    
    # 加载并转换图像
    images = [Image.open(path).convert('RGB') for path in image_files]
    
    # 保存GIF
    images[0].save(gif_path, save_all=True, append_images=images[1:], 
                   duration=1000, loop=0)
```

## 算法原理

### 1. 面积精确匹配算法

使用二分法查找最佳缓冲区距离:

```python
# 目标: 找到buffer_distance使得 buffered_area ≈ target_area
min_buffer = -50000  # 最大内缩50km
max_buffer = 0       # 不外扩
tolerance = 0.01     # 1%误差容忍度

for iteration in range(50):
    mid_buffer = (min_buffer + max_buffer) / 2
    buffered_geom = original_geom.buffer(mid_buffer)
    current_ratio = buffered_geom.area / original_area
    
    if abs(current_ratio - target_ratio) < tolerance:
        return mid_buffer
    elif current_ratio > target_ratio:
        max_buffer = mid_buffer
    else:
        min_buffer = mid_buffer
```

**复杂度**: O(log n), n为搜索空间大小
**精度**: 误差控制在1%以内

### 2. 颜色映射算法

非线性颜色映射增强视觉对比度:

```python
# 线性归一化
linear_ratio = (value - min_val) / (max_val - min_val)

# 非线性增强 (平方函数)
enhanced_ratio = linear_ratio ** 2

# RGB插值
final_color = start_color * (1 - enhanced_ratio) + end_color * enhanced_ratio
```

**数学原理**: 
- 平方函数y=x²在[0,1]区间内凹函数特性
- 让小值区域颜色变化更缓慢
- 让大值区域颜色变化更快速

### 3. 渐变层生成算法

基于距离的多层透明度渐变:

```python
# 计算边界间最大距离
max_distance = orange_boundary.distance(blue_boundary)

# 生成n层渐变
for i in range(n):
    # 等距离扩展
    layer_distance = (i + 1) * max_distance / n
    
    # 透明度递减
    alpha = base_alpha * (1 - i / n)
```

**几何原理**:
- 使用Shapely的buffer操作进行几何扩展
- intersection确保渐变层在蓝色区域内
- difference避免层间重叠

## 性能优化

### 1. 内存优化
- 使用生成器避免大数组存储
- 及时释放中间几何对象
- PIL图像处理时转换为RGB模式

### 2. 计算优化
- 二分法减少迭代次数
- 向量化NumPy操作
- 避免重复的几何计算

### 3. I/O优化
- 批量文件操作
- 高效的PNG压缩
- 合理的GIF帧率设置

## 数据流图

```
shrink_ratio.csv ──┐
                   ├─→ create_map_for_year() ──→ PNG files ──┐
customer_num.csv ──┘                                         ├─→ GIF
beijing.geojson ────────────────────────────────────────────┘
```

## 错误处理机制

### 1. 数据验证
```python
# CSV数据验证
if pd.notna(value) and isinstance(value, (int, float)):
    processed_data[key] = float(value)

# 几何体验证
if not geometry.is_empty and geometry.is_valid:
    process_geometry(geometry)
```

### 2. 异常捕获
```python
try:
    # 几何操作
    result = geometry.buffer(distance)
except Exception as e:
    print(f"几何操作失败: {e}")
    return default_geometry
```

### 3. 渐进降级
- 如果渐变层生成失败，使用纯色填充
- 如果GIF生成失败，保留PNG文件
- 如果某个区域匹配失败，标记为空白区域

## 扩展接口

### 1. 自定义颜色函数
```python
def custom_color_function(value, min_val, max_val):
    # 实现自定义颜色映射逻辑
    return rgb_array
```

### 2. 自定义渐变函数
```python
def custom_gradient_function(geometry, num_layers):
    # 实现自定义渐变效果
    return gradient_layers
```

### 3. 输出格式扩展
支持添加新的输出格式:
- SVG矢量图
- PDF文档
- MP4视频

## 调试指南

### 1. 几何体可视化
```python
# 使用matplotlib直接绘制几何体
import matplotlib.pyplot as plt
from shapely.plotting import plot_polygon

fig, ax = plt.subplots()
plot_polygon(geometry, ax=ax)
plt.show()
```

### 2. 数据检查
```python
# 验证数据范围和分布
print(f"数据范围: {data.min()} - {data.max()}")
print(f"数据分布: {data.describe()}")
```

### 3. 性能分析
```python
import time
start_time = time.time()
# 执行代码
end_time = time.time()
print(f"执行时间: {end_time - start_time:.2f}秒")
```

## 配置参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| num_layers | 8 | 渐变层数量 |
| tolerance | 0.01 | 面积匹配容忍度 |
| dpi | 300 | 图像分辨率 |
| duration | 1000 | GIF帧持续时间(ms) |
| figsize | (12, 10) | 图像尺寸(英寸) |
| alpha_base | 0.8 | 基础透明度 |

---

*此技术文档详细说明了项目的内部实现原理，适合开发者参考和扩展。*
