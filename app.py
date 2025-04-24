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

        # 필요한 컬럼 확인
        required_columns = {'보낸분', '메모1', '메모2', '운송장번호'}
        if required_columns.issubset(df.columns):
            result_df = df[['보낸분', '메모1', '메모2', '운송장번호']].copy()

            # 1. 보낸분 → 쇼핑몰코드
            def convert_sender(name):
                name = str(name)
                if '복싱천' in name:
                    return '00001'
                elif 'SBD KORE' in name:
                    return '00005'
                else:
                    return name

            result_df['쇼핑몰코드'] = result_df['보낸분'].apply(convert_sender)

            # 2. 쇼핑몰코드 → 배송방법코드
            def convert_shipping_method(shop_code):
                if shop_code == '00005':
                    return '0018'
                else:
                    return 'HANJIN'

            result_df['배송방법코드'] = result_df['쇼핑몰코드'].apply(convert_shipping_method)

            # 3. 보낸분 열 제거
            result_df = result_df.drop(columns=['보낸분'])

            # 4. 컬럼 순서 및 이름 변경
            result_df = result_df[['쇼핑몰코드', '메모1', '메모2', '배송방법코드', '운송장번호']]
            result_df.columns = ['쇼핑몰코드', '주문번호', '묶음주문번호', '배송방법코드', '송장번호']

            # 5. 빈 행 제거
            def is_blank_row(row):
                return all((str(cell).strip() == '' or pd.isna(cell)) for cell in row)

            result_df = result_df[~result_df.apply(is_blank_row, axis=1)]

            # 6. 동적 height 설정
            table_height = min(600, 40 * len(result_df) + 60)

            # 결과 출력
            st.success("✅ 변환이 완료되었습니다! 아래에서 결과를 확인하고 다운로드하세요.")
            st.data_editor(
                result_df.reset_index(drop=True),
                height=table_height,
                hide_index=True,
                disabled=True
            )

            # 7. 클립보드 복사 버튼 (텍스트 박스 없이!)
            def dataframe_to_clipboard_text(df):
                return df.to_csv(index=False, header=False, sep="\t")

            clipboard_text = dataframe_to_clipboard_text(result_df)
            # JS 스크립트로 복사 기능 구현
            copy_script = f"""
            <script>
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text).then(function() {{
                    console.log('복사 완료');
                }}, function(err) {{
                    console.error('복사 실패', err);
                }});
            }}
            copyToClipboard(`{clipboard_text}`);
            </script>
            """

            if st.button("📋 결과 복사하기 (제목 제외)"):
                st.components.v1.html(copy_script, height=0)
                st.toast("✅ 복사가 완료되었습니다!")

            # 엑셀 다운로드
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
