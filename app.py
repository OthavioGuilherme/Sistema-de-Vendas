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
USERS = {"othavio": "122008", "isabela": "122008"}  # usuários e senhas simples
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

    # cadastro
    if not visitante:
        with st.form("form_cliente"):
            nome = st.text_input("Nome do Cliente", key="form_cliente_nome")
            if st.form_submit_button("Cadastrar"):
                if not nome.strip():
                    st.warning("Informe um nome válido.")
                elif nome.strip() in st.session_state["clientes"]:
                    st.warning("Cliente já existe.")
                else:
                    st.session_state["clientes"][nome.strip()] = []
                    save_db()
                    st.success(f"Cliente {nome.strip()} cadastrado!")
    else:
        st.info("🔒 Visitantes não podem cadastrar clientes.")

    st.markdown("---")
    st.subheader("Lista de Clientes")
    if not st.session_state["clientes"]:
        st.info("Nenhum cliente cadastrado.")
    for cliente in list(st.session_state["clientes"].keys()):
        cols = st.columns([4,1,1])
        cols[0].write(cliente)
        # botão visualizar vendas
        if cols[1].button("Ver Vendas", key=f"vervendas_{cliente}"):
            st.session_state["venda_cliente_selecionado"] = cliente
            st.session_state["menu_aba_selecionada"] = "Vendas 💰"
            st.rerun()
        # apagar com confirmação
        if not visitante:
            confirmar_key = f"confirm_apagar_{cliente}"
            confirmar = cols[2].checkbox("Confirmar", key=confirmar_key)
            if confirmar:
                if cols[2].button(f"🗑️ Apagar", key=f"btn_apagar_{cliente}"):
                    st.session_state["clientes"].pop(cliente, None)
                    save_db()
                    if st.session_state.get("venda_cliente_selecionado") == cliente:
                        st.session_state.pop("venda_cliente_selecionado", None)
                    st.success(f"Cliente {cliente} apagado!")
                    st.rerun()
        else:
            cols[2].button("Apagar", key=f"disabled_apagar_{cliente}", disabled=True)

