# 配置示例

## 颜色方案配置示例

### 1. 经典热力图配色 (蓝→红)
```python
def calculate_color_by_customer_num(customer_num, min_num, max_num):
    if customer_num is None or pd.isna(customer_num):
        return np.array([1.0, 0.647, 0.0])
    
    if max_num == min_num:
        ratio = 0.5
    else:
        ratio = (customer_num - min_num) / (max_num - min_num)
        ratio = max(0, min(1, ratio))
    
    enhanced_ratio = ratio ** 2
    
    # 蓝色到红色渐变
    cool_blue = np.array([0.0, 0.3, 1.0])    # 冷蓝色
    hot_red = np.array([1.0, 0.0, 0.0])      # 热红色
    
    color = cool_blue * (1 - enhanced_ratio) + hot_red * enhanced_ratio
    return color
```

### 2. 环保主题配色 (绿→红)
```python
def calculate_color_by_customer_num(customer_num, min_num, max_num):
    if customer_num is None or pd.isna(customer_num):
        return np.array([1.0, 0.647, 0.0])
    
    if max_num == min_num:
        ratio = 0.5
    else:
        ratio = (customer_num - min_num) / (max_num - min_num)
        ratio = max(0, min(1, ratio))
    
    enhanced_ratio = ratio ** 2
    
    # 绿色到红色 (环保主题)
    eco_green = np.array([0.0, 0.8, 0.2])    # 生态绿
    warning_red = np.array([0.9, 0.1, 0.1])  # 警告红
    
    color = eco_green * (1 - enhanced_ratio) + warning_red * enhanced_ratio
    return color
```

### 3. 商务专业配色 (灰→橙)
```python
def calculate_color_by_customer_num(customer_num, min_num, max_num):
    if customer_num is None or pd.isna(customer_num):
        return np.array([1.0, 0.647, 0.0])
    
    if max_num == min_num:
        ratio = 0.5
    else:
        ratio = (customer_num - min_num) / (max_num - min_num)
        ratio = max(0, min(1, ratio))
    
    enhanced_ratio = ratio ** 2
    
    # 商务配色
    business_gray = np.array([0.4, 0.4, 0.4])  # 商务灰
    accent_orange = np.array([1.0, 0.5, 0.0])  # 强调橙
    
    color = business_gray * (1 - enhanced_ratio) + accent_orange * enhanced_ratio
    return color
```

## 对比度调整示例

### 1. 超高对比度 (立方函数)
```python
# 在calculate_color_by_customer_num函数中修改
enhanced_ratio = ratio ** 3  # 立方函数，差异极其明显
```

### 2. 柔和对比度 (开方函数)
```python
# 在calculate_color_by_customer_num函数中修改
enhanced_ratio = ratio ** 0.5  # 开方函数，差异更柔和
```

### 3. 分段式对比度
```python
def calculate_color_by_customer_num(customer_num, min_num, max_num):
    if customer_num is None or pd.isna(customer_num):
        return np.array([1.0, 0.647, 0.0])
    
    if max_num == min_num:
        ratio = 0.5
    else:
        ratio = (customer_num - min_num) / (max_num - min_num)
        ratio = max(0, min(1, ratio))
    
    # 分段对比度增强
    if ratio < 0.3:
        enhanced_ratio = ratio * 0.5  # 低值区域变化更缓慢
    elif ratio < 0.7:
        enhanced_ratio = 0.15 + (ratio - 0.3) * 1.25  # 中值区域正常
    else:
        enhanced_ratio = 0.65 + (ratio - 0.7) * 1.17  # 高值区域变化更快
    
    bright_yellow = np.array([1.0, 1.0, 0.2])
    deep_red = np.array([0.8, 0.0, 0.0])
    
    color = bright_yellow * (1 - enhanced_ratio) + deep_red * enhanced_ratio
    return color
```

## 渐变效果配置示例

### 1. 强渐变效果 (更多层)
```python
# 在主程序中修改
gradient_layers = create_gradient_layers(orange_geom, blue_geom, color, num_layers=15)
```

### 2. 锐利边缘 (少量层)
```python
# 在主程序中修改
gradient_layers = create_gradient_layers(orange_geom, blue_geom, color, num_layers=3)
```

### 3. 自定义渐变透明度
```python
def create_gradient_layers(orange_geom, blue_geom, base_color, num_layers=10):
    """创建自定义透明度渐变层"""
    layers = []
    
    if orange_geom.is_empty or blue_geom.is_empty:
        return layers
    
    try:
        orange_boundary = orange_geom.boundary
        blue_boundary = blue_geom.boundary
        max_distance = orange_boundary.distance(blue_boundary)
        
        if max_distance <= 0:
            return layers
        
        for i in range(num_layers):
            layer_distance = (i + 1) * max_distance / num_layers
            expanded_geom = orange_geom.buffer(layer_distance)
            layer_geom = expanded_geom.intersection(blue_geom)
            
            if not layer_geom.is_empty and layer_geom.area > orange_geom.area:
                for j in range(i):
                    if j < len(layers):
                        layer_geom = layer_geom.difference(layers[j]['geometry'])
                
                layer_geom = layer_geom.difference(orange_geom)
                
                if not layer_geom.is_empty:
                    # 自定义透明度曲线 (指数衰减)
                    alpha_ratio = np.exp(-i / 3)  # 指数衰减
                    final_alpha = 0.9 * alpha_ratio
                    
                    layers.append({
                        'geometry': layer_geom,
                        'color': base_color,
                        'alpha': max(0.05, final_alpha)
                    })
    
    except Exception as e:
        print(f"创建渐变层时出错: {e}")
        return []
    
    return layers
```

