import streamlit as st
from datetime import datetime
import json
import os
import io
import pdfplumber

##================== Configuração ==================
st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

USERS = {"othavio": "122008", "isabela": "122008"}
LOG_FILE = "acessos.log"
DB_FILE = "db.json"

# ================== Registro de acesso ==================
def registrar_acesso(usuario: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {usuario}\n")
    except:
        pass

# ================== Session state ==================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "clientes" not in st.session_state:
    st.session_state.clientes = {
        "Tabata": [],
        "Valquiria": [],
        "Vanessa": [],
        "Pamela": [],
        "Elan": [],
        "Claudinha": [],
    }
if "produtos" not in st.session_state:
    st.session_state.produtos = {}
if "vendas" not in st.session_state:
    st.session_state.vendas = {c: [] for c in st.session_state.clientes.keys()}

# ================== Tela de Login ==================
def login():
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    entrar = st.button("Entrar")
    
    if entrar:
        if usuario in USERS and USERS[usuario] == senha:
            st.session_state["usuario"] = usuario
            registrar_acesso(usuario)
            st.experimental_rerun()  # agora dentro do botão, seguro
        else:
            st.error("Usuário ou senha incorretos")

# ================== Execução do login ==================
if st.session_state["usuario"] is None:
    login()
    st.stop()
    
# ========================= app.py - PARTE 2 =========================

# =============== Tela de cadastro de produtos ===============
def tela_produtos():
    st.header("📦 Cadastro de Produtos")
    
    with st.form("form_produto"):
        codigo = st.text_input("Código do Produto")
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Salvar Produto")
        
        if submit:
            if not codigo or not nome:
                st.warning("Preencha código e nome do produto")
            else:
                st.session_state.produtos[codigo] = {"nome": nome, "preco": preco}
                st.success(f"Produto {nome} cadastrado com sucesso!")

    # Upload de nota fiscal PDF
    st.subheader("📄 Upload de Nota Fiscal")
    arquivo = st.file_uploader("Envie a nota fiscal (PDF)", type=["pdf"])
    
    if arquivo is not None:
        try:
            with pdfplumber.open(arquivo) as pdf:
                text_total = ""
                for page in pdf.pages:
                    text_total += page.extract_text() + "\n"
                st.text_area("Conteúdo extraído da nota fiscal", text_total, height=300)
        except Exception as e:
            st.error(f"Erro ao processar PDF: {e}")
# ========================= app.py - PARTE 3 =========================

# =============== Tela de registrar vendas ===============
def tela_vendas():
    st.header("🛒 Registrar Venda")
    
    cliente = st.selectbox("Selecione o cliente", list(st.session_state.clientes.keys()))
    produto = st.selectbox("Selecione o produto", list(st.session_state.produtos.keys()))
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    
    if st.button("Registrar Venda"):
        if produto in st.session_state.produtos:
            preco = st.session_state.produtos[produto]["preco"]
            st.session_state.vendas[cliente].append({
                "codigo": produto,
                "quantidade": quantidade,
                "preco": preco
            })
            st.success(f"Venda registrada para {cliente}: {quantidade}x {st.session_state.produtos[produto]['nome']}")

# =============== Tela de clientes ===============
def tela_clientes():
    st.header("👥 Clientes")
    for cliente in st.session_state.clientes.keys():
        st.write(f"- {cliente} ({len(st.session_state.vendas[cliente])} vendas)")

# =============== Barra lateral ===============
def barra_lateral():
    st.sidebar.title("📋 Menu")
    menu = st.sidebar.radio("Escolha a opção", ["Clientes", "Produtos", "Registrar Vendas"])
    
    if menu == "Clientes":
        tela_clientes()
    elif menu == "Produtos":
        tela_produtos()
    elif menu == "Registrar Vendas":
        tela_vendas()

# =============== Função principal ===============
def main():
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    if st.sidebar.button("Logout"):
        st.session_state["usuario"] = None
        st.experimental_rerun()
    
    barra_lateral()

if __name__ == "__main__":
    main()
