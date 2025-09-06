import streamlit as st

# =========================
# Banco de dados em memória
# =========================
produtos = {
    4470: {"nome": "Cueca Boxe Adidas", "preco": 29.60},
    2750: {"nome": "Calça Cós Laser", "preco": 24.90},
    4239: {"nome": "Tanga Fio Duplo Anelise", "preco": 16.80},
    4142: {"nome": "Tanga Valdira", "preco": 16.50},
    4343: {"nome": "Meia Sap Pompom c/3", "preco": 28.20},
    4122: {"nome": "Calça Fem Mônica", "preco": 103.50},
    4685: {"nome": "Soutien Francesca", "preco": 52.95},
    4184: {"nome": "Meia Masc Manhattan Kit", "preco": 25.20},
    4351: {"nome": "Soutien Soft Ribana", "preco": 54.20},
    3625: {"nome": "Cueca Boxe Carlos", "preco": 28.50},
    4597: {"nome": "Cueca Boxe Roger", "preco": 29.00},
    3900: {"nome": "Cueca Boxe Inf Animada", "preco": 15.90},
    4680: {"nome": "Samba Canção Fernando", "preco": 51.25},
    4726: {"nome": "Tanga Mapola", "preco": 22.70},
    4539: {"nome": "Tanga Kamili", "preco": 19.35},
    4640: {"nome": "Tanga Import Neon", "preco": 18.50},
    3875: {"nome": "Tanga Nazaré", "preco": 17.50},
    4705: {"nome": "Tanga Ilma", "preco": 22.70},
}

# Clientes já cadastrados com as vendas (exemplo que você passou)
clientes_iniciais = {
    "Tabata": [4685, 4184, 4351, 3625, 4597, 3900, 3900, 3900, 4597, 4680, 4726, 4539, 4640, 3875, 4142, 4705],
    "Valquiria": [4702, 4457, 4493, 4310, 4705, 4705, 3698, 3698, 3698, 4494, 4701],
    "Vanessa": [4562, 4699, 4699, 4699, 4539],
    "Pamela": [4681, 4459, 4497, 4673],
    "Elan": [4470, 4470],
    "Claudinha": [2750, 4239, 4239, 4142, 4142, 4343, 4122]
}

# Carrega para o estado da sessão
if "clientes" not in st.session_state:
    st.session_state.clientes = clientes_iniciais.copy()

st.title("🛍️ Sistema de Vendas")

menu = st.sidebar.radio(
    "Menu",
    ["Cadastrar Cliente", "Registrar Venda", "Consultar Cliente", "Relatórios"]
)

def registrar_venda(nome, codigo, qtd):
    if nome not in st.session_state.clientes:
        st.session_state.clientes[nome] = []
    st.session_state.clientes[nome].extend([codigo] * qtd)

def gerar_relatorio_geral():
    rel = "📋 *Relatório Geral de Vendas*\n\n"
    total = 0
    for nome, codigos in st.session_state.clientes.items():
        rel += f"👤 {nome}\n"
        resumo = {}
        for c in codigos:
            if c in produtos:
                resumo[c] = resumo.get(c, 0) + 1
        for c, qtd in resumo.items():
            p = produtos[c]
            subtotal = p["preco"] * qtd
            rel += f"  - {p['nome']} ({qtd}x): R$ {subtotal:.2f}\n"
            total += subtotal
        rel += "\n"
    comissao = total * 0.40
    rel += f"💰 Comissão total: R$ {comissao:.2f}"
    return rel

def gerar_relatorio_cliente(nome):
    if nome not in st.session_state.clientes:
        return f"Cliente {nome} não encontrado."
    codigos = st.session_state.clientes[nome]
    rel = f"📋 *Relatório de {nome}*\n\n"
    total = 0
    resumo = {}
    for c in codigos:
        resumo[c] = resumo.get(c, 0) + 1
    for c, qtd in resumo.items():
        if c in produtos:
            p = produtos[c]
            subtotal = p["preco"] * qtd
            rel += f"- {p['nome']} ({qtd}x): R$ {subtotal:.2f}\n"
            total += subtotal
    rel += f"\n💰 Total do cliente: R$ {total:.2f}"
    return rel

# =========================
# Telas do menu
# =========================
if menu == "Cadastrar Cliente":
    st.subheader("Cadastrar Cliente")
    nome = st.text_input("Nome do cliente")
    if st.button("Cadastrar"):
        if nome.strip() == "":
            st.warning("Digite um nome válido.")
        elif nome in st.session_state.clientes:
            st.info("Cliente já cadastrado.")
        else:
            st.session_state.clientes[nome] = []
            st.success(f"Cliente {nome} cadastrado com sucesso!")

elif menu == "Registrar Venda":
    st.subheader("Registrar Venda")
    if st.session_state.clientes:
        nome = st.selectbox("Selecione o cliente", list(st.session_state.clientes.keys()))
        codigo = st.number_input("Código do produto", step=1)
        qtd = st.number_input("Quantidade", step=1, min_value=1)
        if st.button("Registrar"):
            if codigo not in produtos:
                st.error("Código não cadastrado!")
            else:
                registrar_venda(nome, codigo, int(qtd))
                st.success(f"Venda registrada: {qtd}x {produtos[codigo]['nome']} para {nome}")
    else:
        st.warning("Nenhum cliente cadastrado ainda.")

elif menu == "Consultar Cliente":
    st.subheader("Consultar Cliente")
    if st.session_state.clientes:
        nome = st.selectbox("Selecione o cliente", list(st.session_state.clientes.keys()))
        if st.button("Ver extrato"):
            st.text(gerar_relatorio_cliente(nome))
    else:
        st.warning("Nenhum cliente cadastrado.")

elif menu == "Relatórios":
    st.subheader("Relatórios")
    if st.session_state.clientes:
        opc = st.radio("Escolha", ["Geral", "De um cliente", "Comissão total"])
        if opc == "Geral":
            st.text(gerar_relatorio_geral())
        elif opc == "De um cliente":
            nome = st.selectbox("Selecione o cliente", list(st.session_state.clientes.keys()))
            st.text(gerar_relatorio_cliente(nome))
        elif opc == "Comissão total":
            total = 0
            for codigos in st.session_state.clientes.values():
                for c in codigos:
                    if c in produtos:
                        total += produtos[c]["preco"]
            comissao = total * 0.40
            st.text(f"💰 Comissão total: R$ {comissao:.2f}")
    else:
        st.warning("Nenhum cliente cadastrado.")
