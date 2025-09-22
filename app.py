# ================== PARTE 1 ==================
# Imports e Configuração
import streamlit as st
from datetime import datetime
import json
import os
import io
import pdfplumber
import re

st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# ================== Usuários ==================
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

# ================== Session State ==================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "produtos" not in st.session_state:
    st.session_state["produtos"] = {}
if "clientes" not in st.session_state:
    st.session_state["clientes"] = {
        "Tabata": [],
        "Valquiria": [],
        "Vanessa": [],
        "Pamela": [],
        "Elan": [],
        "Claudinha": [],
    }
if "menu" not in st.session_state:
    st.session_state["menu"] = "Resumo 📊"
if "recarregar" not in st.session_state:
    st.session_state["recarregar"] = False  # flag para simular rerun

# ================== Helpers ==================
def is_visitante():
    return st.session_state["usuario"] and st.session_state["usuario"].startswith("visitante-")

def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "produtos": st.session_state["produtos"],
                "clientes": st.session_state["clientes"],
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Falha ao salvar DB: {e}")

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            prods = {int(k): v for k, v in data.get("produtos", {}).items()}
            clis = {k: v for k, v in data.get("clientes", {}).items()}
            return prods, clis
        except:
            pass
    return {}, st.session_state["clientes"]

# Inicialização DB
st.session_state["produtos"], st.session_state["clientes"] = load_db()
# ================== PARTE 2 ==================
# ================== Login ==================
def login():
    st.title("🔐 Login")
    escolha = st.radio("Como deseja entrar?", ["Usuário cadastrado", "Visitante"], horizontal=True)
    
    if escolha == "Usuário cadastrado":
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if usuario in USERS and USERS[usuario] == senha:
                st.session_state["usuario"] = usuario
                registrar_acesso(f"login-usuario:{usuario}")
                st.success(f"Bem-vindo(a), {usuario}!")
                st.session_state["recarregar"] = not st.session_state["recarregar"]
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        nome = st.text_input("Digite seu nome para entrar como visitante")
        if st.button("Entrar como visitante"):
            if nome.strip():
                st.session_state["usuario"] = f"visitante-{nome.strip()}"
                registrar_acesso(f"login-visitante:{nome.strip()}")
                st.success(f"Bem-vindo(a), visitante {nome.strip()}!")
                st.session_state["recarregar"] = not st.session_state["recarregar"]

# ================== Tela de Resumo ==================
def tela_resumo():
    st.header("📊 Resumo de Vendas")
    visitante = is_visitante()
    total_geral = 0
    for cliente, vendas in st.session_state["clientes"].items():
        total_cliente = sum(v["preco"]*v["quantidade"] for v in vendas)
        total_geral += total_cliente
    
    comissao = total_geral * 0.25
    
    if visitante:
        st.metric("💰 Total Geral de Vendas", "R$ *****")
        st.metric("🧾 Comissão (25%)", "R$ *****")
    else:
        st.metric("💰 Total Geral de Vendas", f"R$ {total_geral:.2f}")
        st.metric("🧾 Comissão (25%)", f"R$ {comissao:.2f}")

# ================== PDF ==================
def tela_pdf():
    st.header("📄 Importar Estoque via Nota Fiscal (PDF)")
    if is_visitante():
        st.info("🔒 Apenas usuários logados podem importar PDF.")
        return
    pdf_file = st.file_uploader("Selecione o PDF da nota fiscal", type=["pdf"])
    if pdf_file is not None:
        if st.button("Substituir estoque pelo PDF"):
            substituir_estoque_pdf(pdf_file)

def substituir_estoque_pdf(uploaded_file):
    data = uploaded_file.read()
    stream = io.BytesIO(data)
    novos_produtos = {}
    linha_regex = re.compile(r'^\s*(\d+)\s+0*(\d{1,6})\s+(.+?)\s+([\d.,]+)\s*$')
    with pdfplumber.open(stream) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for linha in text.splitlines():
                m = linha_regex.match(linha.strip())
                if m:
                    _, cod_s, nome, preco_s = m.groups()
                    cod = int(cod_s)
                    preco = float(preco_s.replace('.', '').replace(',', '.'))
                    novos_produtos[cod] = {"nome": nome.title(), "preco": preco}
    if not novos_produtos:
        st.error("Nenhum produto válido encontrado no PDF.")
        return
    st.session_state["produtos"] = novos_produtos
    save_db()
    st.success("Estoque atualizado a partir do PDF!")

