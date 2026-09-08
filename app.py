"""
旅行手帐 · 智慧旅游助手
日系清新风格 | 樱花粉 | 简约优雅
"""

import streamlit as st
from datetime import datetime
import os
import time
import json
import pandas as pd
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
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("DEEPSEEK_API_KEY")

def get_openai_client():
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        return OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=60.0,
            max_retries=2,
        )
    except:
        return None

# ==================== 日系清新风格 CSS（修复版） ====================
st.markdown("""
<style>
    /* 樱色主题 - 纯CSS，不依赖外部图片 */
    .stApp {
        background: linear-gradient(135deg, #fdf0f4 0%, #fce4ec 50%, #f8e0e8 100%);
    }
    
    /* 主容器 - 半透明白色磨砂 */
    .main .block-container {
        background: rgba(255, 248, 250, 0.92);
        border-radius: 24px;
        padding: 2rem 2.5rem !important;
        margin: 1rem auto;
        box-shadow: 0 8px 40px rgba(200, 150, 160, 0.12);
        border: 1px solid rgba(255, 220, 230, 0.3);
    }
    
    /* 标题 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 300;
        color: #4a3a40;
        margin-bottom: 0.1rem;
        letter-spacing: 4px;
        font-family: 'Georgia', serif;
    }
    .main-title span {
        color: #d4839b;
        font-weight: 400;
    }
    .main-title .sub {
        font-size: 0.9rem;
        color: #b08a96;
        letter-spacing: 6px;
        font-weight: 300;
        display: block;
        margin-top: 2px;
    }
    .sub-title {
        color: #b08a96;
        font-size: 0.9rem;
        margin-bottom: 1.8rem;
        letter-spacing: 2px;
        font-weight: 300;
        border-bottom: 1px solid #f0dce3;
        padding-bottom: 12px;
    }
    
    /* 卡片 */
    .card {
        background: rgba(255, 250, 252, 0.9);
        border-radius: 18px;
        padding: 20px 24px;
        margin-bottom: 16px;
        border: 1px solid rgba(245, 210, 220, 0.4);
        box-shadow: 0 4px 20px rgba(200, 150, 165, 0.06);
    }
    .card-title {
        font-size: 1rem;
        font-weight: 400;
        color: #4a3a40;
        margin-bottom: 12px;
        letter-spacing: 3px;
        font-family: 'Georgia', serif;
        border-bottom: 1px dashed #ecd5dd;
        padding-bottom: 8px;
    }
    
    /* 侧边栏 */
    .css-1d391kg, .css-1aumxhk {
        background: rgba(255, 248, 250, 0.95) !important;
        border-right: 1px solid rgba(235, 200, 210, 0.3) !important;
    }
    .css-1aumxhk .stTextInput > label,
    .css-1aumxhk .stSlider > label,
    .css-1aumxhk .stSelectbox > label,
    .css-1aumxhk .stMultiselect > label {
        color: #6a5a60 !important;
        font-weight: 300 !important;
        letter-spacing: 1px;
    }
    .css-1aumxhk .stTextInput > div > input {
        background: rgba(255, 245, 248, 0.7) !important;
        border: 1px solid #f0dce3 !important;
        border-radius: 12px !important;
        color: #3d3d3d !important;
    }
    
    /* 按钮 */
    .stButton > button {
        background: linear-gradient(135deg, #e8a0b5, #d4839b) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        font-weight: 400 !important;
        letter-spacing: 3px;
        padding: 10px 28px !important;
        box-shadow: 0 4px 16px rgba(200, 120, 145, 0.2) !important;
        font-family: 'Georgia', serif;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(200, 120, 145, 0.3) !important;
        background: linear-gradient(135deg, #eab0c3, #d88ba0) !important;
    }
    
    /* 进度条 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #f0c8d5, #d4839b) !important;
    }
    .stProgress > div {
        background: #f5e4ea !important;
    }
    
    /* 天气卡片 */
    .weather-card {
        background: linear-gradient(135deg, #f5e0e8, #eccee0);
        border-radius: 18px;
        padding: 16px 20px;
        color: #4a3a40;
        margin-bottom: 16px;
        border: 1px solid rgba(235, 200, 215, 0.3);
        box-shadow: 0 4px 16px rgba(200, 150, 170, 0.06);
    }
    .weather-temp {
        font-size: 2rem;
        font-weight: 300;
        color: #4a3a40;
        font-family: 'Georgia', serif;
    }
    .weather-temp .unit {
        font-size: 1rem;
        font-weight: 300;
        color: #b08a96;
    }
    .weather-desc {
        font-size: 0.9rem;
        color: #6a5a60;
        opacity: 0.85;
        font-weight: 300;
        letter-spacing: 1px;
    }
    .weather-place {
        font-size: 0.8rem;
        color: #b08a96;
        letter-spacing: 2px;
        font-weight: 300;
    }
    
    /* 景点列表 */
    .attraction-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 8px;
        border-radius: 10px;
        border-bottom: 1px solid #f5e8ee;
    }
    .attraction-item:last-child {
        border-bottom: none;
    }
    .attraction-item:hover {
        background: #faf0f4;
    }
    .attraction-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .attraction-name {
        font-weight: 350;
        color: #4a3a40;
        font-size: 0.9rem;
    }
    .attraction-desc {
        font-size: 0.75rem;
        color: #b09aa2;
        margin-left: auto;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    .attraction-link {
        color: #d4839b !important;
        text-decoration: none !important;
        font-size: 0.75rem;
        margin-left: 8px;
        border-bottom: 1px dotted #d4839b;
    }
    .attraction-link:hover {
        color: #b86a82 !important;
    }
    
    /* 行程内容 */
    .itinerary-text {
        font-family: 'Georgia', serif;
        line-height: 1.9;
        color: #3d3d3d;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    .itinerary-text strong {
        color: #c07a90;
        font-weight: 400;
    }
    .itinerary-text hr {
        border: 0;
        border-top: 1px dashed #ecd5dd;
        margin: 16px 0;
    }
    
    /* 交通贴士 */
    .travel-tip {
        background: rgba(250, 240, 245, 0.7);
        border-radius: 14px;
        padding: 14px 18px;
        margin-top: 12px;
        border-left: 3px solid #d4839b;
        font-weight: 300;
        color: #4a3a40;
        letter-spacing: 0.5px;
    }
    .travel-tip strong {
        font-weight: 400;
        color: #c07a90;
    }
    
    /* 侧边栏标题 */
    .sidebar-title {
        text-align: center;
        padding: 8px 0 16px 0;
        font-family: 'Georgia', serif;
    }
    .sidebar-title .icon {
        font-size: 2rem;
        color: #d4839b;
        opacity: 0.6;
    }
    .sidebar-title .text {
        font-size: 1rem;
        font-weight: 300;
        color: #4a3a40;
        letter-spacing: 4px;
        margin-top: 2px;
    }
    
    /* 分割线 */
    .divider-sakura {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #ecd5dd, transparent);
        margin: 16px 0;
    }
    
    /* 响应式 */
    @media (max-width: 768px) {
        .main-title { font-size: 1.6rem; }
        .main .block-container { padding: 1rem 1rem !important; }
        .weather-temp { font-size: 1.6rem; }
        .card { padding: 14px 16px; }
    }
    
    /* 滚动条 */
    ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
    }
    ::-webkit-scrollbar-track {
        background: #f5e4ea;
    }
    ::-webkit-scrollbar-thumb {
        background: #d4839b;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 数据函数 ====================

def get_weather(city):
    client = get_openai_client()
    if not client:
        return {"temp": 22, "condition": "晴", "wind": "微风", "delta": "0°C"}
    try:
        prompt = f"请提供{city}今天的天气情况（温度、天气状况、风力），以JSON格式：{{'temp':数字,'condition':'描述','wind':'描述','delta':'变化如+2°C'}}"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        text = response.choices[0].message.content
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        else:
            json_str = text.strip()
        return json.loads(json_str)
    except:
        return {"temp": 22, "condition": "晴", "wind": "微风", "delta": "0°C"}

def get_attractions(city):
    client = get_openai_client()
    if not client:
        return get_default_attractions(city)
    try:
        prompt = f"""
        为城市 {city} 生成至少5个著名景点，每个景点包含：
        name（名称）, lat（纬度）, lng（经度）, desc（简短描述）, url（官网链接，若不知则空）
        以JSON数组返回，不要其他文字。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        text = response.choices[0].message.content
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        else:
            json_str = text.strip()
        return json.loads(json_str)
    except:
        return get_default_attractions(city)

def get_default_attractions(city):
    defaults = {
        "杭州": [
            {"name": "西湖", "lat": 30.2741, "lng": 120.1551, "desc": "5A景区，杭州标志", "url": "https://www.hzwestlake.com"},
            {"name": "灵隐寺", "lat": 30.2391, "lng": 120.1062, "desc": "千年古刹", "url": "https://www.lingyinsi.org"},
            {"name": "宋城", "lat": 30.1882, "lng": 120.1338, "desc": "宋代文化主题公园", "url": "https://www.songcn.com"},
            {"name": "雷峰塔", "lat": 30.2409, "lng": 120.1575, "desc": "西湖十景", "url": ""},
            {"name": "河坊街", "lat": 30.2519, "lng": 120.1666, "desc": "美食购物", "url": ""},
        ],
        "北京": [
            {"name": "故宫", "lat": 39.9163, "lng": 116.3972, "desc": "明清皇宫", "url": "https://www.dpm.org.cn"},
            {"name": "天安门", "lat": 39.9087, "lng": 116.3975, "desc": "国家象征", "url": ""},
            {"name": "长城", "lat": 40.4319, "lng": 116.5704, "desc": "世界奇迹", "url": "https://www.badalinggreatwall.com"},
            {"name": "颐和园", "lat": 39.9999, "lng": 116.2737, "desc": "皇家园林", "url": ""},
            {"name": "天坛", "lat": 39.8819, "lng": 116.4106, "desc": "祭天场所", "url": ""},
        ],
        "成都": [
            {"name": "宽窄巷子", "lat": 30.6586, "lng": 104.0622, "desc": "历史街区", "url": ""},
            {"name": "锦里", "lat": 30.6438, "lng": 104.0567, "desc": "古街", "url": ""},
            {"name": "青城山", "lat": 30.9000, "lng": 103.5692, "desc": "道教名山", "url": "https://www.qingchengshan.com"},
            {"name": "杜甫草堂", "lat": 30.6609, "lng": 104.0207, "desc": "诗人故居", "url": ""},
            {"name": "大熊猫基地", "lat": 30.7362, "lng": 104.1505, "desc": "国宝熊猫", "url": ""},
        ],
    }
    if city in defaults:
        return defaults[city]
    else:
        return [
            {"name": f"{city}中央公园", "lat": 30.0, "lng": 120.0, "desc": "城市绿肺", "url": ""},
            {"name": f"{city}博物馆", "lat": 30.01, "lng": 120.01, "desc": "了解历史", "url": ""},
            {"name": f"{city}老街", "lat": 29.99, "lng": 119.99, "desc": "特色美食", "url": ""},
        ]

def get_coordinates(city):
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
        "南京": [32.0603, 118.7969],
        "厦门": [24.4798, 118.0894],
        "青岛": [36.0671, 120.3826],
        "大连": [38.9140, 121.6147],
        "昆明": [25.0409, 102.7123],
        "丽江": [26.8721, 100.2330],
        "桂林": [25.2736, 110.2903],
        "张家界": [29.1180, 110.4780],
        "扬州": [32.3942, 119.4129],
        "绍兴": [30.0024, 120.5821],
        "宁波": [29.8683, 121.5430],
    }
    return coords.get(city, [30.2741, 120.1551])

