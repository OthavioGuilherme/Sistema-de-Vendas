# ================= PARTE 1 - CONEXÃO COM GOOGLE SHEETS E CONFIGURAÇÕES =================
import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import json
import io
import re
import pdfplumber

# Configuração inicial
st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# URL da sua planilha Google
SHEET_URL = "COLE_AQUI_A_URL_DA_SUA_PLANILHA"

# Função para conectar no Google Sheets
def connect_gsheet():
    try:
        creds = dict(st.secrets["GCP_SA_CREDENTIALS"])
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_url(SHEET_URL)
        return sh
    except Exception as e:
        st.error(f"❌ ERRO FATAL AO CONECTAR: {type(e).__name__} - {e}")
        return None

# Inicializa conexão e cria abas se não existirem
def init_db():
    sh = connect_gsheet()
    if not sh:
        return None, None, None

    try:
        ws_users = sh.worksheet("USUÁRIOS")
    except:
        ws_users = sh.add_worksheet(title="USUÁRIOS", rows=100, cols=20)
        ws_users.append_row(["usuario", "senha"])

    try:
        ws_produtos = sh.worksheet("PRODUTOS")
    except:
        ws_produtos = sh.add_worksheet(title="PRODUTOS", rows=1000, cols=20)
        ws_produtos.append_row(["codigo", "nome", "preco", "quantidade"])

    try:
        ws_vendas = sh.worksheet("VENDAS")
    except:
        ws_vendas = sh.add_worksheet(title="VENDAS", rows=1000, cols=20)
        ws_vendas.append_row(["data", "cliente", "codigo", "nome", "quantidade", "preco", "total"])

    return ws_users, ws_produtos, ws_vendas

# ================== FUNÇÕES DE BANCO DE DADOS (SEM ARQUIVO LOCAL) ==================
def load_db():
    try:
        sh = connect_gsheet()
        ws_produtos = sh.worksheet("PRODUTOS")
        ws_clientes = sh.worksheet("CLIENTES")

        produtos = {int(row["codigo"]): {
                        "nome": row["nome"],
                        "preco": float(row["preco"]),
                        "quantidade": int(row.get("quantidade", 0))}
                    for row in ws_produtos.get_all_records()}

        clientes = {row["nome"]: [] for row in ws_clientes.get_all_records()}

        return produtos, clientes
    except Exception as e:
        st.warning(f"⚠️ Falha ao carregar dados: {e}")
        return {}, {}

def save_produto(codigo, nome, preco, quantidade):
    try:
        sh = connect_gsheet()
        ws = sh.worksheet("PRODUTOS")
        ws.append_row([codigo, nome, preco, quantidade], value_input_option="USER_ENTERED")
    except Exception as e:
        st.error(f"Erro ao salvar produto no Google Sheets: {e}")

def save_cliente(nome):
    try:
        sh = connect_gsheet()
        ws = sh.worksheet("CLIENTES")
        ws.append_row([nome], value_input_option="USER_ENTERED")
    except Exception as e:
        st.error(f"Erro ao salvar cliente no Google Sheets: {e}")

def save_venda(cliente, codigo, nome, preco, quantidade):
    try:
        sh = connect_gsheet()
        ws = sh.worksheet("VENDAS")
        total = preco * quantidade
        ws.append_row([
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            cliente, codigo, nome, quantidade, preco, total
        ], value_input_option="USER_ENTERED")
    except Exception as e:
        st.error(f"Erro ao salvar venda no Google Sheets: {e}")

# ================== Session State inicial ==================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "produtos" not in st.session_state:
    prods_loaded, clients_loaded = load_db()
    st.session_state["produtos"] = prods_loaded or {}
    st.session_state["clientes"] = clients_loaded or {}
if "menu" not in st.session_state:
    st.session_state["menu"] = "Resumo 📊"

# ================== Função: is_visitante ==================
def is_visitante():
    u = st.session_state.get("usuario")
    return isinstance(u, str) and u.startswith("visitante-")
# ================== LOGIN ==================
def login():
    st.title("🔐 Login no Sistema")

    tab_login, tab_visitante = st.tabs(["Login", "Entrar como Visitante"])

    with tab_login:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            ws_users, _, _ = init_db()
            users = {row["usuario"]: row["senha"] for row in ws_users.get_all_records()}

            if usuario in users and users[usuario] == senha:
                st.session_state["usuario"] = usuario
                st.success("✅ Login realizado com sucesso!")
                st.session_state["menu"] = "Resumo 📊"
                st.rerun()
            else:
                st.error("❌ Usuário ou senha inválidos.")

    with tab_visitante:
        if st.button("Entrar como Visitante"):
            st.session_state["usuario"] = f"visitante-{datetime.now().strftime('%H%M%S')}"
            st.session_state["menu"] = "Resumo 📊"
            st.rerun()


# ================== PÁGINA DE RESUMO ==================
def pagina_resumo():
    st.header("📊 Resumo Geral")

    sh = connect_gsheet()
    if not sh:
        return

    ws_vendas = sh.worksheet("VENDAS")
    vendas = ws_vendas.get_all_records()

    if not vendas:
        st.info("Nenhuma venda registrada ainda.")
        return

    df = pd.DataFrame(vendas)
    df["total"] = df["total"].astype(float)

    total_vendas = df["total"].sum()
    qtd_vendas = len(df)

    col1, col2 = st.columns(2)
    col1.metric("💰 Total em Vendas", f"R$ {total_vendas:,.2f}")
    col2.metric("🛒 Quantidade de Vendas", qtd_vendas)

    st.subheader("📅 Últimas Vendas")
    st.dataframe(df.tail(10))


