import pydeck as pdk

def render_map(city_name, attractions, width=400, height=350):
    """使用 pydeck 渲染地图（更稳定，避免 DOM 错误）"""
    if not attractions:
        st.info("暂无景点数据")
        return
    
    # 创建 DataFrame，将 lng 列重命名为 lon
    df = pd.DataFrame(attractions)
    if 'lng' in df.columns:
        df = df.rename(columns={'lng': 'lon'})
    
    # 确保有 lat 和 lon
    if 'lat' not in df.columns or 'lon' not in df.columns:
        st.error("景点数据缺少经纬度")
        return
    
    # 计算中心点
    center_lat = df['lat'].mean()
    center_lon = df['lon'].mean()
    
    # 创建散点图层
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position='[lon, lat]',
        get_radius=200,
        get_fill_color='[26, 109, 255, 180]',  # 高德蓝
        pickable=True,
        auto_highlight=True,
        radius_min_pixels=10,
        radius_max_pixels=30,
    )
    
    # 添加文本标签（景点名称）
    text_layer = pdk.Layer(
        'TextLayer',
        data=df,
        get_position='[lon, lat]',
        get_text='name',
        get_size=12,
        get_color='[0, 0, 0, 200]',
        get_alignment_baseline='"bottom"',
        get_pixel_offset=[0, -20],
    )
    
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=12,
        pitch=0,
    )
    
    deck = pdk.Deck(
        layers=[layer, text_layer],
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/light-v10',
        tooltip={"html": "<b>{name}</b><br/>{desc}", "style": {"backgroundColor": "white", "color": "black"}}
    )
    
    st.pydeck_chart(deck)
    st.caption("📍 蓝色标记为景点，悬停显示名称")