# ==================== 地图渲染（st.map） ====================

def render_map(city_name, attractions, width=400, height=350):
    if not attractions:
        st.info("暂无景点数据")
        return
    df = pd.DataFrame(attractions)
    if 'lng' in df.columns:
        df = df.rename(columns={'lng': 'lon'})
    if 'lat' not in df.columns or 'lon' not in df.columns:
        st.error("景点数据缺少经纬度")
        return
    st.map(df[['lat', 'lon']], zoom=12, use_container_width=True)
    st.caption("景点位置")

# ==================== 行程生成 ====================

def generate_itinerary(destination, days, budget, interests, travel_style, accommodation):
    client = get_openai_client()
    if not client:
        return generate_simple_itinerary(destination, days, budget, interests, travel_style, accommodation)
    try:
        interests_str = ", ".join(interests)
        prompt = f"""
        为以下旅行需求生成详细{days}天行程，必须包含每天的详细交通指引：
        目的地：{destination}
        天数：{days}
        预算：{budget}
        兴趣：{interests_str}
        风格：{travel_style}
        住宿：{accommodation}
        交通要求：每段标注具体公交线路（如27路）、地铁线、上下车站点、方向、站数、时间、票价。
        格式示例：公交27路（开往植物园）| 断桥站→茅家埠站 | 4站 | 约10分钟 | 2元
        请用中文数字标记天数，表述优雅简洁。
        按天输出，Markdown格式。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是资深旅行规划师，精通公共交通。表述优雅简洁。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=3000,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"生成失败：{e}")
        return generate_simple_itinerary(destination, days, budget, interests, travel_style, accommodation)

def generate_simple_itinerary(destination, days, budget, interests, travel_style, accommodation):
    itin = f"**{destination} {days}日{travel_style}之旅** (预算：{budget})\n\n"
    for i in range(1, days+1):
        itin += f"**第{i}日**\n"
        itin += "上午：搭乘公交或地铁前往景点（具体线路请查询当地交通应用）\n"
        itin += "下午：漫步周边街区，感受当地生活气息\n"
        itin += "傍晚：寻觅特色美食\n\n"
    itin += "交通贴士：建议下载当地公交应用，使用地图应用实时查询。"
    return itin

# ==================== 初始化 ====================

if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_itinerary' not in st.session_state:
    st.session_state.current_itinerary = ""
if 'attractions' not in st.session_state:
    st.session_state.attractions = []
if 'city_coords' not in st.session_state:
    st.session_state.city_coords = [30.2741, 120.1551]

# ==================== 侧边栏 ====================

with st.sidebar:
    st.markdown("""
    <div class="sidebar-title">
        <div class="icon">🌸</div>
        <div class="text">旅行设置</div>
    </div>
    """, unsafe_allow_html=True)
    
    destination = st.text_input("目的地", placeholder="如：杭州、京都...", value="杭州")
    days = st.slider("旅行天数", 1, 10, 3)
    budget = st.selectbox("预算", ["经济型 (200-500元/天)", "舒适型 (500-1000元/天)", "豪华型 (1000元以上/天)"])
    interests = st.multiselect("兴趣偏好", ["自然风光", "历史文化", "美食探店", "购物", "主题乐园", "休闲度假"], default=["自然风光", "美食探店"])
    with st.expander("更多选项"):
        travel_style = st.selectbox("旅行风格", ["悠闲放松", "深度探索", "网红打卡", "亲子游"])
        accommodation = st.selectbox("住宿偏好", ["特色民宿", "经济酒店", "星级酒店"])
    with st.expander("API 设置"):
        api_key_input = st.text_input("DeepSeek API Key", type="password", placeholder="留空使用示例数据")
        if api_key_input:
            os.environ["DEEPSEEK_API_KEY"] = api_key_input
            st.success("已设置")
        else:
            st.caption("不设置可使用示例数据")
    
    generate_btn = st.button("生成行程", type="primary", use_container_width=True)
    
    st.markdown('<hr class="divider-sakura">', unsafe_allow_html=True)
    st.markdown("**旅行记录**")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history[-5:]):
            if st.button(f"{item['destination']} ({item['date']})", key=f"hist_{i}"):
                st.session_state.current_itinerary = item['itinerary']
                st.rerun()
    else:
        st.caption("暂无记录")

# ==================== 主界面 ====================

st.markdown("""
<div class="main-title">
    旅行手帐
    <span>· 智慧旅游助手</span>
    <span class="sub">— 为你定制专属旅程 —</span>
