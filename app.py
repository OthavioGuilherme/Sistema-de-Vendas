# app.py (TESTE DE IMPORTAÇÃO CRÍTICO)
import streamlit as st
import sys

# Tenta importar a biblioteca de conexão do Google Sheets, que é o provável ponto de falha.
try:
    from st_gsheets_connection import GSheetsConnection
    st.success("✅ st-gsheets-connection foi importada com sucesso!")
except ImportError:
    st.error("❌ ERRO CRÍTICO: st-gsheets-connection NÃO foi encontrada. Verifique seu requirements.txt!")
    GSheetsConnection = None
except Exception as e:
    st.exception(f"❌ Erro desconhecido na importação: {e}")
    GSheetsConnection = None

# O resto das importações pode ter falhado, mas vamos ver o que o Streamlit exibe.
try:
    import pandas as pd
    st.success("✅ Pandas importado com sucesso!")
except:
    st.error("❌ Pandas não importado.")


st.title("Sistema de Vendas - Teste de Funcionamento 🛠️")
st.write("Se você está vendo esta tela, seu Streamlit está funcionando!")
st.write(f"Status da Conexão: {'Pronto' if GSheetsConnection else 'FALHOU ou Desativada'}")

st.info("Se o app travar novamente antes de exibir este texto, o problema é muito mais fundamental no ambiente de deploy.")
