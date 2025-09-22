# ==========================
# Parte 1 - Configuração, Banco e Utilitários (com lembrar login)
# ==========================

import streamlit as st
from datetime import datetime
import json
import os
from PIL import Image
import pytesseract

# =============== Config página ===============
st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# =============== Arquivos ===============
LOG_FILE = "acessos.log"
DB_FILE = "db.json"
LOGIN_FILE = "login_salvo.json"  # arquivo para salvar login

# =============== Usuários ==================
USERS = {
    "othavio": "122008",
    "isabela": "122008",
}

# ================= Funções =================
def registrar_acesso(label: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {label}\n")
    except Exception:
        pass

def is_visitante():
    return bool(st.session_state.get("usuario")) and str(st.session_state.get("usuario")).startswith("visitante-")

# ================= Persistência JSON =================
def save_db():
    try:
        data = {
            "produtos": st.session_state.produtos,
            "clientes": st.session_state.clientes,
            "vendas": st.session_state.vendas,
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.toast(f"Falha ao salvar: {e}", icon="⚠️")

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            prods = {int(k): v for k, v in data.get("produtos", {}).items()}
            clis = {k: v for k, v in data.get("clientes", {}).items()}
            vendas = data.get("vendas", [])
            return prods, clis, vendas
        except Exception:
            pass
    return {}, {}, []

def save_login(usuario):
    try:
        with open(LOGIN_FILE, "w", encoding="utf-8") as f:
            json.dump({"usuario": usuario}, f)
    except:
        pass

def load_login():
    if os.path.exists(LOGIN_FILE):
        try:
            with open(LOGIN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("usuario", "")
        except:
            return ""
    return ""

# =============== Session state inicial =================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "produtos" not in st.session_state or "clientes" not in st.session_state or "vendas" not in st.session_state:
    p, c, v = load_db()
    st.session_state.produtos = p
    st.session_state.clientes = c
    st.session_state.vendas = v

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "filtro_cliente" not in st.session_state:
    st.session_state.filtro_cliente = ""
if "menu" not in st.session_state:
    st.session_state.menu = "Resumo"

# ================= Helpers =================
def total_cliente(nome: str) -> float:
    vendas = st.session_state.clientes.get(nome, [])
    return sum(v["preco"] * v["quantidade"] for v in vendas)

def total_geral() -> float:
    return sum(total_cliente(c) for c in st.session_state.clientes.keys())

# ================= Login =================
def tela_login():
    st.title("🔑 Login")

    usuario_salvo = load_login()

    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuário", value=usuario_salvo, key="usuario_input")
        senha = st.text_input("Senha", type="password", key="senha_input")
        lembrar = st.checkbox("Lembrar meu login")

        if st.button("Entrar"):
            if usuario.strip() in USERS and senha.strip() == USERS[usuario.strip()]:
                st.session_state.usuario = usuario.strip()
                st.session_state.logado = True
                registrar_acesso(f"Login - {usuario}")
                if lembrar:
                    save_login(usuario.strip())
                st.success(f"Bem-vindo {usuario}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos")

    with col2:
        st.write("Ou entre como visitante")
        if st.button("Entrar como visitante"):
            st.session_state.usuario = f"visitante-{int(datetime.now().timestamp())}"
            st.session_state.logado = True
            st.info("Você entrou como visitante (apenas leitura)")
            st.experimental_rerun()
# ========================== 
# ===============================
# ==================== PARTE 2 - CADASTRO E VENDAS ====================

import streamlit as st
from datetime import datetime

# ---------------- FUNÇÃO: Tela de Produtos ----------------
def tela_produtos():
    st.header("📦 Cadastro de Produtos")

    if "produtos" not in st.session_state:
        st.session_state.produtos = {}

    with st.form("form_produto"):
        codigo = st.text_input("Código do Produto")
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Salvar Produto")

        if submitted:
            if codigo and nome and preco > 0:
                st.session_state.produtos[codigo] = {
                    "nome": nome,
                    "preco": preco
                }
                st.success(f"✅ Produto {nome} cadastrado!")
            else:
                st.error("⚠️ Preencha todos os campos.")

    if st.session_state.produtos:
        st.subheader("📋 Produtos cadastrados")
        for codigo, dados in st.session_state.produtos.items():
            st.write(f"**{codigo}** - {dados['nome']} - R$ {dados['preco']:.2f}")


# ---------------- FUNÇÃO: Tela de Clientes ----------------
def tela_clientes():
    st.header("👥 Cadastro de Clientes")

    if "clientes" not in st.session_state:
        st.session_state.clientes = {}

    with st.form("form_cliente"):
        cpf = st.text_input("CPF do Cliente")
        nome = st.text_input("Nome do Cliente")
        telefone = st.text_input("Telefone")
        submitted = st.form_submit_button("Salvar Cliente")

        if submitted:
            if cpf and nome:
                st.session_state.clientes[cpf] = {
                    "nome": nome,
                    "telefone": telefone
                }
                st.success(f"✅ Cliente {nome} cadastrado!")
            else:
                st.error("⚠️ Informe pelo menos CPF e Nome.")

    if st.session_state.clientes:
        st.subheader("📋 Clientes cadastrados")
        for cpf, dados in st.session_state.clientes.items():
            st.write(f"**{cpf}** - {dados['nome']} - {dados['telefone']}")


# ---------------- FUNÇÃO: Tela de Vendas ----------------
def tela_vendas():
    st.header("🛒 Registrar Vendas")

    if "vendas" not in st.session_state:
        st.session_state.vendas = []

    if "produtos" not in st.session_state or not st.session_state.produtos:
        st.warning("⚠️ Cadastre produtos antes de registrar uma venda.")
        return

    if "clientes" not in st.session_state or not st.session_state.clientes:
        st.warning("⚠️ Cadastre clientes antes de registrar uma venda.")
        return

    with st.form("form_venda"):
        cpf_cliente = st.selectbox("Selecione o Cliente", list(st.session_state.clientes.keys()))
        codigo_produto = st.selectbox("Selecione o Produto", list(st.session_state.produtos.keys()))
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        submitted = st.form_submit_button("Registrar Venda")

        if submitted:
            produto = st.session_state.produtos[codigo_produto]
            cliente = st.session_state.clientes[cpf_cliente]
            total = produto["preco"] * quantidade
            venda = {
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "cliente": cliente["nome"],
                "produto": produto["nome"],
                "quantidade": quantidade,
                "total": total
            }
            st.session_state.vendas.append(venda)
            st.success(f"✅ Venda registrada: {cliente['nome']} comprou {quantidade}x {produto['nome']} (R$ {total:.2f})")

    if st.session_state.vendas:
        st.subheader("📋 Histórico de Vendas")
        for venda in st.session_state.vendas:
            st.write(f"{venda['data']} - {venda['cliente']} - {venda['quantidade']}x {venda['produto']} - R$ {venda['total']:.2f}")
# ==========================
# Parte 3 - Barra lateral, login e roteamento
# ==========================

import streamlit as st

# ---------------- Função de login ----------------
def tela_login():
    st.title("🔐 Login")
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")
    visitante_input = st.checkbox("Entrar como visitante (somente leitura)")

    if st.button("Entrar"):
        if visitante_input:
            st.session_state.usuario = f"visitante-{datetime.now().strftime('%H%M%S')}"
            st.session_state.logado = True
            st.success("Entrou como visitante")
            registrar_acesso(f"Visitante entrou: {st.session_state.usuario}")
            st.rerun()
        elif usuario_input in USERS and USERS[usuario_input] == senha_input:
            st.session_state.usuario = usuario_input
            st.session_state.logado = True
            st.success(f"Bem-vindo {usuario_input}!")
            registrar_acesso(f"Login: {usuario_input}")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")


# ---------------- Barra lateral ----------------
def barra_lateral():
    st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario}")

    opcoes = [
        "Resumo",
        "Registrar venda por foto",
        "Clientes",
        "Produtos",
        "Relatórios",
        "Sair"
    ]
    if not is_visitante():
        opcoes.insert(-1, "Acessos")

    idx_atual = opcoes.index(st.session_state.menu) if st.session_state.menu in opcoes else 0
    st.session_state.menu = st.sidebar.radio("Menu", opcoes, index=idx_atual)


# ---------------- Função principal ----------------
def main():
    if "logado" not in st.session_state:
        st.session_state.logado = False
    if "menu" not in st.session_state:
        st.session_state.menu = "Resumo"

    if not st.session_state.logado:
        tela_login()
    else:
        barra_lateral()
        menu = st.session_state.menu

        if menu == "Resumo":
            tela_resumo()
        elif menu == "Registrar venda por foto":
            tela_registrar_venda_foto()
        elif menu == "Clientes":
            tela_clientes()
        elif menu == "Produtos":
            tela_produtos()
        elif menu == "Relatórios":
            tela_relatorios()
        elif menu == "Acessos" and not is_visitante():
            tela_acessos()
        elif menu == "Sair":
            st.session_state.logado = False
            st.session_state.usuario = None
            st.rerun()


# ----------------- Start App -----------------
if __name__ == "__main__":
    # Inicializar listas de vendas, produtos e clientes se não existirem
    if "vendas" not in st.session_state:
        st.session_state.vendas = []
    if "produtos" not in st.session_state:
        st.session_state.produtos = {}
    if "clientes" not in st.session_state:
        st.session_state.clientes = {}

    main()