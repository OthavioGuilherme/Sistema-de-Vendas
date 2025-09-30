# ================= PARTE 1 ==============
import streamlit as st
from datetime import datetime
import sqlite3
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
DB_FILE = "vendas.db"

# ================== Conexão SQLite ==================
def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS produtos (
        cod INTEGER PRIMARY KEY,
        nome TEXT,
        preco REAL,
        quantidade INTEGER
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        produto_cod INTEGER,
        quantidade INTEGER,
        data TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(produto_cod) REFERENCES produtos(cod)
    )""")
    conn.commit()
    conn.close()

init_db()

# ================== Registro de acesso ==================
def registrar_acesso(usuario: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {usuario}\n")
    except:
        pass

# ================== Session State inicial ==================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "menu" not in st.session_state:
    st.session_state["menu"] = "Resumo 📊"

# ================== Função: is_visitante ==================
def is_visitante():
    u = st.session_state.get("usuario")
    return isinstance(u, str) and u.startswith("visitante-")
# ========= PARTE 2 ================
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

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT SUM(v.quantidade * p.preco)
                   FROM vendas v 
                   JOIN produtos p ON v.produto_cod = p.cod""")
    total_geral = cur.fetchone()[0] or 0.0
    conn.close()

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

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos")  # limpa estoque
    for cod, dados in novos_produtos.items():
        cur.execute("INSERT OR REPLACE INTO produtos (cod, nome, preco, quantidade) VALUES (?, ?, ?, ?)",
                    (cod, dados["nome"], dados["preco"], dados["quantidade"]))
    conn.commit()
    conn.close()

    st.success("✅ Estoque atualizado a partir do PDF!")

# ================== Produtos ==================
def adicionar_produto_manual(cod, nome, preco, qtd=10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO produtos (cod, nome, preco, quantidade) VALUES (?, ?, ?, ?)",
                (int(cod), nome.strip(), float(preco), int(qtd)))
    conn.commit()
    conn.close()
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
            if not nome.strip():
                st.warning("Informe um nome válido.")
            else:
                adicionar_produto_manual(cod, nome, preco, quantidade)

    elif acao == "Listar/Buscar":
        termo = st.text_input("Buscar por nome ou código").lower()
        st.subheader("Lista de Produtos")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT cod, nome, preco, quantidade FROM produtos ORDER BY cod")
        produtos = cur.fetchall()
        conn.close()

        for cod, nome, preco, qtd in produtos:
            if termo in str(cod) or termo in nome.lower() or termo == "":
                st.write(f"{cod} - {nome} (R$ {preco:.2f}) | Estoque: {qtd}")

    elif acao == "Importar PDF":
        if visitante:
            st.info("🔒 Visitantes não podem importar PDF.")
            return
        pdf_file = st.file_uploader("Selecione o PDF da nota fiscal", type=["pdf"])
        if pdf_file is not None:
            if st.button("Substituir estoque pelo PDF"):
                substituir_estoque_pdf(pdf_file)
# ================ PARTE 3 =================
# ================== Clientes ==================
def adicionar_cliente(nome):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO clientes (nome) VALUES (?)", (nome.strip(),))
    conn.commit()
    conn.close()
    st.success(f"Cliente {nome} adicionado!")

def tela_clientes():
    st.header("👥 Clientes")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Listar", "Adicionar"], horizontal=True)

    if acao == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar clientes.")
            return
        nome = st.text_input("Nome do cliente")
        if st.button("Salvar cliente"):
            if nome.strip():
                adicionar_cliente(nome)
            else:
                st.warning("Digite um nome válido.")

    else:  # Listar
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, nome FROM clientes ORDER BY nome")
        clientes = cur.fetchall()
        conn.close()

        st.subheader("Lista de Clientes")
        for cid, nome in clientes:
            st.write(f"{cid} - {nome}")

