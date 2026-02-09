# 3. 데이터 로드 및 정렬 로직 (에러 수정 버전)
@st.cache_data
def load_data():
    if os.path.exists("data.xlsx"):
        # 엑셀을 읽을 때 header 위치를 자동으로 찾거나, 
        # 첫 번째 실제 데이터가 있는 행을 찾기 위해 skiprows를 조정합니다.
        df = pd.read_excel("data.xlsx", skiprows=1)
        
        # 컬럼 공백 제거 및 이름 확인
        df.columns = [str(c).strip() for c in df.columns]
        
        # 💡 만약 엑셀의 컬럼명이 '번호'가 아니라 'No' 또는 다른 이름일 경우를 대비
        # '번호' 컬럼이 없으면 첫 번째 컬럼을 '번호'로 간주합니다.
        if '번호' not in df.columns and len(df.columns) > 0:
            df.rename(columns={df.columns[0]: '번호'}, inplace=True)
    else:
        df = pd.DataFrame(columns=['번호', '시군', '발생내용', '사육규모'])

    # 💡 데이터 전처리: '번호' 컬럼에서 유효한 행만 필터링
    # 결측치 제거 및 문자열 변환 후 숫자(isdigit)인 것만 남김
    df = df.dropna(subset=['번호']).copy()
    df = df[df['번호'].apply(lambda x: str(x).replace('.0', '').isdigit())].copy()

    # 💡 63번, 64번 추가
    new_data = pd.DataFrame([
        {"번호": 63, "시군": "고령", "발생내용": "양돈농장 발생 (25.02.09)", "사육규모": 1200, "위도": 35.7258, "경도": 128.2635},
        {"번호": 64, "시군": "청주", "발생내용": "양돈농장 발생 (25.02.10)", "사육규모": 3500, "위도": 36.6424, "경도": 127.4890}
    ])
    
    # 데이터 합치기
    df = pd.concat([df, new_data], ignore_index=True)
    
    # 번호순 정렬 (숫자로 변환)
    df['번호'] = pd.to_numeric(df['번호'])
    df = df.sort_values(by='번호', ascending=True)

    # 💡 '계' 행 계산 및 추가 (53-1 등 예외 제외한 순수 합계)
    total_scale = pd.to_numeric(df['사육규모'], errors='coerce').sum()
    summary_row = pd.DataFrame([{"번호": "계", "시군": "-", "발생내용": "총 발생 합계", "사육규모": total_scale}])
    
    return pd.concat([df, summary_row], ignore_index=True)

df = load_data()
