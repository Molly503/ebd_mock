import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

# 设置随机种子保证可重现性
np.random.seed(42)
random.seed(42)

def generate_eyebuydirect_data():
    """
    生成EyeBuyDirect模拟数据集
    包含用户信息、订单数据、行为数据等
    """
    
    print("🚀 开始生成EyeBuyDirect数据集...")
    
    # 1. 基础配置
    num_users = 5000
    start_date = datetime(2023, 1, 1).date()
    end_date = datetime(2025, 8, 17).date()
    
    # 地区配置（基于EyeBuyDirect真实业务分布）
    regions = ['US', 'Australia', 'France', 'UK', 'Japan']
    region_weights = [0.95, 0.015, 0.015, 0.01, 0.01]  # 美国95%，其他国家共5%
    region_currencies = {
        'US': 'USD', 
        'Australia': 'AUD', 
        'France': 'EUR', 
        'UK': 'GBP', 
        'Japan': 'JPY'
    }
    
    # 获客渠道配置
    channels = ['Social Media', 'Google Search', 'Direct', 'Email Marketing', 'Influencer']
    channel_weights = [0.35, 0.25, 0.20, 0.10, 0.10]
    
    # 产品配置（基于EyeBuyDirect实际产品线）
    products = {
        'Basic Frames': {'price_usd': (6, 30), 'weight': 0.4},
        'Fashion Frames': {'price_usd': (31, 80), 'weight': 0.35},
        'Premium Frames': {'price_usd': (81, 150), 'weight': 0.15},
        'Ray-Ban': {'price_usd': (151, 250), 'weight': 0.07},
        'Oakley': {'price_usd': (120, 200), 'weight': 0.03}
    }
    
    # 验证权重总和
    total_weight = sum(products[p]['weight'] for p in products.keys())
    if abs(total_weight - 1.0) > 0.001:
        print(f"⚠️ 警告：产品权重总和为 {total_weight}，将自动调整")
        for product in products:
            products[product]['weight'] = products[product]['weight'] / total_weight
    
    # 2. 生成用户数据
    print("👥 生成用户数据...")
    users_data = []
    
    for user_id in range(1, num_users + 1):
        # 随机选择地区
        region = np.random.choice(regions, p=region_weights)
        
        # 随机选择获客渠道
        channel = np.random.choice(channels, p=channel_weights)
        
        # 随机注册时间
        days_range = (end_date - start_date).days
        random_days = random.randint(0, days_range)
        registration_date = start_date + timedelta(days=random_days)
        
        # 用户年龄影响购买行为
        age = max(18, min(70, int(np.random.normal(35, 12))))
        
        users_data.append({
            'user_id': user_id,
            'region': region,
            'acquisition_channel': channel,
            'registration_date': registration_date,
            'age': age,
            'currency': region_currencies[region]
        })
    
    users_df = pd.DataFrame(users_data)
    
    # 3. 生成订单数据
    print("🛒 生成订单数据...")
    orders_data = []
    order_id = 1
    
    # 转化率配置（美国市场最成熟）
    conversion_rates = {
        'US': 0.72,       # 美国主要市场，转化率最高
        'Australia': 0.65, # 英语市场，转化率较高
        'France': 0.58,    # 欧洲市场，转化率中等
        'UK': 0.68,        # 英国市场，转化率较高
        'Japan': 0.55      # 亚洲市场，转化率稍低
    }
    
    # 获客成本配置
    cac_by_channel = {
        'Social Media': 25,
        'Google Search': 30,
        'Direct': 5,
        'Email Marketing': 10,
        'Influencer': 35
    }
    
    for _, user in users_df.iterrows():
        # 决定用户是否会购买
        if random.random() > conversion_rates[user['region']]:
            continue  # 这个用户不购买
            
        # 决定购买次数（基于市场成熟度）
        if user['region'] == 'US':
            num_orders = max(1, min(10, np.random.poisson(2.8)))  # 美国市场购买频率最高
        elif user['region'] in ['Australia', 'UK']:
            num_orders = max(1, min(10, np.random.poisson(2.2)))  # 英语市场中等
        elif user['region'] == 'France':
            num_orders = max(1, min(10, np.random.poisson(1.9)))  # 欧洲市场
        else:  # Japan
            num_orders = max(1, min(10, np.random.poisson(1.8)))  # 日本市场
        
        # 生成每个订单
        last_order_date = user['registration_date']
        
        for order_num in range(num_orders):
            # 订单时间计算
            if order_num == 0:
                # 第一单：注册后0-30天内
                days_after_reg = min(30, int(np.random.exponential(7)))
                order_date = user['registration_date'] + timedelta(days=days_after_reg)
            else:
                # 后续订单：间隔30-365天
                days_interval = max(30, min(365, int(np.random.exponential(120))))
                order_date = last_order_date + timedelta(days=days_interval)
            
            # 确保订单不超过今天
            if order_date > end_date:
                break
                
            # 选择产品 - 修复版本
            product_names = list(products.keys())
            product_weights = [products[p]['weight'] for p in product_names]
            product = np.random.choice(product_names, p=product_weights)
            
            # 价格计算
            price_range = products[product]['price_usd']
            price_usd = round(random.uniform(price_range[0], price_range[1]), 2)
            
            # 转换为当地货币
            if user['currency'] == 'JPY':
                price = round(price_usd * 150, 0)  # 1USD = 150JPY
                currency = 'JPY'
            elif user['currency'] == 'EUR':
                price = round(price_usd * 0.85, 2)  # 1USD = 0.85EUR
                currency = 'EUR'
            elif user['currency'] == 'GBP':
                price = round(price_usd * 0.75, 2)  # 1USD = 0.75GBP
                currency = 'GBP'
            elif user['currency'] == 'AUD':
                price = round(price_usd * 1.45, 2)  # 1USD = 1.45AUD
                currency = 'AUD'
            else:
                price = price_usd
                currency = 'USD'
            
            # 只有第一单计算获客成本
            customer_acquisition_cost = cac_by_channel[user['acquisition_channel']] if order_num == 0 else 0
            
            orders_data.append({
                'order_id': order_id,
                'user_id': user['user_id'],
                'order_date': order_date,
                'product': product,
                'price': price,
                'currency': currency,
                'price_usd': price_usd,  # 统一货币用于分析
                'region': user['region'],
                'acquisition_channel': user['acquisition_channel'],
                'customer_acquisition_cost': customer_acquisition_cost,
                'order_number': order_num + 1  # 用户的第几单
            })
            
            order_id += 1
            last_order_date = order_date
    
    orders_df = pd.DataFrame(orders_data)
    
    # 4. 生成Google Analytics行为数据
    print("📊 生成Google Analytics行为数据...")
    ga_data = []
    
    for _, user in users_df.iterrows():
        # 生成用户的会话数据
        user_orders = orders_df[orders_df['user_id'] == user['user_id']]
        
        # 即使没有购买的用户也会有浏览行为
        if len(user_orders) == 0:
            num_sessions = max(1, min(20, np.random.poisson(2)))  # 未转化用户的会话数
        else:
            num_sessions = max(1, min(20, len(user_orders) * np.random.poisson(3)))  # 购买用户会有更多会话
        
        for session_num in range(num_sessions):
            # 会话时间
            if len(user_orders) > 0:
                # 围绕购买时间生成会话
                order_dates = user_orders['order_date'].tolist()
                base_date = random.choice(order_dates)
                days_before = max(0, int(np.random.exponential(5)))
                session_date = base_date - timedelta(days=days_before)
                # 确保会话不早于注册时间
                if session_date < user['registration_date']:
                    session_date = user['registration_date']
            else:
                # 未购买用户的随机会话时间
                days_range = (end_date - user['registration_date']).days
                if days_range > 0:
                    random_days = random.randint(0, days_range)
                    session_date = user['registration_date'] + timedelta(days=random_days)
                else:
                    session_date = user['registration_date']
            
            # 会话指标
            page_views = max(1, min(50, np.random.poisson(8)))
            session_duration = max(10, min(1800, int(np.random.exponential(180))))  # 秒
            
            # 虚拟试戴使用（20%的用户使用）
            used_virtual_tryOn = random.random() < 0.2
            
            # 是否在这个会话中购买
            purchased_in_session = any(
                order_date == session_date for order_date in user_orders['order_date']
            ) if len(user_orders) > 0 else False
            
            ga_data.append({
                'user_id': user['user_id'],
                'session_date': session_date,
                'page_views': page_views,
                'session_duration_seconds': session_duration,
                'used_virtual_tryOn': used_virtual_tryOn,
                'purchased_in_session': purchased_in_session,
                'region': user['region'],
                'acquisition_channel': user['acquisition_channel']
            })
    
    ga_df = pd.DataFrame(ga_data)
    
    # 5. 保存数据
    print("💾 保存数据集...")
    try:
        users_df.to_csv('eyebuydirect_users.csv', index=False)
        orders_df.to_csv('eyebuydirect_orders.csv', index=False)
        ga_df.to_csv('eyebuydirect_ga_data.csv', index=False)
        print("✅ 数据文件保存成功")
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")
        return None, None, None
    
    # 6. 数据概览
    print("\n📈 数据集概览:")
    print(f"👥 用户数量: {len(users_df):,}")
    print(f"🛒 订单数量: {len(orders_df):,}")
    print(f"📊 GA会话数量: {len(ga_df):,}")
    
    if len(orders_df) > 0:
        print(f"💰 总销售额: ${orders_df['price_usd'].sum():,.2f}")
        
        print("\n🌍 按地区分布:")
        region_counts = users_df['region'].value_counts()
        for region, count in region_counts.items():
            percentage = count / len(users_df) * 100
            print(f"  {region}: {count:,} ({percentage:.1f}%)")
        
        print("\n🛒 转化率统计:")
        total_users_by_region = users_df.groupby('region').size()
        converted_users_by_region = orders_df.groupby('region')['user_id'].nunique()
        for region in total_users_by_region.index:
            total = total_users_by_region[region]
            converted = converted_users_by_region.get(region, 0)
            conversion_rate = converted / total * 100
            print(f"  {region}: {conversion_rate:.1f}% ({converted}/{total})")
    
    print("\n✅ 数据生成完成！文件已保存:")
    print("  📁 eyebuydirect_users.csv")
    print("  📁 eyebuydirect_orders.csv") 
    print("  📁 eyebuydirect_ga_data.csv")
    
    return users_df, orders_df, ga_df

if __name__ == "__main__":
    try:
        users_df, orders_df, ga_df = generate_eyebuydirect_data()
        if users_df is not None:
            print("\n🎉 数据生成成功！可以继续运行分析程序了。")
        else:
            print("\n❌ 数据生成失败，请检查错误信息")
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()