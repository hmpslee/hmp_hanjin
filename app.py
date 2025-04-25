import streamlit as st
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components

# 🔁 앱 초기화 함수
#def reset_app():
    #st.session_state.clear()
    #st.rerun()

# 제목
st.title("📦 택배사 운송장 변환기 - HANJIN")
st.markdown("Creator by hmp_slee")

# 업로드
uploaded_file = st.file_uploader("엑셀 파일을 업로드 해주세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        required_columns = {'보낸분', '메모1', '메모2', '운송장번호'}
        if required_columns.issubset(df.columns):
            result_df = df[['보낸분', '메모1', '메모2', '운송장번호']].copy()

            def convert_sender(name):
                name = str(name)
                if '복싱천' in name:
                    return '00001'
                elif 'SBD KORE' in name:
                    return '00005'
                else:
                    return name

            result_df['쇼핑몰코드'] = result_df['보낸분'].apply(convert_sender)

            def convert_shipping_method(shop_code):
                return '0018' if shop_code == '00005' else 'HANJIN'

            result_df['배송방법코드'] = result_df['쇼핑몰코드'].apply(convert_shipping_method)

            result_df = result_df.drop(columns=['보낸분'])

            result_df = result_df[['쇼핑몰코드', '메모1', '메모2', '배송방법코드', '운송장번호']]
            result_df.columns = ['쇼핑몰코드', '주문번호', '묶음주문번호', '배송방법코드', '송장번호']

            def is_blank_row(row):
                return all((str(cell).strip() == '' or pd.isna(cell)) for cell in row)

            result_df = result_df[~result_df.apply(is_blank_row, axis=1)]

            table_height = min(600, 40 * len(result_df) + 60)

            st.success("✅ 변환이 완료되었습니다! 아래에서 결과를 확인하고 다운로드하세요.")
            st.data_editor(
                result_df.reset_index(drop=True),
                height=table_height,
                hide_index=True,
                disabled=True
            )

            # ✅ 복사 텍스트 (제목 제외)
            clipboard_text = result_df.to_csv(index=False, header=False, sep="\t").replace("`", "'")

            # ✅ JS 기반 복사 버튼
            copy_script = f"""
            <script>
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text).then(function() {{
                    const toast = document.createElement("div");
                    toast.innerText = "✅ 복사가 완료되었습니다!";
                    toast.style.position = "fixed";
                    toast.style.bottom = "20px";
                    toast.style.right = "20px";
                    toast.style.background = "#333";
                    toast.style.color = "#fff";
                    toast.style.padding = "10px 20px";
                    toast.style.borderRadius = "8px";
                    toast.style.zIndex = "9999";
                    document.body.appendChild(toast);
                    setTimeout(() => toast.remove(), 2000);
                }});
            }}
            </script>
            <button onclick="copyToClipboard(`{clipboard_text}`)" style="margin-top:20px; background-color:#f33; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">
                📋 결과 복사하기 (제목 제외)
            </button>
            """

            components.html(copy_script, height=80)

            # 📥 엑셀 다운로드 + 🔄 다시 시작 버튼 나란히
            col1, col2 = st.columns([1, 1])
            with col1:
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

            #with col2:
                #st.button("🔄 다시 시작하기", on_click=reset_app)

        else:
            st.error(f"❌ 엑셀 파일에 필요한 열이 없습니다. 다음 컬럼이 필요합니다: {', '.join(required_columns)}")

    except Exception as e:
        st.error(f"❌ 파일을 처리하는 중 오류가 발생했습니다: {e}")
