# -*- coding: utf-8 -*-
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import get_cmap
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import scale
from PIL import Image
import sys
import os

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']  # 支持中文显示
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取北京行政区 GeoJSON
gdf = gpd.read_file("beijing.geojson")

# 读取比例数据
ratio_df = pd.read_csv("shrink_ratio.csv")

# 读取客户数量数据
customer_df = pd.read_csv("customer_num.csv")

# 投影为米制坐标（方便做面积计算）
gdf = gdf.to_crs(epsg=32650)

# 获取年份列表
years = ratio_df.columns[1:].tolist()  # 跳过第一列的district列
print(f"发现年份数据：{years}")
print(f"将生成 {len(years)} 张地图")

# 创建输出目录
output_dir = "map_outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"创建输出目录：{output_dir}")

def calculate_color_by_customer_num(customer_num, min_num, max_num):
    """根据客户数量计算颜色，从亮黄色到深红色，使用非线性映射增强对比度"""
    if customer_num is None or pd.isna(customer_num):
        # 默认橙色
        return np.array([1.0, 0.647, 0.0])
    
    # 归一化到0-1范围
    if max_num == min_num:
        ratio = 0.5  # 如果最大最小值相同，使用中间值
    else:
        ratio = (customer_num - min_num) / (max_num - min_num)
        ratio = max(0, min(1, ratio))  # 确保在0-1范围内
    
    # 使用非线性映射增强对比度（平方函数让差异更明显）
    enhanced_ratio = ratio ** 2
    
    # 使用更强烈的颜色对比：从亮黄色到深红色
    bright_yellow = np.array([1.0, 1.0, 0.2])   # 亮黄色，更鲜明
    deep_red = np.array([0.8, 0.0, 0.0])        # 深红色，更浓郁
    
    # 线性插值
    color = bright_yellow * (1 - enhanced_ratio) + deep_red * enhanced_ratio
    
    return color

def create_gradient_layers(orange_geom, blue_geom, base_color, num_layers=10):
    """创建橙色渐变层"""
    layers = []
    
    if orange_geom.is_empty or blue_geom.is_empty:
        return layers
    
    # 计算橙色区域到蓝色区域边界的最大距离
    try:
        # 获取橙色区域的边界
        orange_boundary = orange_geom.boundary
        blue_boundary = blue_geom.boundary
        
        # 计算橙色区域边界到蓝色区域边界的距离
        max_distance = orange_boundary.distance(blue_boundary)
        
        if max_distance <= 0:
            return layers
        
        # 创建橙色渐变层
        for i in range(num_layers):
            # 计算每层的扩展距离
            layer_distance = (i + 1) * max_distance / num_layers
            
            # 向外扩展橙色区域
            expanded_geom = orange_geom.buffer(layer_distance)
            
            # 确保在蓝色区域内
            layer_geom = expanded_geom.intersection(blue_geom)
            
            if not layer_geom.is_empty and layer_geom.area > orange_geom.area:
                # 减去内层的所有区域
                for j in range(i):
                    if j < len(layers):
                        layer_geom = layer_geom.difference(layers[j]['geometry'])
                
                # 减去橙色核心区域
                layer_geom = layer_geom.difference(orange_geom)
                
                if not layer_geom.is_empty:
                    # 计算橙色渐变（从橙色渐变到透明）
                    # 使用固定的橙色，只改变透明度
                    orange_rgb = base_color
                    
                    # 透明度从内到外递减
                    alpha_ratio = 1 - (i / num_layers)  # 从1到0
                    final_alpha = 0.8 * alpha_ratio  # 最高透明度0.8，向外递减
                    
                    layers.append({
                        'geometry': layer_geom,
                        'color': orange_rgb,
                        'alpha': max(0.1, final_alpha)  # 最小透明度0.1，避免完全透明
                    })
    
    except Exception as e:
        print(f"创建橙色渐变层时出错: {e}")
        return []
    
    return layers

