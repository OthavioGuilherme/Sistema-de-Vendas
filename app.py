# ================= PARTE 1 =================
# CONFIGURAÇÕES DA PLANILHA
PLANILHA_NOME = "Sistema de vendas"
ABA_VENDAS = "Vendas"
ABA_CLIENTES = "Clientes"
ABA_PRODUTOS = "Produtos"

# BIBLIOTECAS
import gspread
from gspread.exceptions import WorksheetNotFound, SpreadsheetNotFound
import json
import streamlit as st
from datetime import datetime
import os
import io
import re

try:
    import pdfplumber
except Exception:
    pdfplumber = None

st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# ================== Usuários ==================
USERS = {"othavio": "122008", "isabela": "122008"}
LOG_FILE = "acessos.log"
DB_FILE = "db.json"

# ================== Conexão com Google Sheets ==================
GSHEETS_CONECTADO = False
gc = None

from google.oauth2 import service_account

try:
    credentials_dict = st.secrets["GCP_SA_CREDENTIALS"]
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = service_account.Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    gc = gspread.authorize(creds)
    GSHEETS_CONECTADO = True

except KeyError:
    st.error("❌ ERRO DE CONFIGURAÇÃO: Streamlit não encontrou a chave 'GCP_SA_CREDENTIALS' nos Secrets.")
    st.info("Rodando sem conexão com o Google Sheets.")

except Exception as e:
    st.error(f"❌ ERRO FATAL AO CONECTAR: {type(e).__name__} - {e}")