# ================== Vendas ==================
def tela_vendas():
    st.header("💰 Vendas")
    visitante = is_visitante()
    clientes = list(st.session_state["clientes"].keys())
    if not clientes:
        st.info("Nenhum cliente cadastrado.")
        return

    cliente_sel = st.selectbox(
        "Selecione o cliente",
        clientes,
        index=(clientes.index(st.session_state.get("venda_cliente_selecionado")) 
               if st.session_state.get("venda_cliente_selecionado") in clientes else 0)
    )

    vendas = st.session_state["clientes"].get(cliente_sel, [])

    st.markdown("### ➕ Adicionar Venda")
    if not visitante:
        produto_input = st.text_input("Buscar produto por código ou nome", key="venda_busca_produto")
        opcoes_produtos = [
            f"{cod} - {p['nome']}" for cod, p in st.session_state["produtos"].items()
            if produto_input.lower() in str(cod) or produto_input.lower() in p["nome"].lower()
        ]
        if opcoes_produtos:
            produto_selecionado = st.selectbox("Produto", [""] + opcoes_produtos, key="venda_select_produto")
        else:
            produto_selecionado = None
        quantidade = st.number_input("Quantidade", min_value=1, step=1, key="venda_qtd")
        if st.button("Adicionar venda", key="btn_adicionar_venda"):
            if produto_selecionado and produto_selecionado != "":
                cod = int(produto_selecionado.split(" - ")[0])
                p = st.session_state["produtos"][cod]
                if quantidade > p.get("quantidade", 0):
                    st.warning(f"Estoque insuficiente! Disponível: {p.get('quantidade',0)}")
                else:
                    vendas.append({"cod": cod, "nome": p["nome"], "preco": p["preco"], "quantidade": quantidade})
                    p["quantidade"] -= quantidade  # atualiza estoque
                    st.session_state["clientes"][cliente_sel] = vendas
                    save_db()
                    st.success(f"Venda adicionada ao cliente {cliente_sel}!")
                    st.rerun()
            else:
                st.warning("Escolha um produto válido.")
    else:
        st.info("🔒 Visitantes não podem adicionar vendas.")

    st.markdown("### 📝 Vendas do Cliente")
    if not vendas:
        st.info("Nenhuma venda registrada para este cliente.")
    for idx, v in enumerate(vendas):
        col1, col2, col3 = st.columns([5,1.5,1.5])
        cod = v.get("cod")
        nome = v.get("nome", "???")
        quantidade = v.get("quantidade", 0)
        preco = v.get("preco", 0.0)
        valor_exibir = f"R$ {preco:.2f}" if not visitante else "R$ *****"
        col1.write(f"{cod} - {nome} x {quantidade} ({valor_exibir} cada)")

        if visitante:
            col2.button("Apagar", key=f"apagar_disabled_{cliente_sel}_{idx}", disabled=True)
            col3.number_input("Qtde", min_value=1, value=quantidade, key=f"editar_disabled_{cliente_sel}_{idx}", disabled=True)
        else:
            if col2.button("Apagar", key=f"apagar_{cliente_sel}_{idx}"):
                vendas.pop(idx)
                st.session_state["clientes"][cliente_sel] = vendas
                st.session_state["produtos"][cod]["quantidade"] += quantidade  # devolve ao estoque
                save_db()
                st.success("Venda apagada")
                st.rerun()
            nova_qtd = col3.number_input("Qtde", min_value=1, value=quantidade, key=f"editar_{cliente_sel}_{idx}")
            if col3.button("Salvar", key=f"salvar_{cliente_sel}_{idx}"):
                diff = nova_qtd - quantidade
                if diff > st.session_state["produtos"][cod]["quantidade"]:
                    st.warning(f"Estoque insuficiente! Disponível: {st.session_state['produtos'][cod]['quantidade']}")
                else:
                    vendas[idx]["quantidade"] = nova_qtd
                    st.session_state["produtos"][cod]["quantidade"] -= diff
                    st.session_state["clientes"][cliente_sel] = vendas
                    save_db()
                    st.success("Venda atualizada")
                    st.rerun()

# ================== Relatórios ==================
def tela_relatorios():
    st.header("📊 Relatórios")
    visitante = is_visitante()

    if visitante:
        st.warning("Visitante não pode ver valores de vendas e comissão.")
        for cliente, vendas in st.session_state["clientes"].items():
            st.write(f"Cliente: {cliente}")
            for v in vendas:
                st.write(f"- {v.get('nome','?')} x {v.get('quantidade',0)} (R$ **** cada)")
        return

    total_geral = 0.0
    for cliente, vendas in st.session_state["clientes"].items():
        total_cliente = sum((v.get("preco",0.0)*v.get("quantidade",0)) for v in vendas)
        st.subheader(f"Cliente: {cliente} — Total R$ {total_cliente:.2f}")
        for v in vendas:
            st.write(f"- {v.get('nome','?')} x {v.get('quantidade',0)} (R$ {v.get('preco',0.0):.2f} cada)")
        total_geral += total_cliente

    comissao = total_geral * 0.25
    st.success(f"💰 Total Geral: R$ {total_geral:.2f} | Comissão: R$ {comissao:.2f}")

# ================== NAVEGAÇÃO ==================
def main_tabs():
    tabs = st.tabs(["Resumo 📊", "Clientes 👥", "Produtos 📦", "Vendas 💰", "Relatórios 📋", "Config ⚙️"])
    with tabs[0]: tela_resumo()
    with tabs[1]: tela_clientes()
    with tabs[2]: tela_produtos()
    with tabs[3]: tela_vendas()
    with tabs[4]: tela_relatorios()
    with tabs[5]:
        st.header("⚙️ Configuração")
        st.write(f"Usuário atual: **{st.session_state.get('usuario', '---')}**")
        if st.button("🚪 Sair"):
            st.session_state.clear()
            st.session_state["usuario"] = None
            st.rerun()

# ================== MAIN ==================
def main():
    if st.session_state.get("usuario") is None:
        login()
    else:
        main_tabs()

if __name__ == "__main__":
    main()