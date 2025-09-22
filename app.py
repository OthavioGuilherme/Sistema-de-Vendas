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
# ========================== PARTE 2
# ===============================
# PARTE 2 - Produtos e Vendas
# ===============================

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re

# Configurar caminho do Tesseract no Streamlit Cloud (caso necessário futuramente)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ---------- Função para processar imagem ----------
def processar_imagem(imagem):
    img = imagem.convert("L")  # escala de cinza
    img = img.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    return img


# ---------- Tela de Produtos ----------
def tela_produtos():
    st.header("📦 Gestão de Produtos")

    if "db" not in st.session_state:
        st.session_state.db = {"produtos": {}, "vendas": []}

    produtos = st.session_state.db.get("produtos", {})

    with st.form("novo_produto"):
        codigo = st.text_input("Código do Produto")
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço do Produto (R$)", min_value=0.0, format="%.2f")
        submit = st.form_submit_button("Cadastrar Produto")

        if submit:
            if codigo and nome and preco > 0:
                produtos[codigo] = {"nome": nome, "preco": preco}
                st.session_state.db["produtos"] = produtos
                salvar_db(st.session_state.db)
                st.success(f"✅ Produto {nome} cadastrado com sucesso!")
            else:
                st.error("⚠️ Preencha todos os campos para cadastrar.")


# ---------- Tela de Registrar Vendas por Foto ----------
def tela_registrar_venda_foto():
    st.header("🖼️ Registrar Venda por Foto")

    uploaded_file = st.file_uploader("Envie uma foto da etiqueta", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        img_proc = processar_imagem(img)

        # Extrair texto da imagem
        texto = pytesseract.image_to_string(img_proc, lang="por")
        st.text_area("📄 Texto detectado:", texto, height=150)

        # ==========================
        # Extrair Código (Ref) e Preço (Sxxxx)
        # ==========================
        ref_match = re.search(r"Ref[:\s]*([0-9]+)", texto, re.IGNORECASE)
        codigo = ref_match.group(1) if ref_match else None

        preco_match = re.search(r"S\s*([0-9]{2,})([0-9]{2})", texto, re.IGNORECASE)
        preco = None
        if preco_match:
            preco = float(f"{preco_match.group(1)}.{preco_match.group(2)}")

        # Se não encontrar código
        if not codigo:
            st.error("⚠️ Não foi possível detectar a referência (código) na etiqueta.")
            return

        produtos = st.session_state.db.get("produtos", {})

        # Produto já cadastrado
        if codigo in produtos:
            produto = produtos[codigo]
            st.success(f"✅ Produto encontrado: {produto['nome']} - R$ {produto['preco']:.2f}")

            qtd = st.number_input("Quantidade", min_value=1, step=1, key=f"qtd_{codigo}")
            if st.button("Registrar Venda"):
                venda = {
                    "codigo": codigo,
                    "nome": produto["nome"],
                    "preco": produto["preco"],
                    "quantidade": qtd,
                }
                st.session_state.db["vendas"].append(venda)
                salvar_db(st.session_state.db)
                st.success("💰 Venda registrada com sucesso!")

        # Produto não cadastrado → opção de cadastro
        else:
            st.warning(f"⚠️ Produto não cadastrado. Código: {codigo}")

            nome_prod = st.text_input(f"Nome do produto para cadastrar (Código {codigo})")
            preco_prod = st.number_input(
                f"Preço do produto (R$) para cadastrar (Código {codigo})",
                min_value=0.0,
                format="%.2f",
                value=preco if preco else 0.0,
            )

            if st.button(f"Cadastrar produto {codigo}"):
                if nome_prod and preco_prod > 0:
                    produtos[codigo] = {"nome": nome_prod, "preco": preco_prod}
                    st.session_state.db["produtos"] = produtos
                    salvar_db(st.session_state.db)
                    st.success(f"✅ Produto {nome_prod} cadastrado com sucesso!")
                else:
                    st.error("⚠️ Preencha nome e preço para cadastrar.")


# ---------- Tela de Resumo ----------
def tela_resumo():
    st.header("📊 Resumo de Vendas")

    vendas = st.session_state.db.get("vendas", [])
    if not vendas:
        st.info("Nenhuma venda registrada ainda.")
        return

    total = sum(v["preco"] * v["quantidade"] for v in vendas)
    st.write(f"### 💰 Total vendido: R$ {total:.2f}")

    st.table(vendas)
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