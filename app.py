import streamlit as st
import pandas as pd
from io import BytesIO

# 제목
st.title("📦 택배사 운송장 변환기 - HANJIN 버전")
st.markdown("업로드하신 엑셀에서 필요한 열만 추출하고, 'HANJIN' 텍스트를 자동 삽입해드립니다.")

# 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일을 업로드 해주세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # 필요한 컬럼만 추출
        if {'보낸분', '메모1', '메모2', '운송장번호'}.issubset(df.columns):
            result_df = df[['보낸분', '메모1', '메모2', '운송장번호']].copy()
            result_df.insert(3, '고정텍스트', 'HANJIN')  # 세 번째 열에 HANJIN 추가

            st.success("✅ 변환이 완료되었습니다! 아래에서 결과를 확인하고 다운로드하세요.")
            st.dataframe(result_df.head(10))

            # 엑셀 다운로드
            def to_excel(dataframe):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    dataframe.to_excel(writer, index=False, sheet_name='결과')
                processed_data = output.getvalue()
                return processed_data

            st.download_button(
                label="📥 엑셀 다운로드",
                data=to_excel(result_df),
                file_name="hanjin_운송장_가공결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("❌ 엑셀 파일에 필요한 열이 모두 존재하지 않습니다. '보낸분', '메모1', '메모2', '운송장번호' 열을 확인해주세요.")

    except Exception as e:
        st.error(f"❌ 파일을 처리하는 중 오류가 발생했습니다: {e}")
