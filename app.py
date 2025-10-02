# ================= PARTE 1 =================
# =================================================================
# CONFIGURAÇÕES (AJUSTE NOME DA PLANILHA)
# =================================================================
PLANILHA_NOME = "Sistema de vendas"
ABA_VENDAS = "Vendas"
ABA_CLIENTES = "Clientes"
ABA_PRODUTOS = "Produtos"

# =================================================================
# BIBLIOTECAS
# =================================================================
import streamlit as st
import gspread
from gspread.exceptions import WorksheetNotFound, SpreadsheetNotFound
import json
from datetime import datetime
import os
import io
import re

# PDF opcional
try:
    import pdfplumber
except Exception:
    pdfplumber = None

st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# ================== Usuários (login) ==================
USERS = {"othavio": "122008", "isabela": "122008"}
LOG_FILE = "acessos.log"
DB_FILE = "db.json"

# ================== Conexão com Google Sheets ==================
GSHEETS_CONECTADO = False
gc = None

def connect_gsheet():
    global gc, GSHEETS_CONECTADO
    try:
        json_string = st.secrets.get("GCP_SA_CREDENTIALS")
        credentials_dict = json.loads(json_string)
        gc = gspread.service_account_from_dict(credentials_dict)
        GSHEETS_CONECTADO = True
    except Exception as e:
        GSHEETS_CONECTADO = False
        st.error(f"❌ ERRO FATAL AO CONECTAR: {type(e).__name__} - {e}")
        st.info("Verifique se o JSON está colado corretamente e se a Conta de Serviço tem permissão de Editor na planilha.")

connect_gsheet()

