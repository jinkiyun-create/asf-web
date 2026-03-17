import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-title {
        font-size: 40px !important;
        font-weight: 800;
        color: #d32f2f;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# 🏢 로고 및 제목
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)
    else:
        st.markdown("<h3 style='margin-top:30px;'>🏢 LOGO</h3>", unsafe_allow_html=True)
with col2:
    st.markdown('<p class="main-title">아프리카돼지열병(ASF) 발생 현황 관리 시스템</p>', unsafe_allow_html=True)

# 2. 좌표 사전 (번호 기반)
location_map = {
    1: [37.7402, 126.7481], 2: [37.9625, 126.9112], 3: [37.6865, 126.5912],
    4: [38.0035, 126.9234], 5: [37.7852, 126.4746], 6: [37.6961, 126.5055],
    7: [37.6841, 126.3312], 8: [37.7461, 126.4842], 9: [37.7944, 126.4252],
    10: [37.9304, 126.8521], 11: [38.0035, 126.9234], 12: [37.8542, 126.7885],
    13: [37.6865, 126.5912], 14: [38.2215, 127.1082], 15: [38.1631, 127.6321],
    16: [38.1631, 127.6321], 17: [38.3712, 128.4612], 18: [38.3712, 128.4612],
    19: [38.0696, 128.1703], 20: [37.8212, 128.1412], 21: [38.0696, 128.1703],
    22: [37.7412, 127.9612], 23: [38.1051, 127.9897], 24: [37.7912, 127.7812],
    25: [37.7912, 127.7812], 26: [37.7112, 126.6341], 27: [37.8542, 126.7885],
    28: [38.2062, 127.2215], 29: [38.1158, 127.2452], 30: [38.2062, 127.2215],
    31: [37.6865, 126.5912], 32: [38.0412, 128.6412], 33: [37.9942, 127.2512],
    34: [38.0055, 127.1654], 35: [37.9942, 127.2512], 36: [38.0055, 127.1654],
    37: [38.1462, 127.3465], 38: [38.0612, 127.6741], 39: [36.5012, 129.4112],
    40: [38.0035, 126.9234], 41: [38.1462, 127.3465], 42: [36.0512, 128.9512],
    43: [36.5212, 128.7912], 44: [36.8012, 128.3712], 45: [36.0512, 128.9512],
    46: [37.7011, 126.5412], 47: [38.0712, 127.5231], 48: [37.8561, 126.9912],
    49: [37.8561, 126.9912], 50: [37.8561, 126.9912], 51: [37.8712, 127.0212],
    52: [37.8561, 126.9912], 53: [37.9304, 126.8521], 54: [37.9812, 126.9854],
    55: [36.9512, 126.6812], 56: [37.7212, 128.9812], 57: [36.9312, 127.2412],
    58: [38.1158, 127.2452], 59: [35.3912, 126.4412], 60: [35.3512, 126.6512],
    61: [36.4312, 126.5812], 62: [35.6112, 128.5112], 63: [38.1158, 127.2452],
    64: [37.2084, 126.8177], 65: [34.9315, 126.7958], 66: [36.8531, 126.6854],
    67: [35.6133, 126.8144], 68: [36.0592, 128.0581], 69: [36.5273, 126.5915],
    70: [35.5412, 128.5007], 71: [37.0792, 126.8114], 72: [37.0012, 126.9315],
    73: [38.2259, 127.4294], 74: [35.0934, 126.3151], 75: [35.5186, 128.3241],
    76: [35.7954, 128.1408], 77: [37.9575, 127.0267], 78: [35.3115, 127.9463],
    79: [35.1385, 126.4952]
}

# 3. 데이터 로드
@st.cache_data(ttl=10)
def load_data():
    if os.path.exists("data.xlsx"):
        df = pd.read_excel("data.xlsx", skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        
        if '번호' in df.columns:
            # 번호를 숫자로 변환 (73-1 같은 경우는 73으로 처리)
            df['번호_clean'] = df['번호'].astype(str).apply(lambda x: x.split('-')[0])
            df['번호_clean'] = pd.to_numeric(df['번호_clean'], errors='coerce').fillna(0).astype(int)
            df = df[df['번호_clean'] > 0].sort_values(by='번호_clean')
            return df
    return pd.DataFrame()

df = load_data()

# 4. 필터링 및 지도
if not df.empty:
    st.sidebar.header("🔍 검색 및 필터")
    search = st.sidebar.text_input("지역 또는 내용 검색")
    
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df

    st.subheader(f"📍 ASF 발생 위치 (표시 중: {len(df_filtered)}건)")
    
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster(spiderfy_on_max_zoom=True).add_to(m)

    for _, row in df_filtered.iterrows():
        # 데이터 추출 및 문자열 변환(TypeError 방지)
        num_display = str(row.get('번호', '0'))
        num_key = int(row.get('번호_clean', 0))
        city_text = str(row.get('시군', '정보없음'))
        content = str(row.get('발생내용', '내용 없음'))
        scale = str(row.get('사육규모', '-'))

        coords = None
        # 1순위: 엑셀에 위도/경도가 직접 있는 경우
        lat_ex = pd.to_numeric(row.get('위도'), errors='coerce')
        lon_ex = pd.to_numeric(row.get('경도'), errors='coerce')
        
        if pd.notnull(lat_ex) and pd.notnull(lon_ex):
            coords = [lat_ex, lon_ex]
        else:
            # 2순위: 번호(num_key)를 이용해 location_map에서 찾기
            coords = location_map.get(num_key)
        
        if coords:
            popup_html = f"""
            <div style="width:200px; font-family: 'Malgun Gothic', sans-serif;">
                <h4 style="margin:0; color:#d32f2f;">{num_display}번 발생</h4>
                <hr style="margin:5px 0;">
                <p style="margin:2px 0;"><b>📍 지역:</b> {city_text}</p>
                <p style="margin:2px 0;"><b>🐷 규모:</b> {scale}</p>
                <p style="margin:2px 0;"><b>📝 내용:</b> {content}</p>
            </div>
            """
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='red', icon='warning', prefix='fa')
            ).add_to(marker_cluster)

    st_folium(m, width="100%", height=600, returned_objects=[])

    # 5. 목록 표시
    st.subheader("📋 상세 발생 목록")
    display_df = df_filtered.copy()
    # 보조 컬럼 제거
    if '번호_clean' in display_df.columns:
        display_df = display_df.drop(columns=['번호_clean'])
    display_df = display_df.drop(columns=['위도', '경도'], errors='ignore')
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("데이터가 없거나 엑셀 형식이 잘못되었습니다. '번호' 컬럼을 확인해 주세요.")
