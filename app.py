# app.py
import streamlit as st
import pandas as pd

# =========================
# Banco de dados em memória
# =========================
if "clientes" not in st.session_state:
    st.session_state.clientes = {
        "Tabata": [
            ("4685", "Produto A", 52.95, 1),
            ("4184", "Produto B", 25.20, 1),
            ("4351", "Produto C", 54.20, 1),
            ("3625", "Produto D", 28.50, 1),
            ("4597", "Produto E", 29.00, 2),
            ("3900", "Produto F", 15.90, 3),
            ("4680", "Produto G", 51.25, 1),
            ("4726", "Produto H", 22.70, 1),
            ("4539", "Produto I", 19.35, 1),
            ("4640", "Produto J", 18.50, 1),
            ("3875", "Produto K", 17.50, 1),
            ("4142", "Produto L", 16.50, 1),
            ("4705", "Produto M", 22.70, 1),
        ],
        "Valquiria": [
            ("4702", "Produto N", 58.40, 1),
            ("4457", "Produto O", 83.80, 1),
            ("4493", "Produto P", 25.50, 1),
            ("4310", "Produto Q", 17.30, 1),
            ("4705", "Produto M", 27.70, 2),
            ("3698", "Produto R", 14.10, 3),
            ("4494", "Produto S", 65.10, 1),
            ("4701", "Produto T", 71.00, 1),
        ],
        "Vanessa": [
            ("4562", "Produto U", 65.10, 1),
            ("4699", "Produto V", 18.90, 3),
            ("4539", "Produto I", 19.35, 1),
        ],
        "Pamela": [
            ("4681", "Produto W", 11.20, 1),
            ("4459", "Produto X", 19.75, 1),
            ("4497", "Produto Y", 27.15, 1),
            ("4673", "Produto Z", 83.80, 1),
        ],
        "Elan": [
            ("4470", "Produto AA", 29.60, 2),
        ],
        "Claudinha": [
            ("2750", "CALÇA CÓS LASER", 24.90, 1),
            ("4239", "TANGA FIO DUPLO ANELISE", 16.80, 2),
            ("4142", "TANGA VALDIRA", 16.50, 2),
            ("4343", "MEIA SAP POMPOM C/3", 28.20, 1),
            ("4122", "CALÇA FEM MÔNICA", 103.50, 1),
        ],
    }

# =========================
# Funções auxiliares
# =========================
def calcular_total(cliente):
    return sum(preco * qtd for _, _, preco, qtd in st.session_state.clientes[cliente])

def calcular_comissao_total():
    total_vendas = sum(calcular_total(c) for c in st.session_state.clientes)
    return total_vendas * 0.40

def gerar_relatorio(cliente=None):
    if cliente:
        vendas = st.session_state.clientes.get(cliente, [])
        rel = f"📋 *Relatório de {cliente}*\n\n"
        for codigo, nome, preco, qtd in vendas:
            rel += f"- {nome} ({qtd}x): R$ {preco*qtd:.2f}\n"
        rel += f"\n💰 Total do cliente: R$ {calcular_total(cliente):.2f}"
    else:
        rel = "📋 *Relatório Geral de Vendas*\n\n"
        for c in st.session_state.clientes:
            rel += f"- {c}: R$ {calcular_total(c):.2f}\n"
        total = sum(calcular_total(c) for c in st.session_state.clientes)
        comissao = total * 0.40
        rel += f"\n💰 Total geral: R$ {total:.2f}\n"
        rel += f"💸 Comissão (40%): R$ {comissao:.2f}"
    return rel

# =========================
# Interface Streamlit
# =========================
st.set_page_config(page_title="Sistema de Vendas", layout="wide")
st.title("📊 Sistema de Vendas")

menu = st.sidebar.radio("Menu", [
    "Página inicial",
    "Cadastrar cliente",
    "Registrar venda",
    "Consultar cliente",
    "Relatórios"
])

# Página inicial
if menu == "Página inicial":
    st.subheader("Resumo geral")
    total_geral = sum(calcular_total(c) for c in st.session_state.clientes)
    comissao = total_geral * 0.40
    st.write("📋 **Relatório Geral de Vendas**")
    for c in st.session_state.clientes:
        st.write(f"- {c}: R$ {calcular_total(c):.2f}")
    st.success(f"💰 Total geral: R$ {total_geral:.2f}")
    st.info(f"💸 Comissão (40%): R$ {comissao:.2f}")

# Cadastrar cliente
elif menu == "Cadastrar cliente":
    st.subheader("Cadastrar novo cliente")
    nome = st.text_input("Nome do cliente")
    if st.button("Cadastrar"):
        if nome in st.session_state.clientes:
            st.warning("Cliente já cadastrado.")
        else:
            st.session_state.clientes[nome] = []
            st.success(f"Cliente {nome} cadastrado com sucesso!")

# Registrar venda
elif menu == "Registrar venda":
    st.subheader("Registrar venda")
    cliente = st.selectbox("Selecione o cliente", list(st.session_state.clientes.keys()))
    codigo = st.text_input("Código do produto")
    nome = st.text_input("Nome do produto")
    preco = st.number_input("Preço", min_value=0.0, format="%.2f")
    qtd = st.number_input("Quantidade", min_value=1, step=1)
    if st.button("Adicionar venda"):
        st.session_state.clientes[cliente].append((codigo, nome, preco, qtd))
        st.success(f"Venda registrada para {cliente}!")

# Consultar cliente
elif menu == "Consultar cliente":
    st.subheader("Consultar cliente")
    cliente = st.selectbox("Selecione o cliente", list(st.session_state.clientes.keys()))
    if cliente:
        st.write(gerar_relatorio(cliente))

# Relatórios
elif menu == "Relatórios":
    st.subheader("Relatórios")
    opc = st.radio("Escolha o relatório", ["Geral", "Por cliente", "Comissão total"])
    if opc == "Geral":
        st.text_area("Copie e cole no WhatsApp", gerar_relatorio(), height=300)
    elif opc == "Por cliente":
        cliente = st.selectbox("Selecione o cliente", list(st.session_state.clientes.keys()))
        st.text_area("Copie e cole no WhatsApp", gerar_relatorio(cliente), height=300)
    elif opc == "Comissão total":
        st.info(f"💸 Comissão total: R$ {calcular_comissao_total():.2f}")
