# app.py
import streamlit as st

# ========================
# Banco inicial
# ========================
clientes_iniciais = {
    "Tabata": [
        {"codigo": "4685", "nome": "Produto 4685", "valor": 52.95, "quantidade": 1},
        {"codigo": "4184", "nome": "Produto 4184", "valor": 25.20, "quantidade": 1},
        {"codigo": "4351", "nome": "Produto 4351", "valor": 54.20, "quantidade": 1},
        {"codigo": "3625", "nome": "Produto 3625", "valor": 28.50, "quantidade": 1},
        {"codigo": "4597", "nome": "Produto 4597", "valor": 29.00, "quantidade": 2},
        {"codigo": "3900", "nome": "Produto 3900", "valor": 15.90, "quantidade": 3},
        {"codigo": "4680", "nome": "Produto 4680", "valor": 51.25, "quantidade": 1},
        {"codigo": "4726", "nome": "Produto 4726", "valor": 22.70, "quantidade": 1},
        {"codigo": "4539", "nome": "Produto 4539", "valor": 19.35, "quantidade": 1},
        {"codigo": "4640", "nome": "Produto 4640", "valor": 18.50, "quantidade": 1},
        {"codigo": "3875", "nome": "Produto 3875", "valor": 17.50, "quantidade": 1},
        {"codigo": "4142", "nome": "Produto 4142", "valor": 16.50, "quantidade": 1},
        {"codigo": "4705", "nome": "Produto 4705", "valor": 22.70, "quantidade": 1},
    ],
    "Valquiria": [
        {"codigo": "4702", "nome": "Produto 4702", "valor": 58.40, "quantidade": 1},
        {"codigo": "4457", "nome": "Produto 4457", "valor": 83.80, "quantidade": 1},
        {"codigo": "4493", "nome": "Produto 4493", "valor": 25.50, "quantidade": 1},
        {"codigo": "4310", "nome": "Produto 4310", "valor": 17.30, "quantidade": 1},
        {"codigo": "4705", "nome": "Produto 4705", "valor": 27.70, "quantidade": 2},
        {"codigo": "3698", "nome": "Produto 3698", "valor": 14.10, "quantidade": 3},
        {"codigo": "4494", "nome": "Produto 4494", "valor": 65.10, "quantidade": 1},
        {"codigo": "4701", "nome": "Produto 4701", "valor": 71.00, "quantidade": 1},
    ],
    "Vanessa": [
        {"codigo": "4562", "nome": "Produto 4562", "valor": 65.10, "quantidade": 1},
        {"codigo": "4699", "nome": "Produto 4699", "valor": 18.90, "quantidade": 3},
        {"codigo": "4539", "nome": "Produto 4539", "valor": 19.35, "quantidade": 1},
    ],
    "Pamela": [
        {"codigo": "4681", "nome": "Produto 4681", "valor": 11.20, "quantidade": 1},
        {"codigo": "4459", "nome": "Produto 4459", "valor": 19.75, "quantidade": 1},
        {"codigo": "4497", "nome": "Produto 4497", "valor": 27.15, "quantidade": 1},
        {"codigo": "4673", "nome": "Produto 4673", "valor": 83.80, "quantidade": 1},
    ],
    "Elan": [
        {"codigo": "4470", "nome": "Produto 4470", "valor": 29.60, "quantidade": 2},
    ],
    "Claudinha": [
        {"codigo": "2750", "nome": "CALÇA CÓS LASER", "valor": 24.90, "quantidade": 1},
        {"codigo": "4239", "nome": "TANGA FIO DUPLO ANELISE", "valor": 16.80, "quantidade": 2},
        {"codigo": "4142", "nome": "TANGA VALDIRA", "valor": 16.50, "quantidade": 2},
        {"codigo": "4343", "nome": "MEIA SAP POMPOM C/3", "valor": 28.20, "quantidade": 1},
        {"codigo": "4122", "nome": "CALÇA FEM MÔNICA", "valor": 103.50, "quantidade": 1},
    ],
}

# Inicialização do estado
if "clientes" not in st.session_state:
    st.session_state.clientes = clientes_iniciais.copy()

COMISSAO = 0.40

# Funções auxiliares
def calcular_total_cliente(cliente):
    return sum(float(v["valor"]) * int(v["quantidade"]) for v in st.session_state.clientes.get(cliente, []))

