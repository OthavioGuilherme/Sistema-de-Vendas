import streamlit as st
import json
import os

# ==========================
# Funções utilitárias
# ==========================
CLIENTES_FILE = "clientes.json"
VENDAS_FILE = "vendas.json"

def carregar_dados(arquivo, padrao):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# ==========================
# Produtos cadastrados
# ==========================
produtos = {
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

# ==========================
# Clientes e vendas iniciais
# ==========================
clientes_iniciais = [
    {"nome": "Tabata"},
    {"nome": "Valquiria"},
    {"nome": "Vanessa"},
    {"nome": "Pamela"},
    {"nome": "Elan"},
    {"nome": "Claudinha"},
]

vendas_iniciais = [
    # Tabata
    {"cliente": "Tabata", "codigo": 4685, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 4184, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 4351, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 3625, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 4597, "quantidade": 2},
    {"cliente": "Tabata", "codigo": 3900, "quantidade": 3},
    {"cliente": "Tabata", "codigo": 4680, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 4726, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 4539, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 4640, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 3875, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 4142, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 4705, "quantidade": 1},
    # Valquiria (corrigir depois se faltar)
    {"cliente": "Valquiria", "codigo": 4702, "quantidade": 1},
    {"cliente": "Valquiria", "codigo": 4457, "quantidade": 1},
    {"cliente": "Valquiria", "codigo": 4493, "quantidade": 1},
    {"cliente": "Valquiria", "codigo": 4310, "quantidade": 1},
    {"cliente": "Valquiria", "codigo": 4705, "quantidade": 2},
    {"cliente": "Valquiria", "codigo": 3698, "quantidade": 3},
    {"cliente": "Valquiria", "codigo": 4494, "quantidade": 1},
    {"cliente": "Valquiria", "codigo": 4701, "quantidade": 1},
    # Vanessa
    {"cliente": "Vanessa", "codigo": 4562, "quantidade": 1},
    {"cliente": "Vanessa", "codigo": 4699, "quantidade": 3},
    {"cliente": "Vanessa", "codigo": 4539, "quantidade": 1},
    # Pamela
    {"cliente": "Pamela", "codigo": 4681, "quantidade": 1},
    {"cliente": "Pamela", "codigo": 4459, "quantidade": 1},
    {"cliente": "Pamela", "codigo": 4497, "quantidade": 1},
    {"cliente": "Pamela", "codigo": 4673, "quantidade": 1},
    # Elan
    {"cliente": "Elan", "codigo": 4470, "quantidade": 2},
    # Claudinha
    {"cliente": "Claudinha", "codigo": 2750, "quantidade": 1},
    {"cliente": "Claudinha", "codigo": 4239, "quantidade": 2},
    {"cliente": "Claudinha", "codigo": 4142, "quantidade": 2},
    {"cliente": "Claudinha", "codigo": 4343, "quantidade": 1},
    {"cliente": "Claudinha", "codigo": 4122, "quantidade": 1},
]

# Carregar ou criar dados
clientes = carregar_dados(CLIENTES_FILE, clientes_iniciais)
vendas = carregar_dados(VENDAS_FILE, vendas_iniciais)

# Funções
def cadastrar_cliente(nome):
    clientes.append({"nome": nome})
    salvar_dados(CLIENTES_FILE, clientes)

def registrar_venda(cliente_nome, codigo_produto, quantidade):
    vendas.append({"cliente": cliente_nome, "codigo": codigo_produto, "quantidade": quantidade})
    salvar_dados(VENDAS_FILE, vendas)

def calcular_totais():
    totais = {}
    for v in vendas:
        cli = v["cliente"]
        prod = produtos.get(v["codigo"])
        if not prod:
            continue
        valor = prod["preco"] * v["quantidade"]
        totais[cli] = totais.get(cli, 0) + valor
    return totais

# Interface
st.title("📦 Sistema de Vendas")

menu = st.sidebar.radio("Menu", ["📊 Visão Geral", "👤 Clientes", "🛒 Vendas"])

if menu == "📊 Visão Geral":
    st.header("Resumo Geral de Vendas")
    totais = calcular_totais()
    total_geral = sum(totais.values())
    comissao = total_geral * 0.40
    for nome, valor in sorted(totais.items()):
        st.write(f"- **{nome}**: R$ {valor:.2f}")
    st.markdown(f"**💰 Total geral:** R$ {total_geral:.2f}")
    st.markdown(f"**💸 Comissão (40%):** R$ {comissao:.2f}")

elif menu == "👤 Clientes":
    st.header("Gerenciar Clientes")
    nome_cli = st.text_input("Novo cliente")
    if st.button("Cadastrar cliente") and nome_cli:
        cadastrar_cliente(nome_cli)
        st.success(f"Cliente {nome_cli} cadastrado!")
    st.write("Clientes cadastrados:")
    for c in sorted(clientes, key=lambda x: x['nome'].lower()):
        st.write(f"- {c['nome']}")

elif menu == "🛒 Vendas":
    st.header("Registrar Venda")
    if not clientes:
        st.warning("Cadastre um cliente primeiro.")
    else:
        nomes = sorted([c['nome'] for c in clientes], key=str.lower)
        cliente_escolhido = st.selectbox("Escolha o cliente", nomes)
        codigo = st.number_input("Código do produto", step=1)
        qtd = st.number_input("Quantidade", min_value=1, step=1)
        if st.button("Registrar venda"):
            if int(codigo) in produtos:
                registrar_venda(cliente_escolhido, int(codigo), int(qtd))
                st.success("Venda registrada!")
            else:
                st.error("Código de produto inválido.")
