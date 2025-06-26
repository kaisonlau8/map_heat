# 北京地图数据可视化项目

## 项目简介

这是一个基于北京行政区地理数据的动态可视化项目，能够根据CSV数据动态调整地图区域的大小和颜色，生成多年份的静态地图和GIF动画。项目支持双数据源驱动：区域面积比例和客户数量颜色映射。

## 核心功能

- 📊 **数据驱动的地图可视化** - 根据CSV数据动态调整区域大小
- 🎨 **智能颜色映射** - 基于客户数量从黄色到红色的颜色渐变
- 🌈 **渐变边缘效果** - 区域边缘的透明度渐变，提升视觉效果
- 📅 **多年份时间序列** - 支持2022-2025年数据的批量处理
- 🎬 **GIF动画生成** - 自动将多年份地图合成为动态GIF
- 🎯 **高精度匹配** - 平均误差控制在0.5%以内

## 项目结构

```
map/
├── map.py                    # 主程序文件
├── heatmap.py               # 热力图生成程序
├── beijing.geojson          # 北京行政区地理数据
├── shrink_ratio.csv         # 区域面积比例数据
├── customer_num.csv         # 客户数量数据
├── map_outputs/             # 输出目录
│   ├── 2022.png            # 2022年地图
│   ├── 2023.png            # 2023年地图
│   ├── 2024.png            # 2024年地图
│   ├── 2025.png            # 2025年地图
│   └── beijing_map_animation.gif  # GIF动画
└── README.md               # 项目文档
```

## 数据文件说明

### 1. beijing.geojson
- **格式**: GeoJSON
- **内容**: 北京16个行政区的地理边界数据
- **坐标系**: WGS84，程序中转换为UTM Zone 50N (EPSG:32650)

### 2. shrink_ratio.csv
- **格式**: CSV
- **列结构**: `district,2022,2023,2024,2025`
- **数据范围**: 0.3-1.0 (30%-100%的原始面积)
- **作用**: 控制橙色区域相对于蓝色区域的面积比例

### 3. customer_num.csv
- **格式**: CSV
- **列结构**: `district,2022,2023,2024,2025`
- **数据范围**: 981-11252 (客户数量)
- **作用**: 控制橙色区域的颜色深浅

## 技术架构

### 核心依赖
```python
geopandas >= 0.10.0    # 地理数据处理
matplotlib >= 3.5.0    # 图形可视化
pandas >= 1.3.0        # 数据处理
numpy >= 1.21.0        # 数值计算
shapely >= 1.8.0       # 几何运算
Pillow >= 8.0.0        # 图像处理（GIF生成）
```

### 关键算法

#### 1. 面积比例算法
```python
# 使用二分法查找最佳buffer距离
target_area = original_area * target_ratio
best_buffer = binary_search_buffer(geometry, target_area)
orange_geometry = blue_geometry.buffer(best_buffer)
```

#### 2. 颜色映射算法
```python
# 非线性颜色映射增强对比度
enhanced_ratio = (customer_num - min_num) / (max_num - min_num) ** 2
color = yellow * (1 - enhanced_ratio) + red * enhanced_ratio
```

#### 3. 渐变层生成算法
```python
# 创建多层透明度渐变
for i in range(num_layers):
    layer_distance = i * max_distance / num_layers
    expanded_geom = orange_geom.buffer(layer_distance)
    alpha = base_alpha * (1 - i / num_layers)
```

## 安装与运行

### 环境要求
- Python >= 3.8
- Windows/Linux/macOS

### 安装依赖
```bash
pip install geopandas matplotlib pandas numpy shapely pillow
```

### 运行程序
```bash
# 生成地图和GIF动画
python map.py

# 生成热力图（如果需要）
python heatmap.py
```

## 输出说明

### 1. 静态地图 (PNG)
- **分辨率**: 300 DPI
- **尺寸**: 12×10 英寸
- **格式**: RGB PNG
- **命名**: `YYYY.png` (如 2022.png)

### 2. GIF动画
- **文件名**: `beijing_map_animation.gif`
- **帧数**: 4帧 (2022-2025)
- **帧率**: 1 FPS
- **循环**: 无限循环
- **大小**: 约1.5MB

### 3. 颜色编码
- **🟡 亮黄色**: 客户数量最少的区域
- **🟠 橙色**: 客户数量中等的区域
- **🔴 深红色**: 客户数量最多的区域
- **🔵 蓝色**: 流失客户区域（橙色区域外的部分）
- **⚪ 白色**: 无数据区域

## 数据洞察

### 覆盖区域 (8个)
昌平区、朝阳区、大兴区、房山区、丰台区、海淀区、石景山区、通州区

### 数据趋势
- **面积比例**: 2022年95%+ → 2025年35%-85%，整体呈下降趋势
- **客户数量**: 2022年1930-11252 → 2025年981-9717，全面减少
- **领先区域**: 朝阳区在客户数量上始终领先
- **下降最快**: 海淀区2025年客户数量降至最低

## 技术特点

### 1. 高精度地理计算
- 使用UTM投影确保面积计算精度
- 二分法迭代确保面积比例误差<1%
- Shapely库提供精确的几何运算

### 2. 智能颜色映射
- 非线性映射增强视觉对比度
- 自动归一化适应不同年份的数据范围
- 平方函数让颜色差异更加明显

### 3. 视觉效果优化
- 多层透明度渐变营造立体感
- 中文字体支持确保标注清晰
- 高DPI输出保证图像质量

### 4. 批量处理能力
- 自动遍历多个年份数据
- 统一的输出格式和命名规范
- 错误处理和进度提示

## 自定义配置

### 修改颜色方案
```python
# 在 calculate_color_by_customer_num 函数中修改
bright_yellow = np.array([1.0, 1.0, 0.2])  # 起始颜色
deep_red = np.array([0.8, 0.0, 0.0])       # 结束颜色
```

### 调整渐变层数
```python
# 在主程序中修改
gradient_layers = create_gradient_layers(orange_geom, blue_geom, color, num_layers=8)
```

### 修改GIF参数
```python
# 在 create_gif_from_images 函数中修改
duration=1000,  # 每帧持续时间（毫秒）
loop=0         # 循环次数（0为无限循环）
```

## 故障排除

### 常见问题

1. **中文显示乱码**
   - 确保系统安装了中文字体
   - 检查Python环境的编码设置

2. **地理数据读取失败**
   - 确认beijing.geojson文件存在且格式正确
   - 检查文件路径和权限

3. **内存不足**
   - 减少渐变层数量
   - 降低输出图像分辨率

4. **颜色差异不明显**
   - 调整enhanced_ratio的指数（当前为2）
   - 修改颜色范围的起止值

## 版本历史

- **v3.0** - 添加GIF动画生成功能
- **v2.1** - 优化颜色对比度，增强视觉差异
- **v2.0** - 添加客户数量驱动的颜色映射
- **v1.1** - 实现橙色渐变边缘效果
- **v1.0** - 基础地图生成和区域缩放功能

## 许可证

本项目采用 MIT 许可证开源。

## 作者

- **开发者**: AI Assistant (Cascade)
- **技术栈**: Python + GeoPandas + Matplotlib
- **开发时间**: 2025年6月

---

*本文档最后更新时间: 2025-06-26*
