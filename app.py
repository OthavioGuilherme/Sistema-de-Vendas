# ================== PARTE 1 ==================
# Imports e Configuração
import streamlit as st
from datetime import datetime
import json
import os
import io
import re

# Se você usa importação de PDF, deixe a linha abaixo (requer pdfplumber instalado)
try:
    import pdfplumber
except Exception:
    pdfplumber = None

st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# ================== Usuários (login) ==================
# ====================
# PARTE 1 - LOGIN
# ====================

import streamlit as st
from parte3 import main  # importa a parte 3

def tela_login():
    st.title("🔑 Sistema de Vendas - Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == "admin" and senha == "123":
            st.session_state["usuario"] = usuario
            st.success("Login realizado com sucesso!")
            st.rerun()  # força recarregar e ir pra parte 3
        elif usuario == "visitante" and senha == "visitante":
            st.session_state["usuario"] = "visitante"
            st.success("Login como visitante realizado!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos!")

def main_login():
    if "usuario" not in st.session_state or st.session_state["usuario"] is None:
        tela_login()
    else:
        main()  # chama a parte 3

main_login()
USERS = {"othavio": "122008", "isabela": "122008"}  # usuários e senhas em texto (simples)
LOG_FILE = "acessos.log"
DB_FILE = "db.json"

# ================== Registro de acesso ==================
def registrar_acesso(usuario: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {usuario}\n")
    except:
        pass

# ================== Helpers: salvar/carregar DB ==================
def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "produtos": st.session_state.get("produtos", {}),
                "clientes": st.session_state.get("clientes", {}),
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Falha ao salvar DB: {e}")

def load_db():
    # retorna (produtos_dict, clientes_dict)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            prods = {}
            for k, v in data.get("produtos", {}).items():
                try:
                    prods[int(k)] = v
                except:
                    prods[k] = v
            clis = {k: v for k, v in data.get("clientes", {}).items()}
            return prods, clis
        except Exception:
            pass
    # default (se não existir DB)
    default_clients = {
        "Tabata": [],
        "Valquiria": [],
        "Vanessa": [],
        "Pamela": [],
        "Elan": [],
        "Claudinha": [],
    }
    return {}, default_clients

# ================== Session State inicial ==================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "produtos" not in st.session_state or not st.session_state["produtos"]:
    prods_loaded, clients_loaded = load_db()
    # se DB vazio, load_db já retornou defaults
    st.session_state["produtos"] = prods_loaded or {}
    st.session_state["clientes"] = clients_loaded or {
        "Tabata": [], "Valquiria": [], "Vanessa": [], "Pamela": [], "Elan": [], "Claudinha": []
    }
if "menu" not in st.session_state:
    st.session_state["menu"] = "Resumo 📊"
# flag auxiliar (não necessária, mas mantida para compatibilidade)
if "recarregar" not in st.session_state:
    st.session_state["recarregar"] = False

# ================== Função: is_visitante ==================
def is_visitante():
    u = st.session_state.get("usuario")
    return isinstance(u, str) and u.startswith("visitante-")

# ================== PARTE 2 ==================
# ================== Login ==================
def login():
    st.title("🔐 Login")
    escolha = st.radio("Como deseja entrar?", ["Usuário cadastrado", "Visitante"], horizontal=True)

    if escolha == "Usuário cadastrado":
        usuario = st.text_input("Usuário", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar"):
            if usuario in USERS and USERS[usuario] == senha:
                st.session_state["usuario"] = usuario
                registrar_acesso(f"login-usuario:{usuario}")
                st.success(f"Bem-vindo(a), {usuario}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        nome = st.text_input("Digite seu nome para entrar como visitante", key="login_visitante")
        if st.button("Entrar como visitante"):
            if nome.strip():
                st.session_state["usuario"] = f"visitante-{nome.strip()}"
                registrar_acesso(f"login-visitante:{nome.strip()}")
                st.success(f"Bem-vindo(a), visitante {nome.strip()}!")
                st.rerun()

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

# ================== PDF (opcional) ==================
def tela_pdf():
    st.header("📄 Importar Estoque via Nota Fiscal (PDF)")
    if is_visitante():
        st.info("🔒 Apenas usuários logados podem importar PDF.")
        return
    if pdfplumber is None:
        st.warning("A biblioteca pdfplumber não está disponível no ambiente.")
        return
    pdf_file = st.file_uploader("Selecione o PDF da nota fiscal", type=["pdf"])
    if pdf_file is not None:
        if st.button("Substituir estoque pelo PDF"):
            substituir_estoque_pdf(pdf_file)

def substituir_estoque_pdf(uploaded_file):
    data = uploaded_file.read()
    stream = io.BytesIO(data)
    novos_produtos = {}
    # Regex adaptável (depende do layout do PDF)
    linha_regex = re.compile(r'^\s*(\d+)\s+0*(\d{1,6})\s+(.+?)\s+([\d.,]+)\s*$')
    try:
        with pdfplumber.open(stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                for linha in text.splitlines():
                    m = linha_regex.match(linha.strip())
                    if m:
                        _, cod_s, nome, preco_s = m.groups()
                        try:
                            cod = int(cod_s)
                        except:
                            cod = int(cod_s) if cod_s.isdigit() else None
                        try:
                            preco = float(preco_s.replace('.', '').replace(',', '.'))
                        except:
                            preco = 0.0
                        if cod is not None:
                            novos_produtos[cod] = {"nome": nome.title(), "preco": preco}
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
        return

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
        for cod, dados in sorted(st.session_state["produtos"].items(), key=lambda x: str(x[0])):
            if termo in str(cod) or termo in dados["nome"].lower() or termo == "":
                st.write(f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f})")

# ================== PARTE 3 ==================
# ====================
# PARTE 3 - NAVEGAÇÃO E RELATÓRIOS
# ====================

import streamlit as st

# Função para tela de clientes
def tela_clientes():
    st.header("👫 Clientes")
    if "clientes" not in st.session_state:
        st.session_state["clientes"] = {}

    with st.form("form_cliente"):
        nome = st.text_input("Nome do Cliente")
        if st.form_submit_button("Cadastrar"):
            if nome:
                st.session_state["clientes"][nome] = []
                st.success(f"Cliente {nome} cadastrado com sucesso!")

    st.subheader("Lista de Clientes")
    for cliente in list(st.session_state["clientes"].keys()):
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(cliente)
        with col2:
            if st.button(f"Apagar {cliente}"):
                del st.session_state["clientes"][cliente]
                st.success(f"Cliente {cliente} removido!")
                st.rerun()

# Função para tela de produtos
def tela_produtos():
    st.header("📦 Produtos")
    st.info("Aqui entra o cadastro de produtos (já feito na Parte 2).")

# Função para tela de vendas
def tela_vendas():
    st.header("💰 Vendas")
    if st.session_state.get("usuario") == "visitante":
        st.warning("Visitante não pode registrar vendas.")
        return

    st.info("Aqui entra a tela de vendas (já feita na Parte 2).")

# Função para tela de relatórios
def tela_relatorios():
    st.header("📊 Relatórios")

    if st.session_state.get("usuario") == "visitante":
        st.warning("Visitante não pode ver os valores de vendas e comissão.")
        if "clientes" in st.session_state:
            for cliente, vendas in st.session_state["clientes"].items():
                st.write(f"Cliente: {cliente}")
                for v in vendas:
                    st.write(f"- {v['nome']} x {v['quantidade']} (??? cada)")
        return

    st.info("Aqui entra a tela de relatórios (já feita na Parte 2).")

# Menu no topo
def menu_topo():
    st.markdown("## 🛒 Sistema de Vendas")

    escolha = st.radio(
        "Navegação:",
        ["Clientes 👫", "Produtos 📦", "Vendas 💰", "Relatórios 📊", "Sair 🚪"],
        horizontal=True
    )

    if escolha == "Clientes 👫":
        tela_clientes()
    elif escolha == "Produtos 📦":
        tela_produtos()
    elif escolha == "Vendas 💰":
        tela_vendas()
    elif escolha == "Relatórios 📊":
        tela_relatorios()
    elif escolha == "Sair 🚪":
        st.session_state.clear()
        st.session_state["usuario"] = None
        st.rerun()

# Função principal
def main():
    if "usuario" not in st.session_state or st.session_state["usuario"] is None:
        st.warning("⚠️ Você precisa fazer login para acessar o sistema.")
    else:
        menu_topo()

main()