# app.py (COMPLETO E UNIFICADO COM CORREÇÕES DE LOOP E CACHE)
# ================= PARTE 1 - IMPORTAÇÕES E CONFIGURAÇÃO ==================
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import re
from st_gsheets_connection import GSheetsConnection

# Importa pdfplumber de forma segura
try:
    import pdfplumber
except ImportError:
    pdfplumber = None # Garante que o código não quebre se a lib faltar


st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# ================== Variáveis Globais e Conexão ==================
USERS = {"othavio": "122008", "isabela": "122008"}
LOG_FILE = "acessos.log" # Apenas para registro local, se necessário

# O nome "gsheets" deve bater com o [gsheets] no secrets.toml
# Se o app travar aqui com o erro 1ST, é problema de secrets.toml/permissão
conn = st.connection("gsheets", type=GSheetsConnection) 

# ================== Funções de Leitura (READ - Usando Caching) ==================
# Função genérica para ler uma aba (sheet)
@st.cache_data(ttl=600) # Mantém os dados em cache por 10 minutos
def load_data(sheet_name: str) -> pd.DataFrame:
    try:
        # CORREÇÃO CRÍTICA: Removido o ttl=0. O @st.cache_data(ttl=600) é quem controla o tempo.
        df = conn.read(worksheet=sheet_name) 
        df = df.dropna(how='all')
        
        # Garante que o ID e cod são numéricos para joins e buscas
        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        if sheet_name == 'produtos':
             if 'cod' in df.columns:
                df['cod'] = pd.to_numeric(df['cod'], errors='coerce').fillna(0).astype(int)
        if sheet_name == 'vendas':
            if 'cliente_id' in df.columns:
                df['cliente_id'] = pd.to_numeric(df['cliente_id'], errors='coerce').fillna(0).astype(int)
            if 'produto_cod' in df.columns:
                df['produto_cod'] = pd.to_numeric(df['produto_cod'], errors='coerce').fillna(0).astype(int)

        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da aba '{sheet_name}'. Verifique o nome da aba e a configuração de segredos. Erro: {e}")
        return pd.DataFrame()

# ================== Funções de Escrita (WRITE) ==================
def get_worksheet(sheet_name: str):
    try:
        # Acessa a interface do gspread autenticado
        gc = conn.client
        # Usa o URL do secrets.toml (st.secrets.gsheets.spreadsheet_url)
        sheet = gc.open_by_url(st.secrets.gsheets.spreadsheet_url) 
        return sheet.worksheet(sheet_name)
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha para escrita: {e}. Verifique as permissões.")
        return None

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
                    # CORREÇÃO: Usando experimental_rerun para maior estabilidade
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
                    # CORREÇÃO: Usando experimental_rerun para maior estabilidade
                    st.experimental_rerun()

