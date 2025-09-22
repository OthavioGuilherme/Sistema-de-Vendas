# ==========================
# PARTE 1 - Inicialização e Login
# ==========================
import streamlit as st
import json
import os
from datetime import datetime

DB_FILE = "db.json"

# ---------------- FUNÇÃO: Salvar DB ----------------
def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "produtos": st.session_state.get("produtos", {}),
                "clientes": st.session_state.get("clientes", {})
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Erro ao salvar DB:", e)

# ---------------- FUNÇÃO: Carregar DB ----------------
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state["produtos"] = {int(k): v for k, v in data.get("produtos", {}).items()}
                st.session_state["clientes"] = data.get("clientes", {})
        except Exception:
            st.session_state["produtos"] = {}
            st.session_state["clientes"] = {}
    else:
        st.session_state["produtos"] = {}
        st.session_state["clientes"] = {}

# ---------------- FUNÇÃO: Verifica visitante ----------------
def is_visitante():
    return st.session_state.get("visitante", False)

# ---------------- FUNÇÃO: Tela de Login ----------------
def login():
    st.title("🔐 Sistema de Vendas")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == "admin" and senha == "123":
            st.session_state["usuario"] = usuario
            st.session_state["visitante"] = False
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos!")

    if st.button("Entrar como Visitante"):
        st.session_state["usuario"] = "visitante"
        st.session_state["visitante"] = True
        st.rerun()

# Inicializa DB na primeira execução
if "produtos" not in st.session_state:
    load_db()


# ==========================
# PARTE 2 - Produtos e Vendas
# ==========================

