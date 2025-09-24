# ================== PARTE 1 ==================
import streamlit as st
from datetime import datetime
import json
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
USERS = {"othavio": "122008", "isabela": "122008"}  # usuários e senhas simples
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
    default_clients = {
        "Tabata": [], "Valquiria": [], "Vanessa": [], "Pamela": [], "Elan": [], "Claudinha": []
    }
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
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                if usuario in USERS and USERS[usuario] == senha:
                    st.session_state["usuario"] = usuario
                    registrar_acesso(f"login-usuario:{usuario}")
                    st.success(f"Bem-vindo(a), {usuario}!")
                    st.rerun()
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

# ================== PDF (Importar Estoque) ==================
def substituir_estoque_pdf(uploaded_file):
    data = uploaded_file.read()
    stream = io.BytesIO(data)
    novos_produtos = {}

    # Regex adaptado ao layout da sua nota: quantidade, código (5 dígitos), nome e preço
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
            if cod in st.session_state["produtos"]:
                st.warning("Código já existe.")
            elif not nome.strip():
                st.warning("Informe um nome válido.")
            else:
                adicionar_produto_manual(cod, nome, preco, quantidade)

    elif acao == "Listar/Buscar":
        termo = st.text_input("Buscar por nome ou código").lower()
        st.subheader("Lista de Produtos")
        for cod, dados in sorted(st.session_state["produtos"].items(), key=lambda x: str(x[0])):
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
# ================== PARTE 3 ==================
# ================== Clientes ==================
def tela_clientes():
    st.header("👥 Clientes")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Listar", "Adicionar", "Excluir"], horizontal=True)

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
                st.success(f"Cliente {nome} adicionado.")

    elif acao == "Excluir":
        if visitante:
            st.info("🔒 Visitantes não podem excluir clientes.")
            return
        clientes = list(st.session_state["clientes"].keys())
        if not clientes:
            st.warning("Nenhum cliente cadastrado.")
            return
        nome = st.selectbox("Selecione o cliente para excluir", clientes)
        if st.button("Excluir cliente"):
            del st.session_state["clientes"][nome]
            save_db()
            st.success(f"Cliente {nome} excluído.")

    elif acao == "Listar":
        if not st.session_state["clientes"]:
            st.info("Nenhum cliente cadastrado.")
        else:
            for cliente in sorted(st.session_state["clientes"].keys()):
                st.write(f"- {cliente}")

# ================== Registrar Venda ==================
def registrar_venda(cliente, cod, quantidade):
    cod = int(cod)
    if cod not in st.session_state["produtos"]:
        st.error("Produto não encontrado.")
        return
    produto = st.session_state["produtos"][cod]
    if quantidade > produto.get("quantidade", 0):
        st.error("Estoque insuficiente.")
        return
    produto["quantidade"] -= quantidade
    venda = {
        "cod": cod,
        "nome": produto["nome"],
        "preco": produto["preco"],
        "quantidade": quantidade
    }
    st.session_state["clientes"][cliente].append(venda)
    save_db()
    st.success(f"Venda registrada: {produto['nome']} x {quantidade} para {cliente}")

def tela_vendas():
    st.header("🛒 Vendas")
    visitante = is_visitante()
    if visitante:
        st.info("🔒 Visitantes não podem registrar vendas.")
        return
    clientes = list(st.session_state["clientes"].keys())
    if not clientes:
        st.warning("Nenhum cliente cadastrado.")
        return
    cliente = st.selectbox("Selecione o cliente", clientes)
    produtos = st.session_state["produtos"]
    if not produtos:
        st.warning("Nenhum produto disponível.")
        return
    cod = st.selectbox("Selecione o produto", list(produtos.keys()))
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    if st.button("Registrar venda"):
        registrar_venda(cliente, cod, quantidade)

# ================== Relatórios ==================
def tela_relatorios():
    st.header("📑 Relatórios")
    visitantes = is_visitante()
    if visitantes:
        st.info("🔒 Visitantes não podem acessar relatórios.")
        return
    for cliente, vendas in st.session_state["clientes"].items():
        st.subheader(f"Cliente: {cliente}")
        if not vendas:
            st.write("Nenhuma venda registrada.")
        else:
            total = 0.0
            for v in vendas:
                subtotal = v["preco"] * v["quantidade"]
                total += subtotal
                st.write(f"- {v['nome']} x {v['quantidade']} = R$ {subtotal:.2f}")
            st.write(f"**Total: R$ {total:.2f}**")

# ================== Navegação Principal ==================
def main_app():
    st.sidebar.title("📌 Menu")
    pagina = st.sidebar.radio("Ir para", ["Resumo", "Produtos", "Clientes", "Vendas", "Relatórios"])
    if pagina == "Resumo":
        tela_resumo()
    elif pagina == "Produtos":
        tela_produtos()
    elif pagina == "Clientes":
        tela_clientes()
    elif pagina == "Vendas":
        tela_vendas()
    elif pagina == "Relatórios":
        tela_relatorios()

# ================== Execução ==================
def main():
    st.set_page_config(page_title="Sistema de Vendas", layout="wide")
    if "usuario" not in st.session_state:
        login()
    else:
        usuario = st.session_state["usuario"]
        st.sidebar.write(f"👤 Usuário: {usuario}")
        if st.sidebar.button("Sair"):
            del st.session_state["usuario"]
            st.rerun()
        main_app()

if __name__ == "__main__":
    main()