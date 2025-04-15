import streamlit as st
import pandas as pd
from io import BytesIO

# 제목
st.title("📦 택배사 운송장 변환기 - HANJIN")
st.markdown("Creator by hmp_slee")

# 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일을 업로드 해주세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # 필요한 컬럼이 있는지 확인
        required_columns = {'보낸분', '메모1', '메모2', '운송장번호'}
        if required_columns.issubset(df.columns):
            result_df = df[['보낸분', '메모1', '메모2', '운송장번호']].copy()
            result_df.insert(3, '고정텍스트', 'HANJIN')  # '고정텍스트' 열 삽입

            # 보낸분 텍스트 → 쇼핑몰 코드로 변환
            def convert_sender(name):
                name = str(name)
                if '복싱천' in name:
                    return '00001'
                elif 'SBD KORE' in name:
                    return '00005'
                else:
                    return name

            result_df['보낸분'] = result_df['보낸분'].apply(convert_sender)

            # 결과 출력
            st.success("✅ 변환이 완료되었습니다! 아래에서 결과를 확인하고 다운로드하세요.")
            st.dataframe(result_df.head(10))

            # 엑셀로 다운로드
            def to_excel(dataframe):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    dataframe.to_excel(writer, index=False, sheet_name='결과')
                return output.getvalue()

            st.download_button(
                label="📥 엑셀 다운로드",
                data=to_excel(result_df),
                file_name="hanjin_운송장_가공결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error(f"❌ 엑셀 파일에 필요한 열이 없습니다. 다음 컬럼이 필요합니다: {', '.join(required_columns)}")

    except Exception as e:
        st.error(f"❌ 파일을 처리하는 중 오류가 발생했습니다: {e}")
