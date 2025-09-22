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
    st.session_state["menu"] = "Resumo 📊"

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
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        nome = st.text_input("Digite seu nome para entrar como visitante")
        if st.button("Entrar como visitante"):
            if nome.strip():
                st.session_state["usuario"] = f"visitante-{nome.strip()}"
                registrar_acesso(f"login-visitante:{nome.strip()}")
                st.success(f"Bem-vindo(a), visitante {nome.strip()}!")

# ================== Execução do login ==================
if st.session_state["usuario"] is None:
    login()
    st.stop()  # impede execução das telas principais até login
# ================== Funções principais ==================
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

def adicionar_produto_manual(cod, nome, preco):
    cod = int(cod)
    st.session_state["produtos"][cod] = {"nome": nome.strip(), "preco": float(preco)}
    save_db()
    st.success(f"Produto {nome} adicionado/atualizado!")

# ================== Telas ==================
# ================== Telas ==================

def tela_resumo():
    st.header("📊 Resumo Geral")
    total_geral = 0
    for c, vendas in st.session_state["clientes"].items():
        total_cliente = sum(v.get("preco", 0) * v.get("quantidade", 1) for v in vendas)
        total_geral += total_cliente
        st.write(f"Cliente {c}: R$ {total_cliente:.2f}")
    st.markdown(f"**💰 Total geral: R$ {total_geral:.2f}**")
    # Comissão: 25% até metade do total, 35% até total completo, 40% total geral
    com_25 = total_geral * 0.25
    com_35 = total_geral * 0.35
    com_40 = total_geral * 0.40
    st.write(f"Comissão 25%: R$ {com_25:.2f}")
    st.write(f"Comissão 35%: R$ {com_35:.2f}")
    st.write(f"Comissão 40%: R$ {com_40:.2f}")

def tela_pdf():
    st.header("📄 Importar Estoque via Nota Fiscal (PDF)")
    if is_visitante():
        st.info("🔒 Apenas usuários logados podem importar PDF.")
        return
    pdf_file = st.file_uploader("Selecione o PDF da nota fiscal", type=["pdf"], key="upload_pdf")
    if pdf_file is not None:
        if st.button("Substituir estoque pelo PDF", key="btn_substituir_pdf"):
            substituir_estoque_pdf(pdf_file)

def tela_produtos():
    st.header("📦 Produtos")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Listar/Buscar", "Adicionar"], horizontal=True, key="acao_produtos")
    
    if acao == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar produtos.")
            return
        cod = st.number_input("Código", min_value=1, step=1, key="codigo_produto")
        nome = st.text_input("Nome do produto", key="nome_produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.10, format="%.2f", key="preco_produto")
        if st.button("Salvar produto", key="btn_salvar_produto"):
            if cod in st.session_state["produtos"]:
                st.warning("Código já existe.")
            elif not nome.strip():
                st.warning("Informe um nome válido.")
            else:
                adicionar_produto_manual(cod, nome, preco)
    else:
        termo = st.text_input("Buscar por nome ou código", key="busca_produtos").lower()
        st.subheader("Lista de Produtos")
        for cod, dados in sorted(st.session_state["produtos"].items(), key=lambda x: x[1]["nome"].lower()):
            if termo in str(cod) or termo in dados["nome"].lower() or termo == "":
                st.write(f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f})")

