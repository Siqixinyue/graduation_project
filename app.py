#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import threading
import time
import shutil
from PIL import Image
import streamlit as st

# 导入页面模块
from pages import (
    auth_page,          # 用户认证页面（登录/注册）
    dashboard_page,     # 仪表盘页面
    diagnosis_page,     # 病虫害识别页面
    farm_page,          # 农场管理页面
    inventory_page,     # 农资库存管理页面
    market_page,        # 交易市场页面
    analytics_page,     # 数据分析页面
    profile_page,       # 用户个人资料页面
    learning_page,      # 新病虫害学习中心页面
)

# 导入工具模块
from utils.database import db          # 数据库操作模块
from utils.model import load_model, predict  # AI模型加载和推理模块
from utils.class_names import get_class_name  # 病害类别名称获取模块

# Streamlit页面配置
st.set_page_config(
    page_title="智农云平台",      # 页面标题
    page_icon="🌾",               # 页面图标
    layout="wide"                 # 宽屏布局
)

# 自动检测配置
AUTO_IMAGE_SOURCE_FOLDER = r"C:\Users\17528\Desktop\picture"
PROCESSED_IMAGE_FOLDER = os.path.join(os.getcwd(), "processed_images")
AUTO_DETECTION_INTERVAL = 60  # 自动检测间隔时间（秒）
AUTO_DETECTION_USER_ID = 1    # 自动检测使用的管理员用户ID


