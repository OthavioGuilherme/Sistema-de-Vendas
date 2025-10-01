# app.py (MODO DE TESTE: GOOGLE SHEETS DESABILITADO)
# ================= PARTE 1 - IMPORTAÇÕES E CONFIGURAÇÃO ==================
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import re
# Importa GSheetsConnection, mas não vamos usá-la.
from st_gsheets_connection import GSheetsConnection 

# Importa pdfplumber de forma segura
try:
    import pdfplumber
except ImportError:
    pdfplumber = None # Garante que o código não quebre se a lib faltar


st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# ================== Variáveis Globais e Conexão (TESTE) ==================
USERS = {"othavio": "122008", "isabela": "122008"}
LOG_FILE = "acessos.log" 

# MUDANÇA CRÍTICA PARA TESTE: Não tenta conectar. Se o app carregar, o problema é nas credenciais.
conn = None 

# ================== Funções de Leitura (READ - MODO TESTE) ==================
# Função genérica para ler uma aba (sheet)
@st.cache_data(ttl=600) 
def load_data(sheet_name: str) -> pd.DataFrame:
    # MUDANÇA CRÍTICA PARA TESTE: Retorna dados dummy para forçar a renderização
    st.info(f"MODO DE TESTE: Carregando dados fictícios para a aba '{sheet_name}'.")

    if sheet_name == 'clientes':
        return pd.DataFrame({'id': [1, 2], 'nome': ['Cliente Teste A', 'Cliente Teste B']})
    elif sheet_name == 'produtos':
        return pd.DataFrame({
            'cod': [10001, 10002], 
            'nome': ['Produto A', 'Produto B'],
            'preco': [50.00, 25.00],
            'quantidade': [10, 5]
        })
    elif sheet_name == 'vendas':
        return pd.DataFrame({
            'id': [1], 
            'cliente_id': [1], 
            'produto_cod': [10001],
            'quantidade': [1], 
            'data': [datetime.now().isoformat()]
        })
    else:
        return pd.DataFrame()

# ================== Funções de Escrita (WRITE - MODO TESTE) ==================
def get_worksheet(sheet_name: str):
    # MODO TESTE: Não retorna nada que permita escrita
    st.warning("MODO DE TESTE: Operações de escrita desabilitadas.")
    return None

# Funções de Escrita Adaptadas para o Teste
def substituir_estoque_pdf(uploaded_file):
    st.warning("MODO DE TESTE: A substituição de estoque está desabilitada.")
    
def adicionar_produto_manual(cod, nome, preco, qtd=10):
    st.warning(f"MODO DE TESTE: O produto '{nome}' não foi salvo.")

def adicionar_cliente(nome):
    st.warning(f"MODO DE TESTE: O cliente '{nome}' não foi salvo.")

def registrar_venda(cliente_nome, produto_cod, quantidade):
    st.warning(f"MODO DE TESTE: A venda de {quantidade} unidades de {produto_cod} não foi registrada.")


# ================== Funções de Interface (SEM MUDANÇAS) ==================

# ================== Registro de acesso e Session State ==================
def registrar_acesso(usuario: str):
    pass 

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "menu" not in st.session_state:
    st.session_state["menu"] = "Resumo 📊"

def is_visitante():
    u = st.session_state.get("usuario")
    return isinstance(u, str) and u.startswith("visitante-")

# ================== Login ==================
def login():
    st.title("🔐 Login")
    escolha = st.radio("Como deseja entrar?", ["Usuário cadastrado", "Visitante"], horizontal=True)

    if escolha == "Usuário cadastrado":
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                if usuario in USERS and USERS[usuario] == senha:
                    st.session_state["usuario"] = usuario
                    registrar_acesso(f"login-usuario:{usuario}")
                    st.success(f"Bem-vindo(a), {usuario}!")
                    st.experimental_rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    else:
        with st.form("form_visitante"):
            nome = st.text_input("Digite seu nome")
            if st.form_submit_button("Entrar como visitante"):
                if nome.strip():
                    st.session_state["usuario"] = f"visitante-{nome.strip()}"
                    registrar_acesso(f"login-visitante:{nome.strip()}")
                    st.success(f"Bem-vindo(a), visitante {nome.strip()}!")
                    st.experimental_rerun()