# ---------------- FUNÇÃO: Tela de Produtos ----------------
def tela_produtos():
    st.header("📦 Cadastro de Produtos")

    visitante = is_visitante()
    if visitante:
        st.info("🔒 Visitantes não podem cadastrar produtos.")
        return

    with st.form("form_produto"):
        codigo = st.number_input("Código do produto", min_value=1, step=1)
        nome = st.text_input("Nome do produto")
        preco = st.number_input("Preço", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Salvar Produto")

        if submitted:
            st.session_state["produtos"][codigo] = {"nome": nome, "preco": preco}
            save_db()
            st.success(f"Produto {nome} cadastrado com sucesso!")

    if st.session_state["produtos"]:
        st.subheader("Lista de Produtos")
        for cod, p in st.session_state["produtos"].items():
            st.write(f"{cod} - {p['nome']} - R$ {p['preco']:.2f}")


# ==========================
# PARTE 3 - Clientes, Relatórios e Menu
# ==========================

# ---------------- FUNÇÃO: Tela de Clientes ----------------
def tela_clientes():
    st.header("👥 Clientes")
    visitante = is_visitante()

    aba = st.radio("Ação", ["Consultar cliente", "Cadastrar cliente"], horizontal=True)

    if visitante and aba == "Cadastrar cliente":
        st.info("🔒 Visitantes não podem cadastrar clientes.")
        return

    if aba == "Cadastrar cliente":
        nome = st.text_input("Nome do cliente")
        if st.button("Salvar cliente"):
            if not nome.strip():
                st.warning("Informe um nome válido.")
            elif nome in st.session_state["clientes"]:
                st.warning("Cliente já existe.")
            else:
                st.session_state["clientes"][nome.strip()] = []
                save_db()
                st.success(f"Cliente {nome} cadastrado!")
        return

    # Consultar cliente
    filtro = st.text_input("Buscar cliente (2+ letras)").lower()
    matches = [c for c in st.session_state["clientes"] if filtro in c.lower()]
    cliente = st.selectbox("Selecione o cliente", matches) if matches else None

    if cliente:
        st.subheader(f"Cliente: {cliente}")
        vendas = st.session_state["clientes"][cliente]

        # ➕ Adicionar Venda
        st.markdown("### ➕ Adicionar Venda")
        if visitante:
            st.info("🔒 Visitantes não podem adicionar vendas.")
        else:
            produto_input = st.text_input("Digite código ou nome do produto")
            opcoes_produtos = [
                f"{cod} - {p['nome']}" for cod, p in st.session_state["produtos"].items()
                if produto_input.lower() in str(cod) or produto_input.lower() in p["nome"].lower()
            ]
            produto_selecionado = st.selectbox("Escolha o produto", opcoes_produtos) if opcoes_produtos else None
            quantidade = st.number_input("Quantidade", min_value=1, step=1)

            if st.button("Adicionar venda"):
                if produto_selecionado:
                    cod = int(produto_selecionado.split(" - ")[0])
                    p = st.session_state["produtos"][cod]
                    vendas.append({"cod": cod, "nome": p["nome"], "preco": p["preco"], "quantidade": quantidade})
                    st.session_state["clientes"][cliente] = vendas
                    save_db()
                    st.success(f"Venda adicionada ao cliente {cliente}!")

        # 📝 Vendas do Cliente
        st.markdown("### 📝 Vendas do Cliente")
        if not vendas:
            st.info("Nenhuma venda registrada.")
        for idx, v in enumerate(vendas):
            col1, col2, col3 = st.columns([5,2,2])
            cod = v.get("cod")
            nome = v.get("nome", "???")
            quantidade = v.get("quantidade", 0)
            preco = v.get("preco", 0.0)
            valor_exibir = f"R$ {preco:.2f}" if not visitante else "R$ *****"

            linha_exibir = f"{nome} x {quantidade} ({valor_exibir} cada)" if cod is None else f"{cod} - {nome} x {quantidade} ({valor_exibir} cada)"
            col1.write(linha_exibir)

            if visitante:
                col2.button("Apagar", key=f"apagar_{cliente}_{idx}", disabled=True)
                col3.number_input("Editar Qtde", min_value=1, value=quantidade, key=f"editar_{cliente}_{idx}", disabled=True)
                col3.button("Salvar", key=f"salvar_{cliente}_{idx}", disabled=True)
            else:
                if col2.button("Apagar", key=f"apagar_{cliente}_{idx}"):
                    vendas.pop(idx)
                    st.session_state["clientes"][cliente] = vendas
                    save_db()
                    st.success("Venda apagada")
                    st.rerun()

                nova_qtd = col3.number_input("Editar Qtde", min_value=1, value=quantidade, key=f"editar_{cliente}_{idx}")
                if col3.button("Salvar", key=f"salvar_{cliente}_{idx}"):
                    vendas[idx]["quantidade"] = nova_qtd
                    save_db()
                    st.success("Venda atualizada")

        # Apagar cliente
        if not visitante:
            confirmar = st.checkbox(f"Confirme que deseja apagar o cliente {cliente}")
            if confirmar:
                if st.button(f"🗑️ Apagar cliente {cliente}"):
                    st.session_state["clientes"].pop(cliente)
                    save_db()
                    st.success(f"Cliente {cliente} apagado!")
                    st.rerun()


# ---------------- FUNÇÃO: Relatório ----------------
def tela_relatorio():
    st.header("📊 Relatório de Vendas")

    visitante = is_visitante()
    if not st.session_state["clientes"]:
        st.info("Nenhum cliente cadastrado.")
        return

    total_vendas = 0

    for cliente, vendas in st.session_state["clientes"].items():
        st.subheader(f"Cliente: {cliente}")

        if not vendas:
            st.write("Nenhuma venda registrada.")
            continue

        for v in vendas:
            nome = v.get("nome", "Produto")
            quantidade = v.get("quantidade", 0)
            valor = v.get("preco", 0.0)
            cod = v.get("cod")

            if visitante:
                valor_exibir = "R$ ???"
            else:
                valor_exibir = f"R$ {valor:.2f}"

            if cod:
                linha_exibir = f"{cod} - {nome} x {quantidade} ({valor_exibir} cada)"
            else:
                linha_exibir = f"{nome} x {quantidade} ({valor_exibir} cada)"

            st.write(linha_exibir)

            if not visitante:
                total_vendas += quantidade * valor

    if not visitante:
        if total_vendas < 1000:
            comissao = total_vendas * 0.30
        elif total_vendas < 2000:
            comissao = total_vendas * 0.35
        else:
            comissao = total_vendas * 0.40

        st.subheader(f"💰 Total de Vendas: R$ {total_vendas:.2f}")
        st.subheader(f"🏆 Comissão: R$ {comissao:.2f}")
    else:
        st.subheader("💰 Total de Vendas: R$ ???")
        st.subheader("🏆 Comissão: R$ ???")


# ---------------- FUNÇÃO: Barra Lateral ----------------
def barra_lateral():
    st.sidebar.title("📌 Menu")

    visitante = is_visitante()
    opcoes = {
        "Cadastro de Produtos": tela_produtos,
        "Cadastro de Clientes": tela_clientes,
    }

    if not visitante:
        opcoes.update({
            "Relatório": tela_relatorio,
        })
    else:
        opcoes.update({
            "Relatório (Visualização)": tela_relatorio,
        })

    escolha = st.sidebar.radio("Ir para:", list(opcoes.keys()))
    func = opcoes[escolha]
    func()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.session_state["usuario"] = None
        st.rerun()


# ---------------- FUNÇÃO PRINCIPAL ----------------
def main():
    if st.session_state.get("usuario") is None:
        login()
    else:
        barra_lateral()


if __name__ == "__main__":
    main()