import streamlit as st

# ===============================
# BANCO DE DADOS (em memória)
# ===============================

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

clientes = {
    "Tabata": [{"codigo": 4685, "quantidade": 1}],
    "Valquiria": [{"codigo": 4705, "quantidade": 2}],
    "Vanessa": [{"codigo": 4562, "quantidade": 1}],
    "Pamela": [{"codigo": 4681, "quantidade": 1}],
    "Elan": [{"codigo": 4470, "quantidade": 2}],
    "Claudinha": [{"codigo": 2750, "quantidade": 1}],
}

# ===============================
# FUNÇÕES AUXILIARES
# ===============================

def calcular_total_cliente(vendas):
    return sum(produtos[v["codigo"]]["preco"] * v["quantidade"] for v in vendas)

def calcular_total_geral():
    return sum(calcular_total_cliente(vendas) for vendas in clientes.values())

def calcular_comissao():
    return calcular_total_geral() * 0.40

# ===============================
# INTERFACE
# ===============================

st.set_page_config(page_title="Sistema de Vendas", layout="wide")
st.title("📊 Sistema de Vendas")

st.subheader("Resumo Geral")
st.write(f"💰 **Total de vendas:** R$ {calcular_total_geral():.2f}")
st.write(f"💵 **Comissão (40%):** R$ {calcular_comissao():.2f}")

menu = st.sidebar.radio("Menu", ["Cadastrar cliente", "Registrar venda", "Consultar cliente", "Relatórios"])

if menu == "Cadastrar cliente":
    st.subheader("👤 Cadastrar Cliente")
    nome = st.text_input("Nome do cliente:")
    if st.button("Cadastrar"):
        if nome.strip() == "":
            st.warning("Digite um nome válido.")
        elif nome in clientes:
            st.warning("Cliente já cadastrado.")
        else:
            clientes[nome] = []
            st.success(f"Cliente {nome} cadastrado com sucesso!")

elif menu == "Registrar venda":
    st.subheader("🛒 Registrar Venda")
    cliente = st.selectbox("Selecione o cliente", sorted(clientes.keys()))
    codigo = st.number_input("Código do produto", step=1)
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    if st.button("Registrar"):
        if codigo in produtos:
            clientes[cliente].append({"codigo": codigo, "quantidade": quantidade})
            st.success(f"Venda registrada para {cliente}.")
        else:
            st.error("Código de produto não encontrado.")

elif menu == "Consultar cliente":
    st.subheader("🔍 Consultar Cliente")
    termo = st.text_input("Buscar cliente (digite ao menos 2 letras):")
    if len(termo) >= 2:
        lista_filtrada = sorted([n for n in clientes if termo.lower() in n.lower()])
        if lista_filtrada:
            selecionado = st.selectbox("Selecione o cliente", lista_filtrada)
            if selecionado:
                st.write(f"📋 Relatório de **{selecionado}**")
                total = calcular_total_cliente(clientes[selecionado])
                for i, v in enumerate(clientes[selecionado]):
                    p = produtos[v['codigo']]
                    st.write(f"- {p['nome']} ({v['quantidade']}x): R$ {p['preco'] * v['quantidade']:.2f}")
                st.write(f"💰 Total do cliente: R$ {total:.2f}")

                if st.button("Apagar cliente"):
                    clientes.pop(selecionado)
                    st.success("Cliente apagado com sucesso.")
        else:
            st.info("Nenhum cliente encontrado.")
    else:
        st.info("Digite ao menos 2 caracteres para buscar.")

elif menu == "Relatórios":
    st.subheader("📑 Relatórios")
    opc = st.radio("Escolha:", ["Geral", "Por cliente", "Comissão total"])
    if opc == "Geral":
        st.write("📋 Relatório Geral de Vendas")
        for nome, vendas in clientes.items():
            st.write(f"- {nome}: R$ {calcular_total_cliente(vendas):.2f}")
        st.write(f"💰 Total geral: R$ {calcular_total_geral():.2f}")
        st.write(f"💵 Comissão (40%): R$ {calcular_comissao():.2f}")
    elif opc == "Por cliente":
        cli = st.selectbox("Selecione o cliente", sorted(clientes.keys()))
        total = calcular_total_cliente(clientes[cli])
        st.write(f"📋 Relatório de {cli}")
        for v in clientes[cli]:
            p = produtos[v['codigo']]
            st.write(f"- {p['nome']} ({v['quantidade']}x): R$ {p['preco'] * v['quantidade']:.2f}")
        st.write(f"💰 Total do cliente: R$ {total:.2f}")
    else:
        st.write(f"💵 Comissão total: R$ {calcular_comissao():.2f}")
