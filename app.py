import streamlit as st
import pandas as pd
import os
from openai import OpenAI

st.set_page_config(page_title="旅行手帐", page_icon="🌸", layout="wide")

# 樱色主题 - 极简CSS，只改颜色
st.markdown("""
<style>
    .stApp {
        background-color: #fdf0f4;
    }
    .stButton > button {
        background-color: #d4839b !important;
        color: white !important;
        border-radius: 30px !important;
    }
    .stButton > button:hover {
        background-color: #c07a90 !important;
    }
    .css-1d391kg, .css-1aumxhk {
        background-color: #fff5f8 !important;
    }
    h1, h2, h3 {
        color: #4a3a40 !important;
        font-family: 'Georgia', serif !important;
        font-weight: 300 !important;
    }
    .stTextInput > label {
        color: #6a5a60 !important;
    }
</style>
""", unsafe_allow_html=True)

def get_api_key():
    try:
        return st.secrets["DEEPSEEK_API_KEY"]
    except:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("DEEPSEEK_API_KEY")

def get_weather(city):
    key = get_api_key()
    if not key:
        return {"temp": "22", "condition": "晴", "wind": "微风"}
    try:
        client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"{city}天气，JSON格式：{{'temp':数字,'condition':'描述','wind':'描述'}}"}],
            temperature=0.3,
            max_tokens=100
        )
        import json
        return json.loads(response.choices[0].message.content)
    except:
        return {"temp": "22", "condition": "晴", "wind": "微风"}

st.title("🌸 旅行手帐")
st.caption("智慧旅游助手 · 樱色主题")
destination = st.text_input("目的地", value="杭州")
if st.button("查询天气"):
    w = get_weather(destination)
    st.write(f"天气：{w['condition']}，温度：{w['temp']}°C，{w['wind']}")
