import streamlit as st
import json, os

# Caminhos dos arquivos de dados
CLIENTES_FILE = "clientes.json"
VENDAS_FILE = "vendas.json"

# Funções utilitárias
def carregar(arquivo, padrao):
    return json.load(open(arquivo, "r", encoding="utf-8")) if os.path.exists(arquivo) else padrao

def salvar(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Produtos cadastrados
produtos = {
    3900: {"nome": "Cueca Boxe Inf Animada", "preco": 15.90},
    4416: {"nome": "Calcinha Inf Canelada", "preco": 13.00},
    # ... todos os outros produtos conforme lista anterior...
    4460: {"nome": "Meia Masc Saulo Kit C/3", "preco": 31.50},
}

# Clientes e vendas iniciais (para já aparecer tudo carregado)
clientes_iniciais = [{"nome": n} for n in ["Tabata", "Valquiria", "Vanessa", "Pamela", "Elan", "Claudinha"]]
vendas_iniciais = [
    {"cliente": "Tabata", "codigo": 4685, "quantidade": 1},
    {"cliente": "Tabata", "codigo": 4184, "quantidade": 1},
    # ... todas as vendas conforme suas listas ...
    {"cliente": "Claudinha", "codigo": 4122, "quantidade": 1},
]

# Carrega ou inicializa os dados
clientes = carregar(CLIENTES_FILE, clientes_iniciais)
vendas = carregar(VENDAS_FILE, vendas_iniciais)

# Ações com persistência
def cadastrar_cliente(nome):
    clientes.append({"nome": nome})
    salvar(CLIENTES_FILE, clientes)

def registrar_venda(cli, cod, qtd):
    vendas.append({"cliente": cli, "codigo": cod, "quantidade": qtd})
    salvar(VENDAS_FILE, vendas)

def calcular_totais():
    tot = {}
    for v in vendas:
        prod = produtos.get(v["codigo"])
        if prod:
            tot[v["cliente"]] = tot.get(v["cliente"], 0) + prod["preco"] * v["quantidade"]
    return tot

# Interface Streamlit
st.set_page_config(page_title="Sistema de Vendas", layout="wide")
st.title("📦 Sistema de Vendas")

totais = calcular_totais()
menu = st.sidebar.radio("Menu", ["📊 Visão Geral", "👤 Clientes", "🛒 Vendas", "📑 Relatórios"])

if menu == "📊 Visão Geral":
    st.header("Resumo Geral de Vendas")
    total_geral = sum(totais.values())
    st.write(f"💰 Total geral: R$ {total_geral:.2f}")
    st.write(f"💸 Comissão (40%): R$ {total_geral*0.40:.2f}")
    for nome, valor in sorted(totais.items()):
        st.write(f"- {nome}: R$ {valor:.2f}")

elif menu == "👤 Clientes":
    st.header("Gerenciar Clientes")
    novo = st.text_input("Cadastrar novo cliente")
    if st.button("Cadastrar") and novo.strip():
        cadastrar_cliente(novo.strip())
        st.success(f"Cliente {novo} cadastrado!")

    busca = st.text_input("Buscar cliente (2+ letras)")
    if len(busca) >= 2:
        sugestoes = sorted([c["nome"] for c in clientes if busca.lower() in c["nome"].lower()])
        if sugestoes:
            escolha = st.selectbox("Selecione", sugestoes)
            if escolha:
                st.subheader(f"{escolha}: Vendas")
                for idx, v in enumerate([x for x in vendas if x["cliente"] == escolha]):
                    prod = produtos.get(v["codigo"], {"nome": "Desconhecido"})
                    st.write(f"{idx+1}. {prod['nome']} x{v['quantidade']} — R$ {prod.get('preco',0)*v['quantidade']:.2f}")
                    if st.button(f"Apagar venda {idx+1}", key=f"del_v_{idx}"):
                        vendas.remove(v); salvar(VENDAS_FILE, vendas); st.experimental_rerun()
                if st.button("Apagar cliente inteiro"):
                    clientes[:] = [c for c in clientes if c["nome"] != escolha]
                    salvar(CLIENTES_FILE, clientes)
                    vendas[:] = [v for v in vendas if v["cliente"] != escolha]
                    salvar(VENDAS_FILE, vendas)
                    st.success("Cliente e vendas apagados!")
        else:
            st.info("Nenhum cliente encontrado.")
    else:
        st.info("Digite ao menos 2 caracteres.")

elif menu == "🛒 Vendas":
    st.header("Registrar Venda")
    nomes = sorted([c["nome"] for c in clientes], key=str.lower)
    cli = st.selectbox("Cliente", nomes)
    cod = st.number_input("Código do produto", step=1)
    qtd = st.number_input("Quantidade", min_value=1, step=1)
    if st.button("Registrar"):
        if cod in produtos:
            registrar_venda(cli, cod, qtd)
            st.success("Venda registrada!")
        else:
            st.error("Código inválido.")

elif menu == "📑 Relatórios":
    st.header("Relatórios")
    tipo = st.radio("Tipo:", ["Geral", "Por cliente", "Comissão"])
    if tipo == "Geral":
        st.subheader("Relatório Geral")
        for n, v in sorted(totais.items()):
            st.write(f"- {n}: R$ {v:.2f}")
        st.write(f"**Total geral**: R$ {sum(totais.values()):.2f}")
    elif tipo == "Por cliente":
        cli = st.selectbox("Cliente", sorted([c["nome"] for c in clientes]))
        st.subheader(f"Relatório de {cli}")
        total = 0
        for v in [x for x in vendas if x["cliente"] == cli]:
            prod = produtos.get(v["codigo"], {"nome": "Desconhecido", "preco": 0})
            subtotal = prod["preco"] * v["quantidade"]
            total += subtotal
            st.write(f"- {prod['nome']} x{v['quantidade']} → R$ {subtotal:.2f}")
        st.write(f"**Total**: R$ {total:.2f}")
    else:
        st.write(f"**Comissão total (40%)**: R$ {sum(totais.values())*0.40:.2f}")
