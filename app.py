import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

# 보안 스타일
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# 2. 전국 시군 좌표 사전 (더 촘촘하게 보강)
location_map = {
    # 기존 지역
    "연천": [38.0964, 127.0754], "파주": [37.7600, 126.7798], "철원": [38.1463, 127.3132],
    "화천": [38.1061, 127.7081], "양구": [38.1051, 127.9897], "인제": [38.0696, 128.1703],
    "고성": [38.3805, 128.4687], "포천": [37.8949, 127.2003], "양양": [38.0754, 128.6189],
    "홍천": [37.6970, 127.8887], "춘천": [37.8813, 127.7298], "강릉": [37.7518, 128.8761],
    "횡성": [37.4912, 127.9853], "평창": [37.3705, 128.3902], "영월": [37.1837, 128.4619],
    "원주": [37.3422, 127.9202], "보은": [36.4894, 127.7345], "충주": [36.9910, 127.9259],
    "제천": [37.1326, 128.2141], "괴산": [36.8115, 127.7946], "단양": [36.9845, 128.3653],
    "안동": [36.5684, 128.7296], "영덕": [36.4150, 129.3653], "영천": [35.9732, 128.9385],
    "경주": [35.8562, 129.2247], "상주": [36.4109, 128.1591], "문경": [36.5861, 128.1868],
    "의성": [36.3522, 128.6970], "청송": [36.4362, 129.0573], "영양": [36.6666, 129.1120],
    "봉화": [36.8931, 128.7325], "울진": [36.9931, 129.4005], "김포": [37.6151, 126.7154],
    "강화": [37.7461, 126.4842], "인천": [37.4562, 126.7052], "부산": [35.1798, 129.0750],
    "보령": [36.3333, 126.6122], "영광": [35.2742, 126.5122],
    # 누락 의심 지역 추가
    "예산": [36.6925, 126.8456], "태안": [36.7456, 126.2978], "서산": [36.7845, 126.4503],
    "진천": [36.8553, 127.4356], "음성": [36.9397, 127.6906], "봉화": [36.8931, 128.7325],
    "담양": [35.3211, 126.9881], "함평": [35.0661, 126.5168], "진도": [34.4868, 126.2634]
}

@st.cache_data
def load_data():
    if os.path.exists("data.xlsx"):
        df = pd.read_excel("data.xlsx", skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    return pd.DataFrame()

df = load_data()

if not df.empty:
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)] if search_term else df

    # 3. 지도 및 마커 로직
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)
    
    mapped_count = 0
    missing_cities = [] # 좌표를 못 찾은 지역 리스트

    for _, row in df_filtered.iterrows():
        city_text = str(row.get('시군', ''))
        coords = None
        
        # 엑셀 좌표 확인
        lat_val = pd.to_numeric(row.get('위도'), errors='coerce')
        lon_val = pd.to_numeric(row.get('경도'), errors='coerce')
        
        if pd.notnull(lat_val) and pd.notnull(lon_val):
            coords = [lat_val, lon_val]
        else:
            # 사전 매칭
            for key, val in location_map.items():
                if key in city_text:
                    coords = val
                    break
        
        if coords:
            mapped_count += 1
            scale = row.get('사육규모', 0)
            scale_formatted = f"{scale:,.0f}" if isinstance(scale, (int, float)) and pd.notnull(scale) else "0"
            
            html = f"""<div style="font-family: 'Malgun Gothic'; min-width: 200px;">
                        <b>{city_text}</b><br>규모: {scale_formatted}두<br>{row.get('발생내용', '')}</div>"""
            folium.Marker(location=coords, popup=folium.Popup(html, max_width=300), 
                          icon=folium.Icon(color='red', icon='warning', prefix='fa')).add_to(marker_cluster)
        else:
            missing_cities.append(city_text)

    # 상단 요약 정보
    st.subheader(f"📍 ASF 발생 위치 (표시: {mapped_count}건 / 전체: {len(df_filtered)}건)")
    
    # 💡 누락된 지역이 있다면 개발자(나)에게만 보이게 알림
    if missing_cities:
        with st.expander("⚠️ 지도 표시 누락 지역 확인"):
            st.write("아래 지역은 좌표가 등록되지 않아 지도에 나오지 않습니다:")
            st.write(", ".join(set(missing_cities)))

    st_folium(m, width="100%", height=500)
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
