import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster  # 💡 중복 위치 표시 해결
import os

# 1. 페이지 설정 및 보안 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

# 🔒 [보안] 우측 상단 메뉴(햄버거 버튼)와 하단 푸터를 숨겨서 일반 사용자가 수정을 시도하지 못하게 합니다.
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* 제목 스타일 강화 */
    .main-title {
        font-size: 40px !important;
        font-weight: 800;
        color: #d32f2f;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# 로고 및 제목 레이아웃
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)
    else:
        st.markdown("<h3 style='margin-top:30px;'>🏢 LOGO</h3>", unsafe_allow_html=True)
with col2:
    st.markdown('<p class="main-title">아프리카돼지열병(ASF) 발생 현황 관리 시스템</p>', unsafe_allow_html=True)

# 2. 전국 주요 발생 지역 좌표 사전 (누락 지역 8곳 포함 전체 업데이트)
location_map = {
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
    "소초": [37.3881, 127.9942], "신북": [37.9405, 127.2185], "가평": [37.8315, 127.5095], 
    "포항": [36.0190, 129.3435], "예천": [36.6575, 128.4528], "정선": [37.3806, 128.6608],
    "보령": [36.3333, 126.6128], "영광": [35.2773, 126.5120], "창녕": [35.5446, 128.4922],
    "청주": [36.6424, 127.4890], "음성": [36.9399, 127.6913], "고령": [35.7258, 128.2635]
}

# 3. 데이터 로드
@st.cache_data
def load_data():
    if os.path.exists("data.xlsx"):
        df = pd.read_excel("data.xlsx", skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # 검색 기능
    st.sidebar.header("🔍 검색 및 필터")
    search = st.sidebar.text_input("지역 또는 내용 검색")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df

    # 4. 지도 및 요약 표시
    # 💡 [요청사항 수정] 총 발생건수 문구를 62건으로 고정 표기 (동적 데이터 반영 시 len(df_filtered) 대신 62 사용 가능하나, 여기서는 문맥상 62건으로 수정)
    st.subheader(f"📍 ASF 발생 위치 (총 발생건수: 62건)")
    
    # 지도 생성
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    
    # 💡 마커 클러스터 추가
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df_filtered.iterrows():
        city_text = str(row.get('시군', ''))
        coords = None
        
        lat_val = pd.to_numeric(row.get('위도'), errors='coerce')
        lon_val = pd.to_numeric(row.get('경도'), errors='coerce')
        
        if pd.notnull(lat_val) and pd.notnull(lon_val):
            coords = [lat_val, lon_val]
        else:
            for key, val in location_map.items():
                if key in city_text:
                    coords = val
                    break
        
        if coords:
            scale = row.get('사육규모', 0)
            scale_formatted = f"{scale:,.0f}" if isinstance(scale, (int, float)) and pd.notnull(scale) else str(scale)
            
            popup_html = f"""
            <div style="font-family: 'Malgun Gothic', sans-serif; width: 200px;">
                <h4 style="margin: 0 0 5px 0; color: #d32f2f;">{city_text}</h4>
                <hr style="margin: 5px 0;">
                <p style="margin: 3px 0;"><b>규모:</b> {scale_formatted} 두</p>
                <p style="margin: 3px 0;"><b>내용:</b> {row.get('발생내용', '')}</p>
            </div>
            """
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='red', icon='warning', prefix='fa')
            ).add_to(marker_cluster)

    st_folium(m, width="100%", height=600)

    # 5. 목록 표시
    st.subheader("📋 상세 발생 목록")
    display_df = df_filtered.copy()
    if '사육규모' in display_df.columns:
        display_df['사육규모'] = display_df['사육규모'].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and pd.notnull(x) else x)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.warning("data.xlsx 파일을 찾을 수 없거나 데이터가 비어 있습니다.")
