# ==========================
# Parte 1 - Configuração, Banco e Utilitários
# ==========================

import streamlit as st
from datetime import datetime
import json
import os
import re
import pdfplumber
from PIL import Image
import pytesseract

# =============== Config página ===============
st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# =============== Autenticação ===============
USERS = {
    "othavio": "122008",
    "isabela": "122008",
}
LOG_FILE = "acessos.log"
DB_FILE  = "db.json"

def registrar_acesso(label: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {label}\n")
    except Exception:
        pass

def is_visitante():
    return bool(st.session_state.get("usuario")) and str(st.session_state.get("usuario")).startswith("visitante-")

# =============== Dados iniciais (pode personalizar) ===============
PRODUTOS_INICIAIS = {
    1001: {"nome": "Camiseta Polo", "preco": 59.90},
    1002: {"nome": "Calça Jeans", "preco": 120.00},
    1003: {"nome": "Tênis Esportivo", "preco": 199.99},
    1004: {"nome": "Boné Estiloso", "preco": 39.90},
}
VENDAS_INICIAIS = {
    "Maria": [
        {"codigo": 1001, "quantidade": 2, "preco": 59.90},
        {"codigo": 1003, "quantidade": 1, "preco": 189.99},
    ],
    "João": [
        {"codigo": 1002, "quantidade": 1, "preco": 120.00},
    ]
}

# =============== Persistência JSON ===============
def save_db():
    try:
        data = {
            "produtos": st.session_state.produtos,
            "clientes": st.session_state.clientes,
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
            clis  = {k: v for k, v in data.get("clientes", {}).items()}
            return prods, clis
        except Exception:
            pass
    return ({k: v.copy() for k, v in PRODUTOS_INICIAIS.items()},
            {k: [i.copy() for i in lst] for k, lst in VENDAS_INICIAIS.items()})

# =============== Session state inicial ===============
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "produtos" not in st.session_state or "clientes" not in st.session_state:
    p, c = load_db()
    st.session_state.produtos = p
    st.session_state.clientes = c
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "filtro_cliente" not in st.session_state:
    st.session_state.filtro_cliente = ""
if "menu" not in st.session_state:
    st.session_state.menu = "Resumo"

# =============== Helpers ===============
def total_cliente(nome: str) -> float:
    vendas = st.session_state.clientes.get(nome, [])
    return sum(v["preco"] * v["quantidade"] for v in vendas)

def total_geral() -> float:
    return sum(total_cliente(c) for c in st.session_state.clientes.keys())

def opcao_produtos_fmt():
    items = []
    for cod, dados in st.session_state.produtos.items():
        items.append(f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f})")
    return sorted(items, key=lambda s: s.split(" - ",1)[1].lower())

def parse_codigo_from_fmt(s: str):
    try:
        return int(s.split(" - ",1)[0].strip())
    except:
        return None

def filtrar_clientes(filtro: str):
    if not filtro or len(filtro.strip()) < 2:
        return []
    f = filtro.strip().lower()
    return sorted([c for c in st.session_state.clientes if f in c.lower()], key=lambda x: x.lower())

def remover_venda(nome, idx):
    try:
        st.session_state.clientes[nome].pop(idx)
        save_db()
        st.success("Venda removida.")
        st.rerun()
    except:
        st.error("Não foi possível remover.")

def editar_venda(nome, idx, nova_qtd, novo_preco):
    try:
        st.session_state.clientes[nome][idx]["quantidade"] = int(nova_qtd)
        st.session_state.clientes[nome][idx]["preco"] = float(novo_preco)
        save_db()
        st.success("Venda atualizada.")
        st.rerun()
    except:
        st.error("Não foi possível editar.")

def renomear_cliente(nome_antigo, nome_novo):
    if not nome_novo.strip():
        st.warning("Informe um nome válido.")
        return
    if nome_novo in st.session_state.clientes and nome_novo != nome_antigo:
        st.warning("Já existe cliente com esse nome.")
        return
    st.session_state.clientes[nome_novo] = st.session_state.clientes.pop(nome_antigo)
    save_db()
    st.success("Cliente renomeado.")
    st.rerun()

def apagar_cliente(nome):
    st.session_state.clientes.pop(nome, None)
    save_db()
    st.success("Cliente apagado.")
    st.rerun()

def adicionar_produto_manual(codigo, nome, quantidade, preco_unitario):
    try:
        cod = int(codigo)
    except:
        raise ValueError("Código inválido")
    st.session_state.produtos[cod] = {"nome": nome.strip(), "preco": float(preco_unitario)}
    save_db()

def zerar_todas_vendas():
    for k in list(st.session_state.clientes.keys()):
        st.session_state.clientes[k] = []
    save_db()
# ==========================
# Parte 2 - Telas principais
# ==========================

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re

# ---------------- Tela Resumo ----------------
def tela_resumo():
    st.title("📊 Resumo")
    vendas = st.session_state.db["vendas"]
    if not vendas:
        st.info("Nenhuma venda registrada ainda.")
        return

    total = sum(v["total"] for v in vendas)
    st.metric("Total de vendas registradas", f"R$ {total:,.2f}")

    for v in vendas:
        with st.expander(f"{v['cliente']} - {v['data']} - R$ {v['total']:.2f}"):
            for p in v["produtos"]:
                st.write(f"- {p['nome']} (Ref {p['codigo']}): {p['preco']:.2f}")

# ---------------- Tela Registrar Venda Manual ----------------
def tela_registrar_venda():
    st.title("🛒 Registrar Venda (Manual)")

    clientes = list(st.session_state.db["clientes"].keys())
    cliente = st.selectbox("Selecione o cliente", options=clientes)

    carrinho = st.session_state.get("carrinho", [])

    produto = st.selectbox("Selecione o produto", options=st.session_state.db["produtos"])
    if st.button("Adicionar ao carrinho"):
        carrinho.append(produto)
        st.session_state.carrinho = carrinho

    st.subheader("Carrinho")
    if carrinho:
        for i, p in enumerate(carrinho):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"{p['nome']} (Ref {p['codigo']}) - R$ {p['preco']:.2f}")
            if col2.button("Remover", key=f"rem{i}"):
                carrinho.pop(i)
                st.session_state.carrinho = carrinho
                st.rerun()

        total = sum(p["preco"] for p in carrinho)
        st.write(f"**Total: R$ {total:.2f}**")

        if st.button("Finalizar venda"):
            nova_venda = {
                "cliente": cliente,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "produtos": carrinho.copy(),
                "total": total
            }
            st.session_state.db["vendas"].append(nova_venda)
            salvar_db()
            st.session_state.carrinho = []
            st.success("Venda registrada com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum produto no carrinho ainda.")

