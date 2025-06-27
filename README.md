# 区域数据可视化工具配置说明

## 概述

`config.py` 是一个统一的配置脚本，可以方便地管理和运行地图生成和热力图生成功能。本工具支持任何城市或区域的数据可视化分析。

## 功能特性

### 1. 地图生成模式
支持3种区域名称显示模式：
- **all**: 显示所有区域名称
- **partial**: 只显示有数据的区域名称  
- **none**: 不显示任何区域名称

### 2. 热力图生成
- 生成客户流失率热力图
- 百分比格式显示，更直观

### 3. 批量处理
- 可以一次性生成所有模式
- 自动组织文件结构

## 使用方法

### 方法1：交互式菜单运行
```bash
python config.py
```

然后按提示选择：
```
1. Generate map - Show all region names
2. Generate map - Show partial region names (data regions only)  
3. Generate map - Hide all region names
4. Generate heatmap
5. Generate all 3 map modes + heatmap
6. Custom mode selection
0. Exit
```

### 方法2：直接调用函数
```python
import config

# 生成单一模式地图
config.run_map_generation(['partial'])

# 生成热力图
config.run_heatmap_generation()

# 生成所有模式
config.run_map_generation(['all', 'partial', 'none'])
```

### 方法3：演示脚本
```bash
python demo.py
```
一次性生成所有模式的地图和热力图

## 数据文件要求

使用本工具需要准备以下数据文件：
- `heat_map.csv` - 客户流失数据（必需）
- `map.geojson` - 地理边界数据（必需）
- `shrink_ratio.csv` - 比例数据（必需）
- `customer_num.csv` - 客户数量数据（必需）

## 输出文件结构

```
map_outputs/
├── all/                    # 显示所有区域名称
│   ├── 2022.png
│   ├── 2023.png
│   ├── 2024.png
│   ├── 2025.png
│   └── map_animation_all.gif
├── partial/                # 只显示有数据区域名称  
│   ├── 2022.png
│   ├── 2023.png
│   ├── 2024.png
│   ├── 2025.png
│   └── map_animation_partial.gif
└── none/                   # 不显示区域名称
    ├── 2022.png
    ├── 2023.png
    ├── 2024.png
    ├── 2025.png
    └── map_animation_none.gif

heatmap_output/             # 热力图输出
├── customer_churn_heatmap.png
└── heatmap_analysis.txt
```

## 功能说明

### 地图生成
- 每种模式生成4张年度地图（2022-2025）
- 自动生成GIF动画展示时间序列变化
- 根据模式自动调整区域名称标注

### 热力图生成  
- 客户流失率数据以百分比格式显示
- 生成热力图图片和分析报告
- 包含统计信息和趋势分析

## 技术特性

- ✅ 支持多种显示模式
- ✅ 自动文件夹管理
- ✅ 错误处理和日志输出
- ✅ 模块化设计，易于扩展
- ✅ 编码兼容性优化

## 依赖文件

确保以下文件存在：
- `map.py` - 地图生成主程序
- `heatmap.py` - 热力图生成程序
- `beijing_heat.csv` - 客户流失数据
- 其他必要的数据文件和地图文件

## 故障排除

1. **编码错误**: 脚本已优化编码兼容性
2. **文件缺失**: 检查数据文件是否存在
3. **权限问题**: 确保输出目录有写入权限

## 更新日志

- v2.0: 添加多种显示模式支持
- v1.1: 优化编码兼容性  
- v1.0: 初始版本
