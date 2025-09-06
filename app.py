# app.py
import streamlit as st

# =========================
# Banco de dados em memória
# =========================

clientes = {
    "Tabata": [
        {"codigo": 4685, "produto": "Soutien Francesca", "quantidade": 1, "valor": 52.95},
        {"codigo": 4184, "produto": "Meia Masc Manhattan Kit", "quantidade": 1, "valor": 25.20},
        {"codigo": 4351, "produto": "Soutien Soft Ribana", "quantidade": 1, "valor": 54.20},
        {"codigo": 3625, "produto": "Cueca Boxe Carlos", "quantidade": 1, "valor": 28.50},
        {"codigo": 4597, "produto": "Cueca Boxe Roger", "quantidade": 2, "valor": 29.00},
        {"codigo": 3900, "produto": "Cueca Boxe Inf Animada", "quantidade": 3, "valor": 15.90},
        {"codigo": 4680, "produto": "Samba Canção Fernando", "quantidade": 1, "valor": 51.25},
        {"codigo": 4726, "produto": "Tanga Mapola", "quantidade": 1, "valor": 22.70},
        {"codigo": 4539, "produto": "Tanga Kamili", "quantidade": 1, "valor": 19.35},
        {"codigo": 4640, "produto": "Tanga Import Neon", "quantidade": 1, "valor": 18.50},
        {"codigo": 3875, "produto": "Tanga Nazaré", "quantidade": 1, "valor": 17.50},
        {"codigo": 4142, "produto": "Tanga Valdira", "quantidade": 1, "valor": 16.50},
        {"codigo": 4705, "produto": "Tanga Ilma", "quantidade": 1, "valor": 22.70},
    ],
    "Valquiria": [
        {"codigo": 4702, "produto": "Top Sueli032", "quantidade": 1, "valor": 58.40},
        {"codigo": 4457, "produto": "Conjunto Verena", "quantidade": 1, "valor": 83.80},
        {"codigo": 4493, "produto": "Meia Fem Analu Kit C/3", "quantidade": 1, "valor": 25.50},
        {"codigo": 4310, "produto": "Tangao Nani Suede", "quantidade": 1, "valor": 17.30},
        {"codigo": 4705, "produto": "Tanga Ilma", "quantidade": 2, "valor": 27.70},
        {"codigo": 3698, "produto": "Tanga Fio Cerejeira", "quantidade": 3, "valor": 14.10},
        {"codigo": 4494, "produto": "Top Import Coração", "quantidade": 1, "valor": 65.10},
        {"codigo": 4701, "produto": "Short Doll Brenda", "quantidade": 1, "valor": 71.00},
    ],
    "Vanessa": [
        {"codigo": 4562, "produto": "Short Doll Analis", "quantidade": 1, "valor": 65.10},
        {"codigo": 4699, "produto": "Tanga Bolívia", "quantidade": 3, "valor": 18.90},
        {"codigo": 4539, "produto": "Tanga Kamili", "quantidade": 1, "valor": 19.35},
    ],
    "Pamela": [
        {"codigo": 4681, "produto": "Short Doll Inf Alcinha", "quantidade": 1, "valor": 11.20},
        {"codigo": 4459, "produto": "Meia BB Pelucia Masc", "quantidade": 1, "valor": 19.75},
        {"codigo": 4497, "produto": "Cueca Boxe Boss", "quantidade": 1, "valor": 27.15},
        {"codigo": 4673, "produto": "Short Doll Alice Plus", "quantidade": 1, "valor": 83.80},
    ],
    "Elan": [
        {"codigo": 4470, "produto": "Cueca Boxe Adidas", "quantidade": 2, "valor": 29.60},
    ],
    "Claudinha": [
        {"codigo": 2750, "produto": "Calça Cós Laser", "quantidade": 1, "valor": 24.90},
        {"codigo": 4239, "produto": "Tanga Fio Duplo Anelise", "quantidade": 2, "valor": 16.80},
        {"codigo": 4142, "produto": "Tanga Valdira", "quantidade": 2, "valor": 16.50},
        {"codigo": 4343, "produto": "Meia Sap Pompom C/3", "quantidade": 1, "valor": 28.20},
        {"codigo": 4122, "produto": "Calça Fem Mônica", "quantidade": 1, "valor": 103.50},
    ],
}

