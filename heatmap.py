# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_heatmap():
    """创建各区客户流失率热力图"""
    
    # 读取数据
    df = pd.read_csv('heat_map.csv', encoding='utf-8')
    
    # 处理流失率数据，直接使用数值（数据已经是数值格式）
    df['流失率数值'] = df['客户流失率']
    
    # 将流失率转换为百分比格式用于显示
    df['流失率百分比'] = df['客户流失率'] * 100
    
    # 创建透视表用于热力图
    pivot_table = df.pivot(index='区名', columns='年份', values='流失率数值')
    
    # 创建用于标注的透视表
    count_table = df.pivot(index='区名', columns='年份', values='累计客户流失数量')
    rate_table = df.pivot(index='区名', columns='年份', values='流失率百分比')
    
    # 创建组合标注：数量 + 百分比
    combined_annotations = np.empty_like(count_table, dtype=object)
    for i in range(count_table.shape[0]):
        for j in range(count_table.shape[1]):
            count = count_table.iloc[i, j]
            rate = rate_table.iloc[i, j]
            if pd.isna(count) or pd.isna(rate):
                combined_annotations[i, j] = ''
            else:
                combined_annotations[i, j] = f'{int(count)}\n{rate:.2f}%'
    
    # 设置图形大小
    plt.figure(figsize=(30, 10))
    
    # 创建热力图
    ax = sns.heatmap(
        pivot_table,
        annot=combined_annotations,
        fmt='',
        cmap='Oranges',
        cbar_kws={'label': '客户流失率 (%)'},
        linewidths=1,
        linecolor='white',
        annot_kws={'size': 20, 'weight': 'bold', 'ha': 'center', 'va': 'center'}
    )
    
    # 设置标题和标签
    #plt.title('各区客户流失率热力图 (2022-2025年)', 
    #          fontsize=20, fontweight='bold', pad=30)
    plt.xlabel('年份', fontsize=16, fontweight='bold')
    plt.ylabel('区名', fontsize=16, fontweight='bold')
    
    # 调整坐标轴
    plt.xticks(rotation=0, fontsize=14)
    plt.yticks(rotation=0, fontsize=14)
    
    # 添加说明文字
    #plt.figtext(0.02, 0.02, 
    #            '说明：颜色越深表示流失率越高\n上行数字：客户流失数量\n下行数字：客户流失率', 
    #            fontsize=12, 
    #            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('customer_churn_heatmap.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # 显示图片
    plt.show()
    
    # 将分析结果写入文件
    with open('heatmap_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("各区客户流失率热力图分析报告\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"统计区域数量：{len(pivot_table)} 个区\n")
        f.write(f"年份范围：{pivot_table.columns.min()} - {pivot_table.columns.max()}\n")
        f.write(f"流失率范围：{pivot_table.min().min():.2f}% - {pivot_table.max().max():.2f}%\n\n")
        
        # 找到最高流失率的位置
        max_rate = pivot_table.max().max()  
        max_year = pivot_table.max().idxmax()
        max_district = pivot_table[max_year].idxmax()
        max_count = count_table.loc[max_district, max_year]
        
        f.write(f"最高流失率：{max_rate:.2f}%\n")
        f.write(f"最高流失率位置：{max_district} ({max_year}年)\n")
        f.write(f"对应流失数量：{max_count} 人\n\n")
        
        f.write("各年份平均流失率：\n")
        yearly_avg = pivot_table.mean()
        for year, rate in yearly_avg.items():
            f.write(f"  {year}年：{rate:.2f}%\n")
        
        f.write("\n各区域平均流失率（从高到低）：\n")
        district_avg = pivot_table.mean(axis=1).sort_values(ascending=False)
        for district, rate in district_avg.items():
            f.write(f"  {district}：{rate:.2f}%\n")
    
    return True

def generate_analysis_report():
    """生成各区客户流失率热力图分析报告"""
    try:
        # 读取数据
        df = pd.read_csv('heat_map.csv', encoding='utf-8')
        
        # 基本统计信息
        total_regions = len(df['区名'].unique())
        years = sorted(df['年份'].unique())
        year_range = f"{min(years)} - {max(years)}"
        
        # 计算流失率范围（转换为百分比）
        min_rate = df['客户流失率'].min() * 100
        max_rate = df['客户流失率'].max() * 100
        
        # 找到最高流失数量地区
        max_loss_row = df.loc[df['累计客户流失数量'].idxmax()]
        max_loss_region = max_loss_row['区名']
        max_loss_year = int(max_loss_row['年份'])
        max_loss_rate = max_loss_row['客户流失率'] * 100
        max_loss_count = int(max_loss_row['累计客户流失数量'])
        
        # 计算各年份平均流失率
        yearly_avg = df.groupby('年份')['客户流失率'].mean() * 100
        
        # 计算各区域平均流失率（从高到低）
        regional_avg = df.groupby('区名')['客户流失率'].mean() * 100
        regional_avg_sorted = regional_avg.sort_values(ascending=False)
        
        # 生成报告
        report = f"""各区客户流失率热力图分析报告
============================================================

统计区域数量：{total_regions} 个区
年份范围：{year_range}
流失率范围：{min_rate:.2f}% - {max_rate:.2f}%

最高流失数量地区：{max_loss_region}（{max_loss_year}年）
流失率：{max_loss_rate:.2f}%
对应流失数量：{max_loss_count} 人

各年份平均流失率："""

        for year in sorted(yearly_avg.index):
            report += f"\n  {int(year)}年：{yearly_avg[year]:.2f}%"

        report += "\n\n各区域平均流失率（从高到低）："
        for region, rate in regional_avg_sorted.items():
            report += f"\n {region}：{rate:.2f}%"
        
        report += "\n" + "="*60 + "\n"
        
        # 保存报告到文件
        with open('流失率分析报告.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 打印报告（处理编码问题）
        try:
            print(report)
        except UnicodeEncodeError:
            # 如果直接打印有问题，则只打印成功信息
            print("Analysis report generated successfully!")
            print("Report saved to: 流失率分析报告.txt")
        
        return True
        
    except Exception as e:
        print(f"Error generating analysis report: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_heatmap()
    if success:
        # 创建一个简单的成功标记文件
        with open('success.txt', 'w', encoding='utf-8') as f:
            f.write('Heatmap created successfully!')
    generate_analysis_report()
