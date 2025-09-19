# ==========================
# Parte 1 - Configuração, Banco e Utilitários
# ==========================

import streamlit as st
from datetime import datetime
import json
import os
import re
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

# =============== Espaço para produtos e clientes iniciais ===============
# Cole seus produtos aqui (exemplo abaixo)
PRODUTOS_INICIAIS = {
    # 1001: {"nome": "Camiseta Polo", "preco": 59.90},
    # 1002: {"nome": "Calça Jeans", "preco": 120.00},
}

# Cole seus clientes e histórico de vendas aqui (exemplo vazio para começar do zero)
CLIENTES_INICIAIS = {
    # "Maria": [{"codigo": 1001, "quantidade": 2, "preco": 59.90}],
}

# =============== Persistência JSON ===============
def save_db():
    try:
        data = {
            "produtos": st.session_state.produtos,
            "clientes": st.session_state.clientes,
            "vendas": st.session_state.vendas
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
            vendas = data.get("vendas", [])
            return prods, clis, vendas
        except Exception:
            pass
    # Se não houver DB, retorna os iniciais
    return PRODUTOS_INICIAIS.copy(), CLIENTES_INICIAIS.copy(), []

# =============== Session state inicial ===============
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
if "carrinho_foto" not in st.session_state:
    st.session_state.carrinho_foto = []
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

def adicionar_produto_manual(codigo, nome, preco_unitario):
    try:
        cod = int(codigo)
    except:
        raise ValueError("Código inválido")
    st.session_state
# ==========================
# ==========================
# Parte 2 - Telas principais
# ==========================

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import streamlit as st
from datetime import datetime

# ---------------- Tela Resumo ----------------
def tela_resumo():
    st.title("📊 Resumo")
    vendas = st.session_state.db.get("vendas", [])
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

    clientes = list(st.session_state.db.get("clientes", {}).keys())
    cliente = st.selectbox("Selecione o cliente", options=clientes)

    carrinho = st.session_state.get("carrinho", [])

    produto = st.selectbox("Selecione o produto", options=st.session_state.db.get("produtos", []))
    if st.button("Adicionar ao carrinho"):
        carrinho.append(produto)
        st.session_state.carrinho = carrinho

    st.subheader("Carrinho")
    if carrinho:
        for i, p in enumerate(carrinho):
            col1, col2 = st.columns([3, 1])
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
            save_db()
            st.session_state.carrinho = []
            st.success("Venda registrada com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum produto no carrinho ainda.")

# ---------------- Tela Registrar Venda por Foto ----------------
def tela_registrar_venda_foto():
    st.title("📷 Registrar Venda (Por Foto)")

    # Seleção ou cadastro do cliente
    clientes = list(st.session_state.db.get("clientes", {}).keys())
    opcao_cliente = st.radio("Cliente", ["Selecionar existente", "Cadastrar novo"])
    if opcao_cliente == "Selecionar existente":
        if clientes:
            cliente = st.selectbox("Selecione o cliente", options=clientes, key="foto_cliente")
        else:
            st.warning("Nenhum cliente cadastrado. Cadastre um novo.")
            opcao_cliente = "Cadastrar novo"
    if opcao_cliente == "Cadastrar novo":
        cliente_novo = st.text_input("Nome do novo cliente", key="novo_cliente_foto")
        if st.button("Cadastrar cliente"):
            if cliente_novo.strip() == "":
                st.error("Informe um nome válido!")
                return
            st.session_state.db.setdefault("clientes", {})[cliente_novo] = []
            save_db()
            st.success("Cliente cadastrado!")
            cliente = cliente_novo
        else:
            return

    # Upload de múltiplas fotos
    uploaded_files = st.file_uploader(
        "Envie até 10 fotos das etiquetas do produto", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )
    if uploaded_files:
        if len(uploaded_files) > 10:
            st.warning("Você pode enviar no máximo 10 fotos.")
            uploaded_files = uploaded_files[:10]

        carrinho_foto = st.session_state.get("carrinho_foto", [])

        for i, uploaded_file in enumerate(uploaded_files):
            st.markdown(f"**Foto {i+1}**")
            img = Image.open(uploaded_file)
            st.image(img, width=200)

            # Pré-processamento
            img_proc = img.convert("L")
            img_proc = img_proc.filter(ImageFilter.SHARPEN)
            img_proc = ImageEnhance.Contrast(img_proc).enhance(2)

            # OCR com verificação de erro
            try:
                texto = pytesseract.image_to_string(img_proc, lang="por")
            except Exception as e:
                st.error(f"Erro OCR na foto {i+1}: {e}")
                continue

            st.text_area("Texto detectado (OCR):", texto, height=100)

            # Extração de informações
            ref_match = re.search(r"Ref\.?\s*(\d+)", texto, re.IGNORECASE)
            codigo = ref_match.group(1) if ref_match else ""

            preco_match = re.search(r"(\d{1,3}[.,]\d{2})", texto)
            preco = preco_match.group(1).replace(",", ".") if preco_match else ""

            nome_match = re.search(r"(SOUTIEN.*|CALCINHA.*|CAMISE.*|PRODUTO.*)", texto, re.IGNORECASE)
            nome = nome_match.group(0).strip() if nome_match else ""

            st.write(f"**Leitura extraída:** Código: {codigo}, Nome: {nome}, Preço: {preco}")

            # Apenas produtos cadastrados
            produtos_cadastrados = st.session_state.db.get("produtos", {})
            if codigo and codigo in map(str, produtos_cadastrados.keys()):
                st.success("Produto reconhecido no cadastro.")
            else:
                st.warning("Produto não cadastrado. Ajuste os dados antes de adicionar.")

            # Campos editáveis
            codigo = st.text_input(f"Código do produto (Foto {i+1})", value=codigo, key=f"cod_foto{i}")
            nome = st.text_input(f"Nome do produto (Foto {i+1})", value=nome, key=f"nome_foto{i}")
            preco = st.text_input(f"Preço (R$) (Foto {i+1})", value=preco, key=f"preco_foto{i}")

            if st.button(f"Adicionar produto da foto {i+1}"):
                try:
                    preco_float = float(preco)
                except:
                    st.error("Preço inválido. Corrija antes de continuar.")
                    continue

                produto = {"codigo": codigo, "nome": nome, "preco": preco_float}
                carrinho_foto.append(produto)
                st.session_state.carrinho_foto = carrinho_foto
                st.success("Produto adicionado ao carrinho!")

    # Mostrar carrinho final
    st.subheader("Carrinho (Foto)")
    carrinho_foto = st.session_state.get("carrinho_foto", [])
    if carrinho_foto:
        for i, p in enumerate(carrinho_foto):
            col1, col2 = st.columns([3, 1])
            col1.write(f"{p['nome']} (Ref {p['codigo']}) - R$ {p['preco']:.2f}")
            if col2.button("Remover", key=f"rem_foto{i}"):
                carrinho_foto.pop(i)
                st.session_state.carrinho_foto = carrinho_foto
                st.rerun()

        total = sum(p["preco"] for p in carrinho_foto)
        st.write(f"**Total: R$ {total:.2f}**")

        if st.button("Finalizar venda por foto"):
            nova_venda = {
                "cliente": cliente,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "produtos": carrinho_foto.copy(),
                "total": total
            }
            st.session_state.db.setdefault("vendas", []).append(nova_venda)
            save_db()
            st.session_state.carrinho_foto = []
            st.success("Venda registrada com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum produto no carrinho ainda.")

# ---------------- Tela Clientes ----------------
def tela_clientes():
    st.title("👥 Clientes")
    clientes = st.session_state.db.get("clientes", {})

    novo_cliente = st.text_input("Adicionar novo cliente")
    if st.button("Adicionar cliente"):
        if novo_cliente and novo_cliente not in clientes:
            clientes[novo_cliente] = []
            save_db()
            st.success("Cliente adicionado.")
            st.rerun()

    for cliente, _ in clientes.items():
        with st.expander(cliente):
            col1, col2 = st.columns([1, 1])
            if col1.button("Renomear", key=f"ren_{cliente}"):
                novo_nome = st.text_input(f"Novo nome para {cliente}", key=f"in_ren_{cliente}")
                if st.button("Salvar", key=f"salvar_{cliente}"):
                    clientes[novo_nome] = clientes.pop(cliente)
                    save_db()
                    st.success("Cliente renomeado.")
                    st.rerun()
            if col2.button("Apagar", key=f"del_{cliente}"):
                del clientes[cliente]
                save_db()
                st.warning("Cliente removido.")
                st.rerun()

# ---------------- Tela Produtos ----------------
def tela_produtos():
    st.title("📦 Produtos")
    produtos = st.session_state.db.get("produtos", {})

    codigo = st.text_input("Código do produto")
    nome = st.text_input("Nome do produto")
    preco = st.number_input("Preço", min_value=0.0, format="%.2f")

    if st.button("Adicionar produto"):
        if codigo and nome and preco > 0:
            produtos[int(codigo)] = {"nome": nome, "preco": preco}
            save_db()
            st.success("Produto adicionado.")
            st.rerun()

    for cod, p in produtos.items():
        st.write(f"{p['nome']} (Ref {cod}) - R$ {p['preco']:.2f}")

# ---------------- Tela Relatórios ----------------
def tela_relatorios():
    st.title("📑 Relatórios")
    vendas = st.session_state.db.get("vendas", [])
    if not vendas:
        st.info("Nenhuma venda registrada.")
        return

    for v in vendas:
        st.write(f"{v['cliente']} - {v['data']} - R$ {v['total']:.2f}")

# ---------------- Tela Acessos ----------------
def tela_acessos():
    st.title("🔐 Acessos")
    try:
        with open(LOG_FILE, "r") as f:
            st.text(f.read())
    except Exception:
        st.warning("Não foi possível carregar o log de acessos.")
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