def create_map_for_year(year):
    """为指定年份创建地图"""
    print(f"\n正在处理 {year} 年的数据...")
    
    # 创建该年份的比例字典
    orange_ratios = {}
    
    # 从CSV中读取该年份的数据
    year_data = ratio_df.set_index('district')[year]
    
    for district_name, orange_value in year_data.items():
        if pd.notna(orange_value):  # 检查是否为空值
            orange_ratios[district_name.lower()] = float(orange_value)
    
    print(f"  {year} 年有数据的区域：{list(orange_ratios.keys())}")
    
    # 创建该年份的客户数量字典
    customer_nums = {}
    
    # 从客户数量CSV中读取该年份的数据
    customer_year_data = customer_df.set_index('district')[year]
    
    for district_name, customer_value in customer_year_data.items():
        if pd.notna(customer_value):  # 检查是否为空值
            customer_nums[district_name.lower()] = int(customer_value)
    
    # 计算客户数量的最大最小值，用于颜色归一化
    if customer_nums:
        min_customer = min(customer_nums.values())
        max_customer = max(customer_nums.values())
        print(f"  {year} 年客户数量范围：{min_customer} - {max_customer}")
    else:
        min_customer = max_customer = 0
    
    # 为每个行政区创建精确比例的橙色区域
    orange_areas = []
    orange_colors = []  # 存储每个区域对应的颜色
    matched_regions = []  # 存储有CSV数据的区域
    blank_regions = []    # 存储没有CSV数据的区域（白色填充）
    validation_results = []  # 存储验证结果

    for idx, region in gdf.iterrows():
        # 获取区域名称并标准化
        region_name = region['name'].lower() if 'name' in region else str(idx)
        
        # 原始区域几何体
        blue_geom = region.geometry
        original_area = blue_geom.area
        
        # 直接使用中文名称查找对应的橙色比例
        if region_name in orange_ratios:
            target_ratio = orange_ratios[region_name]
            
            # 使用迭代方法找到合适的buffer距离来达到目标面积比例
            target_area = original_area * target_ratio
            
            # 二分法查找合适的buffer距离
            min_buffer = -50000  # 最大内缩50km
            max_buffer = 0       # 不扩大
            tolerance = 0.01     # 面积误差容忍度
            
            best_buffer = 0
            for _ in range(50):  # 最多迭代50次
                mid_buffer = (min_buffer + max_buffer) / 2
                buffered_geom = blue_geom.buffer(mid_buffer)
                
                if buffered_geom.is_empty:
                    min_buffer = mid_buffer
                    continue
                    
                current_area = buffered_geom.area
                area_ratio = current_area / original_area
                
                if abs(area_ratio - target_ratio) < tolerance:
                    best_buffer = mid_buffer
                    break
                elif area_ratio > target_ratio:
                    max_buffer = mid_buffer
                else:
                    min_buffer = mid_buffer
            
            # 生成最终的橙色区域
            orange_geom = blue_geom.buffer(best_buffer)
            
            # 确保橙色区域在蓝色区域内部
            if not orange_geom.is_empty:
                orange_geom = orange_geom.intersection(blue_geom)
            
            if orange_geom.is_empty:
                # 如果buffer操作导致空几何体，使用较小的内缩距离
                orange_geom = blue_geom.buffer(-100)  # 内缩100米
                if orange_geom.is_empty:
                    orange_geom = blue_geom  # 如果还是空的，就使用原始几何体
            
            # 计算实际面积比例
            actual_orange_area = orange_geom.area
            actual_ratio = actual_orange_area / original_area
            
            # 存储有数据的区域
            orange_areas.append(orange_geom)
            orange_colors.append(calculate_color_by_customer_num(customer_nums.get(region_name), min_customer, max_customer))
            matched_regions.append(region)
            
            # 保存验证结果
            validation_results.append({
                'district': region_name,
                'target_ratio': target_ratio,
                'actual_ratio': actual_ratio,
                'error': abs(actual_ratio - target_ratio),
                'error_percent': abs(actual_ratio - target_ratio) / target_ratio * 100,
                'status': 'matched'
            })
            
        else:
            # 没有找到对应比例，作为空白区域处理
            blank_regions.append(region)
            
            # 保存验证结果
            validation_results.append({
                'district': region_name,
                'target_ratio': None,
                'actual_ratio': None,
                'error': None,
                'error_percent': None,
                'status': 'blank'
            })

    # 绘图
    fig, ax = plt.subplots(figsize=(12, 10))

    # 1. 先画空白区域（白色填充）
    if blank_regions:
        blank_gdf = gpd.GeoDataFrame(blank_regions)
        blank_gdf.plot(ax=ax, color='white', edgecolor='black', linewidth=0.5, alpha=1.0)

    # 2. 再画有数据区域的蓝色底色
    if matched_regions:
        matched_gdf = gpd.GeoDataFrame(matched_regions)
        matched_gdf.plot(ax=ax, color='#1E90FF', alpha=0.4, edgecolor='black', linewidth=0.5)

    # 3. 为每个区域创建渐变效果
    all_gradient_layers = []
    for i, (orange_geom, blue_region, orange_color) in enumerate(zip(orange_areas, matched_regions, orange_colors)):
        # 获取蓝色区域的几何形状
        blue_geom = blue_region.geometry if hasattr(blue_region, 'geometry') else blue_region
        gradient_layers = create_gradient_layers(orange_geom, blue_geom, orange_color, num_layers=8)
        all_gradient_layers.extend(gradient_layers)
    
    # 4. 绘制渐变层（从外到内）
    for layer in reversed(all_gradient_layers):  # 从外层到内层绘制
        try:
            gpd.GeoSeries([layer['geometry']]).plot(
                ax=ax, 
                color=layer['color'], 
                alpha=layer['alpha'], 
                edgecolor='none'
            )
        except Exception as e:
            print(f"绘制渐变层时出错: {e}")
            continue

    # 5. 最后画橙色核心区域
    if orange_areas:
        gpd.GeoSeries(orange_areas).plot(
            ax=ax, color=orange_colors, alpha=0.9, edgecolor='none')

    # 手动创建图例
    # from matplotlib.patches import Patch
    # legend_elements = [
    #     Patch(facecolor='white', edgecolor='black', label='无数据区域'),
    #     Patch(facecolor='#1E90FF', alpha=0.4, label='流失客户'),
    #     Patch(facecolor='#FFA500', alpha=0.9, label='回厂客户'),
    # ]

    # 美化图层
    # plt.title(f"{year}年北京各区客户分布情况（橙色渐变效果）", fontsize=16, fontweight='bold')
    # plt.legend(handles=legend_elements, loc='upper right', fontsize=12)

    # 添加区域名称标注
    for idx, region in gdf.iterrows():
        # 获取区域的中心点
        centroid = region.geometry.centroid
        region_name = region['name'] if 'name' in region else f"区域{idx}"
        
        # 在地图上添加文本标注
        plt.text(centroid.x, centroid.y, region_name, 
                 fontsize=10, ha='center', va='center',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'),
                 fontweight='bold')

    plt.axis('off')
    plt.tight_layout()
    
    # 保存图片
    output_file = os.path.join(output_dir, f"{year}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  已保存：{output_file}")
    
    # 显示图片
    plt.show()
    
    # 输出匹配情况统计
    matched_count = len([r for r in validation_results if r['status'] == 'matched'])
    blank_count = len([r for r in validation_results if r['status'] == 'blank'])

    print(f"  {year}年匹配成功：{matched_count} 个区域")
    print(f"  {year}年空白区域：{blank_count} 个区域")
    
    # 计算有数据区域的统计
    matched_results = [r for r in validation_results if r['status'] == 'matched']
    if matched_results:
        total_error = sum(r['error'] for r in matched_results)
        avg_error = total_error / len(matched_results)
        max_error = max(r['error'] for r in matched_results)
        max_error_district = [r for r in matched_results if r['error'] == max_error][0]

        print(f"  {year}年平均误差：{avg_error:.4f} ({avg_error*100:.2f}%)")
        print(f"  {year}年最大误差：{max_error:.4f} ({max_error*100:.2f}%) in {max_error_district['district']}")
    
    return validation_results