def calcular_total_geral():
    return sum(calcular_total_cliente(c) for c in st.session_state.clientes)

def gerar_relatorio(tipo, cliente=None):
    if tipo == "geral":
        rel = "📋 *Relatório Geral de Vendas*\n\n"
        for c in st.session_state.clientes:
            rel += f"- {c}: R$ {calcular_total_cliente(c):.2f}\n"
        total = calcular_total_geral()
        rel += f"\n💰 *Total geral*: R$ {total:.2f}\n"
        rel += f"💰 *Comissão (40%)*: R$ {total*COMISSAO:.2f}\n"
        return rel
    elif tipo == "cliente" and cliente:
        rel = f"📋 *Relatório de {cliente}*\n\n"
        for v in st.session_state.clientes[cliente]:
            rel += f"- {v['nome']} ({v['quantidade']}x): R$ {float(v['valor'])*int(v['quantidade']):.2f}\n"
        rel += f"\n💰 Total do cliente: R$ {calcular_total_cliente(cliente):.2f}\n"
        return rel
    elif tipo == "comissao":
        return f"💰 Comissão total (40%): R$ {calcular_total_geral()*COMISSAO:.2f}"

# ========================
# Layout principal
# ========================
st.title("🛍️ Sistema de Vendas")

menu = st.sidebar.radio("Menu", [
    "Cadastrar cliente",
    "Registrar venda",
    "Consultar clientes",
    "Relatórios"
])

if menu == "Cadastrar cliente":
    st.header("Cadastrar cliente")
    nome = st.text_input("Nome do cliente:")
    if st.button("Cadastrar"):
        if nome.strip() and nome not in st.session_state.clientes:
            st.session_state.clientes[nome] = []
            st.success(f"Cliente {nome} cadastrado!")
        else:
            st.warning("Cliente já existe ou nome inválido.")

elif menu == "Registrar venda":
    st.header("Registrar venda")
    cliente = st.selectbox("Selecione o cliente:", list(st.session_state.clientes.keys()))
    codigo = st.text_input("Código:")
    nome_prod = st.text_input("Nome do produto:")
    preco = st.number_input("Preço unitário (R$):", min_value=0.0, step=0.01)
    qtd = st.number_input("Quantidade:", min_value=1, step=1, value=1)
    if st.button("Registrar"):
        st.session_state.clientes[cliente].append({
            "codigo": codigo,
            "nome": nome_prod,
            "valor": float(preco),
            "quantidade": int(qtd)
        })
        st.success("Venda registrada!")

elif menu == "Consultar clientes":
    st.header("Clientes")
    for cliente in list(st.session_state.clientes.keys()):
        with st.expander(f"{cliente} ⋮"):
            st.write("**Vendas:**")
            total = 0
            for v in st.session_state.clientes[cliente]:
                subtotal = float(v['valor']) * int(v['quantidade'])
                st.write(f"- {v['nome']} ({v['quantidade']}x) → R$ {subtotal:.2f}")
                total += subtotal
            st.write(f"**Total do cliente:** R$ {total:.2f}")
            st.markdown("---")
            novo_nome = st.text_input(f"Novo nome para {cliente}:", cliente, key=f"rename_{cliente}")
            cols = st.columns(2)
            if cols[0].button(f"Salvar nome de {cliente}", key=f"save_{cliente}"):
                if novo_nome.strip() and novo_nome != cliente:
                    st.session_state.clientes[novo_nome] = st.session_state.clientes.pop(cliente)
                    st.experimental_rerun()
            if cols[1].button(f"🗑️ Apagar {cliente}", key=f"del_{cliente}"):
                st.session_state.clientes.pop(cliente)
                st.experimental_rerun()

elif menu == "Relatórios":
    st.header("Relatórios")
    opc = st.radio("Escolha:", ["Relatório geral", "Relatório de um cliente", "Comissão total"])
    if opc == "Relatório geral":
        st.text_area("Copie e cole no WhatsApp:", gerar_relatorio("geral"), height=300)
    elif opc == "Relatório de um cliente":
        cliente = st.selectbox("Cliente:", list(st.session_state.clientes.keys()))
        st.text_area("Copie e cole no WhatsApp:", gerar_relatorio("cliente", cliente), height=300)
    else:
        st.success(gerar_relatorio("comissao"))