# ================== Registro de acesso ==================
def registrar_acesso(usuario: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {usuario}\n")
    except:
        pass

# ================== Funções Google Sheets ==================
def gsheets_append_venda(cliente: str, produto: str, quantidade: int, preco: float):
    if not GSHEETS_CONECTADO:
        return
    global gc
    try:
        data_registro = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha = gc.open(PLANILHA_NOME)
        aba = planilha.worksheet(ABA_VENDAS)
        nova_linha = [
            data_registro,
            cliente,
            produto,
            quantidade,
            f"{preco:.2f}".replace('.', ','),
            f"{(preco * quantidade):.2f}".replace('.', ',')
        ]
        aba.append_row(nova_linha, value_input_option='USER_ENTERED')
        st.toast("✅ Venda salva no Google Sheets!", icon='sheets')
    except Exception as e:
        st.warning(f"Falha ao salvar a venda no Google Sheets: {e}")
# ================= PARTE 2 =================
def gsheets_delete_venda(cliente: str, produto: str, valor: float):
    if GSHEETS_CONECTADO:
        st.warning("⚠️ Exclusão/edição foi feita apenas localmente. No Google Sheets precisa remover manualmente.")

def gsheets_adicionar_cliente(nome: str):
    if not GSHEETS_CONECTADO:
        return
    global gc
    try:
        planilha = gc.open(PLANILHA_NOME)
        aba = planilha.worksheet(ABA_CLIENTES)
        aba.append_row([nome], value_input_option='USER_ENTERED')
        st.toast("✅ Cliente salvo no Google Sheets!", icon='sheets')
    except Exception as e:
        st.warning(f"Falha ao salvar cliente no Google Sheets: {e}")

def gsheets_deletar_cliente(nome: str):
    if GSHEETS_CONECTADO:
        st.warning(f"⚠️ Cliente '{nome}' removido do sistema local. Remova manualmente do Google Sheets.")

# ================== Helpers: salvar/carregar DB local ==================
def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "produtos": st.session_state.get("produtos", {}),
                "clientes": st.session_state.get("clientes", {}),
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Falha ao salvar DB local: {e}")

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            prods = {int(k): v for k, v in data.get("produtos", {}).items()}
            clis = {k: v for k, v in data.get("clientes", {}).items()}
            return prods, clis
        except Exception:
            pass
    # clientes padrão
    default_clients = {"Tabata": [], "Valquiria": [], "Vanessa": [], "Pamela": [], "Elan": [], "Claudinha": []}
    return {}, default_clients

# ================== Session State inicial ==================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "produtos" not in st.session_state or not st.session_state["produtos"]:
    prods_loaded, clients_loaded = load_db()
    st.session_state["produtos"] = prods_loaded or {}
    st.session_state["clientes"] = clients_loaded or {
        "Tabata": [], "Valquiria": [], "Vanessa": [], "Pamela": [], "Elan": [], "Claudinha": []
    }
if "menu" not in st.session_state:
    st.session_state["menu"] = "Resumo 📊"

# ================== Função: is_visitante ==================
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
# ================= PARTE 3 =================
# ================== Tela de Resumo ==================
def tela_resumo():
    st.header("📊 Resumo de Vendas")
    visitante = is_visitante()
    total_geral = 0.0
    for cliente, vendas in st.session_state["clientes"].items():
        total_cliente = sum((v.get("preco", 0.0) * v.get("quantidade", 0)) for v in vendas)
        total_geral += total_cliente
    comissao = total_geral * 0.25
    if visitante:
        st.metric("💰 Total Geral de Vendas", "R$ *****")
        st.metric("🧾 Comissão (25%)", "R$ *****")
    else:
        st.metric("💰 Total Geral de Vendas", f"R$ {total_geral:.2f}")
        st.metric("🧾 Comissão (25%)", f"R$ {comissao:.2f}")

# ================== PDF (Importar Estoque) ==================
def substituir_estoque_pdf(uploaded_file):
    data = uploaded_file.read()
    stream = io.BytesIO(data)
    novos_produtos = {}

    linha_regex = re.compile(r'^\s*(\d+)\s+(\d{5})\s+(.+?)\s+([\d.,]+)\s*$')

    try:
        with pdfplumber.open(stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                for linha in text.splitlines():
                    m = linha_regex.match(linha.strip())
                    if m:
                        qtd_s, cod_s, nome, preco_s = m.groups()
                        try:
                            qtd = int(qtd_s)
                        except:
                            qtd = 0
                        try:
                            cod = int(cod_s)
                        except:
                            cod = None
                        try:
                            preco = float(preco_s.replace('.', '').replace(',', '.'))
                        except:
                            preco = 0.0
                        if cod is not None:
                            novos_produtos[cod] = {
                                "nome": nome.title(),
                                "preco": preco,
                                "quantidade": qtd
                            }
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
        return

    if not novos_produtos:
        st.error("Nenhum produto válido encontrado no PDF.")
        return
    st.session_state["produtos"] = novos_produtos
    save_db()
    st.success("✅ Estoque atualizado a partir do PDF!")

# ================== Produtos ==================
def adicionar_produto_manual(cod, nome, preco, qtd=10):
    cod = int(cod)
    st.session_state["produtos"][cod] = {
        "nome": nome.strip(),
        "preco": float(preco),
        "quantidade": qtd
    }
    save_db()
    gsheets_append_venda("Sistema", nome, qtd, preco)  # salva no Google Sheets
    st.success(f"Produto {nome} adicionado/atualizado!")

def tela_produtos():
    st.header("📦 Produtos")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Adicionar", "Listar/Buscar", "Importar PDF"], horizontal=True)

    if acao == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar produtos.")
            return
        cod = st.number_input("Código", min_value=1, step=1)
        nome = st.text_input("Nome do produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.10, format="%.2f")
        quantidade = st.number_input("Quantidade inicial", min_value=0, step=1)
        if st.button("Salvar produto"):
            if cod in st.session_state["produtos"]:
                st.warning("Código já existe.")
            elif not nome.strip():
                st.warning("Informe um nome válido.")
            else:
                adicionar_produto_manual(cod, nome, preco, quantidade)

    elif acao == "Listar/Buscar":
        termo = st.text_input("Buscar por nome ou código").lower()
        st.subheader("Lista de Produtos")
        for cod, dados in sorted(st.session_state["produtos"].items(), key=lambda x: str(x)):
            if termo in str(cod) or termo in dados["nome"].lower() or termo == "":
                st.write(f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f}) | Estoque: {dados.get('quantidade', 0)}")

    elif acao == "Importar PDF":
        if visitante:
            st.info("🔒 Visitantes não podem importar PDF.")
            return
        pdf_file = st.file_uploader("Selecione o PDF da nota fiscal", type=["pdf"])
        if pdf_file is not None:
            if st.button("Substituir estoque pelo PDF"):
                substituir_estoque_pdf(pdf_file)

# ================== Clientes ==================
def tela_clientes():
    st.header("👥 Clientes")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Adicionar", "Listar"], horizontal=True)

    if acao == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar clientes.")
            return
        nome = st.text_input("Nome do cliente")
        if st.button("Salvar cliente"):
            if not nome.strip():
                st.warning("Informe um nome válido.")
            elif nome in st.session_state["clientes"]:
                st.warning("Cliente já existe.")
            else:
                st.session_state["clientes"][nome] = []
                save_db()
                gsheets_adicionar_cliente(nome)
                st.success(f"Cliente {nome} adicionado!")

    elif acao == "Listar":
        st.subheader("Lista de Clientes")
        for cliente in sorted(st.session_state["clientes"].keys()):
            st.write(cliente)

# ================== Vendas ==================
def registrar_venda(cliente, codigo, quantidade):
    produtos = st.session_state["produtos"]
    if codigo not in produtos:
        st.error("Produto não encontrado.")
        return
    if produtos[codigo].get("quantidade", 0) < quantidade:
        st.error("Estoque insuficiente.")
        return
    produtos[codigo]["quantidade"] -= quantidade
    venda = {
        "codigo": codigo,
        "nome": produtos[codigo]["nome"],
        "preco": produtos[codigo]["preco"],
        "quantidade": quantidade,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    st.session_state["clientes"][cliente].append(venda)
    save_db()
    gsheets_append_venda(cliente, produtos[codigo]["nome"], quantidade, produtos[codigo]["preco"])
    st.success("Venda registrada!")

def tela_vendas():
    st.header("🛒 Vendas")
    if not st.session_state["clientes"]:
        st.warning("Cadastre um cliente primeiro.")
        return
    if not st.session_state["produtos"]:
        st.warning("Cadastre produtos primeiro.")
        return

    cliente = st.selectbox("Selecione o cliente", list(st.session_state["clientes"].keys()))
    codigos_disponiveis = list(st.session_state["produtos"].keys())
    codigo = st.selectbox("Código do produto", codigos_disponiveis, format_func=lambda x: f"{x} - {st.session_state['produtos'][x]['nome']}")
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    if st.button("Registrar venda"):
        registrar_venda(cliente, codigo, quantidade)

    st.subheader("📋 Histórico de Vendas")
    for cliente, vendas in st.session_state["clientes"].items():
        if vendas:
            st.write(f"### {cliente}")
            for v in vendas:
                st.write(f"- {v['data']} | {v['nome']} (x{v['quantidade']}) - R$ {v['preco']:.2f}")

# ================== Relatórios ==================
def tela_relatorios():
    st.header("📑 Relatórios")
    visitante = is_visitante()
    for cliente, vendas in st.session_state["clientes"].items():
        if vendas:
            total = sum(v["preco"] * v["quantidade"] for v in vendas)
            if visitante:
                st.write(f"Cliente: {cliente} — Total: R$ *****")
            else:
                st.write(f"Cliente: {cliente} — Total: R$ {total:.2f}")

# ================== Menu Superior ==================
def menu():
    st.title("📌 Menu do Sistema")
    opcoes = ["Resumo", "Produtos", "Clientes", "Vendas", "Relatórios", "Sair"]
    escolha = st.selectbox("Selecione a seção", opcoes, index=0, key="menu_superior")
    if escolha == "Resumo":
        tela_resumo()
    elif escolha == "Produtos":
        tela_produtos()
    elif escolha == "Clientes":
        tela_clientes()
    elif escolha == "Vendas":
        tela_vendas()
    elif escolha == "Relatórios":
        tela_relatorios()
    elif escolha == "Sair":
        if st.button("Confirmar saída"):
            st.session_state.clear()
            st.experimental_rerun()

# ================== Main ==================
def main():
    if "usuario" not in st.session_state or not st.session_state["usuario"]:
        login()
    else:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
        menu()

if __name__ == "__main__":
    main()