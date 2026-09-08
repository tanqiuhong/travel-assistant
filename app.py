"""
旅行手帐 · 智慧旅游助手（功能增强版）
所有内容由 DeepSeek AI 生成 | 日系樱色主题
功能：行程规划 · 美食推荐 · 住宿建议 · 交通指引 · 旅行贴士 · 打包清单 · 每日花费估算
"""

import streamlit as st
import pandas as pd
import os
import json
import time
from datetime import datetime, timedelta
from openai import OpenAI

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="旅行手帐 · 智慧旅游助手",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== API Key 读取 ====================
def get_api_key():
    try:
        return st.secrets["DEEPSEEK_API_KEY"]
    except:
        return os.getenv("DEEPSEEK_API_KEY")

def get_openai_client():
    key = get_api_key()
    if not key:
        return None
    try:
        return OpenAI(api_key=key, base_url="https://api.deepseek.com", timeout=60)
    except:
        return None

# ==================== 日系樱色 CSS ====================
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #fdf0f4, #fce4ec); }
    .main .block-container {
        background: rgba(255,248,250,0.92);
        border-radius: 24px;
        padding: 2rem 2.5rem !important;
        box-shadow: 0 8px 40px rgba(200,150,160,0.12);
    }
    .stButton > button {
        background: #d4839b !important;
        color: white !important;
        border-radius: 30px !important;
        box-shadow: 0 4px 16px rgba(200,120,145,0.2) !important;
    }
    .stButton > button:hover {
        background: #c07a90 !important;
        transform: translateY(-2px);
    }
    h1, h2, h3 { color: #4a3a40 !important; font-family: 'Georgia', serif !important; font-weight: 300 !important; }
    .css-1d391kg, .css-1aumxhk { background: #fff5f8 !important; }
    .card {
        background: rgba(255,250,252,0.9);
        border-radius: 18px;
        padding: 20px 24px;
        margin-bottom: 16px;
        border: 1px solid rgba(245,210,220,0.4);
        box-shadow: 0 4px 20px rgba(200,150,165,0.06);
    }
    .card-title {
        font-family: 'Georgia', serif;
        font-weight: 400;
        color: #4a3a40;
        border-bottom: 1px dashed #ecd5dd;
        padding-bottom: 8px;
        margin-bottom: 12px;
        letter-spacing: 2px;
    }
    .weather-card {
        background: linear-gradient(135deg, #f5e0e8, #eccee0);
        border-radius: 18px;
        padding: 16px 20px;
        margin-bottom: 16px;
        border: 1px solid rgba(235,200,215,0.3);
    }
    .weather-temp { font-size: 2rem; font-weight: 300; color: #4a3a40; }
    .weather-desc { color: #6a5a60; font-weight: 300; }
    .feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 10px 0; }
    .feature-item {
        background: rgba(255,245,248,0.6);
        border-radius: 12px;
        padding: 8px 14px;
        text-align: center;
        font-size: 0.8rem;
        color: #4a3a40;
        border: 1px solid #f0dce3;
        cursor: pointer;
        transition: all 0.2s;
    }
    .feature-item:hover { background: #f5e4ea; border-color: #d4839b; }
    .feature-item.active { background: #d4839b; color: white; border-color: #d4839b; }
    .travel-tip {
        background: rgba(250,240,245,0.7);
        border-radius: 14px;
        padding: 14px 18px;
        border-left: 3px solid #d4839b;
        font-weight: 300;
        color: #4a3a40;
    }
    .divider-sakura {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #ecd5dd, transparent);
        margin: 16px 0;
    }
    .sidebar-title { text-align: center; padding: 8px 0 16px 0; font-family: 'Georgia', serif; }
    .sidebar-title .icon { font-size: 2rem; color: #d4839b; opacity: 0.6; }
    .sidebar-title .text { font-size: 1rem; font-weight: 300; color: #4a3a40; letter-spacing: 4px; }
    .attraction-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 8px;
        border-bottom: 1px solid #f5e8ee;
    }
    .attraction-item:last-child { border-bottom: none; }
    .attraction-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
    .attraction-name { font-weight: 350; color: #4a3a40; font-size: 0.9rem; }
    .attraction-desc { font-size: 0.75rem; color: #b09aa2; margin-left: auto; }
    .budget-item { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #f5e8ee; }
    .budget-item .label { color: #6a5a60; }
    .budget-item .value { color: #4a3a40; font-weight: 400; }
</style>
""", unsafe_allow_html=True)

# ==================== DeepSeek 驱动函数 ====================

def call_deepseek(prompt, system_prompt="你是一位专业的旅行规划师，善于提供详细、实用的旅行建议。"):
    """通用 DeepSeek 调用函数"""
    client = get_openai_client()
    if not client:
        return None
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return None

# ==================== 各功能模块 ====================

def generate_itinerary(destination, days, budget, interests, travel_style, accommodation):
    """生成完整行程（含交通指引）"""
    prompt = f"""
    为以下旅行生成{days}天详细行程（含每天的交通指引）：

    目的地：{destination}
    天数：{days}天
    预算：{budget}
    兴趣偏好：{interests}
    旅行风格：{travel_style}
    住宿偏好：{accommodation}

    请按天输出，每天包含：
    1. 上午/下午/傍晚的行程安排
    2. 从一处到另一处的具体交通方式（公交线路、地铁线路、换乘方式、大致时间）
    3. 推荐的景点和活动

    用 Markdown 格式，简洁优雅，减少表情符号。
    """
    return call_deepseek(prompt)

def generate_food_recommendations(destination, budget, interests):
    """美食推荐"""
    prompt = f"""
    为{destination}旅行推荐特色美食：

    预算等级：{budget}
    兴趣偏好：{interests}

    请提供：
    1. 当地必吃美食（3-5种）
    2. 推荐餐厅（含人均价格和特色菜）
    3. 美食街区推荐
    4. 本地人常去的小吃店

    用简洁的列表形式，不要用表情符号。
    """
    return call_deepseek(prompt, "你是一位美食达人，熟悉各地特色美食和地道餐厅。")

def generate_accommodation_advice(destination, budget, travel_style):
    """住宿建议"""
    prompt = f"""
    为{destination}旅行提供住宿建议：

    预算等级：{budget}
    旅行风格：{travel_style}

    请提供：
    1. 推荐住宿区域（2-3个，说明各自特点）
    2. 不同类型住宿的参考价格
    3. 预订建议（提前多久、使用什么平台）
    4. 注意事项

    用简洁的列表形式。
    """
    return call_deepseek(prompt, "你是一位旅行住宿专家，熟悉各地酒店和民宿情况。")

def generate_packing_list(destination, days, season="春秋"):
    """打包清单"""
    prompt = f"""
    为{destination} {days}天旅行生成打包清单：

    季节：{season}
    天数：{days}天

    请分类列出：
    1. 衣物（按季节和天数）
    2. 个人用品
    3. 电子设备
    4. 药品/急救
    5. 其他必备物品

    用分类列表形式，简洁实用。
    """
    return call_deepseek(prompt, "你是一位经验丰富的旅行者，擅长整理实用的打包清单。")

def generate_budget_estimate(destination, days, budget):
    """花费估算"""
    prompt = f"""
    为{destination} {days}天旅行估算各项花费：

    预算等级：{budget}

    请按以下分类给出每日/总预算：
    1. 住宿
    2. 餐饮
    3. 交通（市内+城际）
    4. 门票/景点
    5. 购物/其他

    给出每个类别的预算范围和建议。
    """
    return call_deepseek(prompt, "你是一位旅行预算专家，擅长合理规划旅行开销。")

def generate_travel_tips(destination, season="春秋"):
    """旅行贴士"""
    prompt = f"""
    为{destination}旅行提供实用贴士：

    季节：{season}

    请提供：
    1. 最佳旅行时间
    2. 当地交通（如何出行、常用APP）
    3. 语言/沟通
    4. 安全注意事项
    5. 文化礼仪
    6. 紧急联系方式
    """
    return call_deepseek(prompt, "你是一位资深旅行顾问，熟悉各地旅行注意事项。")

def get_weather(city):
    """天气查询（通过 DeepSeek）"""
    prompt = f"{city}今天的天气情况，以JSON格式：{{'temp':数字,'condition':'描述','wind':'描述'}}"
    result = call_deepseek(prompt, "你是一位天气助手，提供准确的天气信息。")
    if result:
        try:
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result.strip()
            return json.loads(json_str)
        except:
            pass
    return {"temp": "22", "condition": "晴", "wind": "微风"}

def get_attractions(city):
    """景点推荐"""
    prompt = f"""
    {city}著名景点列表，JSON数组格式：
    [{{"name":"名称","lat":纬度,"lng":经度,"desc":"简短描述","url":"官网链接"}}]
    至少5个景点。
    """
    result = call_deepseek(prompt, "你是一位旅游地理专家。")
    if result:
        try:
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result.strip()
            return json.loads(json_str)
        except:
            pass
    return get_default_attractions(city)

def get_default_attractions(city):
    """默认景点数据（备用）"""
    defaults = {
        "杭州": [
            {"name": "西湖", "lat": 30.2741, "lng": 120.1551, "desc": "5A景区", "url": ""},
            {"name": "灵隐寺", "lat": 30.2391, "lng": 120.1062, "desc": "千年古刹", "url": ""},
            {"name": "宋城", "lat": 30.1882, "lng": 120.1338, "desc": "主题公园", "url": ""},
        ],
        "北京": [
            {"name": "故宫", "lat": 39.9163, "lng": 116.3972, "desc": "明清皇宫", "url": "https://www.dpm.org.cn"},
            {"name": "天安门", "lat": 39.9087, "lng": 116.3975, "desc": "国家象征", "url": ""},
            {"name": "长城", "lat": 40.4319, "lng": 116.5704, "desc": "世界奇迹", "url": ""},
        ],
    }
    return defaults.get(city, [{"name": f"{city}公园", "lat": 30.0, "lng": 120.0, "desc": "城市绿肺", "url": ""}])

def get_coordinates(city):
    """获取城市坐标"""
    coords = {
        "杭州": [30.2741, 120.1551],
        "北京": [39.9042, 116.4074],
        "上海": [31.2304, 121.4737],
        "成都": [30.5728, 104.0668],
        "广州": [23.1291, 113.2644],
        "深圳": [22.5431, 114.0579],
        "武汉": [30.5928, 114.3055],
        "西安": [34.3416, 108.9398],
        "重庆": [29.4316, 106.9123],
        "苏州": [31.2990, 120.5853],
    }
    return coords.get(city, [30.2741, 120.1551])

def render_map(city_name, attractions):
    """渲染地图"""
    if not attractions:
        st.info("暂无景点数据")
        return
    df = pd.DataFrame(attractions)
    if 'lng' in df.columns:
        df = df.rename(columns={'lng': 'lon'})
    if 'lat' in df.columns and 'lon' in df.columns:
        st.map(df[['lat', 'lon']], zoom=12, use_container_width=True)
        st.caption("景点位置")

# ==================== 初始化 ====================
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_itinerary' not in st.session_state:
    st.session_state.current_itinerary = ""
if 'attractions' not in st.session_state:
    st.session_state.attractions = []
if 'current_module' not in st.session_state:
    st.session_state.current_module = "行程规划"
if 'module_results' not in st.session_state:
    st.session_state.module_results = {}

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown('<div class="sidebar-title"><div class="icon">🌸</div><div class="text">旅行设置</div></div>', unsafe_allow_html=True)

    destination = st.text_input("目的地", value="杭州")
    days = st.slider("旅行天数", 1, 10, 3)
    budget = st.selectbox("预算等级", ["经济型 (200-500元/天)", "舒适型 (500-1000元/天)", "豪华型 (1000元以上/天)"])
    season = st.selectbox("旅行季节", ["春季", "夏季", "秋季", "冬季"])
    interests = st.multiselect("兴趣偏好", ["自然风光", "历史文化", "美食探店", "购物", "主题乐园", "休闲度假", "摄影", "户外运动"], default=["自然风光", "美食探店"])

    with st.expander("更多选项"):
        travel_style = st.selectbox("旅行风格", ["悠闲放松", "深度探索", "网红打卡", "亲子游", "独自旅行", "情侣出游"])
        accommodation = st.selectbox("住宿偏好", ["特色民宿", "经济酒店", "星级酒店", "青年旅舍"])

    with st.expander("API设置"):
        api_key_input = st.text_input("DeepSeek API Key", type="password", placeholder="留空使用示例数据")
        if api_key_input:
            os.environ["DEEPSEEK_API_KEY"] = api_key_input
            st.success("已设置")

    st.markdown('<hr class="divider-sakura">', unsafe_allow_html=True)

    # 功能模块选择
    st.markdown("**功能模块**")
    modules = ["行程规划", "美食推荐", "住宿建议", "打包清单", "花费估算", "旅行贴士"]
    for mod in modules:
        if st.button(mod, key=f"mod_{mod}", use_container_width=True):
            st.session_state.current_module = mod

    st.markdown('<hr class="divider-sakura">', unsafe_allow_html=True)
    st.markdown("**旅行记录**")
    if st.session_state.history:
        for item in st.session_state.history[-3:]:
            st.caption(f"{item['destination']} - {item['date']}")
    else:
        st.caption("暂无记录")

    if st.button("重置", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==================== 主界面 ====================
st.markdown("""
<div style="font-size:2.2rem;font-weight:300;color:#4a3a40;font-family:'Georgia',serif;">
    旅行手帐 <span style="color:#d4839b;">·</span> 智慧旅游助手
</div>
<div style="color:#b08a96;font-size:0.9rem;margin-bottom:1.8rem;border-bottom:1px solid #f0dce3;padding-bottom:12px;">
    DeepSeek 驱动 · 多样化旅行规划
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1], gap="medium")

# ----- 左栏（主内容） -----
with col1:
    # 功能模块切换
    current_mod = st.session_state.current_module

    # 生成按钮 - 根据不同模块显示不同内容
    generate_key = f"generate_{current_mod}"

    if st.button(f"生成 {current_mod}", key=generate_key, type="primary"):
        with st.spinner(f"AI 正在生成 {current_mod}..."):
            if current_mod == "行程规划":
                result = generate_itinerary(destination, days, budget, ", ".join(interests), travel_style, accommodation)
                if result:
                    st.session_state.current_itinerary = result
                    st.session_state.history.append({'destination': destination, 'date': datetime.now().strftime("%Y-%m-%d %H:%M")})
            elif current_mod == "美食推荐":
                result = generate_food_recommendations(destination, budget, ", ".join(interests))
                st.session_state.module_results['food'] = result
            elif current_mod == "住宿建议":
                result = generate_accommodation_advice(destination, budget, travel_style)
                st.session_state.module_results['accommodation'] = result
            elif current_mod == "打包清单":
                result = generate_packing_list(destination, days, season)
                st.session_state.module_results['packing'] = result
            elif current_mod == "花费估算":
                result = generate_budget_estimate(destination, days, budget)
                st.session_state.module_results['budget'] = result
            elif current_mod == "旅行贴士":
                result = generate_travel_tips(destination, season)
                st.session_state.module_results['tips'] = result

            # 更新景点数据（供地图使用）
            attrs = get_attractions(destination)
            st.session_state.attractions = attrs

    # 显示结果
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">{current_mod}</div>', unsafe_allow_html=True)

    if current_mod == "行程规划":
        if st.session_state.current_itinerary:
            st.markdown(st.session_state.current_itinerary)
        else:
            st.caption("点击「生成行程规划」开始")
    else:
        result_key = {
            "美食推荐": "food",
            "住宿建议": "accommodation",
            "打包清单": "packing",
            "花费估算": "budget",
            "旅行贴士": "tips"
        }.get(current_mod)
        if result_key and st.session_state.module_results.get(result_key):
            st.markdown(st.session_state.module_results[result_key])
        else:
            st.caption(f"点击「生成 {current_mod}」开始")

    # 导出按钮（仅对行程规划）
    if current_mod == "行程规划" and st.session_state.current_itinerary:
        st.download_button("导出行程", data=st.session_state.current_itinerary, file_name=f"{destination}_行程.txt")

    st.markdown('</div>', unsafe_allow_html=True)

# ----- 右栏（天气 + 地图 + 景点） -----
with col2:
    # 天气
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    weather = get_weather(destination)
    st.markdown(f'<div class="weather-temp">{weather.get("temp", "22")}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="weather-desc">{weather.get("condition", "晴")} · {weather.get("wind", "微风")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.8rem;color:#b08a96;">{destination}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 地图
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">景点地图</div>', unsafe_allow_html=True)
    attrs = st.session_state.attractions if st.session_state.attractions else get_attractions(destination)
    if attrs:
        render_map(destination, attrs)
    else:
        st.info("暂无景点数据")
    st.markdown('</div>', unsafe_allow_html=True)

    # 景点列表
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">推荐景点</div>', unsafe_allow_html=True)
    if attrs:
        colors = ['#d4839b','#e8a0b5','#c07a90','#dbb0c0','#e8b8c8']
        for i, attr in enumerate(attrs):
            color = colors[i % len(colors)]
            url = attr.get('url', '')
            if url:
                st.markdown(f'<div class="attraction-item"><span class="attraction-dot" style="background:{color};"></span><span class="attraction-name">{attr["name"]}</span><a href="{url}" target="_blank" style="color:#d4839b;font-size:0.75rem;text-decoration:none;margin-left:auto;">官网</a></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="attraction-item"><span class="attraction-dot" style="background:{color};"></span><span class="attraction-name">{attr["name"]}</span><span class="attraction-desc">{attr.get("desc", "")}</span></div>', unsafe_allow_html=True)
    else:
        st.caption("暂无景点")
    st.markdown('</div>', unsafe_allow_html=True)

# ----- 底部 -----
st.markdown('<hr class="divider-sakura">', unsafe_allow_html=True)
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption("由 DeepSeek AI 驱动")
with col_f2:
    st.caption("日系樱色主题 · 旅行手帐")
with col_f3:
    st.caption(datetime.now().strftime("%Y年%m月%d日"))
