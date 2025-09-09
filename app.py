# sistema_vendas.py
import streamlit as st
from datetime import datetime
import json
import os

# =============== Configuração da página ===============
st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# =============== Autenticação ===============
USERS = {
    "othavio": "122008",
    "isabela": "122008",
}
LOG_FILE = "acessos.log"
DB_FILE = "db.json"

def registrar_acesso(usuario):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {usuario}\n")
    except Exception:
        pass

def autenticar(usuario, senha):
    if USERS.get(usuario) == senha:
        st.session_state.logado = True
        st.session_state.usuario = usuario
        registrar_acesso(usuario)
        return True
    return False

def is_visitante():
    return bool(st.session_state.get("usuario")) and str(st.session_state.get("usuario")).startswith("visitante-")

# =============== Dados iniciais ===============
PRODUTOS_INICIAIS = {
    3900: {"nome": "Cueca Boxe Inf Animada", "preco": 15.90},
    4416: {"nome": "Calcinha Inf Canelada", "preco": 13.00},
    4497: {"nome": "Cueca Boxe Boss", "preco": 27.15},
    4470: {"nome": "Cueca Boxe Adidas", "preco": 29.60},
    4597: {"nome": "Cueca Boxe Roger", "preco": 29.00},
    3625: {"nome": "Cueca Boxe Carlos", "preco": 28.50},
    4685: {"nome": "Soutien Francesca", "preco": 52.95},
    4351: {"nome": "Soutien Soft Ribana", "preco": 54.20},
    3866: {"nome": "Soutien Edite", "preco": 48.80},
    4696: {"nome": "Tangão Emanuela", "preco": 26.90},
    4402: {"nome": "Cueca Fem Suede", "preco": 19.30},
    4310: {"nome": "Tangao Nani Suede", "preco": 17.30},
    2750: {"nome": "Calça Cós Laser", "preco": 24.90},
    4705: {"nome": "Tanga Ilma", "preco": 27.70},
    4699: {"nome": "Tanga Bolívia", "preco": 18.90},
    4539: {"nome": "Tanga Kamili", "preco": 19.35},
    4726: {"nome": "Tanga Mapola", "preco": 22.70},
    4640: {"nome": "Tanga Import. Neon", "preco": 18.50},
    4187: {"nome": "Tanga Fio Zaira", "preco": 16.40},
    4239: {"nome": "Tanga Fio Duplo Anelise", "preco": 16.80},
    4142: {"nome": "Tanga Valdira", "preco": 16.50},
    4592: {"nome": "Tanga Conforto Suede Estampada", "preco": 21.05},
    3875: {"nome": "Tanga Nazaré", "preco": 17.50},
    3698: {"nome": "Tanga Fio Cerejeira", "preco": 14.10},
    4322: {"nome": "Conj. M/M Ribana", "preco": 37.50},
    4719: {"nome": "Conjunto Camila", "preco": 68.90},
    4462: {"nome": "Conjunto Cleide", "preco": 68.00},
    4457: {"nome": "Conjunto Verena", "preco": 83.80},
    4543: {"nome": "Conjunto Soft Mapola", "preco": 71.00},
    4702: {"nome": "Top Sueli032", "preco": 58.40},
    4494: {"nome": "Top Import Coração", "preco": 65.10},
    4680: {"nome": "Samba Cançao Fernando", "preco": 51.25},
    4498: {"nome": "Pijama Suede Silk", "preco": 117.20},
    4673: {"nome": "Short Doll Alice Plus", "preco": 83.80},
    4675: {"nome": "Short Doll Can. Regata", "preco": 74.55},
    4681: {"nome": "Short Doll Inf. Alcinha", "preco": 41.20},
    4562: {"nome": "Short Doll Analis", "preco": 65.10},
    4701: {"nome": "Short Doll Brenda", "preco": 71.00},
    4122: {"nome": "Calça Fem Mônica", "preco": 103.50},
    4493: {"nome": "Meia Fem Analu Kit C/3", "preco": 25.50},
    4343: {"nome": "Meia Sap Pompom Kit C/3", "preco": 28.20},
    4184: {"nome": "Meia Masc Manhattan Kit", "preco": 25.20},
    4458: {"nome": "Meia BB Pelúcia Fem", "preco": 19.75},
    4459: {"nome": "Meia BB Pelucia Masc", "preco": 19.75},
    4460: {"nome": "Meia Masc Saulo Kit C/3", "preco": 31.50},
}

