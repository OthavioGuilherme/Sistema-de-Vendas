import streamlit as st
from datetime import datetime
import json
import os
import io
import pdfplumber
import re

# ================== Configuração ==================
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
    st.session_state["produtos"] = {}  # estoque vazio inicial
if "clientes" not in st.session_state:
    st.session_state["clientes"] = {
        "Tabata": [],
        "Valquiria": [],
        "Vanessa": [],
        "Pamela": [],
        "Elan": [],
        "Claudinha": [],
    }
if "carrinho" not in st.session_state:
    st.session_state["carrinho"] = []
if "menu" not in st.session_state:
    st.session_state["menu"] = "Resumo"

# ================== Helpers ==================
def is_visitante():
    return st.session_state["usuario"] and st.session_state["usuario"].startswith("visitante-")

def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "produtos": st.session_state["produtos"],
                "clientes": st.session_state["clientes"],
            }, ensure_ascii=False, indent=2)
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
    return {}, st.session_state["clientes"]  # produtos vazio, clientes mantidos

# ================== Inicialização DB ==================
st.session_state["produtos"], st.session_state["clientes"] = load_db()

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
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        nome = st.text_input("Digite seu nome para entrar como visitante")
        if st.button("Entrar como visitante"):
            if nome.strip():
                st.session_state["usuario"] = f"visitante-{nome.strip()}"
                registrar_acesso(f"login-visitante:{nome.strip()}")
                st.success(f"Bem-vindo(a), visitante {nome.strip()}!")
                st.experimental_rerun()
            else:
                st.warning("Por favor, digite um nome.")

# ================== Tela PDF ==================
def substituir_estoque_pdf(uploaded_file):
    """
    Substitui estoque a partir do PDF da nota fiscal.
    Formato esperado por linha: <quantidade> <codigo> <nome> <valor unitario>
    """
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

def tela_pdf():
    st.header("📄 Importar Estoque via Nota Fiscal (PDF)")
    if is_visitante():
        st.info("🔒 Apenas usuários logados podem importar PDF.")
        return
    pdf_file = st.file_uploader("Selecione o PDF da nota fiscal", type=["pdf"])
    if pdf_file is not None:
        if st.button("Substituir estoque pelo PDF"):
            substituir_estoque_pdf(pdf_file)

# ================== Produtos ==================
def adicionar_produto_manual(cod, nome, preco):
    cod = int(cod)
    st.session_state["produtos"][cod] = {"nome": nome.strip(), "preco": float(preco)}
    save_db()
    st.success(f"Produto {nome} adicionado/atualizado!")

def tela_produtos():
    st.header("📦 Produtos")
    visitante = is_visitante()
    sub = st.radio("Ação", ["Listar/Buscar", "Adicionar"], horizontal=True)
    
    if sub == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar produtos.")
            return
        cod = st.number_input("Código", min_value=1, step=1)
        nome = st.text_input("Nome do produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.10, format="%.2f")
        if st.button("Salvar produto"):
            if cod in st.session_state["produtos"]:
                st.warning("Código já existe.")
            elif not nome.strip():
                st.warning("Informe um nome válido.")
            else:
                adicionar_produto_manual(cod, nome, preco)
    else:
        termo = st.text_input("Buscar por nome ou código").lower()
        for cod, dados in sorted(st.session_state["produtos"].items(), key=lambda x: x[1]["nome"].lower()):
            if termo in str(cod) or termo in dados["nome"].lower():
                st.write(f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f})")

# ================== Clientes ==================
def tela_clientes():
    st.header("👥 Clientes")
    visitante = is_visitante()
    aba = st.radio("Ação", ["Consultar cliente", "Cadastrar cliente"], horizontal=True)
    
    if visitante and aba == "Cadastrar cliente":
        st.info("🔒 Visitantes não podem cadastrar clientes.")
        return
    
    if aba == "Cadastrar cliente":
        nome = st.text_input("Nome do cliente")
        if st.button("Salvar cliente"):
            if not nome.strip():
                st.warning("Informe um nome válido.")
            elif nome in st.session_state["clientes"]:
                st.warning("Cliente já existe.")
            else:
                st.session_state["clientes"][nome.strip()] = []
                save_db()
                st.success(f"Cliente {nome} cadastrado!")
        return
    
    # Consultar cliente
    filtro = st.text_input("Buscar cliente (2+ letras)").lower()
    matches = [c for c in st.session_state["clientes"] if filtro in c.lower()]
    cliente = st.selectbox("Selecione o cliente", matches) if matches else None
    
    if cliente:
        st.subheader(f"{cliente}")
        st.info("Vendas estão zeradas neste sistema simplificado.")
        
