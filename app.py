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
        usuario = st.text_input("Usuário", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", key="btn_login_usuario"):
            if usuario in USERS and USERS[usuario] == senha:
                st.session_state["usuario"] = usuario
                registrar_acesso(f"login-usuario:{usuario}")
                st.success(f"Bem-vindo(a), {usuario}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        nome = st.text_input("Digite seu nome para entrar como visitante", key="login_visitante")
        if st.button("Entrar como visitante", key="btn_login_visitante"):
            if nome.strip():
                st.session_state["usuario"] = f"visitante-{nome.strip()}"
                registrar_acesso(f"login-visitante:{nome.strip()}")
                st.success(f"Bem-vindo(a), visitante {nome.strip()}!")
                st.experimental_rerun()

# ================== Substituir estoque via PDF ==================
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

# ================== Adicionar/Atualizar produto manual ==================
def adicionar_produto_manual(cod, nome, preco):
    cod = int(cod)
    st.session_state["produtos"][cod] = {"nome": nome.strip(), "preco": float(preco)}
    save_db()
    st.success(f"Produto {nome} adicionado/atualizado!")
# ================== TELAS ==================

# ---------------- Tela Resumo ----------------
def tela_resumo():
    st.header("📊 Resumo de Vendas")
    total_geral = 0
    for cliente, vendas in st.session_state["clientes"].items():
        total_cliente = sum(v.get("preco", 0) * v.get("quantidade", 1) for v in vendas)
        total_geral += total_cliente
        st.write(f"- {cliente}: R$ {total_cliente:.2f}")
    
    st.markdown(f"### 💰 Total geral: R$ {total_geral:.2f}")
    
    # Comissão progressiva
    if total_geral <= 1000:
        comissao = 0.25
    elif total_geral <= 5000:
        comissao = 0.30
    else:
        comissao = 0.40
    st.markdown(f"### 🏆 Comissão: {comissao*100:.0f}%")

# ---------------- Tela PDF ----------------
def tela_pdf():
    st.header("📄 Importar Estoque via Nota Fiscal (PDF)")
    if is_visitante():
        st.info("🔒 Apenas usuários logados podem importar PDF.")
        return
    pdf_file = st.file_uploader("Selecione o PDF da nota fiscal", type=["pdf"])
    if pdf_file is not None:
        if st.button("Substituir estoque pelo PDF"):
            substituir_estoque_pdf(pdf_file)

# ---------------- Tela Produtos ----------------
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

# ---------------- Tela Clientes ----------------
def tela_clientes():
    st.header("👥 Clientes")
    visitante = is_visitante()
    aba = st.radio("Ação", ["Consultar cliente", "Cadastrar cliente"], horizontal=True)
    
    if visitante and aba == "Cadastrar cliente":
        st.info("🔒 Visitantes não podem cadastrar clientes.")
        return
    
    # Cadastrar cliente
    if aba == "Cadastrar cliente":
        nome = st.text_input("Nome do cliente", key="nome_cliente")
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
    
    # Consultar cliente e registrar venda
    filtro = st.text_input("Buscar cliente (2+ letras)", key="buscar_cliente").lower()
    matches = [c for c in st.session_state["clientes"] if filtro in c.lower()]
    cliente = st.selectbox("Selecione o cliente", matches) if matches else None
    
    if cliente:
        st.subheader(f"{cliente}")
        vendas = st.session_state["clientes"].get(cliente, [])

        # Botão zerar vendas
        if not visitante:
            if st.button("🗑️ Zerar todas as vendas deste cliente", key=f"zerar_{cliente}"):
                st.session_state["clientes"][cliente] = []
                save_db()
                st.success("Vendas zeradas!")
                st.experimental_rerun()

        # Adicionar venda
        st.markdown("### ➕ Adicionar venda")
        produto_input = st.text_input(
            "Produto (código ou nome)",
            key=f"produto_input_{cliente}"
        )
        # Autocomplete de produtos
        opcoes_produtos = [
            f"{cod} - {p['nome']} (R$ {p['preco']:.2f})"
            for cod, p in st.session_state["produtos"].items()
            if produto_input.lower() in str(cod) or produto_input.lower() in p["nome"].lower()
        ]
        produto_selecionado = st.selectbox("Selecione o produto", opcoes_produtos, key=f"select_prod_{cliente}") if opcoes_produtos else None
        quantidade = st.number_input("Quantidade", min_value=1, step=1, key=f"qtde_venda_{cliente}")
        if st.button("Adicionar venda", key=f"btn_add_venda_{cliente}"):
            if produto_selecionado:
                cod = int(produto_selecionado.split(" - ")[0])
                p = st.session_state["produtos"][cod]
                vendas.append({
                    "cod": cod,
                    "nome": p["nome"],
                    "preco": p["preco"],
                    "quantidade": quantidade
                })
                st.session_state["clientes"][cliente] = vendas
                save_db()
                st.success(f"{quantidade}x {p['nome']} adicionados à venda")
                st.experimental_rerun()
            else:
                st.warning("Selecione um produto válido.")

        # Listar vendas do cliente com opção editar/apagar
        st.markdown("### 📝 Vendas do Cliente")
        if vendas:
            for idx, v in enumerate(vendas):
                col1, col2, col3 = st.columns([5,2,2])
                col1.write(f"{v['cod']} - {v['nome']} x {v['quantidade']} (R$ {v['preco']:.2f} cada)")
                if col2.button("Apagar", key=f"apagar_{cliente}_{idx}"):
                    vendas.pop(idx)
                    st.session_state["clientes"][cliente] = vendas
                    save_db()
                    st.experimental_rerun()
                nova_qtde = st.number_input("Editar Qtde", min_value=1, value=v["quantidade"], key=f"editar_{cliente}_{idx}")
                if col3.button("Salvar", key=f"salvar_{cliente}_{idx}"):
                    vendas[idx]["quantidade"] = nova_qtde
                    st.session_state["clientes"][cliente] = vendas
                    save_db()
                    st.success("Venda atualizada")
        else:
            st.write("Nenhuma venda registrada.")
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
    ]
    
    # Usuário logado pode acessar backup
    if not is_visitante():
        menu_items.append(("Backup 🗂️", bloco_backup_sidebar))
    
    menu_items.append(("Sair 🚪", None))
    
    # Menu moderno via selectbox
    opcoes_dict = {title: func for title, func in menu_items}
    menu_selecionado = st.sidebar.selectbox(
        "Menu",
        list(opcoes_dict.keys()),
        index=list(opcoes_dict.keys()).index(st.session_state.get("menu", "Resumo 📊"))
    )
    st.session_state["menu"] = menu_selecionado
    
    # Executa a função correspondente
    func = opcoes_dict.get(menu_selecionado)
    if func:
        func()
    elif menu_selecionado == "Sair 🚪":
        st.session_state.clear()
        st.experimental_rerun()
    
    # Mostra bloco de backup caso seja usuário logado
    if not is_visitante():
        bloco_backup_sidebar()
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

    # Executa login se não houver usuário logado
    if st.session_state["usuario"] is None:
        login()
        st.stop()  # impede execução das telas principais até login

    # Barra lateral moderna
    barra_lateral()

    # Roteador executa a tela selecionada
    roteador()

# ================== Execução ==================
if __name__ == "__main__":
    main()