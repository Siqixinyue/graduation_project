#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智农云平台 - 页面模块

本文件包含智农云平台的所有页面函数实现，使用Streamlit框架构建用户界面。
每个页面函数对应应用中的一个功能模块，提供了完整的用户交互体验。

主要页面模块：
- auth_page: 用户认证页面（登录/注册）
- dashboard_page: 系统仪表盘，显示统计信息和概览
- diagnosis_page: 病虫害识别中心，支持图片上传和AI识别
- farm_page: 农场管理页面，管理农场信息和作物规划
- inventory_page: 农资库存管理，管理农业物资库存
- market_page: 农产品交易市场，支持买卖交易
- analytics_page: 数据分析页面，提供统计图表
- profile_page: 用户个人资料管理
- learning_page: 新病害学习中心，支持模型学习

辅助功能：
- 惠农网商品数据获取和模拟
- 市场数据刷新和更新
- 页面导航和状态管理

"""

import re
import os
import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import date, datetime

import streamlit as st
from PIL import Image
import pandas as pd

# 导入工具模块
from utils.class_names import get_class_name          # 病害类别名称获取
from utils.database import db                         # 数据库操作模块
from utils.disease_advice import get_disease_advice   # 病害防治建议获取
from utils.disease_knowledge import (
    get_crop_types,                                   # 获取作物类型
    get_disease_knowledge,                           # 获取病害知识库
    get_diseases_by_crop                             # 根据作物获取病害信息
)
from utils.model import batch_predict, predict        # AI模型推理功能

# 惠农网商品数据获取函数
def get_cnhnb_listings():
    """
    获取惠农网商品数据

    从惠农网网站抓取最新的农产品和农资商品信息，
    用于在交易市场页面展示外部商品数据。

    返回：
    - list: 商品信息列表，每个商品包含id、标题、价格、描述等信息
    """
    return [
        {
            "id": 1001,
            "seller_id": 999,  # 模拟惠农网卖家ID
            "seller_name": "湘潭县厂家",
            "title": "湘潭县新莲小颗粒精选过筛去芯带芯磨白莲",
            "category": "粮食",
            "description": "厂家直供量大从优，干度保证，货版一致，7天退换",
            "price": 14.80,
            "quantity": 1000.0,
            "unit": "斤",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 10:00:00"
        },
        {
            "id": 1002,
            "seller_id": 999,
            "seller_name": "金堂县农资店",
            "title": "阿维乙螨唑柑橘树红蜘蛛杀螨剂杀虫剂",
            "category": "农资",
            "description": "阿维菌素+乙螨唑，假货必赔，破损补发，货版一致，部分包邮",
            "price": 72.00,
            "quantity": 500.0,
            "unit": "套",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 09:30:00"
        },
        {
            "id": 1003,
            "seller_id": 999,
            "seller_name": "潍坊农资",
            "title": "土传病害30%甲霜恶霉灵果树蔬菜中药材杀菌剂",
            "category": "农资",
            "description": "根腐立枯猝倒死棵烂苗，假货必赔，破损补发，货版一致，部分包邮，7天退换",
            "price": 29.00,
            "quantity": 200.0,
            "unit": "瓶",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 08:45:00"
        },
        {
            "id": 1004,
            "seller_id": 999,
            "seller_name": "五常市厂家",
            "title": "五常大米2025源头工厂一件代发产地直发",
            "category": "粮食",
            "description": "OEM代工大宗批发，不对版包赔，坏损包赔，货版一致，部分包邮",
            "price": 34.00,
            "quantity": 5000.0,
            "unit": "袋",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 08:00:00"
        },
        {
            "id": 1005,
            "seller_id": 999,
            "seller_name": "新沂市农资",
            "title": "45%咪鲜胺炭疽病冠腐病褐斑病叶斑病柑橘果树农药杀菌剂",
            "category": "农资",
            "description": "假货必赔，破损补发，货版一致，部分包邮",
            "price": 6.80,
            "quantity": 1000.0,
            "unit": "瓶",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 07:30:00"
        },
        {
            "id": 1006,
            "seller_id": 999,
            "seller_name": "韩城市厂家",
            "title": "陕西韩城花椒产地直供香红麻净直供餐饮烹饪",
            "category": "调料",
            "description": "食品厂火锅店，不对版包赔，坏损包赔，货版一致，部分包邮，7天退换",
            "price": 11.50,
            "quantity": 2000.0,
            "unit": "斤",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 07:00:00"
        },
        {
            "id": 1007,
            "seller_id": 999,
            "seller_name": "安国市种子店",
            "title": "半夏种子半夏种苗半夏种球包芽率包邮各种规格",
            "category": "种子",
            "description": "保质保量，假种必赔，保证发芽，货版一致，部分包邮",
            "price": 8.00,
            "quantity": 300.0,
            "unit": "斤",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 06:30:00"
        },
        {
            "id": 1008,
            "seller_id": 999,
            "seller_name": "江门厂家",
            "title": "新会陈皮20年泡水老陈皮干茶陈皮一斤一罐礼盒包",
            "category": "茶叶",
            "description": "大量批发，茶厂直发，不对版包赔，货版一致，包邮",
            "price": 72.00,
            "quantity": 100.0,
            "unit": "斤",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 06:00:00"
        },
        {
            "id": 1009,
            "seller_id": 999,
            "seller_name": "鹤山市水产",
            "title": "优鲈3号鲈鱼苗全驯化吃饲料鲈鱼苗大规格苗场直供",
            "category": "水产",
            "description": "死亡包赔，规格保障，货版一致，部分包邮",
            "price": 0.25,
            "quantity": 10000.0,
            "unit": "尾",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 05:30:00"
        },
        {
            "id": 1010,
            "seller_id": 999,
            "seller_name": "信丰县果园",
            "title": "新鲜江西赣南脐橙甜蜜多汁现摘现发信丰县直供",
            "category": "水果",
            "description": "不对版包赔，坏果包赔，货版一致，部分包邮",
            "price": 19.00,
            "quantity": 500.0,
            "unit": "箱",
            "quality_level": "优",
            "status": "on_sale",
            "created_at": "2024-03-25 05:00:00"
        }
    ]

# 页面导航辅助函数
def safe_rerun():
    """
    安全的重运行函数

    根据Streamlit版本选择合适的重运行方法，
    确保在不同版本的Streamlit中都能正常工作。
    """
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.warning("请刷新页面以使导航生效")

# 备用惠农网商品数据获取函数
def get_static_cnhnb_products():
    """
    获取内置的固定惠农网商品数据

    当在线抓取失败时使用的备用商品数据，
    确保交易市场功能在网络异常时仍能正常展示商品。

    返回：
    - list: 固定商品信息列表
    """
    return [
        {
            "title": "湘潭县新莲小颗粒精选过筛去芯带芯磨白莲",
            "category": "粮食",
            "description": "厂家直供量大从优，干度保证，货版一致，7天退换",
            "price": 14.80,
            "quantity": 1000.0,
            "unit": "斤",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/7429118/",
        },
        {
            "title": "阿维乙螨唑柑橘树红蜘蛛杀螨剂杀虫剂",
            "category": "农资",
            "description": "阿维菌素+乙螨唑，假货必赔，破损补发，货版一致，部分包邮",
            "price": 72.00,
            "quantity": 500.0,
            "unit": "套",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/4652388/",
        },
        {
            "title": "土传病害30%甲霜恶霉灵果树蔬菜中药材杀菌剂",
            "category": "农资",
            "description": "根腐立枯猝倒死棵烂苗，假货必赔，破损补发，货版一致，部分包邮，7天退换",
            "price": 29.00,
            "quantity": 200.0,
            "unit": "瓶",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/8203334/",
        },
        {
            "title": "五常大米2025源头工厂一件代发产地直发",
            "category": "粮食",
            "description": "OEM代工大宗批发，不对版包赔，坏损包赔，货版一致，部分包邮",
            "price": 34.00,
            "quantity": 5000.0,
            "unit": "袋",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/8497929/",
        },
        {
            "title": "45%咪鲜胺炭疽病冠腐病褐斑病叶斑病柑橘果树农药杀菌剂",
            "category": "农资",
            "description": "假货必赔，破损补发，货版一致，部分包邮",
            "price": 6.80,
            "quantity": 1000.0,
            "unit": "瓶",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/7400184/",
        },
        {
            "title": "陕西韩城花椒产地直供香红麻净直供餐饮烹饪",
            "category": "调料",
            "description": "食品厂火锅店，不对版包赔，坏损包赔，货版一致，部分包邮，7天退换",
            "price": 11.50,
            "quantity": 2000.0,
            "unit": "斤",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/3853347/",
        },
        {
            "title": "半夏种子半夏种苗半夏种球包芽率包邮各种规格",
            "category": "种子",
            "description": "保质保量，假种必赔，保证发芽，货版一致，部分包邮",
            "price": 8.00,
            "quantity": 300.0,
            "unit": "斤",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/6742624/",
        },
        {
            "title": "新会陈皮20年泡水老陈皮干茶陈皮一斤一罐礼盒包",
            "category": "茶叶",
            "description": "大量批发，茶厂直发，不对版包赔，货版一致，包邮",
            "price": 72.00,
            "quantity": 100.0,
            "unit": "斤",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/7717776/",
        },
        {
            "title": "优鲈3号鲈鱼苗全驯化吃饲料鲈鱼苗大规格苗场直供",
            "category": "水产",
            "description": "死亡包赔，规格保障，货版一致，部分包邮",
            "price": 0.25,
            "quantity": 10000.0,
            "unit": "尾",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/8130476/",
        },
        {
            "title": "新鲜江西赣南脐橙甜蜜多汁现摘现发信丰县直供",
            "category": "水果",
            "description": "不对版包赔，坏果包赔，货版一致，部分包邮",
            "price": 19.00,
            "quantity": 500.0,
            "unit": "箱",
            "quality_level": "优",
            "source_url": "https://www.cnhnb.com/gongying/6627560/",
        },
    ]


def get_cnhnb_product_pool():
    """在线抓取惠农网供应列表，若失败则回退静态商品。"""
    try:
        url = 'https://www.cnhnb.com/supply/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.select('a.supply-line-item')
        if not cards:
            raise ValueError('没有找到惠农网商品元素')

        products = []
        for card in cards[:30]:
            title = card.select_one('.s-l-title')
            price_node = card.select_one('.s-l-r')
            title_text = title.get_text(strip=True) if title else '无名称'
            price_text = price_node.get_text(strip=True) if price_node else ''

            price = 0.0
            unit = '斤'
            # 价格格式可能为：￥33/斤 或 33/斤
            m = re.search(r'[¥￥]?\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*([^\s]+)', price_text)
            if m:
                try:
                    price = float(m.group(1))
                except Exception:
                    price = round(random.uniform(5.0, 100.0), 2)
                unit = m.group(2)
            else:
                m2 = re.search(r'[¥￥]?\s*([0-9]+(?:\.[0-9]+)?)', price_text)
                if m2:
                    price = float(m2.group(1))

            href = card.get('href', '')
            if href and href.startswith('/'):
                source_url = 'https://www.cnhnb.com' + href
            elif href.startswith('http'):
                source_url = href
            else:
                source_url = 'https://www.cnhnb.com/supply/'

            category = '农资'
            if '粮' in title_text:
                category = '粮食'
            elif '果' in title_text or '橙' in title_text or '梨' in title_text or '苹果' in title_text:
                category = '水果'
            elif '蔬' in title_text:
                category = '蔬菜'
            elif '种子' in title_text or '苗' in title_text:
                category = '种子'

            products.append({
                'title': title_text,
                'category': category,
                'description': title_text,
                'price': price,
                'quantity': float(random.randint(100, 5000)),
                'unit': unit,
                'quality_level': random.choice(['优', '良', '标准', '有机']),
                'source_url': source_url,
            })

        if not products:
            raise ValueError('惠农网抓取到的商品为空')

        return products
    except Exception as e:
        st.warning(f'实时抓取惠农网失败：{e}，使用静态备选商品。')
        return get_static_cnhnb_products()

# 模拟获取惠农网商品列表函数
def simulate_fetch_cnhnb_listings(batch_size=5):
    """
    模拟获取惠农网商品列表

    从商品池中随机选择指定数量的商品，
    删除现有的惠农网商品并添加新的随机商品到数据库。

    参数：
    - batch_size: 要获取的商品数量，默认5个

    返回：
    - list: 选中的商品列表
    """
    # 先删除所有现有的cnhnb商品，确保每次刷新显示不同的商品
    db.delete_cnhnb_listings()

    items = get_cnhnb_product_pool()
    # 使用时间作为随机种子，确保每次刷新选择不同的商品
    import time
    __import__('random').seed(time.time())
    random_items = __import__('random').sample(items, min(batch_size, len(items)))
    for item in random_items:
        db.add_or_update_external_listing(
            title=item['title'],
            category=item['category'],
            description=item['description'],
            price=item['price'],
            quantity=item['quantity'],
            unit=item['unit'],
            quality_level=item['quality_level'],
            source_url=item['source_url'],
            status='on_sale',
            source='cnhnb',
        )
    return random_items

# 市场刷新函数
def simulate_market_refresh(user_id, cnhnb_batch_size=5):
    """
    刷新整个市场：惠农网商品 + 本地商品随机重排

    重新获取惠农网商品并随机重排本地商品的显示顺序，
    模拟市场数据的动态更新。

    参数：
    - user_id: 用户ID（目前未使用）
    - cnhnb_batch_size: 惠农网商品批次大小，默认5个

    返回：
    - bool: 刷新是否成功
    """
    # 刷新惠农网商品
    simulate_fetch_cnhnb_listings(cnhnb_batch_size)

    # 重新排列本地商品的显示顺序（通过更新时间戳来改变排序）
    try:
        with db.get_connection() as conn:
            # 获取所有本地商品
            local_listings = conn.execute(
                "SELECT id FROM market_listings WHERE source = 'local' AND status = 'on_sale'"
            ).fetchall()

            if local_listings:
                # 随机打乱本地商品的创建时间，使显示顺序随机化
                import time
                import random
                random.seed(time.time())

                # 为每个本地商品分配一个随机的时间戳（在最近24小时内）
                for listing in local_listings:
                    # 生成一个随机时间戳（当前时间前后12小时内随机）
                    random_offset = random.randint(-43200, 43200)  # -12小时到+12小时
                    new_timestamp = int(time.time()) + random_offset

                    conn.execute(
                        "UPDATE market_listings SET created_at = datetime(?, 'unixepoch') WHERE id = ?",
                        (new_timestamp, listing[0])
                    )
    except Exception as e:
        st.warning(f"本地商品重排失败: {e}")

    return True

# 用户认证页面函数
def auth_page():
    """
    用户认证页面

    提供用户登录和注册功能，是应用的主要入口页面。
    包含登录表单和注册表单，支持用户名密码认证。

    功能：
    - 用户登录：验证用户名和密码
    - 用户注册：创建新用户账号
    - 表单验证：检查输入数据的有效性
    - 错误处理：显示登录/注册失败的原因
    """
    # 页面标题和描述
    st.markdown('<div class="stTitle">🌾 智农云平台</div>', unsafe_allow_html=True)
    st.caption("集病虫害识别、农场管理、交易流通于一体的农业生产协作平台")

    # 登录和注册标签页
    tab_login, tab_register = st.tabs(["登录", "注册"])

    with tab_login:
        # 登录表单卡片
        with st.form("login_form"):
            st.subheader("用户登录")
            st.write("欢迎回来，请输入您的账号信息")

            # 输入字段
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")

            # 登录按钮
            submitted = st.form_submit_button("登录", type="primary")

            # 登录逻辑
            if submitted:
                if not username or not password:
                    st.warning("请输入用户名和密码")
                else:
                    user = db.login_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.success("登录成功，正在跳转...")
                        st.rerun()
                    else:
                        st.error("用户名或密码错误")

    with tab_register:
        # 注册表单卡片
        with st.form("register_form"):
            st.subheader("创建新账号")
            st.write("填写以下信息，创建您的智农云平台账号")

            # 输入字段
            username = st.text_input("用户名", key="reg_u", placeholder="请设置用户名（至少3位）")
            email = st.text_input("邮箱", key="reg_e", placeholder="请输入邮箱地址")
            full_name = st.text_input("姓名", key="reg_n", placeholder="请输入您的姓名")
            phone = st.text_input("联系电话", key="reg_p", placeholder="请输入联系电话")
            password = st.text_input("密码", type="password", key="reg_pw", placeholder="请设置密码（至少6位）")

            # 注册按钮
            submitted = st.form_submit_button("创建账号", type="primary")

            # 注册逻辑
            if submitted:
                if len(username) < 3:
                    st.warning("用户名至少3位")
                elif len(password) < 6:
                    st.warning("密码至少6位")
                else:
                    ok, msg = db.register_user(username, password, email, full_name, phone)
                    if ok:
                        st.success(msg)
                        st.info("注册成功，请登录")
                    else:
                        st.error(msg)

# 仪表盘页面函数
def dashboard_page(user):
    """
    系统仪表盘页面

    显示用户的核心统计信息和快速导航入口，
    提供系统总览和各模块的快捷访问。

    参数：
    - user: 用户信息字典

    功能：
    - 显示核心指标：农场数量、待办任务、在售商品、识别记录
    - 提供快速导航按钮
    - 显示最近活动和系统提醒
    - 展示数据图表和趋势分析
    """
    st.header("总览仪表盘")

    # 获取统计数据
    stats = db.get_dashboard_stats(user["id"])

    # 指标卡片
    st.subheader("核心指标")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("农场数量", stats["farm_count"])
        if st.button("查看农场管理", key="nav_farm"):
            st.session_state.menu = "农场管理"
            safe_rerun()
    with col2:
        st.metric("待办任务", stats["task_pending"])
        if st.button("查看任务", key="nav_task"):
            st.session_state.menu = "农场管理"
            safe_rerun()
    with col3:
        st.metric("在售商品", stats["listing_on_sale"])
        if st.button("查看交易市场", key="nav_market"):
            st.session_state.menu = "交易市场"
            safe_rerun()
    with col4:
        st.metric("识别记录", stats["diagnosis_count"])
        if st.button("查看识别中心", key="nav_diag"):
            st.session_state.menu = "识别中心"
            safe_rerun()

    # 图表区域
    st.subheader("数据可视化")
    col1, col2 = st.columns(2)

    # 最近识别分布
    history = db.get_diagnosis_history(user["id"], limit=50)
    if history:
        df = pd.DataFrame(history)

        with col1:
            st.subheader("病害识别分布")
            chart_df = df["class_name"].value_counts().head(8)
            st.bar_chart(chart_df)

        with col2:
            st.subheader("识别置信度趋势")
            trend_df = df[["diagnosis_date", "confidence"]].copy()
            trend_df = trend_df.sort_values("diagnosis_date")
            trend_df = trend_df.set_index("diagnosis_date")
            st.line_chart(trend_df)
    else:
        st.info("还没有识别记录，先去识别中心上传一张叶片图像吧。")

    # 最近活动
    st.subheader("最近活动")
    activities = []

    # 获取最近的识别记录
    recent_diagnoses = db.get_diagnosis_history(user["id"], limit=5)
    for diag in recent_diagnoses:
        activities.append({
            "类型": "病害识别",
            "内容": f"识别为 {diag['class_name']}",
            "时间": diag['diagnosis_date']
        })

    # 获取最近的订单
    recent_orders = db.get_orders(user["id"], limit=5)
    for order in recent_orders:
        order_type = order.get('order_type') or order.get('type') or '订单'
        item_title = order.get('item_title') or order.get('title') or '未知商品'
        activities.append({
            "类型": "交易订单",
            "内容": f"{order_type} - {item_title}",
            "时间": order.get('created_at') or order.get('created_at', '')
        })

    # 获取最近的任务
    farms = db.get_farms(user["id"])
    all_tasks = []
    for farm in farms:
        tasks = db.get_tasks(farm["id"])
        all_tasks.extend(tasks)
    # 按创建时间排序，取最近的5个
    all_tasks.sort(key=lambda x: x['created_at'], reverse=True)
    recent_tasks = all_tasks[:5]
    for task in recent_tasks:
        activities.append({
            "类型": "农事任务",
            "内容": f"{task['title']} - {task['status']}",
            "时间": task['created_at']
        })

    # 按时间排序
    activities.sort(key=lambda x: x['时间'], reverse=True)

    if activities:
        st.dataframe(pd.DataFrame(activities)[:10], width="stretch")
    else:
        st.info("暂无活动记录")

    # 自动识别病害提醒
    st.subheader("自动检测预警")
    auto_alerts = db.get_auto_alerts(user["id"])
    if not auto_alerts:
        auto_alerts = db.get_auto_alerts(1)

    # 添加预警管理功能
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"共 {len(auto_alerts)} 条预警信息")
    with col2:
        if auto_alerts and st.button("🗑️ 一键清除所有预警", type="secondary"):
            cleared_count = db.clear_auto_alerts(user["id"])
            if cleared_count > 0:
                st.success(f"已清除 {cleared_count} 条预警信息")
                st.rerun()
            else:
                st.info("没有找到可清除的预警信息")

    if auto_alerts:
        for alert in auto_alerts:
            with st.expander(f"[{alert['detected_at']}] {alert['image_name']} -> {alert['class_name']} ({alert['confidence']:.2%})"):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"图片：{alert['image_name']}")
                    st.write(f"病害：{alert['class_name']}")
                    st.write(f"置信度：{alert['confidence']:.2%}")
                    st.write(f"检测时间：{alert['detected_at']}")
                with col_b:
                    if st.button("❌ 清除", key=f"clear_alert_{alert['id']}", help="清除这条预警信息"):
                        cleared = db.clear_single_auto_alert(alert['id'], user["id"])
                        if cleared > 0:
                            st.success("预警已清除")
                            st.rerun()
                        else:
                            st.error("清除失败")

                if st.button("查看详细诊断记录", key=f"view_alert_{alert['id']}"):
                    st.session_state.menu = "识别中心"
                    safe_rerun()
    else:
        st.info("暂无自动检测异常提醒。")


def diagnosis_page(user, model):
    st.header("病虫害识别中心")
    if model is None:
        st.error("未找到模型文件 `models/model.pth`，请先放入训练模型。")
        return

    def format_advice_for_class(class_id: int):
        custom = db.get_learning_task_by_class_id(class_id)
        if custom:
            symptoms = custom.get("symptoms") or "-"
            prevention = custom.get("prevention") or "-"
            treatment = custom.get("treatment") or "-"
            return f"症状：{symptoms}\n预防：{prevention}\n治疗/处置：{treatment}"

        return get_disease_advice(class_id)

    tab_single, tab_batch, tab_history, tab_knowledge = st.tabs(
        ["单图识别", "批量识别", "识别历史", "病害知识库"]
    )

    with tab_single:
        st.subheader("单张图像识别")
        st.write("上传植物叶片图像，系统将自动识别病害类型")

        uploaded = st.file_uploader(
            "上传叶片图像",
            type=["jpg", "jpeg", "png"],
            key="single_file",
            help="请上传清晰的叶片图像，以便获得更准确的识别结果"
        )

        if uploaded:
            image = Image.open(uploaded)
            st.image(image, caption=uploaded.name, width=400, use_column_width=False)

            if st.button("开始识别", key="btn_single_predict", type="primary"):
                with st.spinner("正在识别中..."):
                    class_id, confidence = predict(model, image)
                    class_name = get_class_name(class_id)
                    db.add_diagnosis_history(
                        user["id"], uploaded.name, class_id, class_name, float(confidence)
                    )

                st.success("识别完成！")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("类别ID", class_id)
                with col2:
                    st.metric("病害名称", class_name)
                with col3:
                    st.metric("置信度", f"{confidence:.2%}")

                st.subheader("防治建议")
                advice = format_advice_for_class(class_id)
                st.info(advice)

                st.subheader("症状信息")
                custom = db.get_learning_task_by_class_id(class_id)
                if custom:
                    st.success(f"症状：{custom.get('symptoms') or '-'}")
                else:
                    knowledge = get_disease_knowledge(class_id)
                    st.success(f"症状：{knowledge['symptoms']}")

    with tab_batch:
        st.subheader("批量图像识别")
        st.write("同时上传多张叶片图像，系统将批量识别")

        files = st.file_uploader(
            "批量上传图像",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="batch_file",
            help="请上传多张清晰的叶片图像"
        )

        if files:
            st.write(f"已上传 {len(files)} 张图像")

            if st.button("开始批量识别", key="btn_batch_predict", type="primary"):
                with st.spinner("正在批量识别中..."):
                    images = [Image.open(f) for f in files]
                    results = batch_predict(model, images)
                    rows = []
                    for f, r in zip(files, results):
                        advice = format_advice_for_class(r["class_id"])
                        db.add_diagnosis_history(
                            user["id"], f.name, r["class_id"], r["class_name"], float(r["confidence"])
                        )
                        rows.append(
                            {
                                "图像": f.name,
                                "类别ID": r["class_id"],
                                "病害名称": r["class_name"],
                                "置信度": round(float(r["confidence"]), 4),
                                "防治建议": advice,
                            }
                        )

                st.success("批量识别完成！")
                st.dataframe(pd.DataFrame(rows), width="stretch")

    with tab_history:
        st.subheader("识别历史")
        st.write("查看历史识别记录")

        records = db.get_diagnosis_history(user["id"], limit=200)
        if records:
            df = pd.DataFrame(records)
            df = df.rename(columns={
                "image_name": "图像名称",
                "class_id": "类别ID",
                "class_name": "病害名称",
                "confidence": "置信度",
                "diagnosis_date": "识别时间",
            })
            st.dataframe(
                df[["图像名称", "类别ID", "病害名称", "置信度", "识别时间"]],
                width="stretch",
                hide_index=True
            )
        else:
            st.info("暂无识别历史。")

    with tab_knowledge:
        st.subheader("病害知识库")
        st.write("浏览不同作物的病害信息和防治方法")

        static_crops = get_crop_types()
        custom_crops = db.get_approved_custom_crops()
        crops = sorted(set(static_crops + custom_crops))
        crop = st.selectbox("作物类型", crops)

        static_diseases = get_diseases_by_crop(crop)
        custom_diseases = [
            d for d in db.get_approved_custom_diseases() if d.get("crop_type") == crop
        ]

        label_to_detail = {}
        option_labels = []

        for class_id, name in static_diseases:
            label = f"系统：{name}"
            label_to_detail[label] = ("static", class_id, name)
            option_labels.append(label)

        for d in custom_diseases:
            label = f"自定义：{d['disease_name']}（#{d['id']}）"
            label_to_detail[label] = ("custom", d["id"], d["disease_name"])
            option_labels.append(label)

        if option_labels:
            selected_label = st.selectbox("病害类型", option_labels)
            source, selected_id, _ = label_to_detail[selected_label]
            if source == "static":
                detail = get_disease_knowledge(selected_id)
                st.write(f"**名称**：{detail['name']}")
                st.write(f"**症状**：{detail['symptoms']}")
                st.write(f"**预防**：{detail['prevention']}")
                st.write(f"**治疗**：{detail['treatment']}")
            else:
                custom = db.get_learning_task(selected_id)
                st.write(f"**名称**：{custom['disease_name']}")
                st.write(f"**症状**：{custom.get('symptoms') or '-'}")
                st.write(f"**预防**：{custom.get('prevention') or '-'}")
                st.write(f"**治疗**：{custom.get('treatment') or '-'}")
                if custom.get("description"):
                    st.caption(custom["description"])
        else:
            st.info("该作物暂无病害信息")


def farm_page(user):
    # 土壤类型映射（处理英文到中文的转换）
    soil_mapping = {
        "Clay": "黏土",
        "Sandy": "砂土", 
        "Loam": "壤土",
        "Black": "黑土",
        "Other": "其他",
        "壤土": "壤土",
        "砂土": "砂土",
        "黏土": "黏土",
        "黑土": "黑土",
        "其他": "其他"
    }
    
    # 灌溉方式映射
    irrigation_mapping = {
        "Drip": "滴灌",
        "Spray": "喷灌",
        "Flood": "漫灌",
        "Rain": "自然降雨为主",
        "滴灌": "滴灌",
        "喷灌": "喷灌",
        "漫灌": "漫灌",
        "自然降雨为主": "自然降雨为主"
    }
    
    st.header("农场管理")
    tab_farm, tab_crop, tab_task, tab_workers, tab_equipment, tab_finance, tab_yields = st.tabs([
        "农场档案", "种植计划", "农事任务", "工人管理", "设备管理", "财务记录", "产量记录"
    ])

    with tab_farm:
        with st.form("add_farm_form"):
            st.subheader("添加农场")
            name = st.text_input("农场名称")
            location = st.text_input("所在地区")
            area_mu = st.number_input("面积（亩）", min_value=0.1, value=10.0, step=0.1)
            soil = st.selectbox("土壤类型", ["壤土", "砂土", "黏土", "黑土", "其他"])
            irrigation = st.selectbox("灌溉方式", ["滴灌", "喷灌", "漫灌", "自然降雨为主"])
            submitted = st.form_submit_button("保存农场")
            if submitted:
                db.add_farm(user["id"], name, location, area_mu, soil, irrigation)
                st.success("农场创建成功")
                st.rerun()

        farms = db.get_farms(user["id"])
        if farms:
            st.subheader("我的农场")
            df = pd.DataFrame(farms)
            df = df.rename(columns={
                "id": "编号",
                "user_id": "用户ID",
                "name": "农场名称",
                "location": "位置",
                "area_mu": "面积(亩)",
                "soil_type": "土壤类型",
                "irrigation_type": "灌溉方式",
                "created_at": "创建时间",
                "owner_id": "所有者ID",
                "area": "面积(旧)",
                "crops": "作物",
            })
            st.dataframe(df, width="stretch")

            st.subheader("管理现有农场")
            farm_options = {f"{f['name']} (#{f['id']})": f for f in farms}
            selected = st.selectbox("选择农场进行编辑/删除", list(farm_options.keys()), key="manage_farm_select")
            farm_data = farm_options[selected]

            with st.form("farm_edit_form"):
                edit_name = st.text_input("农场名称", value=farm_data["name"])
                edit_location = st.text_input("所在地区", value=farm_data["location"])
                edit_area = st.number_input("面积（亩）", min_value=0.1, value=float(farm_data.get("area_mu", 0.0)), step=0.1)
                current_soil = soil_mapping.get(farm_data.get("soil_type", "壤土"), "壤土")
                soil_options = ["壤土", "砂土", "黏土", "黑土", "其他"]
                soil_index = soil_options.index(current_soil) if current_soil in soil_options else 0
                edit_soil = st.selectbox("土壤类型", soil_options, index=soil_index)
                
                current_irrigation = irrigation_mapping.get(farm_data.get("irrigation_type", "自然降雨为主"), "自然降雨为主")
                irrigation_options = ["滴灌", "喷灌", "漫灌", "自然降雨为主"]
                irrigation_index = irrigation_options.index(current_irrigation) if current_irrigation in irrigation_options else 0
                edit_irrigation = st.selectbox("灌溉方式", irrigation_options, index=irrigation_index)
                btn_update = st.form_submit_button("更新农场")
                btn_delete = st.form_submit_button("删除农场")

                if btn_update:
                    db.update_farm(farm_data["id"], edit_name, edit_location, edit_area, edit_soil, edit_irrigation)
                    st.success("农场信息已更新")
                    st.rerun()

                if btn_delete:
                    db.delete_farm(farm_data["id"], user["id"])
                    st.success("农场已删除")
                    st.rerun()

        else:
            st.info("还没有农场记录。")

    farms = db.get_farms(user["id"])
    farm_map = {f"{x['name']} (#{x['id']})": x["id"] for x in farms}

    with tab_crop:
        if not farm_map:
            st.info("请先在“农场档案”里创建农场。")
        else:
            farm_label = st.selectbox("选择农场", list(farm_map.keys()), key="crop_farm")
            farm_id = farm_map[farm_label]
            with st.form("add_crop_plan_form"):
                crop_name = st.text_input("作物名称")
                season = st.selectbox("季节", ["春季", "夏季", "秋季", "冬季"])
                sowing = st.date_input("播种日期", value=date.today())
                harvest = st.date_input("预计采收", value=date.today())
                stage = st.selectbox("生长阶段", ["育苗期", "生长期", "开花期", "结果期", "成熟期"])
                submitted = st.form_submit_button("新增计划")
                if submitted:
                    db.add_crop_plan(farm_id, crop_name, season, str(sowing), str(harvest), stage)
                    st.success("种植计划已添加")
                    st.rerun()
            plans = db.get_crop_plans(farm_id)
            if plans:
                df_plans = pd.DataFrame(plans)
                df_plans = df_plans.rename(columns={
                    "id": "编号",
                    "farm_id": "农场ID",
                    "crop_name": "作物名称",
                    "season": "季节",
                    "sowing_date": "播种日期",
                    "expected_harvest": "预计采收",
                    "growth_stage": "生长阶段",
                    "status": "状态",
                })
                st.dataframe(df_plans, width="stretch")

                st.subheader("编辑/删除种植计划")
                plan_options = {f"{p['crop_name']} (#{p['id']})": p for p in plans}
                selected_plan_key = st.selectbox("选择计划", list(plan_options.keys()), key="manage_plan_select")
                active_plan = plan_options[selected_plan_key]

                with st.form("crop_plan_edit_form"):
                    edit_crop_name = st.text_input("作物名称", value=active_plan["crop_name"])
                    edit_season = st.selectbox("季节", ["春季", "夏季", "秋季", "冬季"], index=["春季", "夏季", "秋季", "冬季"].index(active_plan.get("season", "春季")))
                    edit_sowing = st.date_input("播种日期", value=datetime.fromisoformat(active_plan.get("sowing_date")).date() if active_plan.get("sowing_date") else date.today())
                    edit_harvest = st.date_input("预计采收", value=datetime.fromisoformat(active_plan.get("expected_harvest")).date() if active_plan.get("expected_harvest") else date.today())
                    stages = ["育苗期", "生长期", "开花期", "结果期", "成熟期", "收获期"]
                    current_stage = active_plan.get("growth_stage", "育苗期")
                    stage_index = stages.index(current_stage) if current_stage in stages else 0
                    edit_stage = st.selectbox("生长阶段", stages, index=stage_index)
                    statuses = ["进行中", "已完成", "暂停", "完成"]
                    current_status = active_plan.get("status", "进行中")
                    status_index = statuses.index(current_status) if current_status in statuses else 0
                    edit_status = st.selectbox("状态", statuses, index=status_index)
                    plan_update = st.form_submit_button("更新计划")
                    plan_delete = st.form_submit_button("删除计划")

                    if plan_update:
                        db.update_crop_plan(active_plan["id"], edit_crop_name, edit_season, str(edit_sowing), str(edit_harvest), edit_stage, edit_status)
                        st.success("种植计划已更新")
                        st.rerun()

                    if plan_delete:
                        db.delete_crop_plan(active_plan["id"], farm_id)
                        st.success("种植计划已删除")
                        st.rerun()

            else:
                st.info("暂无种植计划。")

    with tab_task:
        if not farm_map:
            st.info("请先创建农场。")
        else:
            farm_label = st.selectbox("选择农场", list(farm_map.keys()), key="task_farm")
            farm_id = farm_map[farm_label]
            with st.form("add_task_form"):
                title = st.text_input("任务标题")
                due_date = st.date_input("截止日期", value=date.today(), key="task_due")
                priority = st.selectbox("优先级", ["高", "中", "低"])
                notes = st.text_area("备注")
                submitted = st.form_submit_button("添加任务")
                if submitted:
                    db.add_task(farm_id, title, str(due_date), priority, notes)
                    st.success("任务已创建")
                    st.rerun()
            tasks = db.get_tasks(farm_id)
            if tasks:
                for task in tasks:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
                    col1.write(f"**{task['title']}**")
                    col2.write(f"{task['priority']} / {task['due_date']}")
                    col3.write(task["status"])
                    new_status = col4.selectbox(
                        "状态",
                        ["待处理", "进行中", "已完成"],
                        index=["待处理", "进行中", "已完成"].index(task["status"]),
                        key=f"task_status_{task['id']}",
                    )
                    if new_status != task["status"]:
                        db.update_task_status(task["id"], new_status)
                        st.rerun()

                st.subheader("编辑/删除任务")
                task_options = {f"{t['title']} (#{t['id']})": t for t in tasks}
                selected_task_key = st.selectbox("选择任务", list(task_options.keys()), key="manage_task_select")
                selected_task = task_options[selected_task_key]

                with st.form("task_edit_form"):
                    edit_title = st.text_input("任务标题", value=selected_task["title"])
                    edit_due_date = st.date_input("截止日期", value=datetime.fromisoformat(selected_task["due_date"]).date() if selected_task.get("due_date") else date.today())
                    edit_priority = st.selectbox("优先级", ["高", "中", "低"], index=["高", "中", "低"].index(selected_task.get("priority", "中")))
                    edit_notes = st.text_area("备注", value=selected_task.get("notes", ""))
                    edit_status = st.selectbox("状态", ["待处理", "进行中", "已完成"], index=["待处理", "进行中", "已完成"].index(selected_task.get("status", "待处理")))
                    update_task = st.form_submit_button("更新任务")
                    delete_task = st.form_submit_button("删除任务")

                    if update_task:
                        db.update_task(selected_task["id"], edit_title, str(edit_due_date), edit_priority, edit_notes, edit_status)
                        st.success("任务已更新")
                        st.rerun()

                    if delete_task:
                        db.delete_task(selected_task["id"], farm_id)
                        st.success("任务已删除")
                        st.rerun()
            else:
                st.info("暂无任务。")

    with tab_workers:
        if not farm_map:
            st.info("请先创建农场。")
        else:
            farm_label = st.selectbox("选择农场", list(farm_map.keys()), key="worker_farm")
            farm_id = farm_map[farm_label]
            with st.form("add_worker_form"):
                name = st.text_input("工人姓名")
                role = st.selectbox("职位", ["农工", "技术员", "管理员", "会计", "其他"])
                phone = st.text_input("联系电话")
                hire_date = st.date_input("入职日期", value=date.today())
                salary = st.number_input("月薪（元）", min_value=0.0, value=3000.0, step=100.0)
                submitted = st.form_submit_button("添加工人")
                if submitted:
                    db.add_farm_worker(farm_id, name, role, phone, str(hire_date), salary)
                    st.success("工人信息已添加")
                    st.rerun()
            workers = db.get_farm_workers(farm_id)
            if workers:
                df_workers = pd.DataFrame(workers)
                df_workers = df_workers.rename(columns={
                    "id": "编号",
                    "farm_id": "农场ID",
                    "name": "姓名",
                    "role": "职位",
                    "phone": "电话",
                    "hire_date": "入职日期",
                    "salary": "月薪",
                    "status": "状态",
                    "created_at": "创建时间",
                })
                st.dataframe(df_workers, width="stretch")

                st.subheader("编辑/删除工人")
                worker_options = {f"{w['name']} (#{w['id']})": w for w in workers}
                selected_worker_key = st.selectbox("选择工人", list(worker_options.keys()), key="manage_worker_select")
                selected_worker = worker_options[selected_worker_key]

                with st.form("worker_edit_form"):
                    edit_name = st.text_input("工人姓名", value=selected_worker["name"])
                    edit_role = st.selectbox("职位", ["农工", "技术员", "管理员", "会计", "其他"], index=["农工", "技术员", "管理员", "会计", "其他"].index(selected_worker.get("role", "农工")))
                    edit_phone = st.text_input("联系电话", value=selected_worker.get("phone", ""))
                    edit_hire_date = st.date_input("入职日期", value=datetime.fromisoformat(selected_worker.get("hire_date")).date() if selected_worker.get("hire_date") else date.today())
                    edit_salary = st.number_input("月薪（元）", min_value=0.0, value=float(selected_worker.get("salary", 0.0)), step=100.0)
                    edit_status = st.selectbox("状态", ["active", "inactive"], index=["active", "inactive"].index(selected_worker.get("status", "active")))
                    update_worker = st.form_submit_button("更新工人")
                    delete_worker = st.form_submit_button("删除工人")

                    if update_worker:
                        db.update_farm_worker(selected_worker["id"], farm_id, edit_name, edit_role, edit_phone, str(edit_hire_date), edit_salary, edit_status)
                        st.success("工人信息已更新")
                        st.rerun()

                    if delete_worker:
                        db.delete_farm_worker(selected_worker["id"], farm_id)
                        st.success("工人已删除")
                        st.rerun()
            else:
                st.info("暂无工人信息。")

    with tab_equipment:
        if not farm_map:
            st.info("请先创建农场。")
        else:
            farm_label = st.selectbox("选择农场", list(farm_map.keys()), key="equip_farm")
            farm_id = farm_map[farm_label]
            with st.form("add_equipment_form"):
                name = st.text_input("设备名称")
                category = st.selectbox("设备类别", ["机械设备", "农机具", "灌溉设备", "其他"])
                model = st.text_input("型号")
                purchase_date = st.date_input("购买日期", value=date.today())
                purchase_price = st.number_input("购买价格（元）", min_value=0.0, value=10000.0, step=100.0)
                maintenance = st.text_input("保养周期", placeholder="例如：每月保养")
                submitted = st.form_submit_button("添加设备")
                if submitted:
                    db.add_farm_equipment(farm_id, name, category, model, str(purchase_date), purchase_price, maintenance)
                    st.success("设备信息已添加")
                    st.rerun()
            equipment = db.get_farm_equipment(farm_id)
            if equipment:
                df_equip = pd.DataFrame(equipment)
                df_equip = df_equip.rename(columns={
                    "id": "编号",
                    "farm_id": "农场ID",
                    "name": "设备名称",
                    "category": "类别",
                    "model": "型号",
                    "purchase_date": "购买日期",
                    "purchase_price": "购买价格",
                    "status": "状态",
                    "maintenance_schedule": "保养周期",
                    "created_at": "创建时间",
                })
                st.dataframe(df_equip, width="stretch")

                st.subheader("编辑/删除设备")
                equip_options = {f"{e['name']} (#{e['id']})": e for e in equipment}
                selected_equip_key = st.selectbox("选择设备", list(equip_options.keys()), key="manage_equip_select")
                selected_equip = equip_options[selected_equip_key]

                with st.form("equip_edit_form"):
                    edit_name = st.text_input("设备名称", value=selected_equip["name"])
                    edit_category = st.selectbox("设备类别", ["机械设备", "农机具", "灌溉设备", "其他"], index=["机械设备", "农机具", "灌溉设备", "其他"].index(selected_equip.get("category", "机械设备")))
                    edit_model = st.text_input("型号", value=selected_equip.get("model", ""))
                    edit_purchase_date = st.date_input("购买日期", value=datetime.fromisoformat(selected_equip.get("purchase_date")).date() if selected_equip.get("purchase_date") else date.today())
                    edit_purchase_price = st.number_input("购买价格（元）", min_value=0.0, value=float(selected_equip.get("purchase_price", 0.0)), step=100.0)
                    edit_status = st.selectbox("状态", ["正常", "维修中", "报废"], index=["正常", "维修中", "报废"].index(selected_equip.get("status", "正常")))
                    edit_maintenance = st.text_input("保养周期", value=selected_equip.get("maintenance_schedule", ""))
                    update_equip = st.form_submit_button("更新设备")
                    delete_equip = st.form_submit_button("删除设备")

                    if update_equip:
                        db.update_farm_equipment(selected_equip["id"], farm_id, edit_name, edit_category, edit_model, str(edit_purchase_date), edit_purchase_price, edit_status, edit_maintenance)
                        st.success("设备信息已更新")
                        st.rerun()

                    if delete_equip:
                        db.delete_farm_equipment(selected_equip["id"], farm_id)
                        st.success("设备已删除")
                        st.rerun()
            else:
                st.info("暂无设备信息。")

    with tab_finance:
        if not farm_map:
            st.info("请先创建农场。")
        else:
            farm_label = st.selectbox("选择农场", list(farm_map.keys()), key="finance_farm")
            farm_id = farm_map[farm_label]
            with st.form("add_finance_form"):
                type_ = st.selectbox("类型", ["income", "expense"], format_func=lambda x: "收入" if x == "income" else "支出")
                category = st.selectbox("类别", ["种子", "肥料", "农药", "设备", "人工", "销售", "补贴", "其他"])
                amount = st.number_input("金额（元）", min_value=0.01, value=1000.0, step=10.0)
                description = st.text_input("描述")
                transaction_date = st.date_input("交易日期", value=date.today())
                submitted = st.form_submit_button("添加记录")
                if submitted:
                    db.add_farm_finance(farm_id, type_, category, amount, description, str(transaction_date))
                    st.success("财务记录已添加")
                    st.rerun()
            finances = db.get_farm_finances(farm_id)
            if finances:
                df_finance = pd.DataFrame(finances)
                df_finance = df_finance.rename(columns={
                    "id": "编号",
                    "farm_id": "农场ID",
                    "type": "类型",
                    "category": "类别",
                    "amount": "金额",
                    "description": "描述",
                    "transaction_date": "交易日期",
                    "created_at": "创建时间",
                })
                df_finance["类型"] = df_finance["类型"].map({"income": "收入", "expense": "支出"})
                st.dataframe(df_finance, width="stretch")
                
                # 财务汇总
                total_income = df_finance[df_finance["类型"] == "收入"]["金额"].sum()
                total_expense = df_finance[df_finance["类型"] == "支出"]["金额"].sum()
                net_profit = total_income - total_expense
                
                st.subheader("财务汇总")
                col1, col2, col3 = st.columns(3)
                col1.metric("总收入", f"¥{total_income:.2f}")
                col2.metric("总支出", f"¥{total_expense:.2f}")
                col3.metric("净利润", f"¥{net_profit:.2f}")

                st.subheader("编辑/删除财务记录")
                finance_options = {f"{f['category']} {f['transaction_date']} (#{f['id']})": f for f in finances}
                selected_finance_key = st.selectbox("选择记录", list(finance_options.keys()), key="manage_finance_select")
                selected_finance = finance_options[selected_finance_key]

                with st.form("finance_edit_form"):
                    edit_type = st.selectbox("类型", ["income", "expense"], index=["income", "expense"].index(selected_finance.get("type", "income")))
                    edit_category = st.selectbox("类别", ["种子", "肥料", "农药", "设备", "人工", "销售", "补贴", "其他"], index=["种子", "肥料", "农药", "设备", "人工", "销售", "补贴", "其他"].index(selected_finance.get("category", "其他")))
                    edit_amount = st.number_input("金额（元）", min_value=0.01, value=float(selected_finance.get("amount", 0.0)), step=10.0)
                    edit_description = st.text_input("描述", value=selected_finance.get("description", ""))
                    edit_transaction_date = st.date_input("交易日期", value=datetime.fromisoformat(selected_finance.get("transaction_date")).date() if selected_finance.get("transaction_date") else date.today())
                    update_finance = st.form_submit_button("更新记录")
                    delete_finance = st.form_submit_button("删除记录")

                    if update_finance:
                        db.update_farm_finance(selected_finance["id"], farm_id, edit_type, edit_category, edit_amount, edit_description, str(edit_transaction_date))
                        st.success("财务记录已更新")
                        st.rerun()
                    if delete_finance:
                        db.delete_farm_finance(selected_finance["id"], farm_id)
                        st.success("财务记录已删除")
                        st.rerun()
            else:
                st.info("暂无财务记录。")

    with tab_yields:
        if not farm_map:
            st.info("请先创建农场。")
        else:
            farm_label = st.selectbox("选择农场", list(farm_map.keys()), key="yield_farm")
            farm_id = farm_map[farm_label]
            plans = db.get_crop_plans(farm_id)
            if plans:
                plan_options = {f"{p['crop_name']} (计划#{p['id']})": p['id'] for p in plans}
                plan_label = st.selectbox("选择种植计划", list(plan_options.keys()), key="yield_plan")
                plan_id = plan_options[plan_label]
                
                with st.form("add_yield_form"):
                    harvest_date = st.date_input("收获日期", value=date.today())
                    quantity = st.number_input("产量", min_value=0.01, value=100.0, step=1.0)
                    unit = st.selectbox("单位", ["kg", "吨", "斤", "亩"])
                    quality = st.selectbox("质量等级", ["优", "良", "中", "差"])
                    notes = st.text_area("备注")
                    submitted = st.form_submit_button("添加产量记录")
                    if submitted:
                        db.add_crop_yield(plan_id, str(harvest_date), quantity, unit, quality, notes)
                        st.success("产量记录已添加")
                        st.rerun()
                
                yields = db.get_crop_yields(plan_id)
                if yields:
                    df_yields = pd.DataFrame(yields)
                    df_yields = df_yields.rename(columns={
                        "id": "编号",
                        "crop_plan_id": "计划ID",
                        "harvest_date": "收获日期",
                        "quantity": "产量",
                        "unit": "单位",
                        "quality_grade": "质量等级",
                        "notes": "备注",
                        "created_at": "创建时间",
                    })
                    st.dataframe(df_yields, width="stretch")

                    st.subheader("编辑/删除产量记录")
                    yield_options = {f"{y['harvest_date']} {y['quantity']}{y['unit']} (#{y['id']})": y for y in yields}
                    selected_yield_key = st.selectbox("选择记录", list(yield_options.keys()), key="manage_yield_select")
                    selected_yield = yield_options[selected_yield_key]

                    with st.form("yield_edit_form"):
                        edit_harvest_date = st.date_input("收获日期", value=datetime.fromisoformat(selected_yield.get("harvest_date")).date())
                        edit_quantity = st.number_input("产量", min_value=0.01, value=float(selected_yield.get("quantity", 0.0)), step=1.0)
                        edit_unit = st.selectbox("单位", ["kg", "吨", "斤", "亩"], index=["kg", "吨", "斤", "亩"].index(selected_yield.get("unit", "kg")))
                        edit_quality = st.selectbox("质量等级", ["优", "良", "中", "差"], index=["优", "良", "中", "差"].index(selected_yield.get("quality_grade", "优")))
                        edit_notes = st.text_area("备注", value=selected_yield.get("notes", ""))
                        update_yield = st.form_submit_button("更新记录")
                        delete_yield = st.form_submit_button("删除记录")

                        if update_yield:
                            db.update_crop_yield(selected_yield["id"], plan_id, str(edit_harvest_date), edit_quantity, edit_unit, edit_quality, edit_notes)
                            st.success("产量记录已更新")
                            st.rerun()
                        if delete_yield:
                            db.delete_crop_yield(selected_yield["id"], plan_id)
                            st.success("产量记录已删除")
                            st.rerun()
                else:
                    st.info("暂无产量记录。")
            else:
                st.info("请先创建种植计划。")


def inventory_page(user):
    st.header("农资库存")
    tab_inventory, tab_suppliers, tab_batches, tab_transactions = st.tabs([
        "库存管理", "供应商管理", "批次跟踪", "出入库记录"
    ])

    with tab_inventory:
        with st.form("inventory_form"):
            c1, c2, c3 = st.columns(3)
            item_name = c1.text_input("物资名称")
            category = c2.selectbox("分类", ["肥料", "农药", "种子", "设备", "其他"])
            unit = c3.selectbox("单位", ["kg", "袋", "瓶", "包", "台", "个"])
            quantity = st.number_input("当前数量", min_value=0.0, value=0.0, step=1.0)
            warning = st.number_input("预警阈值", min_value=0.0, value=0.0, step=1.0)
            submitted = st.form_submit_button("入库/记录")
            if submitted:
                db.add_inventory_item(user["id"], item_name, category, quantity, unit, warning)
                st.success("库存记录已保存")
                st.rerun()

        items = db.get_inventory(user["id"])
        if items:
            df = pd.DataFrame(items)
            df = df.rename(columns={
                "id": "编号",
                "user_id": "用户ID",
                "item_name": "物资名称",
                "category": "分类",
                "quantity": "数量",
                "unit": "单位",
                "warning_level": "预警阈值",
                "updated_at": "更新时间",
            })
            df["是否预警"] = df.apply(
                lambda x: "是" if float(x["数量"]) <= float(x["预警阈值"]) else "否", axis=1
            )
            st.dataframe(df, width="stretch")

            st.subheader("编辑/删除库存")
            item_options = {f"{i['item_name']} (#{i['id']})": i for i in items}
            selected_item_key = st.selectbox("选择物资", list(item_options.keys()), key="manage_item_select")
            selected_item = item_options[selected_item_key]

            with st.form("item_edit_form"):
                edit_item_name = st.text_input("物资名称", value=selected_item["item_name"])
                edit_category = st.selectbox("分类", ["肥料", "农药", "种子", "设备", "其他"], index=["肥料", "农药", "种子", "设备", "其他"].index(selected_item.get("category", "肥料")))
                edit_quantity = st.number_input("数量", min_value=0.0, value=float(selected_item.get("quantity", 0.0)), step=1.0)
                edit_unit = st.selectbox("单位", ["kg", "袋", "瓶", "包", "台", "个"], index=["kg", "袋", "瓶", "包", "台", "个"].index(selected_item.get("unit", "kg")))
                edit_warning = st.number_input("预警阈值", min_value=0.0, value=float(selected_item.get("warning_level", 0.0)), step=1.0)
                update_item = st.form_submit_button("更新库存")
                delete_item = st.form_submit_button("删除库存")

                if update_item:
                    db.update_inventory_item(selected_item["id"], user["id"], edit_item_name, edit_category, edit_quantity, edit_unit, edit_warning)
                    st.success("库存已更新")
                    st.rerun()
                if delete_item:
                    db.delete_inventory_item(selected_item["id"], user["id"])
                    st.success("库存已删除")
                    st.rerun()
        else:
            st.info("暂无库存记录。")

    with tab_suppliers:
        with st.form("supplier_form"):
            name = st.text_input("供应商名称")
            contact_person = st.text_input("联系人")
            c1, c2 = st.columns(2)
            phone = c1.text_input("联系电话")
            email = c2.text_input("邮箱")
            address = st.text_area("地址")
            submitted = st.form_submit_button("添加供应商")
            if submitted:
                db.add_inventory_supplier(name, contact_person, phone, email, address)
                st.success("供应商信息已保存")
                st.rerun()

        suppliers = db.get_inventory_suppliers()
        if suppliers:
            df_suppliers = pd.DataFrame(suppliers)
            df_suppliers = df_suppliers.rename(columns={
                "id": "编号",
                "name": "供应商名称",
                "contact_person": "联系人",
                "phone": "电话",
                "email": "邮箱",
                "address": "地址",
                "created_at": "创建时间",
            })
            st.dataframe(df_suppliers, width="stretch")

            st.subheader("编辑/删除供应商")
            supplier_options = {f"{s['name']} (#{s['id']})": s for s in suppliers}
            selected_supplier_key = st.selectbox("选择供应商", list(supplier_options.keys()), key="manage_supplier_select")
            selected_supplier = supplier_options[selected_supplier_key]

            with st.form("supplier_edit_form"):
                edit_name = st.text_input("供应商名称", value=selected_supplier["name"])
                edit_contact = st.text_input("联系人", value=selected_supplier.get("contact_person", ""))
                edit_phone = st.text_input("电话", value=selected_supplier.get("phone", ""))
                edit_email = st.text_input("邮箱", value=selected_supplier.get("email", ""))
                edit_address = st.text_area("地址", value=selected_supplier.get("address", ""))
                update_supplier = st.form_submit_button("更新供应商")
                delete_supplier = st.form_submit_button("删除供应商")

                if update_supplier:
                    db.update_inventory_supplier(selected_supplier["id"], edit_name, edit_contact, edit_phone, edit_email, edit_address)
                    st.success("供应商已更新")
                    st.rerun()
                if delete_supplier:
                    db.delete_inventory_supplier(selected_supplier["id"])
                    st.success("供应商已删除")
                    st.rerun()
        else:
            st.info("暂无供应商记录。")

    with tab_batches:
        items = db.get_inventory(user["id"])
        if items:
            item_options = {f"{item['item_name']} (#{item['id']})": item['id'] for item in items}
            item_label = st.selectbox("选择物资", list(item_options.keys()), key="batch_item")
            item_id = item_options[item_label]
            
            suppliers = db.get_inventory_suppliers()
            supplier_options = {f"{s['name']}": s['id'] for s in suppliers}
            
            with st.form("batch_form"):
                batch_number = st.text_input("批次号")
                supplier_id = st.selectbox("供应商", list(supplier_options.keys())) if supplier_options else None
                quantity = st.number_input("数量", min_value=0.01, value=100.0, step=1.0)
                unit_cost = st.number_input("单价（元）", min_value=0.0, value=10.0, step=0.1)
                expiry_date = st.date_input("过期日期", value=None)
                purchase_date = st.date_input("采购日期", value=date.today())
                submitted = st.form_submit_button("添加批次")
                if submitted and supplier_id:
                    supplier_id = supplier_options[supplier_id]
                    db.add_inventory_batch(item_id, supplier_id, batch_number, quantity, unit_cost, str(expiry_date) if expiry_date else None, str(purchase_date))
                    st.success("批次信息已添加")
                    st.rerun()
            
            batches = db.get_inventory_batches(item_id)
            if batches:
                df_batches = pd.DataFrame(batches)
                df_batches = df_batches.rename(columns={
                    "id": "编号",
                    "inventory_item_id": "物资ID",
                    "supplier_id": "供应商ID",
                    "batch_number": "批次号",
                    "quantity": "数量",
                    "unit_cost": "单价",
                    "expiry_date": "过期日期",
                    "purchase_date": "采购日期",
                    "supplier_name": "供应商名称",
                    "created_at": "创建时间",
                })
                st.dataframe(df_batches, width="stretch")

                st.subheader("编辑/删除批次")
                batch_options = {f"{b['batch_number']} (#{b['id']})": b for b in batches}
                selected_batch_key = st.selectbox("选择批次", list(batch_options.keys()), key="manage_batch_select")
                selected_batch = batch_options[selected_batch_key]

                with st.form("batch_edit_form"):
                    edit_batch_number = st.text_input("批次号", value=selected_batch.get("batch_number", ""))
                    supplier_keys = list(supplier_options.keys()) if supplier_options else []
                    current_supplier_label = next((k for k, v in supplier_options.items() if v == selected_batch.get("supplier_id")), supplier_keys[0] if supplier_keys else None)
                    selected_supplier_label = st.selectbox("供应商", supplier_keys, index=supplier_keys.index(current_supplier_label) if current_supplier_label in supplier_keys else 0) if supplier_keys else None
                    edit_quantity = st.number_input("数量", min_value=0.01, value=float(selected_batch.get("quantity", 0.0)), step=1.0)
                    edit_unit_cost = st.number_input("单价（元）", min_value=0.0, value=float(selected_batch.get("unit_cost", 0.0)), step=0.1)
                    edit_expiry = st.date_input("过期日期", value=datetime.fromisoformat(selected_batch.get("expiry_date")).date() if selected_batch.get("expiry_date") else date.today())
                    edit_purchase_date = st.date_input("采购日期", value=datetime.fromisoformat(selected_batch.get("purchase_date")).date() if selected_batch.get("purchase_date") else date.today())
                    update_batch = st.form_submit_button("更新批次")
                    delete_batch = st.form_submit_button("删除批次")

                    if update_batch:
                        supplier_id = supplier_options[selected_supplier_label] if selected_supplier_label else None
                        db.update_inventory_batch(selected_batch["id"], item_id, supplier_id, edit_batch_number, edit_quantity, edit_unit_cost, str(edit_expiry), str(edit_purchase_date))
                        st.success("批次已更新")
                        st.rerun()
                    if delete_batch:
                        db.delete_inventory_batch(selected_batch["id"])
                        st.success("批次已删除")
                        st.rerun()
            else:
                st.info("暂无批次记录。")
        else:
            st.info("请先添加库存物资。")

    with tab_transactions:
        items = db.get_inventory(user["id"])
        if items:
            item_options = {f"{item['item_name']} (#{item['id']})": item['id'] for item in items}
            item_label = st.selectbox("选择物资", list(item_options.keys()), key="trans_item")
            item_id = item_options[item_label]
            
            with st.form("transaction_form"):
                type_ = st.selectbox("类型", ["in", "out"], format_func=lambda x: "入库" if x == "in" else "出库")
                quantity = st.number_input("数量", min_value=0.01, value=10.0, step=1.0)
                reason = st.text_input("原因", placeholder="例如：采购入库、使用出库")
                submitted = st.form_submit_button("记录交易")
                if submitted:
                    db.add_inventory_transaction(item_id, type_, quantity, reason)
                    st.success("交易记录已添加")
                    st.rerun()
            
            transactions = db.get_inventory_transactions(item_id)
            if transactions:
                df_trans = pd.DataFrame(transactions)
                df_trans = df_trans.rename(columns={
                    "id": "编号",
                    "inventory_item_id": "物资ID",
                    "type": "类型",
                    "quantity": "数量",
                    "reason": "原因",
                    "transaction_date": "交易日期",
                    "created_at": "创建时间",
                })
                df_trans["类型"] = df_trans["类型"].map({"in": "入库", "out": "出库"})
                st.dataframe(df_trans, width="stretch")

                st.subheader("删除交易记录")
                trans_options = {f"{t['type']} {t['quantity']} ({t['transaction_date']}) (#{t['id']})": t for t in transactions}
                selected_trans_key = st.selectbox("选择交易记录", list(trans_options.keys()), key="manage_trans_select")
                selected_trans = trans_options[selected_trans_key]
                if st.button("删除交易记录", key="delete_trans_btn"):
                    db.delete_inventory_transaction(selected_trans["id"], item_id)
                    st.success("交易记录已删除")
                    st.rerun()
            else:
                st.info("暂无交易记录。")
        else:
            st.info("请先添加库存物资。")


def market_page(user):
    st.header("交易市场")
    tab_publish, tab_market, tab_order, tab_tracking = st.tabs([
        "发布商品", "市场大厅", "我的订单", "物流跟踪"
    ])

    with tab_publish:
        st.info("📢 商品发布功能：模拟发布到惠农网平台")
        st.write("注意：本系统为毕设演示，发布功能为模拟实现，不会实际发布到惠农网")

        with st.form("listing_form"):
            title = st.text_input("商品名称", placeholder="例如：新鲜大米 5kg装")
            category = st.selectbox("品类", ["水果", "蔬菜", "粮食", "苗木", "农资", "水产", "种子", "茶叶", "调料", "其他"])

            col1, col2 = st.columns(2)
            with col1:
                location = st.text_input("产地", placeholder="例如：湖南湘潭")
                quality = st.selectbox("质量等级", ["优", "良", "标准", "有机"])
            with col2:
                brand = st.text_input("品牌/厂家", placeholder="例如：厂家直供")
                packaging = st.selectbox("包装方式", ["散装", "礼盒装", "罐装", "袋装", "箱装", "其他"])

            description = st.text_area("商品描述", placeholder="详细描述商品特点、优势、保质期等")

            c1, c2, c3 = st.columns(3)
            price = c1.number_input("单价（元）", min_value=0.01, value=10.0, step=0.1)
            quantity = c2.number_input("库存数量", min_value=0.1, value=100.0, step=0.1)
            unit = c3.selectbox("单位", ["斤", "公斤", "吨", "件", "箱", "袋", "瓶", "罐", "盒", "kg"])

            # 物流信息
            logistics = st.multiselect("物流方式", ["快递包邮", "物流发货", "上门自提", "部分包邮"], default=["快递包邮"])

            # 售后服务
            services = st.multiselect("售后服务", ["7天退换", "破损补发", "假货必赔", "货版一致", "坏损包赔"], default=["7天退换", "破损补发"])

            submitted = st.form_submit_button("模拟发布到惠农网", type="primary")

            if submitted:
                # 模拟发布成功
                full_description = f"{description}\n\n产地：{location}\n品牌：{brand}\n包装：{packaging}\n物流：{', '.join(logistics)}\n服务：{', '.join(services)}"

                # 实际保存到本地数据库（用于演示）
                db.add_listing(
                    user["id"], title, category, full_description, price, quantity, unit, quality
                )

                st.success("🎉 模拟发布成功！")
                st.info(f"您的商品《{title}》已模拟发布到惠农网平台\n商品ID: HN{user['id']}{int(datetime.now().timestamp())}\n实际发布请登录惠农网官网：https://www.cnhnb.com/")
                st.balloons()

        my_listings = db.get_user_listings(user["id"])
        if my_listings:
            st.subheader("我模拟发布的商品")
            st.info("这些商品已模拟发布到惠农网，实际交易请前往惠农网平台")

            df_listings = pd.DataFrame(my_listings)
            df_listings = df_listings.rename(columns={
                "id": "编号",
                "title": "商品名称",
                "category": "品类",
                "description": "描述",
                "price": "单价",
                "quantity": "库存",
                "unit": "单位",
                "quality_level": "质量等级",
                "created_at": "发布时间",
                "status": "状态",
            })
            st.dataframe(df_listings, width="stretch")

            st.subheader("编辑/删除模拟发布")
            listing_options = {f"{l['title']} (模拟发布 #{l['id']})": l for l in my_listings}
            selected_listing_key = st.selectbox("选择商品", list(listing_options.keys()), key="manage_listing_select")
            selected_listing = listing_options[selected_listing_key]

            with st.form("listing_edit_form"):
                edit_title = st.text_input("商品名称", value=selected_listing.get("title", ""))

                # 解析描述中的额外信息
                desc = selected_listing.get("description", "")
                location_match = re.search(r'产地：([^\n]+)', desc)
                brand_match = re.search(r'品牌：([^\n]+)', desc)
                packaging_match = re.search(r'包装：([^\n]+)', desc)

                edit_category = st.selectbox("品类", ["水果", "蔬菜", "粮食", "苗木", "农资", "水产", "种子", "茶叶", "调料", "其他"],
                                           index=["水果", "蔬菜", "粮食", "苗木", "农资", "水产", "种子", "茶叶", "调料", "其他"].index(selected_listing.get("category", "水果")) if selected_listing.get("category") in ["水果", "蔬菜", "粮食", "苗木", "农资", "水产", "种子", "茶叶", "调料", "其他"] else 0)

                col1, col2 = st.columns(2)
                with col1:
                    edit_location = col1.text_input("产地", value=location_match.group(1) if location_match else "")
                    edit_quality = col1.selectbox("质量等级", ["优", "良", "标准", "有机"],
                                                index=["优", "良", "标准", "有机"].index(selected_listing.get("quality_level", "标准")) if selected_listing.get("quality_level") in ["优", "良", "标准", "有机"] else 0)
                with col2:
                    edit_brand = col2.text_input("品牌/厂家", value=brand_match.group(1) if brand_match else "")
                    edit_packaging = col2.selectbox("包装方式", ["散装", "礼盒装", "罐装", "袋装", "箱装", "其他"],
                                                  index=["散装", "礼盒装", "罐装", "袋装", "箱装", "其他"].index(packaging_match.group(1) if packaging_match else "散装") if packaging_match and packaging_match.group(1) in ["散装", "礼盒装", "罐装", "袋装", "箱装", "其他"] else 0)

                edit_description = st.text_area("商品描述", value=desc.split('\n\n')[0] if '\n\n' in desc else desc)

                c1, c2, c3 = st.columns(3)
                edit_price = c1.number_input("单价（元）", min_value=0.01, value=float(selected_listing.get("price", 0.0)), step=0.1)
                edit_quantity = c2.number_input("数量", min_value=0.1, value=float(selected_listing.get("quantity", 0.0)), step=0.1)
                units = ["斤", "公斤", "吨", "件", "箱", "袋", "瓶", "罐", "盒", "kg"]
                current_unit = selected_listing.get("unit", "斤")
                unit_index = units.index(current_unit) if current_unit in units else 0
                edit_unit = c3.selectbox("单位", units, index=unit_index)

                edit_status = st.selectbox("状态", ["on_sale", "sold_out", "off_sale"], index=["on_sale", "sold_out", "off_sale"].index(selected_listing.get("status", "on_sale")))

                update_listing = st.form_submit_button("更新模拟发布")
                delete_listing = st.form_submit_button("删除模拟发布")

                if update_listing:
                    # 重新构建完整描述
                    full_description = f"{edit_description}\n\n产地：{edit_location}\n品牌：{edit_brand}\n包装：{edit_packaging}\n物流：快递包邮\n服务：7天退换, 破损补发"

                    db.update_listing(selected_listing["id"], user["id"], edit_title, edit_category, full_description, edit_price, edit_quantity, edit_unit, edit_quality, edit_status)
                    st.success("模拟发布已更新")
                    st.rerun()
                if delete_listing:
                    db.delete_listing(selected_listing["id"], user["id"])
                    st.success("模拟发布已删除")
                    st.rerun()


    with tab_market:
        st.markdown("### 🌾 惠农网市场大厅（数据模拟）")

        # 支持刷新操作，获取一批新的惠农网商品并重新排列本地商品
        if st.button("刷新市场商品"):
            success = simulate_market_refresh(user["id"], cnhnb_batch_size=5)
            if success:
                st.success("市场刷新完成")
                safe_rerun()

        # 初始化：首次进入若数据库中没有 cnhnb 商品则自动抓取一批
        if db.get_cnhnb_listing_count() < 5:
            simulate_fetch_cnhnb_listings(batch_size=5)

        listings = db.get_market_listings(user["id"])

        if not listings:
            st.info("市场暂无可购买商品。")
        else:
            col1, col2, col3 = st.columns(3)
            search_term = col1.text_input("搜索商品", placeholder="输入商品名称")
            category_filter = col2.selectbox("筛选品类", ["全部"] + sorted({l.get("category", "") for l in listings}))
            quality_filter = col3.selectbox("筛选质量", ["全部"] + sorted({l.get("quality_level", "") for l in listings}))

            filtered_listings = listings
            if search_term:
                filtered_listings = [l for l in filtered_listings if search_term.lower() in l.get("title", "").lower()]
            if category_filter != "全部":
                filtered_listings = [l for l in filtered_listings if l.get("category") == category_filter]
            if quality_filter != "全部":
                filtered_listings = [l for l in filtered_listings if l.get("quality_level") == quality_filter]

            st.write(f"找到 {len(filtered_listings)} 个商品")
            st.info("🟢 惠农网商品；🔵 本地用户商品")

            for item in filtered_listings:
                is_cnhnb = item.get("source") == "cnhnb"
                if is_cnhnb:
                    header = f"🟢 {item['title']} | {item['price']}元/{item['unit']} | 来源：惠农网"
                else:
                    header = f"🔵 {item['title']} | {item['price']}元/{item['unit']} | 卖家: {item.get('seller_name', '本地')}"

                with st.expander(header):
                    st.write(item.get("description", "无描述"))
                    st.write(f"库存：{item.get('quantity', 0)} {item.get('unit', '')}，等级：{item.get('quality_level', '')}")

                    if item.get("source_url"):
                        st.markdown(f"[查看惠农网原始链接]({item.get('source_url')})")

                    if is_cnhnb:
                        st.write("📍 此商品为惠农网数据，购买为模拟下单。")
                        qty = st.number_input(
                            "购买数量",
                            min_value=0.1,
                            max_value=float(item.get("quantity", 0)),
                            value=min(1.0, float(item.get("quantity", 0)) if item.get("quantity", 0) > 0 else 1.0),
                            step=0.1,
                            key=f"buy_qty_cnhnb_{item['id']}",
                        )
                        if st.button("立即下单 (模拟)", key=f"buy_cnhnb_{item['id']}"):
                            ok, msg = db.create_order(item['id'], user['id'], qty)
                            if ok:
                                st.success(f"模拟下单成功：{item['title']} x {qty} {item['unit']}，总价 {item['price'] * qty:.2f} 元")
                                st.info("提示：真实交易请前往惠农网平台。")
                            else:
                                st.error(msg)
                            st.rerun()
                    else:
                        qty = st.number_input(
                            "购买数量",
                            min_value=0.1,
                            max_value=float(item.get("quantity", 0)),
                            value=min(1.0, float(item.get("quantity", 0)) if item.get("quantity", 0) > 0 else 1.0),
                            step=0.1,
                            key=f"buy_qty_local_{item['id']}",
                        )
                        if st.button("立即下单", key=f"buy_local_{item['id']}"):
                            ok, msg = db.create_order(item['id'], user['id'], qty)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)
                            st.rerun()

    with tab_order:
        orders = db.get_orders(user["id"])
        if orders:
            df_orders = pd.DataFrame(orders)
            df_orders = df_orders.rename(columns={
                "id": "订单ID",
                "item_id": "商品ID",
                "order_type": "订单类型",
                "title": "商品名称",
                "quantity": "数量",
                "unit": "单位",
                "total_amount": "总金额",
                "status": "状态",
                "created_at": "下单时间",
            })
            st.dataframe(df_orders, width="stretch")

            st.subheader("更新/取消订单")
            order_options = {f"{o['title']} (#{o['id']})": o for o in orders}
            selected_order_key = st.selectbox("选择订单", list(order_options.keys()), key="manage_order_select")
            selected_order = order_options[selected_order_key]

            with st.form("order_edit_form"):
                edit_status = st.selectbox("订单状态", ["待发货", "已发货", "已完成", "已取消"], index=["待发货", "已发货", "已完成", "已取消"].index(selected_order.get("status", "待发货")))
                update_order = st.form_submit_button("更新订单")
                delete_order = st.form_submit_button("取消订单")

                if update_order:
                    db.update_order_status(selected_order["id"], user["id"], edit_status)
                    st.success("订单状态已更新")
                    st.rerun()
                if delete_order:
                    db.delete_order(selected_order["id"], user["id"])
                    st.success("订单已取消")
                    st.rerun()
        else:
            st.info("暂无订单。")

    with tab_tracking:
        orders = db.get_orders(user["id"])
        if orders:
            order_options = {f"订单 #{o['id']} - {o['title']}": o['id'] for o in orders}
            order_label = st.selectbox("选择订单", list(order_options.keys()), key="tracking_order")
            order_id = order_options[order_label]
            
            # 添加物流信息
            with st.form("tracking_form"):
                status = st.selectbox("物流状态", ["待发货", "已发货", "运输中", "已送达", "已完成"])
                location = st.text_input("当前位置", placeholder="例如：北京市朝阳区")
                notes = st.text_area("备注")
                submitted = st.form_submit_button("更新物流")
                if submitted:
                    db.add_order_tracking(order_id, status, location, notes)
                    st.success("物流信息已更新")
                    st.rerun()
            
            # 显示物流跟踪
            tracking = db.get_order_tracking(order_id)
            if tracking:
                df_tracking = pd.DataFrame(tracking)
                df_tracking = df_tracking.rename(columns={
                    "id": "编号",
                    "order_id": "订单ID",
                    "status": "状态",
                    "location": "位置",
                    "notes": "备注",
                    "updated_at": "更新时间",
                    "created_at": "创建时间",
                })
                st.dataframe(df_tracking, width="stretch")
            else:
                st.info("暂无物流信息。")
        else:
            st.info("暂无订单。")


def analytics_page(user):
    st.header("数据分析")
    history = db.get_diagnosis_history(user["id"], limit=500)
    if history:
        df = pd.DataFrame(history)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("识别置信度趋势")
            trend = df[["diagnosis_date", "confidence"]].copy()
            trend = trend.sort_values("diagnosis_date")
            trend = trend.set_index("diagnosis_date")
            st.line_chart(trend)
        with c2:
            st.subheader("高频病害 Top 8")
            top = df["class_name"].value_counts().head(8)
            st.bar_chart(top)
    else:
        st.info("暂无识别数据，无法分析。")

    listings = db.get_user_listings(user["id"])
    orders = db.get_orders(user["id"])
    st.subheader("交易概览")
    c1, c2, c3 = st.columns(3)
    c1.metric("累计发布商品", len(listings))
    c2.metric("累计订单", len(orders))
    c3.metric(
        "累计成交额（买卖）",
        f"{sum(float(x['total_amount']) for x in orders):.2f} 元" if orders else "0.00 元",
    )


def profile_page(user):
    st.header("账号信息")
    st.write(f"用户名：`{user['username']}`")
    st.write(f"邮箱：`{user['email']}`")
    st.write(f"姓名：`{user['full_name'] or '-'} `")
    st.write(f"电话：`{user['phone'] or '-'} `")
    st.write(f"角色：`{user['role']}`")
    st.write(f"注册时间：`{user['created_at']}`")


def learning_page(user):
    st.header("新病虫害学习中心")
    st.caption("提交样本 -> 管理员审核 -> 生成训练数据集与训练作业（数据准备）")

    is_admin = str(user.get("role") or "") == "admin"
    tab_submit, tab_mine, tab_review = st.tabs(["提交学习任务", "我的任务", "审核与数据准备"])

    with tab_submit:
        st.subheader("1) 创建学习任务")
        crops = get_crop_types()
        crops_with_other = crops + ["其他（自定义）"]
        crop_choice = st.selectbox("作物类型", crops_with_other)
        if crop_choice == "其他（自定义）":
            crop_type = st.text_input("自定义作物类型", placeholder="例如：水稻/小麦/……")
        else:
            crop_type = crop_choice
        disease_name = st.text_input("新病虫害名称", placeholder="例如：水稻条纹病（示例）")
        description = st.text_area("任务描述（可选）")

        st.subheader("2) 填写知识库要点（用于审核后展示）")
        symptoms = st.text_area("症状描述（可选但建议填写）")
        prevention = st.text_area("预防措施（可选但建议填写）")
        treatment = st.text_area("治疗/处置建议（可选但建议填写）")

        st.subheader("3) 上传图片样本")
        uploaded_files = st.file_uploader(
            "上传一组叶片/植株图片（建议每个新病害至少 50 张）",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="learning_uploads",
        )

        if st.button("提交并上传样本", type="primary"):
            if not disease_name.strip():
                st.error("请填写“新病虫害名称”。")
                return
            if not crop_type or not str(crop_type).strip():
                st.error("请填写“作物类型”。")
                return
            if not uploaded_files:
                st.error("请先上传图片样本。")
                return

            task_id = db.create_learning_task(
                requester_id=user["id"],
                crop_type=crop_type,
                disease_name=disease_name.strip(),
                description=description,
                symptoms=symptoms,
                prevention=prevention,
                treatment=treatment,
            )

            storage_root = os.path.join(os.getcwd(), "datasets", "learning", f"task_{task_id}", "pending")
            os.makedirs(storage_root, exist_ok=True)

            saved = 0
            for f in uploaded_files:
                file_name = os.path.basename(f.name)
                if not file_name:
                    continue
                safe_name = file_name.replace("..", "").replace("/", "_").replace("\\", "_")
                abs_path = os.path.join(storage_root, safe_name)
                with open(abs_path, "wb") as out:
                    out.write(f.getbuffer())
                db.add_learning_image(task_id, safe_name, abs_path)
                saved += 1

            st.success(f"提交成功：任务ID `{task_id}`，已保存 {saved} 张图片。等待管理员审核。")
            st.rerun()

    with tab_mine:
        st.subheader("我的学习任务进度")
        tasks = db.get_learning_tasks_by_requester(user["id"])
        if not tasks:
            st.info("暂无提交记录。")
        else:
            df = pd.DataFrame(tasks)
            df = df.rename(columns={
                "id": "任务ID",
                "crop_type": "作物类型",
                "disease_name": "病害名称",
                "status": "状态",
                "image_count": "图片数量",
                "reason": "拒绝理由",
                "created_at": "创建时间",
                "approved_at": "审核时间",
            })
            st.dataframe(
                df[
                    [
                        "任务ID",
                        "作物类型",
                        "病害名称",
                        "状态",
                        "图片数量",
                        "拒绝理由",
                        "创建时间",
                        "审核时间",
                    ]
                ],
                width="stretch",
            )

            recent = max(tasks, key=lambda x: x["created_at"]) if tasks else None
            if recent:
                with st.expander("最近任务图片预览（最多 4 张）"):
                    imgs = db.get_learning_images(recent["id"])[:4]
                    cols = st.columns(4)
                    for idx, img in enumerate(imgs):
                        try:
                            im = Image.open(img["storage_path"])
                            cols[idx].image(im, width=120, caption=img["file_name"])
                        except Exception:
                            cols[idx].write("图片读取失败")

    with tab_review:
        st.subheader("管理员审核与训练作业")
        if not is_admin:
            st.info("只有管理员账号可以审核与触发训练作业。")
            return

        st.markdown("### 增量训练参数（建议小步快跑）")
        incr_epochs = st.number_input("epoch 数", min_value=1, max_value=50, value=5, step=1)
        incr_lr = st.number_input("学习率", min_value=1e-7, max_value=1e-1, value=0.0005, format="%.7f")
        incr_batch = st.number_input("批大小", min_value=1, max_value=64, value=16, step=1)
        rehearsal_per_class = st.number_input("旧类回放：每类图片数", min_value=1, max_value=200, value=5, step=1)

        st.markdown("### 待审核任务")
        pending = db.get_pending_learning_tasks()
        if not pending:
            st.caption("当前没有待审核任务。")
        else:
            for t in pending:
                with st.expander(f"任务 #{t['id']}：{t['disease_name']}（{t['crop_type']}） | 图片 {t['image_count']}"):
                    st.write(f"提交者：{t['requester_name']}")
                    st.write(f"描述：{t.get('description') or '-'}")
                    symptoms_editor = st.text_area("症状", value=t.get("symptoms") or "", key=f"sym_{t['id']}")
                    prevention_editor = st.text_area(
                        "预防措施", value=t.get("prevention") or "", key=f"prev_{t['id']}"
                    )
                    treatment_editor = st.text_area(
                        "治疗/处置建议", value=t.get("treatment") or "", key=f"trt_{t['id']}"
                    )
                    reject_reason = st.text_input("驳回原因（仅驳回时填写）", key=f"rej_{t['id']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("批准（approved）", key=f"approve_{t['id']}"):
                            db.review_learning_task(
                                t["id"],
                                "approved",
                                reason="",
                                symptoms=symptoms_editor,
                                prevention=prevention_editor,
                                treatment=treatment_editor,
                            )
                            st.success("已批准。")
                            st.rerun()
                    with c2:
                        if st.button("驳回（rejected）", key=f"reject_{t['id']}"):
                            db.review_learning_task(
                                t["id"],
                                "rejected",
                                reason=reject_reason or "不符合要求",
                            )
                            st.success("已驳回。")
                            st.rerun()

        st.markdown("### 已通过任务：导出数据集 & 触发训练作业")
        approved = db.get_approved_learning_tasks()
        if not approved:
            st.caption("当前没有已通过任务。")
        else:
            for t in approved:
                with st.expander(f"任务 #{t['id']}：{t['disease_name']} | 图片 {t['image_count']}"):
                    st.write(f"任务描述：{t.get('description') or '-'}")
                    c1, c2 = st.columns(2)
                    export_root = os.path.join(os.getcwd(), "datasets", "learning_exports")
                    with c1:
                        if st.button("导出训练数据集", key=f"export_{t['id']}"):
                            try:
                                export_dir = export_approved_task_dataset(t["id"], export_root)
                                st.success(f"导出完成：{export_dir}")
                            except Exception as e:
                                st.error(str(e))
                    with c2:
                        if st.button("触发训练作业（生成日志）", key=f"train_{t['id']}"):
                            os.environ["INCR_EPOCHS"] = str(int(incr_epochs))
                            os.environ["INCR_LR"] = str(float(incr_lr))
                            os.environ["INCR_BATCH"] = str(int(incr_batch))
                            os.environ["INCR_REHEARSAL_PER_CLASS"] = str(int(rehearsal_per_class))
                            job_id = db.create_train_job(t["id"])
                            with st.spinner("运行训练作业（数据准备/导出）中…"):
                                msg = run_learning_training_job(job_id)
                            st.success(f"作业#{job_id}：{msg}")
                            st.rerun()