# ---------------- Tela Registrar Venda por Foto ----------------
def tela_registrar_venda_foto():
    st.title("📷 Registrar Venda (Por Foto)")

    clientes = list(st.session_state.db["clientes"].keys())
    cliente = st.selectbox("Selecione o cliente", options=clientes, key="foto_cliente")

    uploaded_file = st.file_uploader("Envie a foto da etiqueta do produto", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)

        # Pré-processamento da imagem para melhorar OCR
        img = img.convert("L")  # escala de cinza
        img = img.filter(ImageFilter.SHARPEN)
        img = ImageEnhance.Contrast(img).enhance(2)

        texto = pytesseract.image_to_string(img, lang="por")
        st.text_area("Texto detectado (OCR):", texto, height=150)

        # Tentativa de extrair código, nome e preço
        ref_match = re.search(r"Ref\.?\s*(\d+)", texto, re.IGNORECASE)
        codigo = ref_match.group(1) if ref_match else ""

        preco_match = re.search(r"(\d{1,3}[.,]?\d{2})", texto)
        preco = preco_match.group(1).replace(",", ".") if preco_match else ""

        nome_match = re.search(r"(SOUTIEN.*|CALCINHA.*|CAMISE.*|PRODUTO.*)", texto, re.IGNORECASE)
        nome = nome_match.group(0).strip() if nome_match else ""

        # Campos editáveis para revisão manual
        codigo = st.text_input("Código do produto", value=codigo)
        nome = st.text_input("Nome do produto", value=nome)
        preco = st.text_input("Preço (R$)", value=preco)

        if st.button("Adicionar produto da foto"):
            try:
                preco_float = float(preco)
            except:
                st.error("Preço inválido. Corrija antes de continuar.")
                return

            produto = {"codigo": codigo, "nome": nome, "preco": preco_float}
            carrinho = st.session_state.get("carrinho_foto", [])
            carrinho.append(produto)
            st.session_state.carrinho_foto = carrinho
            st.success("Produto adicionado ao carrinho!")

    st.subheader("Carrinho (Foto)")
    carrinho = st.session_state.get("carrinho_foto", [])
    if carrinho:
        for i, p in enumerate(carrinho):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"{p['nome']} (Ref {p['codigo']}) - R$ {p['preco']:.2f}")
            if col2.button("Remover", key=f"rem_foto{i}"):
                carrinho.pop(i)
                st.session_state.carrinho_foto = carrinho
                st.rerun()

        total = sum(p["preco"] for p in carrinho)
        st.write(f"**Total: R$ {total:.2f}**")

        if st.button("Finalizar venda por foto"):
            nova_venda = {
                "cliente": cliente,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "produtos": carrinho.copy(),
                "total": total
            }
            st.session_state.db["vendas"].append(nova_venda)
            salvar_db()
            st.session_state.carrinho_foto = []
            st.success("Venda registrada com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum produto no carrinho ainda.")