# 主程序：为每年生成地图
all_validation_results = {}

for year in years:
    validation_results = create_map_for_year(year)
    all_validation_results[year] = validation_results

print(f"\n{'='*60}")
print("所有地图生成完成！")
print(f"共生成 {len(years)} 张地图，保存在 {output_dir} 目录中")
print(f"文件列表：")
for year in years:
    print(f"  - {year}.png")
print(f"{'='*60}")

# 生成GIF动画
def create_gif_from_images():
    """将生成的PNG图片合成为GIF动画"""
    print(f"\n开始生成GIF动画...")
    
    try:
        # 收集所有PNG文件
        image_files = []
        for year in sorted(years):  # 确保按年份顺序
            img_path = os.path.join(output_dir, f"{year}.png")
            if os.path.exists(img_path):
                image_files.append(img_path)
            else:
                print(f"警告：找不到文件 {img_path}")
        
        if len(image_files) < 2:
            print("错误：需要至少2张图片才能生成GIF")
            return False
        
        # 打开所有图片
        images = []
        for img_path in image_files:
            img = Image.open(img_path)
            # 转换为RGB模式（GIF需要）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
            print(f"  已加载：{os.path.basename(img_path)}")
        
        # 生成GIF文件
        gif_path = os.path.join(output_dir, "beijing_map_animation.gif")
        
        # 保存为GIF动画
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=1000,  # 每帧持续1秒
            loop=0  # 无限循环
        )
        
        print(f"  GIF动画已生成：{gif_path}")
        print(f"  帧数：{len(images)} 帧")
        print(f"  帧率：1帧/秒")
        print(f"  循环：无限循环")
        
        return True
        
    except Exception as e:
        print(f"生成GIF时出错：{e}")
        return False

# 执行GIF生成
gif_success = create_gif_from_images()

print(f"\n{'='*60}")
if gif_success:
    print("项目完成！")
    print(f"生成内容：")
    print(f"  - {len(years)} 张PNG地图")
    print(f"  - 1 个GIF动画")
    print(f"保存位置：{output_dir}")
else:
    print("PNG地图生成完成，但GIF生成失败")
print(f"{'='*60}")