# ================== PÁGINA DE PRODUTOS ==================
def pagina_produtos():
    st.header("📦 Cadastro e Consulta de Produtos")

    tab_cadastrar, tab_listar = st.tabs(["Cadastrar Produto", "Listar / Buscar Produtos"])

    # --- CADASTRAR ---
    with tab_cadastrar:
        with st.form("form_produto"):
            codigo = st.text_input("Código do Produto")
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço (R$)", min_value=0.0, step=0.01)
            quantidade = st.number_input("Quantidade em Estoque", min_value=0, step=1)

            submitted = st.form_submit_button("Salvar Produto")
            if submitted:
                if codigo and nome:
                    save_produto(codigo, nome, preco, quantidade)
                    st.success(f"✅ Produto {nome} salvo com sucesso!")
                else:
                    st.error("Preencha todos os campos.")

    # --- LISTAR ---
    with tab_listar:
        sh = connect_gsheet()
        ws_produtos = sh.worksheet("PRODUTOS")
        produtos = ws_produtos.get_all_records()

        df = pd.DataFrame(produtos)

        busca = st.text_input("🔍 Buscar por código ou nome")

        if busca:
            df = df[df.apply(lambda row:
                             busca.lower() in str(row["codigo"]).lower() or
                             busca.lower() in str(row["nome"]).lower(),
                             axis=1)]

        if not df.empty:
            st.dataframe(df)
        else:
            st.info("Nenhum produto encontrado.")
# ================== CLIENTES ==================
def pagina_clientes():
    st.header("👥 Cadastro e Consulta de Clientes")

    tab_cadastrar, tab_listar = st.tabs(["Cadastrar Cliente", "Listar / Buscar Clientes"])

    # --- CADASTRAR ---
    with tab_cadastrar:
        with st.form("form_cliente"):
            nome = st.text_input("Nome do Cliente")
            telefone = st.text_input("Telefone")
            email = st.text_input("E-mail")

            submitted = st.form_submit_button("Salvar Cliente")
            if submitted:
                if nome:
                    save_cliente(nome, telefone, email)
                    st.success(f"✅ Cliente {nome} salvo com sucesso!")
                else:
                    st.error("Preencha ao menos o nome.")

    # --- LISTAR ---
    with tab_listar:
        sh = connect_gsheet()
        ws_clientes = sh.worksheet("CLIENTES")
        clientes = ws_clientes.get_all_records()

        df = pd.DataFrame(clientes)

        busca = st.text_input("🔍 Buscar cliente")

        if busca:
            df = df[df.apply(lambda row:
                             busca.lower() in str(row["nome"]).lower() or
                             busca.lower() in str(row["telefone"]).lower(),
                             axis=1)]

        if not df.empty:
            st.dataframe(df)
        else:
            st.info("Nenhum cliente encontrado.")


# ================== REGISTRO DE VENDAS ==================
def pagina_vendas():
    st.header("🛒 Registro de Vendas")

    sh = connect_gsheet()
    ws_vendas = sh.worksheet("VENDAS")
    ws_produtos = sh.worksheet("PRODUTOS")

    produtos = ws_produtos.get_all_records()

    if not produtos:
        st.warning("⚠️ Nenhum produto cadastrado.")
        return

    df_produtos = pd.DataFrame(produtos)

    cliente = st.text_input("Nome do Cliente")

    codigos = st.text_input("Digite o código do produto (separados por vírgula)").split(",")

    itens = []
    total = 0

    for codigo in codigos:
        codigo = codigo.strip()
        if codigo:
            produto = df_produtos[df_produtos["codigo"] == codigo]
            if not produto.empty:
                nome = produto.iloc[0]["nome"]
                preco = float(produto.iloc[0]["preco"])
                itens.append({"codigo": codigo, "nome": nome, "preco": preco})
                total += preco

    if itens:
        st.subheader("📝 Itens da Venda")
        st.table(pd.DataFrame(itens))

        st.subheader(f"💰 Total: R$ {total:,.2f}")

        if st.button("Finalizar Venda"):
            save_venda(cliente, itens, total)
            st.success("✅ Venda registrada com sucesso!")


# ================== RELATÓRIOS ==================
def pagina_relatorios():
    st.header("📈 Relatórios de Vendas")

    sh = connect_gsheet()
    ws_vendas = sh.worksheet("VENDAS")
    vendas = ws_vendas.get_all_records()

    if not vendas:
        st.info("Nenhuma venda registrada.")
        return

    df = pd.DataFrame(vendas)
    df["total"] = df["total"].astype(float)

    st.subheader("📅 Vendas por Dia")
    vendas_por_dia = df.groupby("data")["total"].sum()
    st.line_chart(vendas_por_dia)

    st.subheader("🏆 Clientes que mais compraram")
    clientes_top = df.groupby("cliente")["total"].sum().sort_values(ascending=False)
    st.bar_chart(clientes_top)


# ================== MENU PRINCIPAL ==================
def main():
    if "usuario" not in st.session_state:
        login()
        return

    menu = st.sidebar.radio("📌 Menu", [
        "Resumo 📊",
        "Produtos 📦",
        "Clientes 👥",
        "Vendas 🛒",
        "Relatórios 📈"
    ])

    if menu == "Resumo 📊":
        pagina_resumo()
    elif menu == "Produtos 📦":
        pagina_produtos()
    elif menu == "Clientes 👥":
        pagina_clientes()
    elif menu == "Vendas 🛒":
        pagina_vendas()
    elif menu == "Relatórios 📈":
        pagina_relatorios()


if __name__ == "__main__":
    main()