# ================== Vendas ==================
def registrar_venda(cliente_nome, produto_cod, quantidade):
    conn = get_conn()
    cur = conn.cursor()

    # Garante cliente
    cur.execute("INSERT OR IGNORE INTO clientes (nome) VALUES (?)", (cliente_nome.strip(),))
    conn.commit()
    cur.execute("SELECT id FROM clientes WHERE nome=?", (cliente_nome.strip(),))
    cliente_id = cur.fetchone()[0]

    # Confere estoque
    cur.execute("SELECT quantidade FROM produtos WHERE cod=?", (produto_cod,))
    row = cur.fetchone()
    if not row:
        st.error("Produto não encontrado.")
        conn.close()
        return
    estoque = row[0]
    if quantidade > estoque:
        st.error("Quantidade maior que estoque disponível.")
        conn.close()
        return

    # Lança venda
    cur.execute("""INSERT INTO vendas (cliente_id, produto_cod, quantidade, data)
                   VALUES (?, ?, ?, ?)""",
                (cliente_id, produto_cod, quantidade, datetime.now().isoformat()))
    cur.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE cod=?", (quantidade, produto_cod))
    conn.commit()
    conn.close()
    st.success("✅ Venda registrada!")

def tela_vendas():
    st.header("🛒 Vendas")
    visitante = is_visitante()
    if visitante:
        st.info("🔒 Visitantes não podem registrar vendas.")
        return

    # Escolher cliente
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT nome FROM clientes ORDER BY nome")
    clientes = [r[0] for r in cur.fetchall()]
    conn.close()

    cliente_nome = st.selectbox("Cliente", clientes)

    # Escolher produto
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cod, nome, preco, quantidade FROM produtos ORDER BY nome")
    produtos = cur.fetchall()
    conn.close()

    produto_opcoes = {f"{nome} (R$ {preco:.2f}, estoque {qtd})": cod for cod, nome, preco, qtd in produtos}
    produto_escolhido = st.selectbox("Produto", list(produto_opcoes.keys()))
    qtd = st.number_input("Quantidade", min_value=1, step=1)

    if st.button("Registrar Venda"):
        registrar_venda(cliente_nome, produto_opcoes[produto_escolhido], qtd)

# ================== Relatórios ==================
def tela_relatorios():
    st.header("📑 Relatórios")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT c.nome, p.nome, v.quantidade, p.preco, v.data
                   FROM vendas v
                   JOIN clientes c ON v.cliente_id = c.id
                   JOIN produtos p ON v.produto_cod = p.cod
                   ORDER BY v.data DESC""")
    vendas = cur.fetchall()
    conn.close()

    if not vendas:
        st.info("Nenhuma venda registrada ainda.")
        return

    for cliente, produto, qtd, preco, data in vendas:
        st.write(f"🧾 {data[:16]} | Cliente: {cliente} | Produto: {produto} | "
                 f"Qtd: {qtd} | Valor: R$ {qtd*preco:.2f}")

# ================== Navegação ==================
def menu_principal():
    st.sidebar.title("📌 Menu")
    escolha = st.sidebar.radio("Ir para:", 
        ["Resumo 📊", "Produtos 📦", "Clientes 👥", "Vendas 🛒", "Relatórios 📑", "Sair 🚪"])

    st.session_state["menu"] = escolha

    if escolha == "Resumo 📊":
        tela_resumo()
    elif escolha == "Produtos 📦":
        tela_produtos()
    elif escolha == "Clientes 👥":
        tela_clientes()
    elif escolha == "Vendas 🛒":
        tela_vendas()
    elif escolha == "Relatórios 📑":
        tela_relatorios()
    elif escolha == "Sair 🚪":
        st.session_state["usuario"] = None
        st.success("Você saiu do sistema.")
        st.rerun()

# ================== Main ==================
def main():
    if not st.session_state["usuario"]:
        login()
    else:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
        menu_principal()

if __name__ == "__main__":
    main()