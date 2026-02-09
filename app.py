import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

# 2. 좌표 사전 (관인, 남양 포함)
location_map = {
    "연천": [38.0964, 127.0754], "파주": [37.7600, 126.7798], "철원": [38.1463, 127.3132],
    "화천": [38.1061, 127.7081], "양구": [38.1051, 127.9897], "인제": [38.0696, 128.1703],
    "고성": [38.3805, 128.4687], "포천": [37.8949, 127.2003], "관인": [38.1158, 127.2452],
    "양양": [38.0754, 128.6189], "홍천": [37.6970, 127.8887], "춘천": [37.8813, 127.7298],
    "강릉": [37.7518, 128.8761], "횡성": [37.4912, 127.9853], "평창": [37.3705, 128.3902],
    "영월": [37.1837, 128.4619], "원주": [37.3422, 127.9202], "보은": [36.4894, 127.7345],
    "충주": [36.9910, 127.9259], "제천": [37.1326, 128.2141], "괴산": [36.8115, 127.7946],
    "단양": [36.9845, 128.3653], "안동": [36.5684, 128.7296], "영덕": [36.4150, 129.3653],
    "영천": [35.9732, 128.9385], "경주": [35.8562, 129.2247], "상주": [36.4109, 128.1591],
    "문경": [36.5861, 128.1868], "의성": [36.3522, 128.6970], "청송": [36.4362, 129.0573],
    "영양": [36.6666, 129.1120], "봉화": [36.8931, 128.7325], "울진": [36.9931, 129.4005],
    "김포": [37.6151, 126.7154], "강화": [37.7461, 126.4842], "인천": [37.4562, 126.7052],
    "부산": [35.1798, 129.0750], "남양": [37.2084, 126.8177],
    "청주": [36.6424, 127.4890], "고령": [35.7258, 128.2635]
}

# 3. 데이터 로드 (가장 중요한 부분)
@st.cache_data
def load_data():
    if os.path.exists("data.xlsx"):
        # 💡 skiprows=1은 유지하되, 모든 행을 다 읽어옵니다.
        df = pd.read_excel("data.xlsx", skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        
        # 💡 '번호' 컬럼에서 숫자로 변환 가능한 것들만 남깁니다 (63, 64번 포함)
        if '번호' in df.columns:
            # 강제로 숫자로 변환 (변환 안되는 '계' 등은 NaN이 됨)
            df['번호_temp'] = pd.to_numeric(df['번호'], errors='coerce')
            # NaN(숫자 아닌 것)을 제거하고 번호순 정렬
            df = df.dropna(subset=['번호_temp'])
            df = df.sort_values(by='번호_temp').reset_index(drop=True)
            # 원래 번호 컬럼에 깔끔한 숫자 저장
            df['번호'] = df['번호_temp'].astype(int)
            df = df.drop(columns=['번호_temp'])
            
        return df
    return pd.DataFrame()

df = load_data()

# 4. 필터링 및 화면 출력
if not df.empty:
    st.sidebar.header("🔍 검색 및 필터")
    search = st.sidebar.text_input("지역 또는 내용 검색")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df

    # 💡 실제 데이터 개수를 제목에 표시 (자동으로 64건이 되어야 함)
    st.subheader(f"📍 ASF 발생 위치 (총 발생건수: {len(df)}건)")
    
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df_filtered.iterrows():
        city_text = str(row.get('시군', ''))
        coords = None
        for key, val in location_map.items():
            if key in city_text:
                coords = val
                break
        if coords:
            scale = row.get('사육규모', 0)
            popup_html = f"<b>{city_text}</b><br>규모: {scale}"
            folium.Marker(location=coords, popup=folium.Popup(popup_html, max_width=200)).add_to(marker_cluster)

    st_folium(m, width="100%", height=600)

    # 5. 상세 목록 (위도/경도 제외, 1~64번 전체 노출)
    st.subheader("📋 상세 발생 목록")
    
    # 💡 위도, 경도 컬럼만 쏙 빼고 나머지 상세내역은 전부 보여줌
    display_df = df_filtered.copy()
    display_df = display_df.drop(columns=['위도', '경도'], errors='ignore')
    
    if '사육규모' in display_df.columns:
        display_df['사육규모'] = display_df['사육규모'].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)

    # 💡 데이터프레임 출력
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("데이터가 없습니다. 엑셀 파일의 내용을 확인해주세요.")
