"""
地图模块 - 高德地图风格
使用高德瓦片 + 彩色景点标记
"""

import streamlit as st
import folium
from streamlit.components.v1 import html


def render_map(city_name, attractions, width=400, height=350):
    """渲染高德风格地图"""
    if not attractions:
        st.info("暂无景点数据")
        return

    # 计算中心
    lats = [a['lat'] for a in attractions]
    lngs = [a['lng'] for a in attractions]
    center = [sum(lats)/len(lats), sum(lngs)/len(lngs)]

    # 高德地图瓦片（街道图）
    tile_url = 'https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}'
    
    m = folium.Map(
        location=center,
        zoom_start=13,
        tiles=tile_url,
        attr='© 高德地图',
        control_scale=True,
        width='100%',
        height='100%'
    )

    # 城市中心标记（高德蓝）
    folium.Marker(
        location=center,
        popup=f"<b>📍 {city_name}</b><br>城市中心",
        icon=folium.Icon(color='blue', icon='home', prefix='fa'),
        tooltip=f"{city_name}市中心"
    ).add_to(m)

    # 景点标记 - 高德配色
    amap_colors = ['#1a6dff', '#ff6b35', '#00c853', '#ffab00', '#e040fb', '#00bcd4', '#ff5252', '#7c4dff']
    
    for idx, attr in enumerate(attractions):
        color = amap_colors[idx % len(amap_colors)]
        url = attr.get('url', '')
        url_html = f'<br><a href="{url}" target="_blank" style="color:#1a6dff;text-decoration:none;font-weight:500;">🔗 访问官网</a>' if url else ''
        
        popup_html = f"""
        <div style="font-family:'PingFang SC','Microsoft YaHei',sans-serif;min-width:180px;padding:10px 12px;">
            <div style="font-size:17px;font-weight:600;color:#1a1a2e;margin-bottom:4px;">🏛️ {attr['name']}</div>
            <div style="font-size:13px;color:#666;margin-bottom:6px;">{attr.get('desc', '')}</div>
            {url_html}
        </div>
        """
        
        folium.Marker(
            location=[attr['lat'], attr['lng']],
            popup=folium.Popup(popup_html, max_width=320),
            icon=folium.Icon(color='red' if idx % 2 == 0 else 'blue', icon='star', prefix='fa'),
            tooltip=attr['name']
        ).add_to(m)

    # 城市范围圈
    folium.Circle(
        location=center,
        radius=3000,
        color='#1a6dff',
        fill=True,
        fillColor='#1a6dff',
        fillOpacity=0.06,
        weight=2,
        opacity=0.3
    ).add_to(m)

    # 渲染
    try:
        map_html = m._repr_html_()
        html(
            f"""
            <div style="width:{width}px; height:{height}px; border-radius:12px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.08); border:1px solid #eaeaea;">
                {map_html}
            </div>
            """,
            height=height + 10,
            width=width
        )
        st.caption("🔵 蓝色：城市中心  |  🔴 彩色：景点  |  👆 点击查看详情")
    except Exception as e:
        st.error(f"地图渲染失败：{e}")
        show_attractions_list(attractions)


def show_attractions_list(attractions):
    """备用列表"""
    st.write("📋 景点列表：")
    for attr in attractions:
        url = attr.get('url', '')
        if url:
            st.markdown(f"• 🏛️ **{attr['name']}** [🔗 官网]({url})")
        else:
            st.write(f"• 🏛️ **{attr['name']}**")
        st.caption(f"  {attr.get('desc', '')}")