VENDAS_INICIAIS = {
    "Tabata": [
        {"codigo": 4685, "quantidade": 1, "preco": 52.95},
        {"codigo": 4184, "quantidade": 1, "preco": 25.20},
        {"codigo": 4351, "quantidade": 1, "preco": 54.20},
        {"codigo": 3625, "quantidade": 1, "preco": 28.50},
        {"codigo": 4597, "quantidade": 1, "preco": 29.00},
        {"codigo": 3900, "quantidade": 3, "preco": 15.90},
        {"codigo": 4680, "quantidade": 1, "preco": 51.25},
        {"codigo": 4726, "quantidade": 1, "preco": 22.70},
        {"codigo": 4539, "quantidade": 1, "preco": 19.35},
        {"codigo": 4640, "quantidade": 1, "preco": 18.50},
        {"codigo": 3875, "quantidade": 1, "preco": 17.50},
        {"codigo": 4142, "quantidade": 1, "preco": 16.50},
        {"codigo": 4705, "quantidade": 1, "preco": 22.70},
    ],
    "Valquiria": [
        {"codigo": 4702, "quantidade": 1, "preco": 58.40},
        {"codigo": 4457, "quantidade": 1, "preco": 83.80},
        {"codigo": 4493, "quantidade": 1, "preco": 25.50},
        {"codigo": 4310, "quantidade": 1, "preco": 17.30},
        {"codigo": 4705, "quantidade": 2, "preco": 27.70},
        {"codigo": 3698, "quantidade": 3, "preco": 14.10},
        {"codigo": 4494, "quantidade": 1, "preco": 65.10},
        {"codigo": 4701, "quantidade": 1, "preco": 71.00},
    ],
    "Vanessa": [
        {"codigo": 4562, "quantidade": 1, "preco": 65.10},
        {"codigo": 4699, "quantidade": 3, "preco": 18.90},
        {"codigo": 4539, "quantidade": 1, "preco": 19.35},
    ],
    "Pamela": [
        {"codigo": 4681, "quantidade": 1, "preco": 11.20},
        {"codigo": 4459, "quantidade": 1, "preco": 19.75},
        {"codigo": 4497, "quantidade": 1, "preco": 27.15},
        {"codigo": 4673, "quantidade": 1, "preco": 83.80},
    ],
    "Elan": [
        {"codigo": 4470, "quantidade": 2, "preco": 29.60},
    ],
    "Claudinha": [
        {"codigo": 2750, "quantidade": 1, "preco": 24.90},
        {"codigo": 4239, "quantidade": 2, "preco": 16.80},
        {"codigo": 4142, "quantidade": 2, "preco": 16.50},
        {"codigo": 4343, "quantidade": 1, "preco": 28.20},
        {"codigo": 4122, "quantidade": 1, "preco": 103.50},
    ],
}

# =============== Persistência ===============
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
            clis = {k: v for k, v in data.get("clientes", {}).items()}
            return prods, clis
        except:
            pass
    return ({k: v.copy() for k, v in PRODUTOS_INICIAIS.items()},
            {k: [i.copy() for i in lst] for k, lst in VENDAS_INICIAIS.items()})

# =============== Session State ===============
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

# ===================================================
# =================== Helpers ===================
def total_cliente(nome):
    vendas = st.session_state.clientes.get(nome, [])
    return sum(item["preco"] * item["quantidade"] for item in vendas)

def total_geral():
    return sum(total_cliente(c) for c in st.session_state.clientes)

def listar_produtos():
    return [(codigo, info["nome"], info["preco"]) for codigo, info in st.session_state.produtos.items()]