# ================== Registro de acesso ==================
def registrar_acesso(usuario: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {usuario}\n")
    except:
        pass

# ================== Funções Google Sheets ==================
def gsheets_append_produto(cod: int, nome: str, preco: float, quantidade: int):
    if not GSHEETS_CONECTADO:
        return
    try:
        planilha = gc.open(PLANILHA_NOME)
        aba = planilha.worksheet(ABA_PRODUTOS)
        nova_linha = [cod, nome, f"{preco:.2f}".replace('.',','), quantidade]
        aba.append_row(nova_linha, value_input_option='USER_ENTERED')
    except Exception as e:
        st.warning(f"Falha ao salvar produto no Google Sheets: {e}")

def gsheets_append_venda(cliente: str, produto: str, quantidade: int, preco: float):
    if not GSHEETS_CONECTADO:
        return
    try:
        data_registro = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha = gc.open(PLANILHA_NOME)
        aba = planilha.worksheet(ABA_VENDAS)
        nova_linha = [
            data_registro,
            cliente,
            produto,
            quantidade,
            f"{preco:.2f}".replace('.',','),
            f"{(preco * quantidade):.2f}".replace('.',',')
        ]
        aba.append_row(nova_linha, value_input_option='USER_ENTERED')
    except Exception as e:
        st.warning(f"Falha ao salvar venda no Google Sheets: {e}")

def gsheets_adicionar_cliente(nome: str):
    if not GSHEETS_CONECTADO:
        return
    try:
        planilha = gc.open(PLANILHA_NOME)
        aba = planilha.worksheet(ABA_CLIENTES)
        aba.append_row([nome], value_input_option='USER_ENTERED')
    except Exception as e:
        st.warning(f"Falha ao salvar cliente no Google Sheets: {e}")

# ================== Helpers local DB ==================
def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "produtos": st.session_state.get("produtos", {}),
                "clientes": st.session_state.get("clientes", {}),
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Falha ao salvar DB local: {e}")

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
    default_clients = {"Tabata": [], "Valquiria": [], "Vanessa": [], "Pamela": [], "Elan": [], "Claudinha": []}
    return {}, default_clients

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "produtos" not in st.session_state:
    prods_loaded, clients_loaded = load_db()
    st.session_state["produtos"] = prods_loaded or {}
    st.session_state["clientes"] = clients_loaded or {"Tabata": [], "Valquiria": [], "Vanessa": [], "Pamela": [], "Elan": [], "Claudinha": []}

def is_visitante():
    u = st.session_state.get("usuario")
    return isinstance(u, str) and u.startswith("visitante-")

# ================== Sincronização inicial ==================
def sincronizar_tudo_gsheets():
    if not GSHEETS_CONECTADO:
        st.warning("❌ Google Sheets não conectado. Nenhum dado será enviado.")
        return
    
    # Clientes
    for cliente in st.session_state["clientes"].keys():
        try:
            gsheets_adicionar_cliente(cliente)
        except:
            pass
    
    # Produtos
    for cod, dados in st.session_state["produtos"].items():
        try:
            gsheets_append_produto(cod, dados["nome"], dados["preco"], dados.get("quantidade", 0))
        except:
            pass
    
    # Vendas
    for cliente, vendas in st.session_state["clientes"].items():
        for v in vendas:
            try:
                gsheets_append_venda(cliente, v["nome"], v["quantidade"], v["preco"])
            except:
                pass
    
    st.success("✅ Todos os dados existentes foram enviados para o Google Sheets!")
# ================= PARTE 2 =================
# ================== Login ==================
def login():
    st.title("🔐 Login")
    escolha = st.radio("Como deseja entrar?", ["Usuário cadastrado", "Visitante"], horizontal=True)

    if escolha == "Usuário cadastrado":
        usuario_input = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            usuario = usuario_input.lower().strip()  # aceita maiúscula/minúscula
            if usuario in USERS and USERS[usuario] == senha:
                st.session_state["usuario"] = usuario
                registrar_acesso(f"login-usuario:{usuario}")
                st.success(f"Bem-vindo(a), {usuario_input}!")

                # Notificação de Google Sheets conectado
                if GSHEETS_CONECTADO:
                    st.info("Google Sheets conectado ✅")
                    if st.button("Sincronizar todos os dados existentes"):
                        sincronizar_tudo_gsheets()

                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    else:  # Visitante
        nome = st.text_input("Digite seu nome")
        if st.button("Entrar como visitante"):
            if nome.strip():
                st.session_state["usuario"] = f"visitante-{nome.strip()}"
                registrar_acesso(f"login-visitante:{nome.strip()}")
                st.success(f"Bem-vindo(a), visitante {nome.strip()}!")
                st.rerun()

# ================== Produtos ==================
def adicionar_produto_manual(cod, nome, preco, qtd=10):
    cod = int(cod)
    st.session_state["produtos"][cod] = {"nome": nome.strip(), "preco": float(preco), "quantidade": qtd}
    save_db()
    gsheets_append_produto(cod, nome.strip(), float(preco), qtd)
    st.success(f"Produto {nome} adicionado/atualizado e salvo no Google Sheets!")

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
                        try: qtd = int(qtd_s)
                        except: qtd = 0
                        try: cod = int(cod_s)
                        except: cod = None
                        try: preco = float(preco_s.replace('.', '').replace(',', '.'))
                        except: preco = 0.0
                        if cod is not None:
                            novos_produtos[cod] = {"nome": nome.title(), "preco": preco, "quantidade": qtd}
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
        return

    if not novos_produtos:
        st.error("Nenhum produto válido encontrado no PDF.")
        return

    st.session_state["produtos"] = novos_produtos
    save_db()
    
    for cod, dados in novos_produtos.items():
        gsheets_append_produto(cod, dados["nome"], dados["preco"], dados["quantidade"])
    
    st.success("✅ Estoque atualizado a partir do PDF e salvo no Google Sheets!")

def tela_produtos():
    st.header("📦 Produtos")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Adicionar", "Listar/Buscar", "Importar PDF"], horizontal=True)

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
        for cod, dados in sorted(st.session_state["produtos"].items(), key=lambda x: str(x)):
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

# ================== Clientes ==================
def tela_clientes():
    st.header("👥 Clientes")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Adicionar", "Listar"], horizontal=True)

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
                gsheets_adicionar_cliente(nome)
                st.success(f"Cliente {nome} adicionado e salvo no Google Sheets!")
    elif acao == "Listar":
        st.subheader("Lista de Clientes")
        for cliente in sorted(st.session_state["clientes"].keys()):
            st.write(cliente)
# ================= PARTE 3 =================
# ================== Vendas ==================
def registrar_venda(cliente, codigo, quantidade):
    produtos = st.session_state["produtos"]
    if codigo not in produtos:
        st.error("Produto não encontrado.")
        return
    if produtos[codigo].get("quantidade", 0) < quantidade:
        st.error("Estoque insuficiente.")
        return
    produtos[codigo]["quantidade"] -= quantidade
    venda = {
        "codigo": codigo,
        "nome": produtos[codigo]["nome"],
        "preco": produtos[codigo]["preco"],
        "quantidade": quantidade,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    st.session_state["clientes"][cliente].append(venda)
    save_db()
    gsheets_append_venda(cliente, produtos[codigo]["nome"], quantidade, produtos[codigo]["preco"])
    st.success("Venda registrada e salva no Google Sheets!")

def tela_vendas():
    st.header("🛒 Vendas")
    if not st.session_state["clientes"]:
        st.warning("Cadastre um cliente primeiro.")
        return
    if not st.session_state["produtos"]:
        st.warning("Cadastre produtos primeiro.")
        return

    cliente = st.selectbox("Selecione o cliente", list(st.session_state["clientes"].keys()))

    # Autocomplete para código de produto
    codigos_produtos = {str(k): v["nome"] for k, v in st.session_state["produtos"].items()}
    codigo_str = st.text_input("Digite o código do produto", "")
    produtos_filtrados = {k: v for k, v in codigos_produtos.items() if k.startswith(codigo_str)}
    if produtos_filtrados and codigo_str:
        st.write("Sugestões de produtos:")
        for k, v in produtos_filtrados.items():
            st.write(f"{k} - {v}")

    if codigo_str.isdigit():
        codigo = int(codigo_str)
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        if st.button("Registrar venda"):
            registrar_venda(cliente, codigo, quantidade)

    st.subheader("📋 Histórico de Vendas")
    for cliente, vendas in st.session_state["clientes"].items():
        if vendas:
            st.write(f"### {cliente}")
            for v in vendas:
                st.write(f"- {v['data']} | {v['nome']} (x{v['quantidade']}) - R$ {v['preco']:.2f}")

# ================== Relatórios ==================
def tela_relatorios():
    st.header("📑 Relatórios")
    visitante = is_visitante()
    for cliente, vendas in st.session_state["clientes"].items():
        if vendas:
            total = sum(v["preco"] * v["quantidade"] for v in vendas)
            if visitante:
                st.write(f"Cliente: {cliente} — Total: R$ *****")
            else:
                st.write(f"Cliente: {cliente} — Total: R$ {total:.2f}")

# ================== Resumo ==================
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

# ================== Menu Horizontal no Topo ==================
def menu():
    st.title("📌 Menu")
    opcoes = ["Resumo", "Produtos", "Clientes", "Vendas", "Relatórios", "Sair"]
    escolha = st.radio("Selecione a página:", opcoes, horizontal=True)

    if escolha == "Resumo":
        tela_resumo()
    elif escolha == "Produtos":
        tela_produtos()
    elif escolha == "Clientes":
        tela_clientes()
    elif escolha == "Vendas":
        tela_vendas()
    elif escolha == "Relatórios":
        tela_relatorios()
    elif escolha == "Sair":
        if st.button("Confirmar saída"):
            st.session_state.clear()
            st.rerun()

# ================== Main ==================
def main():
    if "usuario" not in st.session_state or st.session_state["usuario"] is None:
        login()
    else:
        st.write(f"👤 Usuário: {st.session_state['usuario']}")
        menu()

if __name__ == "__main__":
    main()