def tela_clientes():
    st.header("👥 Clientes")
    visitante = is_visitante()
    aba = st.radio("Ação", ["Consultar cliente", "Cadastrar cliente"], horizontal=True, key="acao_clientes")
    
    if visitante and aba == "Cadastrar cliente":
        st.info("🔒 Visitantes não podem cadastrar clientes.")
        return
    
    if aba == "Cadastrar cliente":
        nome = st.text_input("Nome do cliente", key="nome_cliente")
        if st.button("Salvar cliente", key="btn_salvar_cliente"):
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
    filtro = st.text_input("Buscar cliente (2+ letras)", key="filtro_cliente").lower()
    matches = [c for c in st.session_state["clientes"] if filtro in c.lower()]
    cliente = st.selectbox("Selecione o cliente", matches, key="select_cliente") if matches else None
    
    if cliente:
        st.subheader(f"{cliente}")
        vendas = st.session_state["clientes"].get(cliente, [])
        
        # Adicionar venda
        st.markdown("### ➕ Registrar venda")
        produtos_opcoes = [f"{cod} - {dados['nome']}" for cod, dados in st.session_state["produtos"].items()]
        produto_sel = st.selectbox("Escolha o produto", produtos_opcoes, key="select_venda_produto")
        quantidade = st.number_input("Quantidade", min_value=1, step=1, key="quantidade_venda")
        if st.button("Adicionar venda", key="btn_adicionar_venda"):
            cod_selecionado = int(produto_sel.split(" - ")[0])
            nome_prod = st.session_state["produtos"][cod_selecionado]["nome"]
            preco_prod = st.session_state["produtos"][cod_selecionado]["preco"]
            vendas.append({"cod": cod_selecionado, "nome": nome_prod, "preco": preco_prod, "quantidade": quantidade})
            st.session_state["clientes"][cliente] = vendas
            save_db()
            st.success(f"Venda adicionada: {nome_prod} x {quantidade}")
        
        # Listar vendas
        st.markdown("### 📝 Vendas do cliente")
        for idx, v in enumerate(vendas):
            st.write(f"{idx+1}. {v['cod']} - {v['nome']} x {v['quantidade']} (R$ {v['preco']:.2f} cada)")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Apagar {idx+1}", key=f"apagar_{idx}"):
                    vendas.pop(idx)
                    st.session_state["clientes"][cliente] = vendas
                    save_db()
                    st.experimental_rerun()
            with col2:
                nova_qtde = st.number_input(f"Editar Qtde {idx+1}", min_value=1, value=v["quantidade"], key=f"editar_{idx}")
                if st.button(f"Salvar {idx+1}", key=f"salvar_{idx}"):
                    vendas[idx]["quantidade"] = nova_qtde
                    st.session_state["clientes"][cliente] = vendas
                    save_db()
                    st.success("Venda atualizada")
        
        if st.button("Zerar vendas deste cliente", key="zerar_vendas_cliente"):
            st.session_state["clientes"][cliente] = []
            save_db()
            st.success(f"Vendas de {cliente} zeradas!")
# ================== Menu lateral moderno ==================
def bloco_backup_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧰 Backup")
    # Exportar
    db_json = json.dumps({
        "produtos": st.session_state["produtos"],
        "clientes": st.session_state["clientes"]
    }, ensure_ascii=False, indent=2)
    st.sidebar.download_button(
        "⬇️ Exportar backup (.json)",
        data=db_json.encode("utf-8"),
        file_name="backup_sistema_vendas.json"
    )
    # Restaurar
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
    menu_items = [
        ("Resumo 📊", tela_resumo),
        ("Upload PDF 📄", tela_pdf),
        ("Clientes 👥", tela_clientes),
        ("Produtos 📦", tela_produtos),
        ("Relatórios 📋", relatorio_geral),
        ("Sair 🚪", None)
    ]
    if not is_visitante():
        menu_items.insert(-1, ("Backup 🗂️", None))

    # Menu moderno usando botões
    for title, func in menu_items:
        if st.sidebar.button(title):
            st.session_state["menu"] = title
            if title == "Sair 🚪":
                st.session_state.clear()
                st.experimental_rerun()
    
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
    menu = st.session_state.get("menu", "Resumo 📊")
    if menu == "Resumo 📊":
        tela_resumo()
    elif menu == "Upload PDF 📄":
        tela_pdf()
    elif menu == "Clientes 👥":
        tela_clientes()
    elif menu == "Produtos 📦":
        tela_produtos()
    elif menu == "Relatórios 📋":
        relatorio_geral()
    elif menu == "Backup 🗂️":
        st.header("🗂️ Backup")
        st.info("Use a lateral para exportar ou restaurar backup.")

# ================== Main ==================
def main():
    if "usuario" not in st.session_state:
        st.session_state["usuario"] = None
    if "menu" not in st.session_state:
        st.session_state["menu"] = "Resumo 📊"

    if st.session_state["usuario"] is None:
        login()
        st.stop()  # impede execução das telas principais até login

    barra_lateral()
    roteador()

if __name__ == "__main__":
    main()