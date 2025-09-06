# app.py
import streamlit as st

# ========================
# Inicialização
# ========================
if "clientes" not in st.session_state:
    st.session_state.clientes = {}

COMISSAO = 0.40  # 40%

# ========================
# Funções
# ========================

def calcular_total_cliente(cliente):
    vendas = st.session_state.clientes.get(cliente, [])
    total = 0.0
    for v in vendas:
        try:
            total += float(v["valor"]) * int(v["quantidade"])
        except (ValueError, TypeError):
            pass
    return total

def calcular_total_geral():
    return sum(calcular_total_cliente(c) for c in st.session_state.clientes)

def gerar_relatorio(tipo, cliente=None):
    if tipo == "geral":
        rel = "📋 *Relatório Geral de Vendas*\n\n"
        for c in st.session_state.clientes:
            total = calcular_total_cliente(c)
            rel += f"- {c}: R$ {total:.2f}\n"
        total_geral = calcular_total_geral()
        rel += f"\n💰 *Total geral*: R$ {total_geral:.2f}\n"
        rel += f"💰 *Comissão (40%)*: R$ {total_geral * COMISSAO:.2f}\n"
        return rel

    elif tipo == "cliente" and cliente:
        rel = f"📋 *Relatório de {cliente}*\n\n"
        total = calcular_total_cliente(cliente)
        for v in st.session_state.clientes[cliente]:
            try:
                rel += f"- {v['nome']} ({int(v['quantidade'])}x): R$ {float(v['valor']) * int(v['quantidade']):.2f}\n"
            except (ValueError, TypeError):
                rel += f"- {v['nome']} ({v['quantidade']}x): R$ {v['valor']}\n"
        rel += f"\n💰 Total do cliente: R$ {total:.2f}\n"
        return rel

    elif tipo == "comissao":
        total_geral = calcular_total_geral()
        return f"💰 Comissão total (40%): R$ {total_geral * COMISSAO:.2f}"

    return "❌ Tipo de relatório inválido."


# ========================
# Layout / Menu
# ========================
st.title("🛍️ Sistema de Vendas")

menu = st.sidebar.radio("Menu", [
    "Cadastrar cliente",
    "Registrar venda",
    "Consultar cliente",
    "Relatórios"
])

# ========================
# Cadastrar cliente
# ========================
if menu == "Cadastrar cliente":
    st.header("Cadastrar cliente")
    nome = st.text_input("Nome do cliente:")
    if st.button("Cadastrar"):
        if nome.strip() == "":
            st.warning("Digite um nome válido.")
        elif nome in st.session_state.clientes:
            st.warning("Cliente já cadastrado.")
        else:
            st.session_state.clientes[nome] = []
            st.success(f"Cliente {nome} cadastrado com sucesso!")

# ========================
# Registrar venda
# ========================
elif menu == "Registrar venda":
    st.header("Registrar venda")
    if not st.session_state.clientes:
        st.warning("Nenhum cliente cadastrado.")
    else:
        cliente = st.selectbox("Selecione o cliente:", list(st.session_state.clientes.keys()))
        codigo = st.text_input("Código do produto:")
        nome_prod = st.text_input("Nome do produto:")
        preco = st.number_input("Preço unitário (R$):", min_value=0.0, step=0.01)
        quantidade = st.number_input("Quantidade:", min_value=1, step=1, value=1)
        if st.button("Registrar"):
            st.session_state.clientes[cliente].append({
                "codigo": codigo,
                "nome": nome_prod,
                "valor": float(preco),
                "quantidade": int(quantidade)
            })
            st.success("Venda registrada com sucesso!")

# ========================
# Consultar cliente (com editar/apagar)
# ========================
elif menu == "Consultar cliente":
    st.header("Consultar / Editar / Apagar venda")
    if not st.session_state.clientes:
        st.warning("Nenhum cliente cadastrado.")
    else:
        cliente = st.selectbox("Selecione o cliente:", list(st.session_state.clientes.keys()))
        vendas = st.session_state.clientes[cliente]
        if not vendas:
            st.info("Esse cliente não tem vendas.")
        else:
            for i, v in enumerate(vendas):
                qtd = int(v.get("quantidade", 0)) if str(v.get("quantidade", "")).isdigit() else v.get("quantidade", "")
                try:
                    preco_unit = float(v.get("valor", 0.0))
                except (ValueError, TypeError):
                    preco_unit = v.get("valor", "")
                st.write(f"**{i+1}.** {v['nome']} ({qtd}x) - R$ {preco_unit:.2f} cada" if isinstance(preco_unit, (int, float)) else f"**{i+1}.** {v['nome']} ({qtd}x) - {preco_unit}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Editar {i}", key=f"edit_{cliente}_{i}"):
                        with st.form(f"form_edit_{cliente}_{i}", clear_on_submit=True):
                            novo_nome = st.text_input("Nome do produto:", v['nome'])
                            nova_qtd = st.number_input("Quantidade:", min_value=1, value=int(qtd) if isinstance(qtd, int) else 1)
                            novo_valor = st.number_input("Valor unitário:", min_value=0.0, step=0.01, value=float(preco_unit) if isinstance(preco_unit, (int, float)) else 0.0)
                            submitted = st.form_submit_button("Salvar alterações")
                            if submitted:
                                v['nome'] = novo_nome
                                v['quantidade'] = int(nova_qtd)
                                v['valor'] = float(novo_valor)
                                st.success("Venda atualizada!")
                                st.experimental_rerun()
                with col2:
                    if st.button(f"🗑️ Apagar {i}", key=f"del_{cliente}_{i}"):
                        vendas.pop(i)
                        st.success("Venda apagada!")
                        st.experimental_rerun()

# ========================
# Relatórios
# ========================
elif menu == "Relatórios":
    st.header("Gerar relatórios")
    opc = st.radio("Escolha:", [
        "Relatório geral",
        "Relatório de um cliente",
        "Comissão total"
    ])

    if opc == "Relatório geral":
        st.text_area("Copie e cole no WhatsApp:", gerar_relatorio("geral"), height=300)
    elif opc == "Relatório de um cliente":
        if not st.session_state.clientes:
            st.warning("Nenhum cliente cadastrado.")
        else:
            cliente = st.selectbox("Selecione o cliente:", list(st.session_state.clientes.keys()))
            st.text_area("Copie e cole no WhatsApp:", gerar_relatorio("cliente", cliente), height=300)
    elif opc == "Comissão total":
        st.success(gerar_relatorio("comissao"))