</div>
<div class="sub-title">输入你的旅行偏好，生成定制行程与交通指引</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1], gap="medium")

# ----- 左栏 -----
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">行程规划</div>', unsafe_allow_html=True)
    
    if generate_btn and destination:
        with st.status("正在规划行程...", expanded=True) as status:
            status.update(label="获取景点信息", state="running")
            try:
                attrs = get_attractions(destination)
                st.session_state.attractions = attrs
                status.update(label=f"已获取 {len(attrs)} 个景点", state="complete")
            except:
                attrs = []
                st.session_state.attractions = []
                status.update(label="景点获取失败，使用默认数据", state="error")
            
            status.update(label="获取地理坐标", state="running")
            try:
                coords = get_coordinates(destination)
                st.session_state.city_coords = coords
                status.update(label="坐标获取完成", state="complete")
            except:
                status.update(label="坐标使用默认值", state="error")
            
            status.update(label="生成行程与交通方案", state="running")
            try:
                itin = generate_itinerary(destination, days, budget, interests, travel_style, accommodation)
                st.session_state.current_itinerary = itin
                status.update(label="行程生成完成", state="complete")
            except:
                itin = "生成失败，请重试。"
                st.session_state.current_itinerary = itin
                status.update(label="生成失败", state="error")
            
            if itin and "失败" not in itin:
                st.session_state.history.append({'destination': destination, 'date': datetime.now().strftime("%Y-%m-%d %H:%M"), 'itinerary': itin})
            status.update(label="规划完成", state="complete")
        
        if st.session_state.current_itinerary:
            st.markdown('<div class="itinerary-text">', unsafe_allow_html=True)
            st.markdown(st.session_state.current_itinerary)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.download_button("导出文本", data=st.session_state.current_itinerary, file_name=f"{destination}_行程.txt", mime="text/plain")
            with col_exp2:
                html_content = f"<html><body><pre>{st.session_state.current_itinerary}</pre></body></html>"
                st.download_button("导出HTML", data=html_content, file_name=f"{destination}_行程.html", mime="text/html")
            
            st.markdown("""
            <div class="travel-tip">
                <strong>出行贴士</strong><br>
                建议下载当地公交应用，使用地图应用实时查询公交到站信息。<br>
                共享单车与打车应用也可作为补充选择。
            </div>
            """, unsafe_allow_html=True)
    elif st.session_state.current_itinerary:
        st.markdown('<div class="itinerary-text">', unsafe_allow_html=True)
        st.markdown(st.session_state.current_itinerary)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("在左侧设置旅行偏好，然后点击「生成行程」")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ----- 右栏 -----