# ================== Produtos ==================
def adicionar_produto_manual(cod, nome, preco):
    cod = int(cod)
    st.session_state["produtos"][cod] = {"nome": nome.strip(), "preco": float(preco)}
    save_db()
    st.success(f"Produto {nome} adicionado/atualizado!")

def tela_produtos():
    st.header("📦 Produtos")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Listar/Buscar", "Adicionar"], horizontal=True)
    
    if acao == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar produtos.")
            return
        cod = st.number_input("Código", min_value=1, step=1, key="cod_produto")
        nome = st.text_input("Nome do produto", key="nome_produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.10, format="%.2f", key="preco_produto")
        if st.button("Salvar produto"):
            if cod in st.session_state["produtos"]:
                st.warning("Código já existe.")
            elif not nome.strip():
                st.warning("Informe um nome válido.")
            else:
                adicionar_produto_manual(cod, nome, preco)
    else:
        termo = st.text_input("Buscar por nome ou código", key="buscar_produto").lower()
        st.subheader("Lista de Produtos")
        for cod, dados in sorted(st.session_state["produtos"].items(), key=lambda x: x[1]["nome"].lower()):
            if termo in str(cod) or termo in dados["nome"].lower() or termo == "":
                st.write(f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f})")
# ================== PARTE 3 ==================
# ==========================
# Parte 3 - Relatórios e Barra Lateral
# ==========================

import streamlit as st
from datetime import datetime
from utils import save_db  # ajusta se seu utils.py estiver em outro local

# ---------------- FUNÇÃO: Relatório ----------------
def tela_relatorio():
    st.header("📊 Relatório de Vendas")

    visitante = st.session_state.get("visitante", False)

    if "clientes" not in st.session_state or not st.session_state["clientes"]:
        st.info("Nenhum cliente cadastrado.")
        return

    total_vendas = 0
    total_comissao = 0

    for cliente, vendas in st.session_state["clientes"].items():
        st.subheader(f"Cliente: {cliente}")

        if not vendas:
            st.write("Nenhuma venda registrada.")
            continue

        for v in vendas:
            nome = v.get("nome", "Produto")
            quantidade = v.get("quantidade", 0)
            valor = v.get("valor", 0.0)
            cod = v.get("cod")

            # Visitante não vê valores
            if visitante:
                valor_exibir = "R$ ???"
            else:
                valor_exibir = f"R$ {valor:.2f}"

            if cod:
                linha_exibir = f"{cod} - {nome} x {quantidade} ({valor_exibir} cada)"
            else:
                linha_exibir = f"{nome} x {quantidade} ({valor_exibir} cada)"

            st.write(linha_exibir)

            if not visitante:
                total_vendas += quantidade * valor

    if not visitante:
        # Comissão progressiva
        if total_vendas < 1000:
            comissao = total_vendas * 0.30
        elif total_vendas < 2000:
            comissao = total_vendas * 0.35
        else:
            comissao = total_vendas * 0.40

        st.subheader(f"💰 Total de Vendas: R$ {total_vendas:.2f}")
        st.subheader(f"🏆 Comissão: R$ {comissao:.2f}")
    else:
        st.subheader("💰 Total de Vendas: R$ ???")
        st.subheader("🏆 Comissão: R$ ???")


# ---------------- FUNÇÃO: Barra Lateral ----------------
def barra_lateral():
    st.sidebar.title("📌 Menu")

    visitante = st.session_state.get("visitante", False)

    opcoes = {
        "Cadastro de Produtos": st.session_state["telas"]["produtos"],
        "Cadastro de Clientes": st.session_state["telas"]["clientes"],
    }

    if not visitante:
        opcoes.update({
            "Registrar Venda": st.session_state["telas"]["vendas"],
            "Relatório": tela_relatorio,
        })
    else:
        opcoes.update({
            "Relatório (Visualização)": tela_relatorio,
        })

    escolha = st.sidebar.radio("Ir para:", list(opcoes.keys()))
    func = opcoes[escolha]
    func()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.session_state["usuario"] = None  # garante volta para login
        st.rerun()  # reroda o app e mostra a tela de login


# ---------------- FUNÇÃO PRINCIPAL ----------------
def main():
    if "usuario" not in st.session_state:
        st.session_state["usuario"] = None

    if st.session_state["usuario"] is None:
        # Chama tela de login
        st.session_state["telas"]["login"]()
    else:
        barra_lateral()