# ---------------- Tela Clientes ----------------
def tela_clientes():
    st.title("👥 Clientes")
    clientes = st.session_state.db["clientes"]

    novo_cliente = st.text_input("Adicionar novo cliente")
    if st.button("Adicionar cliente"):
        if novo_cliente and novo_cliente not in clientes:
            clientes[novo_cliente] = []
            salvar_db()
            st.success("Cliente adicionado.")
            st.rerun()

    for cliente, _ in clientes.items():
        with st.expander(cliente):
            col1, col2 = st.columns([1, 1])
            if col1.button("Renomear", key=f"ren_{cliente}"):
                novo_nome = st.text_input(f"Novo nome para {cliente}", key=f"in_ren_{cliente}")
                if st.button("Salvar", key=f"salvar_{cliente}"):
                    clientes[novo_nome] = clientes.pop(cliente)
                    salvar_db()
                    st.success("Cliente renomeado.")
                    st.rerun()
            if col2.button("Apagar", key=f"del_{cliente}"):
                del clientes[cliente]
                salvar_db()
                st.warning("Cliente removido.")
                st.rerun()

# ---------------- Tela Produtos ----------------
def tela_produtos():
    st.title("📦 Produtos")
    produtos = st.session_state.db["produtos"]

    codigo = st.text_input("Código do produto")
    nome = st.text_input("Nome do produto")
    preco = st.number_input("Preço", min_value=0.0, format="%.2f")

    if st.button("Adicionar produto"):
        if codigo and nome and preco > 0:
            produtos.append({"codigo": codigo, "nome": nome, "preco": preco})
            salvar_db()
            st.success("Produto adicionado.")
            st.rerun()

    for p in produtos:
        st.write(f"{p['nome']} (Ref {p['codigo']}) - R$ {p['preco']:.2f}")

# ---------------- Tela Relatórios ----------------
def tela_relatorios():
    st.title("📑 Relatórios")
    vendas = st.session_state.db["vendas"]
    if not vendas:
        st.info("Nenhuma venda registrada.")
        return

    for v in vendas:
        st.write(f"{v['cliente']} - {v['data']} - R$ {v['total']:.2f}")

# ---------------- Tela Acessos ----------------
def tela_acessos():
    st.title("🔐 Acessos")
    with open(LOG_FILE, "r") as f:
        st.text(f.read())
# ==========================
# Parte 3 - Roteamento e Sidebar
# ==========================

def barra_lateral():
    st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario}")

    opcoes = [
        "Resumo",
        "Registrar venda",
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

    bloco_backup_sidebar()

# ----------------- Roteador principal -----------------
def main():
    if not st.session_state.logado:
        tela_login()
    else:
        barra_lateral()
        menu = st.session_state.menu
        if menu == "Resumo":
            tela_resumo()
        elif menu == "Registrar venda":
            tela_registrar_venda()
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

# ----------------- Start app -----------------
if __name__ == "__main__":
    main()