# ================== Tela de Resumo ==================
def tela_resumo():
    st.header("📊 Resumo de Vendas (Modo Teste)")
    visitante = is_visitante()
    
    df_vendas = load_data('vendas')
    df_produtos = load_data('produtos')

    if df_vendas.empty or df_produtos.empty:
        total_geral = 0.0
    else:
        # Usamos o merge e cálculo, mesmo em modo de teste, para testar a lógica do app.py
        df_merged = pd.merge(df_vendas, df_produtos[['cod', 'preco']], 
                             left_on='produto_cod', right_on='cod', how='left')
        
        df_merged['total'] = pd.to_numeric(df_merged['quantidade'], errors='coerce') * pd.to_numeric(df_merged['preco'], errors='coerce')
        total_geral = df_merged['total'].sum() or 0.0
    
    comissao = total_geral * 0.25
    if visitante:
        st.metric("💰 Total Geral de Vendas", "R$ *****")
        st.metric("🧾 Comissão (25%)", "R$ *****")
    else:
        st.metric("💰 Total Geral de Vendas", f"R$ {total_geral:.2f}")
        st.metric("🧾 Comissão (25%)", f"R$ {comissao:.2f}")

# ================== Funções de Produtos (CRUD) ==================
def tela_produtos():
    st.header("📦 Produtos (Modo Teste)")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Listar/Buscar", "Adicionar", "Importar PDF"], horizontal=True)

    if acao == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar produtos.")
            return
        cod = st.number_input("Código", min_value=1, step=1)
        nome = st.text_input("Nome do produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.10, format="%.2f")
        quantidade = st.number_input("Quantidade inicial", min_value=0, step=1)
        if st.button("Salvar produto"):
            if not nome.strip():
                st.warning("Informe um nome válido.")
            else:
                adicionar_produto_manual(cod, nome, preco, quantidade)

    elif acao == "Listar/Buscar":
        termo = st.text_input("Buscar por nome ou código").lower()
        st.subheader("Lista de Produtos Fictícios")

        df_produtos = load_data('produtos')

        for row in df_produtos.itertuples(index=False):
            cod, nome, preco, qtd = row.cod, row.nome, row.preco, row.quantidade
            if termo in str(cod) or termo in str(nome).lower() or termo == "":
                preco = pd.to_numeric(preco, errors='coerce') or 0.0
                qtd = pd.to_numeric(qtd, errors='coerce') or 0
                st.write(f"{cod} - {nome} (R$ {preco:.2f}) | Estoque: {int(qtd)}")

    elif acao == "Importar PDF":
        if visitante:
            st.info("🔒 Visitantes não podem importar PDF.")
            return
        pdf_file = st.file_uploader("Selecione o PDF da nota fiscal", type=["pdf"])
        if pdf_file is not None:
            if st.button("Substituir estoque pelo PDF"):
                if pdfplumber:
                    substituir_estoque_pdf(pdf_file)
                else:
                    st.error("A biblioteca 'pdfplumber' não pôde ser carregada.")


# ================== Funções de Clientes (CRUD) ==================
def tela_clientes():
    st.header("👥 Clientes (Modo Teste)")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Listar", "Adicionar"], horizontal=True)

    if acao == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar clientes.")
            return
        nome = st.text_input("Nome do cliente")
        if st.button("Salvar cliente"):
            if nome.strip():
                adicionar_cliente(nome)
            else:
                st.warning("Digite um nome válido.")

    else:
        df_clientes = load_data('clientes')
        df_clientes = df_clientes.sort_values(by='nome')
        
        st.subheader("Lista de Clientes Fictícios")
        for row in df_clientes.itertuples(index=False):
            st.write(f"{row.id} - {row.nome}")

# ================== Funções de Vendas (CRUD) ==================
def tela_vendas():
    st.header("🛒 Vendas (Modo Teste)")
    visitante = is_visitante()
    if visitante:
        st.info("🔒 Visitantes não podem registrar vendas.")
        return

    df_clientes = load_data('clientes')
    clientes = df_clientes['nome'].tolist()
    
    if not clientes:
        st.info("Nenhum cliente cadastrado.")
        return

    cliente_nome = st.selectbox("Cliente", clientes)

    df_produtos = load_data('produtos')
    df_produtos['cod'] = df_produtos['cod'].astype(str)
    
    produto_opcoes = {
        f"{row.nome} (R$ {pd.to_numeric(row.preco, errors='coerce'):.2f}, estoque {int(pd.to_numeric(row.quantidade, errors='coerce'))})": row.cod 
        for row in df_produtos.itertuples(index=False) 
        if pd.to_numeric(row.quantidade, errors='coerce') > 0
    }
    
    if not produto_opcoes:
        st.info("Nenhum produto em estoque.")
        return

    produto_escolhido_str = st.selectbox("Produto", list(produto_opcoes.keys()))
    estoque_disponivel = int(pd.to_numeric(df_produtos[df_produtos['cod'] == str(produto_opcoes[produto_escolhido_str])]['quantidade'].iloc[0], errors='coerce'))
    qtd = st.number_input("Quantidade", min_value=1, max_value=estoque_disponivel, step=1)
    
    if st.button("Registrar Venda"):
        produto_cod = int(produto_opcoes[produto_escolhido_str])
        registrar_venda(cliente_nome, produto_cod, qtd)

# ================== Relatórios ==================
def tela_relatorios():
    st.header("📑 Relatórios (Modo Teste)")

    df_vendas = load_data('vendas')
    df_clientes = load_data('clientes')
    df_produtos = load_data('produtos')
    
    if df_vendas.empty:
        st.info("Nenhuma venda registrada ainda.")
        return
        
    df_relatorio = pd.merge(df_vendas, df_clientes[['id', 'nome']], 
                            left_on='cliente_id', right_on='id', how='left').rename(columns={'nome': 'cliente_nome'})
    df_relatorio = pd.merge(df_relatorio, df_produtos[['cod', 'nome', 'preco']], 
                            left_on='produto_cod', right_on='cod', how='left').rename(columns={'nome': 'produto_nome'})
    
    df_relatorio['total'] = pd.to_numeric(df_relatorio['quantidade'], errors='coerce') * pd.to_numeric(df_relatorio['preco'], errors='coerce')
    df_relatorio = df_relatorio.sort_values(by='data', ascending=False)
    
    st.subheader("Vendas Fictícias:")
    for row in df_relatorio.itertuples(index=False):
        data_str = str(row.data)
        data = data_str[:16] if len(data_str) >= 16 else data_str
        
        cliente = row.cliente_nome
        produto = row.produto_nome
        qtd = int(pd.to_numeric(row.quantidade, errors='coerce') or 0)
        total = row.total or 0.0
        
        st.write(f"🧾 {data} | Cliente: {cliente} | Produto: {produto} | "
                 f"Qtd: {qtd} | Valor: R$ {total:.2f}")

# ================== Navegação e Main ==================
def menu_principal():
    st.sidebar.title("📌 Menu")
    escolha = st.sidebar.radio("Ir para:", 
        ["Resumo 📊", "Produtos 📦", "Clientes 👥", "Vendas 🛒", "Relatórios 📑", "Sair 🚪"])

    st.session_state["menu"] = escolha

    if escolha == "Resumo 📊":
        tela_resumo()
    elif escolha == "Produtos 📦":
        tela_produtos()
    elif escolha == "Clientes 👥":
        tela_clientes()
    elif escolha == "Vendas 🛒":
        tela_vendas()
    elif escolha == "Relatórios 📑":
        tela_relatorios()
    elif escolha == "Sair 🚪":
        st.session_state["usuario"] = None
        st.success("Você saiu do sistema.")
        st.experimental_rerun()

def main():
    if not st.session_state["usuario"]:
        login()
    else:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
        menu_principal()

if __name__ == "__main__":
    main()