# ================== Tela de Resumo ==================
def tela_resumo():
    st.header("📊 Resumo de Vendas")
    visitante = is_visitante()
    
    df_vendas = load_data('vendas')
    df_produtos = load_data('produtos')

    if df_vendas.empty or df_produtos.empty:
        total_geral = 0.0
    else:
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
def substituir_estoque_pdf(uploaded_file):
    if not pdfplumber:
        st.error("O processamento de PDF não está disponível. Verifique as dependências.")
        return

    data = uploaded_file.read()
    stream = io.BytesIO(data)
    novos_produtos = []
    # Expressão para extrair: QTD (dígitos), COD (5 dígitos), NOME (qualquer coisa), PREÇO (dígitos com ponto/vírgula)
    linha_regex = re.compile(r'^\s*(\d+)\s+(\d{5})\s+(.+?)\s+([\d.,]+)\s*$') 

    try:
        with pdfplumber.open(stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                for linha in text.splitlines():
                    m = linha_regex.match(linha.strip())
                    if m:
                        qtd_s, cod_s, nome, preco_s = m.groups()
                        cod = int(cod_s) if cod_s else None
                        qtd = int(qtd_s) if qtd_s else 0
                        # Converte o preço para o formato correto (R$ 1.000,00 -> 1000.00)
                        preco = float(preco_s.replace('.', '').replace(',', '.')) if preco_s else 0.0
                        if cod is not None:
                             novos_produtos.append([cod, nome.title(), preco, qtd])
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
        return

    if not novos_produtos:
        st.error("Nenhum produto válido encontrado no PDF.")
        return

    ws = get_worksheet('produtos')
    if ws:
        # Apaga tudo e reescreve o cabeçalho
        ws.clear()
        ws.append_row(['cod', 'nome', 'preco', 'quantidade'])
        # Adiciona os novos produtos
        ws.append_rows(novos_produtos)
        load_data.clear() 
        st.success("✅ Estoque atualizado a partir do PDF!")

def adicionar_produto_manual(cod, nome, preco, qtd=10):
    ws = get_worksheet('produtos')
    if ws:
        df_produtos = load_data('produtos')
        
        # Verifica se o produto existe
        if cod in df_produtos['cod'].values:
            idx = df_produtos[df_produtos['cod'] == cod].index[0]
            # Sheets é 1-based, e a linha 1 é o cabeçalho, então índice é +2
            ws.update_cell(idx + 2, 2, nome.strip())
            ws.update_cell(idx + 2, 3, float(preco))
            ws.update_cell(idx + 2, 4, int(qtd))
        else:
            ws.append_row([int(cod), nome.strip(), float(preco), int(qtd)])
            
        load_data.clear() 
        st.success(f"Produto {nome} adicionado/atualizado!")

def tela_produtos():
    st.header("📦 Produtos")
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
        st.subheader("Lista de Produtos")

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
                # Verifica se a biblioteca foi instalada corretamente
                if pdfplumber:
                    substituir_estoque_pdf(pdf_file)
                else:
                    st.error("A biblioteca 'pdfplumber' não pôde ser carregada. Verifique as dependências (packages.txt e requirements.txt).")


# ================== Funções de Clientes (CRUD) ==================
def adicionar_cliente(nome):
    ws = get_worksheet('clientes')
    df_clientes = load_data('clientes')
    
    if ws:
        if nome.strip() in df_clientes['nome'].values:
             st.info(f"Cliente {nome} já existe.")
             return
             
        novo_id = df_clientes['id'].max() + 1 if not df_clientes.empty and 'id' in df_clientes.columns else 1
        
        ws.append_row([novo_id, nome.strip()])
        load_data.clear()
        st.success(f"Cliente {nome} adicionado!")

def tela_clientes():
    st.header("👥 Clientes")
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
        
        st.subheader("Lista de Clientes")
        for row in df_clientes.itertuples(index=False):
            st.write(f"{row.id} - {row.nome}")

# ================== Funções de Vendas (CRUD) ==================
def registrar_venda(cliente_nome, produto_cod, quantidade):
    ws_vendas = get_worksheet('vendas')
    ws_produtos = get_worksheet('produtos')
    
    if not ws_vendas or not ws_produtos:
        st.error("Erro de conexão com uma das abas (vendas/produtos).")
        return

    df_clientes = load_data('clientes')
    if cliente_nome not in df_clientes['nome'].values:
        st.error("Cliente não encontrado.")
        return
        
    cliente_id = df_clientes[df_clientes['nome'] == cliente_nome]['id'].iloc[0]

    df_produtos = load_data('produtos')
    produto_cod = pd.to_numeric(produto_cod, errors='coerce')
    quantidade = int(quantidade)
    
    produto_row = df_produtos[df_produtos['cod'] == produto_cod]

    if produto_row.empty:
        st.error("Produto não encontrado.")
        return
        
    estoque_atual = pd.to_numeric(produto_row['quantidade'].iloc[0], errors='coerce') or 0

    if quantidade > estoque_atual:
        st.error(f"Quantidade maior que estoque disponível ({estoque_atual}).")
        return

    # 1. Lança venda
    df_vendas = load_data('vendas')
    novo_id_venda = df_vendas['id'].max() + 1 if not df_vendas.empty and 'id' in df_vendas.columns else 1

    ws_vendas.append_row([
        novo_id_venda, 
        cliente_id, 
        produto_cod, 
        quantidade, 
        datetime.now().isoformat()
    ])

    # 2. Atualiza estoque no Sheets
    # O index do Pandas (0-based) precisa ser ajustado para a linha do Sheets (1-based + 1 linha de cabeçalho)
    row_idx_to_update = produto_row.index[0] + 2 
    novo_estoque = estoque_atual - quantidade
    
    # Coluna 4 = 'quantidade'
    ws_produtos.update_cell(row_idx_to_update, 4, int(novo_estoque))

    load_data.clear() # Limpa cache de ambas as abas após a escrita
    st.success("✅ Venda registrada!")

def tela_vendas():
    st.header("🛒 Vendas")
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
    # Pre-seleciona a quantidade máxima disponível, mas permite ajuste
    estoque_disponivel = int(pd.to_numeric(df_produtos[df_produtos['cod'] == str(produto_opcoes[produto_escolhido_str])]['quantidade'].iloc[0], errors='coerce'))
    qtd = st.number_input("Quantidade", min_value=1, max_value=estoque_disponivel, step=1)
    
    if st.button("Registrar Venda"):
        produto_cod = int(produto_opcoes[produto_escolhido_str])
        registrar_venda(cliente_nome, produto_cod, qtd)

# ================== Relatórios ==================
def tela_relatorios():
    st.header("📑 Relatórios")

    df_vendas = load_data('vendas')
    df_clientes = load_data('clientes')
    df_produtos = load_data('produtos')
    
    if df_vendas.empty:
        st.info("Nenhuma venda registrada ainda.")
        return
        
    # Junções (MERGE) para montar o relatório
    df_relatorio = pd.merge(df_vendas, df_clientes[['id', 'nome']], 
                            left_on='cliente_id', right_on='id', how='left').rename(columns={'nome': 'cliente_nome'})
    df_relatorio = pd.merge(df_relatorio, df_produtos[['cod', 'nome', 'preco']], 
                            left_on='produto_cod', right_on='cod', how='left').rename(columns={'nome': 'produto_nome'})
    
    df_relatorio['total'] = pd.to_numeric(df_relatorio['quantidade'], errors='coerce') * pd.to_numeric(df_relatorio['preco'], errors='coerce')
    df_relatorio = df_relatorio.sort_values(by='data', ascending=False)
    
    for row in df_relatorio.itertuples(index=False):
        # Garante que a data é tratada como string e evita erros de formatação
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
        # CORREÇÃO: Usando experimental_rerun para maior estabilidade
        st.experimental_rerun()

def main():
    if not st.session_state["usuario"]:
        login()
    else:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
        menu_principal()

if __name__ == "__main__":
    main()