# 自定义CSS样式 - 为应用提供现代化、美观的界面设计
st.markdown("""
<style>
    /* 全局样式 - 设置整体页面风格 */
    body {
        background-color: #f5f7fa;                                    /* 浅灰色背景 */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* 现代字体 */
        color: black;                                                 /* 黑色字体 */
    }

    /* 标题样式 - 主要页面标题的视觉效果 */
    .stTitle {
        font-size: 2.5rem;           /* 大字体 */
        font-weight: bold;           /* 加粗 */
        color: black;                /* 黑色 */
        text-align: center;          /* 居中对齐 */
        margin-bottom: 1rem;        /* 下边距 */
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1); /* 文字阴影效果 */
    }

    /* 副标题样式 - 页面副标题样式 */
    .stHeader {
        font-size: 1.8rem;           /* 中等字体 */
        font-weight: bold;           /* 加粗 */
        color: black;                /* 黑色 */
        margin-top: 2rem;           /* 上边距 */
        margin-bottom: 1rem;        /* 下边距 */
        border-left: 4px solid #27ae60; /* 左侧绿色边框 */
        padding-left: 1rem;         /* 左侧内边距 */
    }

    /* 卡片样式 - 内容容器的视觉效果 */
    .card {
        background-color: white;     /* 白色背景 */
        border-radius: 10px;         /* 圆角 */
        padding: 1.5rem;            /* 内边距 */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 阴影效果 */
        margin-bottom: 1.5rem;      /* 下边距 */
        transition: transform 0.3s ease, box-shadow 0.3s ease; /* 悬停过渡效果 */
        color: black;                /* 黑色字体 */
    }

    .card:hover {
        transform: translateY(-5px);                        /* 悬停上移 */
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);       /* 增强阴影 */
    }

    /* 按钮样式 - 自定义按钮外观 */
    .stButton > button {
        background-color: #27ae60;      /* 绿色背景 */
        color: black;                   /* 黑色文字 */
        border-radius: 8px;             /* 圆角 */
        padding: 0.5rem 1.5rem;        /* 内边距 */
        font-size: 1rem;               /* 字体大小 */
        font-weight: bold;             /* 加粗 */
        transition: background-color 0.3s ease, transform 0.2s ease; /* 过渡效果 */
    }

    .stButton > button:hover {
        background-color: #229954;      /* 深绿色悬停 */
        transform: translateY(-2px);    /* 悬停上移 */
    }

    /* 主要按钮样式 */
    .stButton > button[type="primary"] {
        background-color: #85c1e9;      /* 蓝色背景 */
    }

    .stButton > button[type="primary"]:hover {
        background-color: #2980b9;      /* 深蓝色悬停 */
    }

    /* 输入框样式 */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 0.5rem;
        transition: border-color 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #27ae60;
        box-shadow: 0 0 0 2px rgba(39, 174, 96, 0.2);
    }

    /* 选择框样式 */
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 0.5rem;
        transition: border-color 0.3s ease;
    }

    .stSelectbox > div > div > select:focus {
        border-color: #27ae60;
        box-shadow: 0 0 0 2px rgba(39, 174, 96, 0.2);
    }

    /* 数据框样式 */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 侧边栏样式（宝塔面板风格） */
section[data-testid="stSidebar"] {
    background-color: #85c1e9 !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    color: #f8fbff !important;
    padding: 0 !important;
    border-radius: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
    min-width: 220px !important;
    max-width: 220px !important;
    border-right: 1px solid #0F172A !important;
}

section[data-testid="stSidebar"] .css-7l0x2m {
    color: #f5f8ff !important;
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #ffffff !important;
    background-color: #0F172A !important;
    padding: 16px 20px !important;
    margin: 0 !important;
    border-bottom: 1px solid #334155 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}

/* 侧边栏导航 */
section[data-testid="stSidebar"] .stRadio > div {
    flex-direction: column;
    gap: 0 !important;
    padding: 10px 0 !important;
}

section[data-testid="stSidebar"] .stRadio label {
    background-color: transparent !important;
    color: #CBD5E1 !important;
    padding: 11px 20px !important;
    border-radius: 0 !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    border: none !important;
    font-size: 14px !important;
    margin: 0 !important;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #334155 !important;
    color: #fff !important;
    transform: none !important;
}

section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label {
    background-color: #1E293B !important;
    border-color: transparent !important;
    color: #38BDF8 !important;
    box-shadow: none !important;
    border-left: 4px solid #38BDF8 !important;
    font-weight: 500 !important;
}

/* 隐藏 radio 小圆点 */
section[data-testid="stSidebar"] .stRadio input[type="radio"] {
    display: none !important;
}

/* 侧边栏按钮 */
.css-1d391kg button {
    background-color: #e74c3c;
    color: black;
    border-radius: 8px;
    margin-top: 2rem;
    width: 100%;
    padding: 0.75rem;
    font-weight: bold;
}

.css-1d391kg button:hover {
    background-color: #c0392b;
}

    /* 信息框样式 */
    .stInfo {
        border-radius: 8px;
        border-left: 4px solid #3498db;
        background-color: #f0f8ff;
        color: black;                /* 黑色字体 */
    }

    /* 成功框样式 */
    .stSuccess {
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        background-color: #f0fff0;
        color: black;                /* 黑色字体 */
    }

    /* 错误框样式 */
    .stError {
        border-radius: 8px;
        border-left: 4px solid #e74c3c;
        background-color: #fff0f0;
        color: black;                /* 黑色字体 */
    }

    /* 警告框样式 */
    .stWarning {
        border-radius: 8px;
        border-left: 4px solid #f39c12;
        background-color: #fffaf0;
        color: black;                /* 黑色字体 */
    }

    /* 标签页样式 */
    .stTabs {
        margin-bottom: 2rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.12) !important;
        color: #000000 !important;
        border: 1px solid rgba(255, 255, 255, 0.12); 
        border-bottom: 2px solid rgba(255, 255, 255, 0.20);
        border-radius: 10px 10px 0 0;
        padding: 0.85rem 1.4rem;
        font-weight: bold;
        transition: all 0.2s ease;
        box-shadow: inset 0 0 0 0 rgba(0,0,0,0);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
        color: #fff !important;
        transform: translateY(-1px);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #267d34 !important;
        color: #ffffff !important;
        border-color: #39b54a !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }

    .stTabs [data-baseweb="tab"][aria-selected="false"] {
        opacity: 0.85;
    }

    /* 表单样式 */
    .stForm {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        color: black;                /* 黑色字体 */
    }

    /* 展开框样式 */
    .stExpander {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        color: black;                /* 黑色字体 */
    }

    .stExpanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 1rem;
        font-weight: bold;
        color: black;                /* 黑色字体 */
    }

    /* 指标卡片样式 */
    .stMetric {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: black;                /* 黑色字体 */
    }

    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }

    /* 响应式调整 */
    @media (max-width: 768px) {
        .css-1d391kg {
            padding: 1rem;
        }

        .stHeader {
            font-size: 1.5rem;
        }

        .card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 模型缓存装饰器 - 使用Streamlit的缓存机制优化模型加载性能
@st.cache_resource
def get_model(model_path: str, model_mtime: float):
    """
    获取AI模型的缓存函数

    使用Streamlit的缓存装饰器来避免重复加载模型，
    提高应用启动速度和内存使用效率。

    参数：
    - model_path: 模型文件路径
    - model_mtime: 模型文件的修改时间戳

    返回：
    - 加载的AI模型对象，如果文件不存在则返回None
    """
    if not os.path.exists(model_path):
        return None
    return load_model(model_path)

# 初始化Session State变量
if "user" not in st.session_state:
    st.session_state.user = None  # 当前登录用户信息

if "menu" not in st.session_state:
    st.session_state.menu = "仪表盘"  # 当前选中的菜单项

# 加载AI模型
model_path = "models/version/model_v1.pth"  # 模型文件路径
model_mtime = os.path.getmtime(model_path) if os.path.exists(model_path) else 0.0  # 获取模型文件修改时间
model = get_model(model_path, model_mtime)  # 加载或获取缓存的模型

# 启动自动图像监控线程（仅启动一次）
if "auto_detection_started" not in st.session_state:
    def run_auto_detection():
        """
        自动检测线程函数

        该函数在后台运行，定期扫描指定文件夹中的新图片，
        使用AI模型进行病虫害识别，并将结果保存到数据库中。

        工作流程：
        1. 检查源文件夹是否存在
        2. 扫描新图片文件（按文件名排序处理）
        3. 对每张图片进行AI识别
        4. 将识别结果保存到诊断历史
        5. 如果检测到病害，生成自动提醒
        6. 将处理过的图片移动到已处理文件夹
        7. 等待指定间隔后重复执行

        注意：这是一个守护线程，会在主程序退出时自动终止
        """
        if not os.path.exists(AUTO_IMAGE_SOURCE_FOLDER):
            return  # 如果源文件夹不存在，直接返回

        # 确保已处理图片文件夹存在
        os.makedirs(PROCESSED_IMAGE_FOLDER, exist_ok=True)

        while True:
            try:
                # 获取源文件夹中的所有图片文件，并按文件名排序
                images = [f for f in os.listdir(AUTO_IMAGE_SOURCE_FOLDER)
                         if f.lower().endswith((".jpg", ".jpeg", ".png"))]

                if images:
                    # 处理第一张图片（先进先出）
                    image_name = images[0]
                    src_path = os.path.join(AUTO_IMAGE_SOURCE_FOLDER, image_name)

                    try:
                        # 加载和预处理图片
                        img = Image.open(src_path)

                        # 使用AI模型进行预测
                        class_id, confidence = predict(model, img)

                        # 获取预测结果的类别名称
                        class_name = get_class_name(class_id)

                        # 将识别结果记录到诊断历史
                        db.add_diagnosis_history(
                            AUTO_DETECTION_USER_ID,
                            image_name,
                            class_id,
                            class_name,
                            float(confidence)
                        )

                        # 如果检测到病害（类别名不包含"健康"），生成自动提醒
                        if "健康" not in class_name:
                            db.add_auto_alert(
                                AUTO_DETECTION_USER_ID,
                                image_name,
                                class_id,
                                class_name,
                                float(confidence)
                            )

                        # 将处理过的图片移动到已处理文件夹
                        dst_path = os.path.join(PROCESSED_IMAGE_FOLDER, image_name)
                        shutil.move(src_path, dst_path)

                    except Exception as process_err:
                        print("自动识别处理图片失败：", process_err)
                        continue

                # 等待指定间隔后继续检测
                time.sleep(AUTO_DETECTION_INTERVAL)

            except Exception as err:
                print("自动识别线程错误：", err)
                time.sleep(AUTO_DETECTION_INTERVAL)

    # 如果模型加载成功，启动自动检测线程
    if model is not None:
        thread = threading.Thread(target=run_auto_detection, daemon=True)
        thread.start()

    st.session_state.auto_detection_started = True

# 用户认证检查 - 确保用户已登录
if st.session_state.user is None:
    # 如果用户未登录，显示认证页面
    auth_page()
    st.stop()  # 停止执行后续代码

# 获取最新的用户信息（确保用户信息是最新的）
latest_user = db.get_user_by_id(st.session_state.user["id"])
if latest_user is None:
    # 如果用户不存在或已被删除，清除登录状态
    st.session_state.user = None
    st.warning("用户状态已失效，请重新登录。")
    st.stop()

# 更新session中的用户信息
st.session_state.user = latest_user

# 侧边栏导航界面
st.sidebar.title("智农云平台")  # 侧边栏标题
st.sidebar.write(f"当前用户：**{latest_user['username']}**")  # 显示当前用户名

# 退出登录按钮
if st.sidebar.button("退出登录"):
    st.session_state.user = None  # 清除用户登录状态
    st.rerun()  # 重新运行应用

# 功能导航菜单
st.session_state.menu = st.sidebar.radio(
    "功能导航",
    ["仪表盘", "识别中心", "新病害学习中心", "农场管理", "农资库存", "交易市场", "数据分析", "我的账号"],
    index=["仪表盘", "识别中心", "新病害学习中心", "农场管理", "农资库存", "交易市场", "数据分析", "我的账号"].index(st.session_state.menu)
)

# 获取当前选中的菜单项
menu = st.session_state.menu

# 页面路由 - 根据用户选择的菜单项显示对应页面
if menu == "仪表盘":
    # 显示仪表盘页面，包含系统概览和统计信息
    dashboard_page(latest_user)
elif menu == "识别中心":
    # 显示病虫害识别页面，允许用户上传图片进行AI识别
    diagnosis_page(latest_user, model)
elif menu == "新病害学习中心":
    # 显示新病害学习页面，用户可以上传新病害样本进行学习
    learning_page(latest_user)
elif menu == "农场管理":
    # 显示农场管理页面，管理农场信息、作物生长记录等
    farm_page(latest_user)
elif menu == "农资库存":
    # 显示农资库存管理页面，管理农药、化肥等农业物资
    inventory_page(latest_user)
elif menu == "交易市场":
    # 显示交易市场页面，农产品买卖交易功能
    market_page(latest_user)
elif menu == "数据分析":
    # 显示数据分析页面，提供各类统计图表和分析报告
    analytics_page(latest_user)
else:
    # 显示用户个人资料页面，包含账号设置和个人信息
    profile_page(latest_user)