# =================== Telas ===================
def tela_login():
    st.title("🧾 Sistema de Vendas - Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if autenticar(usuario, senha):
            st.success(f"Bem-vindo(a), {usuario}!")
        else:
            st.error("Usuário ou senha inválidos.")

def tela_resumo():
    st.header("Resumo de Vendas")
    st.write(f"**Total Geral:** R$ {total_geral():.2f}")
    for cliente in st.session_state.clientes:
        st.write(f"- {cliente}: R$ {total_cliente(cliente):.2f}")

def tela_registrar_venda():
    st.header("Registrar Nova Venda")
    if is_visitante():
        st.warning("Visitantes não podem registrar vendas.")
        return
    cliente = st.text_input("Nome do Cliente")
    codigo = st.number_input("Código do Produto", min_value=0)
    quantidade = st.number_input("Quantidade", min_value=1, value=1)
    if st.button("Adicionar Venda"):
        produto = st.session_state.produtos.get(codigo)
        if not produto:
            st.error("Produto não encontrado.")
            return
        venda = {"codigo": codigo, "quantidade": quantidade, "preco": produto["preco"]}
        st.session_state.clientes.setdefault(cliente, []).append(venda)
        save_db()
        st.success(f"Venda registrada para {cliente}.")

def tela_clientes():
    st.header("Clientes")
    for cliente, vendas in st.session_state.clientes.items():
        st.subheader(cliente)
        for v in vendas:
            prod = st.session_state.produtos.get(v["codigo"], {"nome":"Desconhecido"})
            st.write(f'{prod["nome"]} | Qtde: {v["quantidade"]} | R$ {v["preco"]:.2f}')

def tela_produtos():
    st.header("Produtos")
    for codigo, info in st.session_state.produtos.items():
        st.write(f'{codigo} - {info["nome"]} - R$ {info["preco"]:.2f}')

def tela_relatorios():
    st.header("Relatórios")
    st.write("**Relatório de vendas por cliente:**")
    for cliente in st.session_state.clientes:
        st.write(f"- {cliente}: R$ {total_cliente(cliente):.2f}")
    st.write(f"**Total geral:** R$ {total_geral():.2f}")

def tela_acessos():
    st.header("Histórico de Acessos")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.read()
        st.text(logs)

# =================== Barra Lateral ===================
def barra_lateral():
    menu = st.sidebar.radio("Menu", ["Resumo", "Registrar Venda", "Clientes", "Produtos", "Relatórios", "Acessos"])
    st.session_state.menu = menu

# =================== Roteador ===================
def roteador():
    menu = st.session_state.menu
    if menu == "Resumo":
        tela_resumo()
    elif menu == "Registrar Venda":
        tela_registrar_venda()
    elif menu == "Clientes":
        tela_clientes()
    elif menu == "Produtos":
        tela_produtos()
    elif menu == "Relatórios":
        tela_relatorios()
    elif menu == "Acessos":
        tela_acessos()

# =================== Edição/Remoção de Vendas ===================
def editar_remover_venda():
    st.header("Editar / Remover Vendas")
    if is_visitante():
        st.warning("Visitantes não podem editar/remover vendas.")
        return
    cliente = st.selectbox("Selecione o cliente", list(st.session_state.clientes.keys()))
    vendas = st.session_state.clientes.get(cliente, [])
    for i, v in enumerate(vendas):
        prod = st.session_state.produtos.get(v["codigo"], {"nome": "Desconhecido"})
        col1, col2, col3 = st.columns([4,1,1])
        col1.write(f'{prod["nome"]} | Qtde: {v["quantidade"]} | R$ {v["preco"]:.2f}')
        if col2.button("Editar", key=f"edit_{cliente}_{i}"):
            nova_qtde = st.number_input("Nova quantidade", min_value=1, value=v["quantidade"], key=f"input_{cliente}_{i}")
            v["quantidade"] = nova_qtde
            save_db()
            st.experimental_rerun()
        if col3.button("Remover", key=f"rm_{cliente}_{i}"):
            vendas.pop(i)
            save_db()
            st.experimental_rerun()

# =============== Main ===============
def main():
    if not st.session_state.logado:
        tela_login()
        return
    barra_lateral()
    roteador()

if __name__ == "__main__":
    main()
