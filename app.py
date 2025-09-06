# app.py
import streamlit as st
import json
import os
from datetime import datetime

# ===========================
# Configuração de login
# ===========================
USERS = {
    "Othavio": "122008",
    "Isabela": "122008"
}

ACESSOS_FILE = "acessos.log"

def registrar_acesso(nome, tipo):
    with open(ACESSOS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} — {tipo}: {nome}\n")

def do_login():
    st.title("🔒 Login no Sistema de Vendas")
    aba = st.radio("Escolha como entrar:", ["Usuário autorizado", "Entrar como visitante"])

    if aba == "Usuário autorizado":
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            for user, pwd in USERS.items():
                if u.strip().lower() == user.lower() and p.strip().lower() == pwd.lower():
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    registrar_acesso(user, "USUÁRIO")
                    st.success(f"Bem-vindo(a), {user}!")
                    st.rerun()
                    return
            st.error("Usuário ou senha incorretos.")
    else:
        nome_visitante = st.text_input("Digite seu nome para entrar como visitante")
        if st.button("Entrar como visitante", use_container_width=True):
            if not nome_visitante.strip():
                st.warning("Por favor, digite um nome para entrar.")
                return
            st.session_state.logged_in = True
            st.session_state.user = f"Visitante: {nome_visitante.strip()}"
            registrar_acesso(nome_visitante.strip(), "VISITANTE")
            st.success(f"Bem-vindo(a), {nome_visitante}!")
            st.rerun()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ===========================
# Produtos (fixos)
# ===========================
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

# ===========================
# Banco de dados em memória
# ===========================
if "clientes" not in st.session_state:
    st.session_state.clientes = {}

# ===========================
# Funções principais
# ===========================
def mostrar_resumo():
    st.header("📦 Sistema de Vendas")
    total_geral = sum(
        sum(p["quantidade"] * p["valor"] for p in dados["vendas"])
        for dados in st.session_state.clientes.values()
    )
    comissao = total_geral * 0.40
    st.subheader(f"💰 Total geral: R$ {total_geral:.2f}")
    st.subheader(f"💸 Comissão (40%): R$ {comissao:.2f}")

def cadastrar_cliente():
    nome = st.text_input("Nome do cliente")
    if st.button("Cadastrar cliente"):
        if nome.strip():
            st.session_state.clientes[nome.strip()] = {"vendas": []}
            st.success(f"Cliente {nome} cadastrado!")

def registrar_venda():
    clientes = sorted(st.session_state.clientes.keys(), key=lambda x: x.lower())
    cliente = st.selectbox("Escolha o cliente", [""] + clientes)
    codigo = st.selectbox("Escolha o produto", list(produtos.keys()))
    qtd = st.number_input("Quantidade", min_value=1, step=1)
    if st.button("Registrar venda"):
        if cliente and cliente in st.session_state.clientes:
            p = produtos[codigo]
            st.session_state.clientes[cliente]["vendas"].append({
                "codigo": codigo,
                "nome": p["nome"],
                "quantidade": qtd,
                "valor": p["preco"],
            })
            st.success(f"{qtd}x {p['nome']} para {cliente} registrada!")

def consultar_cliente():
    busca = st.text_input("Digite ao menos 2 letras do nome")
    if len(busca) >= 2:
        sugestoes = sorted([c for c in st.session_state.clientes if busca.lower() in c.lower()])
        cliente = st.selectbox("Selecione o cliente", [""] + sugestoes)
        if cliente:
            st.write(f"### Vendas de {cliente}")
            total = 0
            for i, v in enumerate(st.session_state.clientes[cliente]["vendas"]):
                st.write(f"{i+1}. {v['nome']} ({v['quantidade']}x) — R$ {v['valor']:.2f}")
                total += v["quantidade"] * v["valor"]
            st.write(f"**Total: R$ {total:.2f}**")

def gerar_relatorio():
    opc = st.radio("Escolha o tipo de relatório", ["Geral", "Individual", "Comissão total"])
    if opc == "Geral":
        st.write("📋 **Relatório Geral de Vendas**")
        total_geral = 0
        for c, dados in st.session_state.clientes.items():
            total = sum(p["quantidade"] * p["valor"] for p in dados["vendas"])
            st.write(f"- {c}: R$ {total:.2f}")
            total_geral += total
        st.write(f"\n💰 **Total geral**: R$ {total_geral:.2f}")
    elif opc == "Individual":
        cliente = st.selectbox("Escolha o cliente", [""] + sorted(st.session_state.clientes.keys()))
        if cliente:
            total = sum(p["quantidade"] * p["valor"] for p in st.session_state.clientes[cliente]["vendas"])
            st.write(f"📋 **Relatório de {cliente}**")
            for p in st.session_state.clientes[cliente]["vendas"]:
                st.write(f"- {p['nome']} ({p['quantidade']}x): R$ {p['quantidade']*p['valor']:.2f}")
            st.write(f"\n💰 **Total do cliente**: R$ {total:.2f}")
    else:
        total_geral = sum(
            sum(p["quantidade"] * p["valor"] for p in dados["vendas"])
            for dados in st.session_state.clientes.values()
        )
        st.write(f"💸 **Comissão total (40%)**: R$ {total_geral * 0.40:.2f}")

# ===========================
# Fluxo principal
# ===========================
if not st.session_state.logged_in:
    do_login()
    st.stop()

st.sidebar.title("Menu")
menu = st.sidebar.radio("Escolha uma opção:", [
    "Resumo",
    "Cadastrar cliente",
    "Registrar venda",
    "Consultar cliente",
    "Gerar relatório",
])

if menu == "Resumo":
    mostrar_resumo()
elif menu == "Cadastrar cliente":
    cadastrar_cliente()
elif menu == "Registrar venda":
    registrar_venda()
elif menu == "Consultar cliente":
    consultar_cliente()
elif menu == "Gerar relatório":
    gerar_relatorio()
