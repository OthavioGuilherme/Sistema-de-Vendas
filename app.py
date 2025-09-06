# app.py
import streamlit as st

# =========================
# Banco de dados em memória
# =========================

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
    4705: {"nome": "Tanga Ilma", "preco": 27.70}, # atualizado pelo que você mandou
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

clientes = {
    "Tabata": [
        (4685, 1), (4184, 1), (4351, 1), (3625, 1), (4597, 1),
        (3900, 3), (4597, 1), (4680, 1), (4726, 1), (4539, 1),
        (4640, 1), (3875, 1), (4142, 1), (4705, 1)
    ],
    "Valquiria": [
        (4702, 1), (4457, 1), (4493, 1), (4310, 1),
        (4705, 2), (3698, 3), (4494, 1), (4701, 1)
    ],
    "Vanessa": [
        (4562, 1), (4699, 3), (4539, 1)
    ],
    "Pamela": [
        (4681, 1), (4459, 1), (4497, 1), (4673, 1)
    ],
    "Elan": [
        (4470, 2)
    ],
    "Claudinha": [
        (2750, 1), (4239, 2), (4142, 2), (4343, 1), (4122, 1)
    ]
}

# =========================
# Funções de negócio
# =========================

def calcular_total_cliente(vendas):
    total = 0
    for codigo, qtd in vendas:
        if codigo in produtos:
            total += produtos[codigo]["preco"] * qtd
    return total

def gerar_relatorio_cliente(nome):
    if nome not in clientes:
        return f"Cliente {nome} não encontrado."
    linhas = [f"📋 *Relatório de {nome}*\n"]
    total = 0
    for codigo, qtd in clientes[nome]:
        prod = produtos.get(codigo)
        if prod:
            subtotal = prod["preco"] * qtd
            linhas.append(f"- {prod['nome']} ({qtd}x): R$ {subtotal:.2f}")
            total += subtotal
    linhas.append(f"\n💰 Total do cliente: R$ {total:.2f}")
    return "\n".join(linhas)

def gerar_relatorio_geral():
    linhas = ["📋 *Relatório Geral de Vendas*\n"]
    total_geral = 0
    for nome, vendas in clientes.items():
        total = calcular_total_cliente(vendas)
        linhas.append(f"- {nome}: R$ {total:.2f}")
        total_geral += total
    linhas.append(f"\n💰 Total geral: R$ {total_geral:.2f}")
    return "\n".join(linhas)

def calcular_comissao_total():
    total_vendas = sum(calcular_total_cliente(v) for v in clientes.values())
    return total_vendas * 0.40

# =========================
# Interface Streamlit
# =========================

st.title("💼 Sistema de Vendas")

menu = st.sidebar.selectbox("Menu", [
    "Ver relatório geral",
    "Ver relatório de um cliente",
    "Ver comissão total"
])

if menu == "Ver relatório geral":
    st.text_area("Copie e cole no WhatsApp:", gerar_relatorio_geral(), height=300)

elif menu == "Ver relatório de um cliente":
    nome = st.selectbox("Selecione o cliente", list(clientes.keys()))
    st.text_area("Copie e cole no WhatsApp:", gerar_relatorio_cliente(nome), height=300)

elif menu == "Ver comissão total":
    comissao = calcular_comissao_total()
    st.success(f"💰 Comissão total (40%): R$ {comissao:.2f}")
