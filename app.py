"""
智慧旅游助手 - 完整单文件版
支持手机访问，含地图、交通指引、DeepSeek AI
部署到 Streamlit Cloud 时只需此文件 + requirements.txt
"""

import streamlit as st
from datetime import datetime
import os
import time
import json
import requests
import pandas as pd
import folium
from streamlit.components.v1 import html
from openai import OpenAI
import base64

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="🌍 智慧旅游助手",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== API Key 读取 ====================
def get_api_key():
    """优先从 Streamlit Secrets 读取，其次从环境变量"""
    try:
        return st.secrets["DEEPSEEK_API_KEY"]
    except:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("DEEPSEEK_API_KEY")

# ==================== 高德风格CSS ====================
st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.2rem; }
    .main-title span { color: #1a6dff; }
    .sub-title { color: #666; font-size: 1rem; margin-bottom: 1.5rem; }
    .card {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin-bottom: 16px;
        border: 1px solid #f0f0f0;
    }
    .card-title { font-size: 1.1rem; font-weight: 600; color: #1a1a2e; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .weather-card {
        background: linear-gradient(135deg, #1a6dff, #4a9eff);
        border-radius: 16px;
        padding: 16px 20px;
        color: white;
        margin-bottom: 16px;
    }
    .weather-temp { font-size: 2.2rem; font-weight: 700; }
    .weather-desc { font-size: 0.95rem; opacity: 0.9; }
    .attraction-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 12px;
        border-radius: 10px;
        transition: background 0.2s;
    }
    .attraction-item:hover { background: #f5f7fa; }
    .attraction-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .stButton > button {
        background: #1a6dff !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(26, 109, 255, 0.3) !important;
    }
    .stButton > button:hover {
        background: #1558d4 !important;
        box-shadow: 0 4px 16px rgba(26, 109, 255, 0.4) !important;
        transform: translateY(-1px);
    }
    .stProgress > div > div { background: linear-gradient(90deg, #1a6dff, #4a9eff) !important; }
    /* 移动端优化 */
    @media (max-width: 768px) {
        .main-title { font-size: 1.8rem; }
        .weather-temp { font-size: 1.6rem; }
        .card { padding: 16px; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== 数据函数 ====================

def get_weather(city):
    """获取天气（优先DeepSeek，失败返回默认）"""
    api_key = get_api_key()
    if not api_key:
        return {"temp": 22, "condition": "晴", "wind": "微风", "delta": "0°C"}
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        prompt = f"请提供{city}今天的天气情况（温度、天气状况、风力），以JSON格式：{{'temp':数字,'condition':'描述','wind':'描述','delta':'变化如+2°C'}}"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        text = response.choices[0].message.content
        # 提取JSON
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
    """获取景点列表（优先DeepSeek，失败返回默认）"""
    api_key = get_api_key()
    if not api_key:
        return get_default_attractions(city)
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
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
    """默认景点数据（内置常见城市）"""
    defaults = {
        "杭州": [
            {"name": "西湖", "lat": 30.2741, "lng": 120.1551, "desc": "5A景区，杭州标志", "url": "https://www.hzwestlake.com"},
            {"name": "灵隐寺", "lat": 30.2391, "lng": 120.1062, "desc": "千年古刹", "url": "https://www.lingyinsi.org"},
            {"name": "宋城", "lat": 30.1882, "lng": 120.1338, "desc": "宋代文化主题公园", "url": "https://www.songcn.com"},
        ],
        "北京": [
            {"name": "故宫", "lat": 39.9163, "lng": 116.3972, "desc": "明清皇宫", "url": "https://www.dpm.org.cn"},
            {"name": "天安门", "lat": 39.9087, "lng": 116.3975, "desc": "国家象征", "url": ""},
            {"name": "长城", "lat": 40.4319, "lng": 116.5704, "desc": "世界奇迹", "url": "https://www.badalinggreatwall.com"},
        ],
        "成都": [
            {"name": "宽窄巷子", "lat": 30.6586, "lng": 104.0622, "desc": "历史街区", "url": ""},
            {"name": "锦里", "lat": 30.6438, "lng": 104.0567, "desc": "古街", "url": ""},
            {"name": "青城山", "lat": 30.9000, "lng": 103.5692, "desc": "道教名山", "url": "https://www.qingchengshan.com"},
        ],
    }
    if city in defaults:
        return defaults[city]
    else:
        return [
            {"name": f"{city}中央公园", "lat": 30.0, "lng": 120.0, "desc": "城市绿肺", "url": ""},
            {"name": f"{city}博物馆", "lat": 30.01, "lng": 120.01, "desc": "了解历史", "url": ""},
        ]

def get_coordinates(city):
    """获取城市中心坐标"""
    # 内置常见城市坐标
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

# ==================== 地图渲染 ====================

def render_map(city_name, attractions, width=400, height=350):
    """使用 Folium + 高德底图渲染地图"""
    if not attractions:
        st.info("暂无景点数据")
        return
    # 计算中心
    lats = [a['lat'] for a in attractions]
    lngs = [a['lng'] for a in attractions]
    center = [sum(lats)/len(lats), sum(lngs)/len(lngs)]
    
    # 高德瓦片（街道图）
    tile_url = 'https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}'
    m = folium.Map(location=center, zoom_start=13, tiles=tile_url, attr='© 高德地图', control_scale=True, width='100%', height='100%')
    
    # 城市中心标记
    folium.Marker(location=center, popup=f"<b>📍 {city_name}</b><br>城市中心", icon=folium.Icon(color='blue', icon='home', prefix='fa'), tooltip=f"{city_name}市中心").add_to(m)
    
    # 景点标记
    colors = ['#1a6dff', '#ff6b35', '#00c853', '#ffab00', '#e040fb', '#00bcd4', '#ff5252', '#7c4dff']
    for idx, attr in enumerate(attractions):
        color = colors[idx % len(colors)]
        url = attr.get('url', '')
        url_html = f'<br><a href="{url}" target="_blank" style="color:#1a6dff;">🔗 官网</a>' if url else ''
        popup_html = f"""
        <div style="font-family:sans-serif;min-width:160px;padding:8px;">
            <b style="font-size:16px;">🏛️ {attr['name']}</b><br>
            <span style="color:#666;font-size:13px;">{attr.get('desc', '')}</span>
            {url_html}
        </div>
        """
        folium.Marker(location=[attr['lat'], attr['lng']], popup=folium.Popup(popup_html, max_width=300), icon=folium.Icon(color='red', icon='star', prefix='fa'), tooltip=attr['name']).add_to(m)
    
    # 城市范围圈
    folium.Circle(location=center, radius=3000, color='#1a6dff', fill=True, fillColor='#1a6dff', fillOpacity=0.06, weight=2, opacity=0.3).add_to(m)
    
    try:
        map_html = m._repr_html_()
        html(f"""
        <div style="width:{width}px; height:{height}px; border-radius:12px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.08); border:1px solid #eaeaea;">
            {map_html}
        </div>
        """, height=height+10, width=width)
        st.caption("🔵 蓝色：城市中心  |  🔴 景点  |  👆 点击查看详情")
    except Exception as e:
        st.error(f"地图渲染失败：{e}")

# ==================== 行程生成（含交通指引） ====================

def generate_itinerary(destination, days, budget, interests, travel_style, accommodation):
    """调用 DeepSeek 生成详细行程（含交通指引）"""
    api_key = get_api_key()
    if not api_key:
        return generate_simple_itinerary(destination, days, budget, interests, travel_style, accommodation)
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        interests_str = ", ".join([i.replace("🏔️ ", "").replace("🏛️ ", "").replace("🍜 ", "")
                                  .replace("🛍️ ", "").replace("🎢 ", "").replace("🏖️ ", "") for i in interests])
        prompt = f"""
        为以下旅行需求生成详细{days}天行程，必须包含每天的详细交通指引：
        目的地：{destination}
        天数：{days}
        预算：{budget}
        兴趣：{interests_str}
        风格：{travel_style}
        住宿：{accommodation}

        交通要求：
        - 每段行程标注具体公交线路（如27路）、地铁线（如1号线）、上下车站点、方向、站数、时间、票价
        - 步行/骑行标注时间距离
        - 打车标注费用时间
        格式示例：
        🚌 公交27路（开往植物园）| 断桥站→茅家埠站 | 4站 | 约10分钟 | ¥2
        🚇 地铁1号线（开往湘湖）| 龙翔桥站→定安路站 | 2站 | 约6分钟 | ¥3
        🚶 步行：沿南山路步行约8分钟 | 600米

        按天输出，Markdown格式。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是资深旅行规划师，精通各城市公共交通，必须提供具体线路和站点。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=3000,
            timeout=50
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"DeepSeek 生成失败：{e}")
        return generate_simple_itinerary(destination, days, budget, interests, travel_style, accommodation)

def generate_simple_itinerary(destination, days, budget, interests, travel_style, accommodation):
    """备用简单行程（含交通示例）"""
    days_emoji = ["🎯", "🌟", "✨", "🎪", "🏰", "🌅", "🌄", "🎆", "🏮", "🎉"]
    itin = f"📍 **{destination} {days}天{travel_style}之旅** (预算：{budget})\n\n"
    for i in range(1, days+1):
        itin += f"**{days_emoji[i-1]} Day {i}**\n"
        itin += "上午：🚌 公交/地铁前往景点（具体线路请查询当地交通APP）\n"
        itin += "下午：🚶 步行游览周边\n"
        itin += "晚上：🍜 美食探索\n\n"
    itin += "📌 **交通贴士**：建议下载当地公交APP，使用高德/百度地图实时查询。\n"
    return itin

# ==================== 初始化 Session State ====================

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
    <div style="text-align:center;padding:12px 0 20px 0;">
        <div style="font-size:2.4rem;">🗺️</div>
        <div style="font-size:1.1rem;font-weight:600;color:#1a1a2e;">旅行设置</div>
    </div>
    """, unsafe_allow_html=True)
    
    destination = st.text_input("📍 目的地", placeholder="如：杭州、成都...", value="杭州")
    days = st.slider("📅 天数", 1, 10, 3)
    budget = st.selectbox("💰 预算", ["经济型 (¥200-500/天)", "舒适型 (¥500-1000/天)", "豪华型 (¥1000+/天)"])
    interests = st.multiselect("🎯 兴趣", ["🏔️ 自然风光", "🏛️ 历史文化", "🍜 美食探店", "🛍️ 购物", "🎢 主题乐园", "🏖️ 休闲度假"], default=["🏔️ 自然风光", "🍜 美食探店"])
    with st.expander("⚙️ 更多选项"):
        travel_style = st.selectbox("风格", ["悠闲放松", "深度探索", "网红打卡", "亲子游"])
        accommodation = st.selectbox("住宿", ["特色民宿", "经济酒店", "星级酒店"])
    with st.expander("🔑 API 设置"):
        api_key_input = st.text_input("DeepSeek API Key", type="password", placeholder="留空使用示例数据")
        if api_key_input:
            # 在本地测试时，设置环境变量
            os.environ["DEEPSEEK_API_KEY"] = api_key_input
            st.success("✅ 已设置（当前会话有效）")
        else:
            st.info("💡 不设置可使用示例数据")
    
    generate_btn = st.button("🚀 生成行程计划", type="primary", use_container_width=True)
    
    st.divider()
    st.subheader("📜 历史")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history[-5:]):
            if st.button(f"📌 {item['destination']} ({item['date']})", key=f"hist_{i}"):
                st.session_state.current_itinerary = item['itinerary']
                st.rerun()
    else:
        st.caption("暂无")

# ==================== 主界面 ====================

st.markdown("""
<div class="main-title">🌍 智慧旅游<span>助手</span></div>
<div class="sub-title">✨ AI 定制行程 + 详细交通指引，手机电脑都能用</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1], gap="medium")

# ----- 左栏 -----
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗺️ 推荐行程</div>', unsafe_allow_html=True)
    
    if generate_btn and destination:
        with st.status("🚀 开始规划...", expanded=True) as status:
            status.update(label="🌍 获取景点", state="running")
            try:
                attrs = get_attractions(destination)
                st.session_state.attractions = attrs
                status.update(label=f"✅ 获取 {len(attrs)} 个景点", state="complete")
            except Exception as e:
                status.update(label=f"❌ 景点获取失败", state="error")
                attrs = []
                st.session_state.attractions = []
            
            status.update(label="📍 获取坐标", state="running")
            try:
                coords = get_coordinates(destination)
                st.session_state.city_coords = coords
                status.update(label="✅ 坐标完成", state="complete")
            except:
                status.update(label="⚠️ 坐标使用默认", state="error")
            
            status.update(label="📝 生成行程+交通 (DeepSeek)", state="running")
            try:
                itin = generate_itinerary(destination, days, budget, interests, travel_style, accommodation)
                st.session_state.current_itinerary = itin
                status.update(label="✅ 行程生成", state="complete")
            except Exception as e:
                status.update(label=f"❌ 生成失败", state="error")
                itin = "⚠️ 生成失败，请重试或检查API。"
                st.session_state.current_itinerary = itin
            
            if itin and "失败" not in itin:
                st.session_state.history.append({'destination': destination, 'date': datetime.now().strftime("%Y-%m-%d %H:%M"), 'itinerary': itin})
            status.update(label="🎉 完成！", state="complete")
        
        # 显示结果
        if st.session_state.current_itinerary:
            st.markdown(st.session_state.current_itinerary)
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.download_button("📥 导出文本", data=st.session_state.current_itinerary, file_name=f"{destination}_行程.txt", mime="text/plain")
            with col_exp2:
                html_content = f"<html><body><pre>{st.session_state.current_itinerary}</pre></body></html>"
                st.download_button("📄 导出HTML", data=html_content, file_name=f"{destination}_行程.html", mime="text/html")
            # 交通贴士
            st.markdown("""
            <div style="background:#f0f7ff;border-radius:12px;padding:16px;margin-top:12px;border-left:4px solid #1a6dff;">
                <b>🚌 出行贴士</b><br>
                • 下载当地公交/地铁APP（如：杭州通、亿通行）<br>
                • 高德/百度地图实时查公交到站<br>
                • 共享单车：哈啰/美团<br>
                • 打车：滴滴出行
            </div>
            """, unsafe_allow_html=True)
    elif st.session_state.current_itinerary:
        st.markdown(st.session_state.current_itinerary)
    else:
        st.info("👈 左侧设置偏好，点击生成")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ----- 右栏 -----
with col2:
    # 天气
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="display:flex;justify-content:space-between;"><span style="font-weight:500;">{destination}</span></div>', unsafe_allow_html=True)
    weather = get_weather(destination)
    if weather:
        col_temp, col_cond = st.columns([1,1])
        with col_temp:
            st.markdown(f'<div class="weather-temp">{weather.get("temp","22")}°C</div>', unsafe_allow_html=True)
        with col_cond:
            st.markdown(f'<div class="weather-desc">☀️ {weather.get("condition","晴")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="weather-desc" style="font-size:0.8rem;">💨 {weather.get("wind","微风")}</div>', unsafe_allow_html=True)
        st.caption(f"变化：{weather.get('delta','0°C')}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 地图
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗺️ 景点地图</div>', unsafe_allow_html=True)
    attrs = st.session_state.attractions if st.session_state.attractions else get_attractions(destination)
    if attrs:
        render_map(destination, attrs, width=400, height=320)
    else:
        st.info("暂无景点")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 景点列表
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📍 推荐景点</div>', unsafe_allow_html=True)
    attrs = st.session_state.attractions if st.session_state.attractions else get_attractions(destination)
    if attrs:
        colors = ['#1a6dff','#ff6b35','#00c853','#ffab00','#e040fb','#00bcd4','#ff5252','#7c4dff']
        for i, attr in enumerate(attrs):
            color = colors[i % len(colors)]
            url = attr.get('url', '')
            if url:
                st.markdown(f"""
                <div class="attraction-item">
                    <span class="attraction-dot" style="background:{color};"></span>
                    <span><strong>{attr['name']}</strong></span>
                    <span style="margin-left:auto;font-size:0.8rem;">
                        <a href="{url}" target="_blank" style="color:#1a6dff;text-decoration:none;">🔗 官网</a>
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="attraction-item">
                    <span class="attraction-dot" style="background:{color};"></span>
                    <span><strong>{attr['name']}</strong></span>
                    <span style="margin-left:auto;font-size:0.75rem;color:#999;">{attr.get('desc','')}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("暂无")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 底部 ====================
st.divider()
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption("💡 数据由 DeepSeek AI 实时生成")
with col_f2:
    if st.button("🔄 重置"):
        st.session_state.clear()
        st.rerun()
with col_f3:
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