# =========================
# Funções utilitárias
# =========================

def calcular_total(cliente):
    return sum(v["valor"] * v["quantidade"] for v in clientes.get(cliente, []))

def calcular_comissao_total():
    total_vendas = sum(calcular_total(c) for c in clientes)
    return total_vendas * 0.40

def gerar_relatorio(tipo, cliente_nome=None):
    if tipo == "geral":
        linhas = ["📋 *Relatório Geral de Vendas*\n"]
        for cliente in clientes:
            linhas.append(f"👤 {cliente}")
            for v in clientes[cliente]:
                subtotal = v["valor"] * v["quantidade"]
                linhas.append(f"- {v['produto']} ({v['quantidade']}x): R$ {subtotal:.2f}")
            linhas.append(f"💰 Total do cliente: R$ {calcular_total(cliente):.2f}\n")
        linhas.append(f"💰 *Comissão total*: R$ {calcular_comissao_total():.2f}")
        return "\n".join(linhas)
    elif tipo == "cliente" and cliente_nome:
        if cliente_nome not in clientes:
            return "Cliente não encontrado."
        linhas = [f"📋 *Relatório de {cliente_nome}*\n"]
        for v in clientes[cliente_nome]:
            subtotal = v["valor"] * v["quantidade"]
            linhas.append(f"- {v['produto']} ({v['quantidade']}x): R$ {subtotal:.2f}")
        linhas.append(f"\n💰 Total do cliente: R$ {calcular_total(cliente_nome):.2f}")
        return "\n".join(linhas)
    elif tipo == "comissao":
        return f"💰 Comissão total: R$ {calcular_comissao_total():.2f}"
    else:
        return "Opção inválida."

# =========================
# Interface Streamlit
# =========================

st.set_page_config(page_title="Sistema de Vendas", page_icon="📦", layout="wide")

st.title("📦 Sistema de Vendas")

menu = st.sidebar.selectbox(
    "Menu",
    ["Cadastrar cliente", "Registrar venda", "Consultar cliente", "Extrato geral", "Comissão total", "Relatórios"]
)

if menu == "Cadastrar cliente":
    novo_nome = st.text_input("Nome do novo cliente")
    if st.button("Cadastrar"):
        if novo_nome in clientes:
            st.warning("Cliente já existe!")
        else:
            clientes[novo_nome] = []
            st.success(f"Cliente {novo_nome} cadastrado com sucesso!")

elif menu == "Registrar venda":
    cliente = st.selectbox("Selecione o cliente", list(clientes.keys()))
    codigo = st.text_input("Código do produto")
    produto = st.text_input("Nome do produto")
    quantidade = st.number_input("Quantidade", min_value=1, value=1)
    valor = st.number_input("Valor unitário (R$)", min_value=0.0, format="%.2f")
    if st.button("Registrar"):
        clientes[cliente].append({
            "codigo": codigo,
            "produto": produto,
            "quantidade": quantidade,
            "valor": valor
        })
        st.success(f"Venda registrada para {cliente}!")

elif menu == "Consultar cliente":
    cliente = st.selectbox("Selecione o cliente", list(clientes.keys()))
    st.text(gerar_relatorio("cliente", cliente))

elif menu == "Extrato geral":
    st.text(gerar_relatorio("geral"))

elif menu == "Comissão total":
    st.text(gerar_relatorio("comissao"))

elif menu == "Relatórios":
    opc = st.selectbox("Escolha o relatório", ["Geral", "De um cliente", "Comissão total"])
    if opc == "Geral":
        st.text(gerar_relatorio("geral"))
    elif opc == "De um cliente":
        cliente = st.selectbox("Selecione o cliente", list(clientes.keys()))
        st.text(gerar_relatorio("cliente", cliente))
    else:
        st.text(gerar_relatorio("comissao"))