# ================== Helpers ==================
def is_visitante():
    return st.session_state["usuario"].startswith("visitante-")

def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "produtos": st.session_state["produtos"],
                "clientes": st.session_state["clientes"],
            }, ensure_ascii=False, indent=2)
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

# ================== Resumo inicial ==================
def tela_resumo():
    st.header("📊 Resumo de Vendas")
    total_geral = 0
    for c, vendas in st.session_state["clientes"].items():
        total_cliente = sum(v.get("preco", 0)*v.get("quantidade",1) for v in vendas)
        total_geral += total_cliente
    # Comissão progressiva
    if total_geral <= 500:
        comissao = total_geral * 0.25
    elif total_geral <= 1000:
        comissao = total_geral * 0.30
    else:
        comissao = total_geral * 0.40
    st.metric("💰 Venda Total", f"R$ {total_geral:.2f}")
    st.metric("🪙 Comissão", f"R$ {comissao:.2f}")

# ================== Menu lateral ==================
def bloco_backup_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧰 Backup")
    db_json = json.dumps({
        "produtos": st.session_state["produtos"],
        "clientes": st.session_state["clientes"]
    }, ensure_ascii=False, indent=2)
    st.sidebar.download_button(
        "⬇️ Exportar backup (.json)",
        data=db_json.encode("utf-8"),
        file_name="backup_sistema_vendas.json"
    )
    if not is_visitante():
        up = st.sidebar.file_uploader("⬆️ Restaurar backup (.json)", type=["json"])
        if up is not None:
            try:
                data = json.load(up)
                prods = {int(k): v for k, v in data.get("produtos", {}).items()}
                clis = {k: v for k, v in data.get("clientes", {}).items()}
                st.session_state["produtos"] = prods
                st.session_state["clientes"] = clis
                save_db()
                st.sidebar.success("Backup restaurado!")
                st.experimental_rerun()
            except Exception as e:
                st.sidebar.error(f"Falha ao restaurar: {e}")
    else:
        st.sidebar.caption("🔒 Restauração apenas para usuários logados.")

def barra_lateral():
    st.sidebar.markdown(f"**Usuário:** {st.session_state['usuario']}")
    opcoes = ["Resumo", "Upload PDF", "Clientes", "Produtos", "Relatórios", "Sair"]
    if not is_visitante():
        opcoes.insert(-1, "Backup")
    idx_atual = opcoes.index(st.session_state.get("menu", "Resumo")) \
        if st.session_state.get("menu") in opcoes else 0
    menu = st.sidebar.radio("Menu", opcoes, index=idx_atual)
    st.session_state["menu"] = menu
    bloco_backup_sidebar()

# ================== Relatórios ==================
def relatorio_geral():
    st.header("📋 Relatório Geral")
    linhas = ["📋 Relatório Geral de Vendas", ""]
    for c, vendas in st.session_state["clientes"].items():
        total = sum(v.get("preco", 0)*v.get("quantidade",1) for v in vendas)
        linhas.append(f"- {c}: R$ {total:.2f}")
    total_geral = sum(sum(v.get("preco",0)*v.get("quantidade",1) for v in vendas)
                      for vendas in st.session_state["clientes"].values())
    linhas.append(f"\n💰 Total geral: R$ {total_geral:.2f}")
    st.code("\n".join(linhas))
    st.download_button("Baixar .txt", data="\n".join(linhas), file_name="relatorio_geral.txt")

# ================== Roteador ==================
def roteador():
    menu = st.session_state.get("menu", "Resumo")
    if menu == "Resumo":
        tela_resumo()
    elif menu == "Upload PDF":
        tela_pdf()
    elif menu == "Clientes":
        tela_clientes()
    elif menu == "Produtos":
        tela_produtos()
    elif menu == "Relatórios":
        relatorio_geral()
    elif menu == "Backup":
        st.header("🗂️ Backup")
        st.info("Use a lateral para exportar ou restaurar backup.")
    elif menu == "Sair":
        st.session_state.clear()
        st.experimental_rerun()

# ================== Main ==================
def main():
    if st.session_state.get("usuario") is None:
        login()
        st.stop()
    barra_lateral()
    roteador()

# ================== Execução principal ==================
if __name__ == "__main__":
    main()