## 输出格式配置示例

### 1. 高分辨率输出配置
```python
# 在create_map_for_year函数中修改
fig, ax = plt.subplots(figsize=(16, 12))  # 更大尺寸
plt.savefig(output_file, dpi=600, bbox_inches='tight')  # 高分辨率
```

### 2. 快速预览配置
```python
# 在create_map_for_year函数中修改
fig, ax = plt.subplots(figsize=(8, 6))   # 小尺寸
plt.savefig(output_file, dpi=150, bbox_inches='tight')  # 低分辨率
```

### 3. 打印优化配置
```python
# 在create_map_for_year函数中修改
fig, ax = plt.subplots(figsize=(11.7, 8.3))  # A4比例
plt.savefig(output_file, dpi=300, bbox_inches='tight', 
           facecolor='white', edgecolor='none')  # 打印优化
```

## GIF动画配置示例

### 1. 快速动画
```python
def create_gif_from_images():
    # ... 其他代码 ...
    
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=300,    # 快速切换 (300ms)
        loop=0,          # 无限循环
        optimize=True    # 优化文件大小
    )
```

### 2. 慢速展示动画
```python
def create_gif_from_images():
    # ... 其他代码 ...
    
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=2500,   # 慢速展示 (2.5秒)
        loop=1,          # 只播放一次
        optimize=True
    )
```

### 3. 倒序播放动画
```python
def create_gif_from_images():
    # ... 其他代码 ...
    
    # 正序 + 倒序播放
    forward_images = images.copy()
    backward_images = images[::-1][1:-1]  # 倒序，去除首尾避免重复
    all_images = forward_images + backward_images
    
    all_images[0].save(
        gif_path,
        save_all=True,
        append_images=all_images[1:],
        duration=800,
        loop=0
    )
```

## 中文字体配置示例

### 1. Windows系统字体
```python
# Windows常用中文字体
plt.rcParams['font.sans-serif'] = [
    'Microsoft YaHei',    # 微软雅黑
    'SimHei',            # 黑体
    'SimSun',            # 宋体
    'KaiTi'              # 楷体
]
plt.rcParams['axes.unicode_minus'] = False
```

### 2. macOS系统字体
```python
# macOS常用中文字体
plt.rcParams['font.sans-serif'] = [
    'PingFang SC',       # 苹方
    'Hiragino Sans GB',  # 冬青黑体
    'STHeiti',           # 华文黑体
    'Arial Unicode MS'   # Arial Unicode
]
plt.rcParams['axes.unicode_minus'] = False
```

### 3. Linux系统字体
```python
# Linux常用中文字体
plt.rcParams['font.sans-serif'] = [
    'Noto Sans CJK SC',  # Google Noto字体
    'WenQuanYi Micro Hei', # 文泉驿微米黑
    'DejaVu Sans',       # DejaVu Sans
    'sans-serif'         # 系统默认
]
plt.rcParams['axes.unicode_minus'] = False
```

## 错误处理配置示例

### 1. 详细日志记录
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('map_generation.log'),
        logging.StreamHandler()
    ]
)

def create_map_for_year(year):
    logging.info(f"开始处理 {year} 年数据")
    try:
        # ... 原有代码 ...
        logging.info(f"{year} 年地图生成成功")
    except Exception as e:
        logging.error(f"{year} 年地图生成失败: {e}")
        raise
```

### 2. 数据验证增强
```python
def validate_data(df, required_columns):
    """验证数据完整性"""
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要列: {missing_cols}")
    
    # 检查数据范围
    for col in df.columns[1:]:  # 跳过district列
        if df[col].isna().any():
            print(f"警告: {col} 列包含空值")
        if (df[col] < 0).any():
            print(f"警告: {col} 列包含负值")

# 在主程序开始时调用
validate_data(ratio_df, ['district', '2022', '2023', '2024', '2025'])
validate_data(customer_df, ['district', '2022', '2023', '2024', '2025'])
```

### 3. 自动备份配置
```python
import shutil
from datetime import datetime

def backup_outputs():
    """备份输出文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    if os.path.exists(output_dir):
        shutil.copytree(output_dir, backup_dir)
        print(f"输出文件已备份到: {backup_dir}")

# 在主程序结束时调用
backup_outputs()
```

---

*这些配置示例可以根据具体需求进行组合和修改。建议先测试默认配置，再逐步应用自定义设置。*
