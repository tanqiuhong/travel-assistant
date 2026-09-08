"""
数据模块 - 所有数据通过 DeepSeek API 实时获取
支持任意城市，无需本地预置数据
"""

import json
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_weather(city):
    """
    调用 DeepSeek 获取天气信息（模拟或真实）
    也可以使用免费天气 API，这里为了统一使用 DeepSeek
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        # 如果没有 API Key，返回默认天气
        return {"temp": 22, "condition": "晴", "wind": "微风", "delta": "0°C"}
    
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        prompt = f"请提供{city}今天的天气情况，包括温度、天气状况、风力。以JSON格式返回：{{'temp': 数字, 'condition': '描述', 'wind': '风力描述', 'delta': '温度变化如+2°C'}}"
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个天气助手，返回准确天气信息。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        result_text = response.choices[0].message.content
        # 解析JSON
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = result_text.strip()
        weather = json.loads(json_str)
        return weather
    except Exception as e:
        # 出错时返回默认
        return {"temp": 22, "condition": "晴", "wind": "微风", "delta": "0°C"}


def get_attractions(city):
    """
    调用 DeepSeek 获取城市景点列表（含名称、坐标、描述、官网链接）
    如果API失败，返回默认的示例景点（仅用于演示）
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        # 无API Key时返回默认示例数据
        return get_default_attractions(city)
    
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        prompt = f"""
        请为城市 {city} 生成一份景点列表，包含至少5个著名景点。
        每个景点需要提供：
        - name: 景点名称
        - lat: 纬度（浮点数）
        - lng: 经度（浮点数）
        - desc: 简短描述（20字以内）
        - url: 官方网站链接（如果知道，否则空字符串）

        请以JSON数组格式返回，不要有其他文字。
        示例格式：
        [
            {{"name": "西湖", "lat": 30.2741, "lng": 120.1551, "desc": "杭州标志性景点", "url": "https://www.westlake.com"}},
            ...
        ]
        确保经纬度准确，如果不确定，可以估算。
        """
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个旅游地理专家，擅长提供准确的景点地理信息。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        result_text = response.choices[0].message.content
        
        # 提取JSON
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = result_text.strip()
        
        attractions = json.loads(json_str)
        return attractions
    except Exception as e:
        # 出错时返回默认示例
        return get_default_attractions(city)


def get_default_attractions(city):
    """
    默认景点数据（当API不可用时使用）
    仅作为演示，包含一些中国主要城市
    """
    default_data = {
        "杭州": [
            {"name": "西湖", "lat": 30.2741, "lng": 120.1551, "desc": "杭州标志，5A景区", "url": ""},
            {"name": "灵隐寺", "lat": 30.2391, "lng": 120.1062, "desc": "千年古刹", "url": ""},
            {"name": "宋城", "lat": 30.1882, "lng": 120.1338, "desc": "宋代文化主题公园", "url": ""},
            {"name": "雷峰塔", "lat": 30.2409, "lng": 120.1575, "desc": "西湖十景", "url": ""},
        ],
        "成都": [
            {"name": "宽窄巷子", "lat": 30.6586, "lng": 104.0622, "desc": "历史街区", "url": ""},
            {"name": "锦里", "lat": 30.6438, "lng": 104.0567, "desc": "古街", "url": ""},
            {"name": "青城山", "lat": 30.9000, "lng": 103.5692, "desc": "道教名山", "url": ""},
        ],
        "北京": [
            {"name": "故宫", "lat": 39.9163, "lng": 116.3972, "desc": "明清皇宫", "url": ""},
            {"name": "天安门", "lat": 39.9087, "lng": 116.3975, "desc": "国家象征", "url": ""},
            {"name": "长城", "lat": 40.4319, "lng": 116.5704, "desc": "世界奇迹", "url": ""},
        ],
    }
    # 如果城市在默认数据中，返回对应数据，否则返回通用示例
    if city in default_data:
        return default_data[city]
    else:
        # 生成通用示例（以城市名命名）
        return [
            {"name": f"{city}中央公园", "lat": 30.0, "lng": 120.0, "desc": "城市绿肺", "url": ""},
            {"name": f"{city}博物馆", "lat": 30.01, "lng": 120.01, "desc": "了解城市历史", "url": ""},
            {"name": f"{city}老街", "lat": 29.99, "lng": 119.99, "desc": "特色美食", "url": ""},
        ]


def get_coordinates(city):
    """
    获取城市中心坐标（用于地图初始视图）
    优先使用DeepSeek，失败时返回默认坐标
    """
    # 先尝试从景点数据中获取中心（平均）
    attractions = get_attractions(city)
    if attractions and len(attractions) > 0:
        lats = [a['lat'] for a in attractions]
        lngs = [a['lng'] for a in attractions]
        return [sum(lats)/len(lats), sum(lngs)/len(lngs)]
    else:
        # 默认杭州坐标
        return [30.2741, 120.1551]