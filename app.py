# app.py (TESTE MAIS BÁSICO POSSÍVEL)
import streamlit as st

st.title("✅ SUCESSO! Streamlit rodando!")
st.info("Se você está vendo esta mensagem, o problema NÃO é o Streamlit, mas sim as suas importações (Google Sheets ou PDF).")

# Deixe as importações problemáticas no final, APÓS o texto de sucesso.
try:
    from st_gsheets_connection import GSheetsConnection
    import pdfplumber
    st.success("As importações de GSheets e PDF funcionaram.")
except ImportError as e:
    st.error(f"❌ Erro de importação! Verifique requirements.txt. Detalhe: {e}")
except Exception as e:
    st.error(f"❌ Erro na importação: {e}")