with col2:
    # 天气
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="weather-place">{destination}</div>', unsafe_allow_html=True)
    weather = get_weather(destination)
    if weather:
        col_temp, col_cond = st.columns([1, 1])
        with col_temp:
            st.markdown(f'<div class="weather-temp">{weather.get("temp", "22")}<span class="unit">°C</span></div>', unsafe_allow_html=True)
        with col_cond:
            st.markdown(f'<div class="weather-desc">{weather.get("condition", "晴")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="weather-desc" style="font-size:0.8rem;">{weather.get("wind", "微风")}</div>', unsafe_allow_html=True)
        st.caption(f"变化：{weather.get('delta', '0°C')}")
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
    attrs = st.session_state.attractions if st.session_state.attractions else get_attractions(destination)
    if attrs:
        colors = ['#d4839b','#e8a0b5','#c07a90','#dbb0c0','#e8b8c8','#d0a0b0','#c890a0','#e0b0c0']
        for i, attr in enumerate(attrs):
            color = colors[i % len(colors)]
            url = attr.get('url', '')
            if url:
                st.markdown(f"""
                <div class="attraction-item">
                    <span class="attraction-dot" style="background:{color};"></span>
                    <span class="attraction-name">{attr['name']}</span>
                    <a href="{url}" target="_blank" class="attraction-link">官网</a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="attraction-item">
                    <span class="attraction-dot" style="background:{color};"></span>
                    <span class="attraction-name">{attr['name']}</span>
                    <span class="attraction-desc">{attr.get('desc', '')}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("暂无景点数据")
    st.markdown('</div>', unsafe_allow_html=True)

# ----- 底部 -----
st.markdown('<hr class="divider-sakura">', unsafe_allow_html=True)
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption("数据由 DeepSeek AI 生成")
with col_f2:
    if st.button("重置"):
        st.session_state.clear()
        st.rerun()
with col_f3:
    st.caption(datetime.now().strftime("%Y年%m月%d日"))
