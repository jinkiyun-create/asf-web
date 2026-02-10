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

# 2. 좌표 사전
location_map = {
    "연다산동": [37.7402, 126.7481], "백학면": [37.9625, 126.9112], "통진읍": [37.6865, 126.5912],
    "적성면": [38.0035, 126.9234], "적성읍": [38.0035, 126.9234], "송해면": [37.7852, 126.4746],
    "불은면": [37.6961, 126.5055], "삼산면": [37.6841, 126.3312], "강화읍": [37.7461, 126.4842],
    "하점면": [37.7944, 126.4252], "파평면": [37.9304, 126.8521], "문산읍": [37.8542, 126.7885],
    "신서면": [38.2215, 127.1082], "하성면": [37.7112, 126.6341], "월곶면": [37.7011, 126.5412],
    "미산면": [37.9812, 126.9854],
    "상서면": [38.1631, 127.6321], "동송읍": [38.2062, 127.2215], "관인면": [38.1158, 127.2452],
    "영중면": [37.9942, 127.2512], "창수면": [38.0055, 127.1654], "갈말읍": [38.1462, 127.3465],
    "하남면": [38.0612, 127.6741], "사내면": [38.0712, 127.5231], "남면": [37.8561, 126.9912], 
    "은현면": [37.8712, 127.0212],
    "주천면": [37.2712, 128.2715], "간성읍": [38.3712, 128.4612], "인제읍": [38.0696, 128.1703],
    "내촌면": [37.8212, 128.1412], "화촌면": [37.7412, 127.9612], "국토정중앙면": [38.1051, 127.9897],
    "동산면": [37.7912, 127.7812], "손양면": [38.0412, 128.6412], "축산면": [36.5012, 129.4112],
    "화남면": [36.0512, 128.9512], "남선면": [36.5212, 128.7912], "효자면": [36.8012, 128.3712],
    "송산면": [36.9512, 126.6812], "강동면": [37.7212, 128.9812], "미양면": [36.9312, 127.2412],
    "홍농읍": [35.3912, 126.4412], "성송면": [35.3512, 126.6512], "청소면": [36.4312, 126.5812],
    "대합면": [35.6112, 128.5112], "남양읍": [37.2084, 126.8177],
    "봉황면": [34.9315, 126.7958]
}

# 3. 데이터 로드 및 전처리
@st.cache_data(ttl=5)
def load_data():
    if os.path.exists("data.xlsx"):
        # skiprows=1을 유지하되, 헤더를 읽은 후 이름을 강제로 덮어씌웁니다.
        df = pd.read_excel("data.xlsx", skiprows=1)
        
        # [핵심] 컬럼이 몇 개든 상관없이 첫 4개 컬럼 이름을 강제로 고정합니다.
        # 엑셀 순서가 번호, 시군, 발생내용, 사육규모 순이라고 가정합니다.
        new_cols = ['번호', '시군', '발생내용', '사육규모']
        # 엑셀의 실제 컬럼 수에 맞춰 이름을 매칭합니다.
        df.columns = new_cols + [str(c) for c in df.columns[len(new_cols):]]
        
        # 공백 제거
        df['번호'] = pd.to_numeric(df['번호'], errors='coerce')
        df = df.dropna(subset=['번호'])
        df['번호'] = df['번호'].astype(int)
        
        # 전체 데이터를 번호 기준 최신순 정렬
        df = df.sort_values(by='번호', ascending=False)
        return df
    return pd.DataFrame()

df = load_data()

# 4. 필터링 및 지도
if not df.empty:
    st.sidebar.header("🔍 검색 및 필터")
    search = st.sidebar.text_input("지역 또는 내용 검색")
    
    if search:
        # 모든 컬럼에서 검색어 포함 여부 확인
        df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    else:
        df_filtered = df.copy()

    st.subheader("📍 ASF 발생 위치 (총 발생건수: 65건)")
    
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster(spiderfy_on_max_zoom=True).add_to(m)

    for _, row in df_filtered.iterrows():
        # 데이터 추출 (이름이 고정되었으므로 안전함)
        num_val = row['번호']
        city_text = str(row.get('시군', '정보없음'))
        content = str(row.get('발생내용', '내용 없음'))
        scale = str(row.get('사육규모', '-'))

        coords = None
        # 위경도 컬럼은 이름이 유동적일 수 있으므로 안전하게 처리
        lat_val = row.get('위도')
        lon_val = row.get('경도')
        
        lat_ex = pd.to_numeric(lat_val, errors='coerce')
        lon_ex = pd.to_numeric(lon_val, errors='coerce')
        
        if pd.notnull(lat_ex) and pd.notnull(lon_ex):
            coords = [lat_ex, lon_ex]
        else:
            for key, val in location_map.items():
                if key in city_text:
                    coords = val
                    break
        
        if coords:
            popup_html = f"""
            <div style="width:200px; font-family: 'Malgun Gothic', sans-serif;">
                <h4 style="margin:0; color:#d32f2f;">{num_val}번 발생</h4>
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

    st_folium(m, width="100%", height=600)

    # 5. 목록 표시 (최신순)
    st.subheader("📋 상세 발생 목록 (최신순)")
    
    # 위경도 제외하고 표시
    display_cols = [c for c in df_filtered.columns if c not in ['위도', '경도']]
    final_df = df_filtered[display_cols].copy()
    
    # 다시 한번 내림차순 정렬 확정
    final_df = final_df.sort_values(by='번호', ascending=False)
    
    # 천 단위 콤마
    if '사육규모' in final_df.columns:
        final_df['사육규모'] = final_df['사육규모'].apply(
            lambda x: f"{int(x):,}" if isinstance(x, (int, float)) and pd.notnull(x) else x
        )
    
    st.dataframe(final_df, use_container_width=True, hide_index=True)

else:
    st.warning("데이터를 불러올 수 없습니다. 엑셀 파일의 첫 번째 줄이 '번호'로 시작하는지 확인해주세요.")
