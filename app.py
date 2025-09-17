# app.py
import streamlit as st
from datetime import datetime
import json
import os
import io
import re
import pdfplumber  # biblioteca para leitura de PDF

# =============== Config página ===============
st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# =============== Autenticação ===============
USERS = {
    "othavio": "122008",
    "isabela": "122008",
}
LOG_FILE = "acessos.log"
DB_FILE  = "db.json"

def registrar_acesso(label: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {label}\n")
    except Exception:
        pass

def is_visitante():
    return bool(st.session_state.get("usuario")) and str(st.session_state.get("usuario")).startswith("visitante-")

# =============== Dados iniciais e vendas (mantive seu original) ===============
PRODUTOS_INICIAIS = { ... }  # Mantenha o mesmo dicionário
VENDAS_INICIAIS = { ... }    # Mantenha o mesmo dicionário

# =============== Persistência JSON ===============
def save_db():
    try:
        data = {
            "produtos": st.session_state.produtos,
            "clientes": st.session_state.clientes,
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.toast(f"Falha ao salvar: {e}", icon="⚠️")

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            prods = {int(k): v for k, v in data.get("produtos", {}).items()}
            clis  = {k: v for k, v in data.get("clientes", {}).items()}
            return prods, clis
        except Exception:
            pass
    return ({k: v.copy() for k, v in PRODUTOS_INICIAIS.items()},
            {k: [i.copy() for i in lst] for k, lst in VENDAS_INICIAIS.items()})

# =============== Session state ===============
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "produtos" not in st.session_state or "clientes" not in st.session_state:
    p, c = load_db()
    st.session_state.produtos = p
    st.session_state.clientes = c
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "filtro_cliente" not in st.session_state:
    st.session_state.filtro_cliente = ""
if "menu" not in st.session_state:
    st.session_state.menu = "Resumo"

# =============== Helpers ===============
def total_cliente(nome: str) -> float:
    vendas = st.session_state.clientes.get(nome, [])
    return sum(v["preco"] * v["quantidade"] for v in vendas)

def total_geral() -> float:
    return sum(total_cliente(c) for c in st.session_state.clientes.keys())

def opcao_produtos_fmt():
    items = []
    for cod, dados in st.session_state.produtos.items():
        items.append(f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f})")
    return sorted(items, key=lambda s: s.split(" - ",1)[1].lower())

def parse_codigo_from_fmt(s: str):
    try:
        return int(s.split(" - ",1)[0].strip())
    except:
        return None

def filtrar_clientes(filtro: str):
    if not filtro or len(filtro.strip()) < 2:
        return []
    f = filtro.strip().lower()
    return sorted([c for c in st.session_state.clientes if f in c.lower()], key=lambda x: x.lower())

def remover_venda(nome, idx):
    try:
        st.session_state.clientes[nome].pop(idx)
        save_db()
        st.success("Venda removida.")
        st.rerun()
    except:
        st.error("Não foi possível remover.")

def editar_venda(nome, idx, nova_qtd, novo_preco):
    try:
        st.session_state.clientes[nome][idx]["quantidade"] = int(nova_qtd)
        st.session_state.clientes[nome][idx]["preco"] = float(novo_preco)
        save_db()
        st.success("Venda atualizada.")
        st.rerun()
    except:
        st.error("Não foi possível editar.")

def renomear_cliente(nome_antigo, nome_novo):
    if not nome_novo.strip():
        st.warning("Informe um nome válido.")
        return
    if nome_novo in st.session_state.clientes and nome_novo != nome_antigo:
        st.warning("Já existe cliente com esse nome.")
        return
    st.session_state.clientes[nome_novo] = st.session_state.clientes.pop(nome_antigo)
    save_db()
    st.success("Cliente renomeado.")
    st.rerun()

def apagar_cliente(nome):
    st.session_state.clientes.pop(nome, None)
    save_db()
    st.success("Cliente apagado.")
    st.rerun()

def adicionar_produto_manual(codigo, nome, quantidade, preco_unitario):
    try:
        cod = int(codigo)
    except:
        raise ValueError("Código inválido")
    st.session_state.produtos[cod] = {"nome": nome.strip(), "preco": float(preco_unitario)}
    save_db()

def zerar_todas_vendas():
    for k in list(st.session_state.clientes.keys()):
        st.session_state.clientes[k] = []
    save_db()

# =============== Telas ===============
def tela_login():
    st.title("🔐 Login")
    escolha = st.radio("Como deseja entrar?", ["Usuário cadastrado", "Visitante"], horizontal=True)
    if escolha == "Usuário cadastrado":
        user = st.text_input("Usuário").strip().lower()
        senha = st.text_input("Senha", type="password").strip()
        if st.button("Entrar"):
            if user in USERS and USERS[user].lower() == senha.lower():
                st.session_state.logado = True
                st.session_state.usuario = user
                registrar_acesso(f"login-usuario: {user}")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        nome = st.text_input("Digite seu nome para entrar como visitante").strip()
        if st.button("Entrar como visitante"):
            if nome:
                st.session_state.logado = True
                st.session_state.usuario = f"visitante-{nome}"
                registrar_acesso(f"login-visitante: {nome}")
                st.rerun()
            else:
                st.warning("Por favor, digite um nome.")

# ----------------- Tela Registrar Venda (com remover do carrinho) -----------------
def tela_registrar_venda():
    visitante = is_visitante()
    st.header("🛒 Registrar venda")

    if visitante:
        st.warning("🔒 Visitantes não podem registrar vendas. Campos apenas para visualização.")

    st.session_state.filtro_cliente = st.text_input(
        "Buscar/selecionar cliente (2+ letras):",
        value=st.session_state.filtro_cliente,
        disabled=visitante
    )
    sugestoes = filtrar_clientes(st.session_state.filtro_cliente)
    cliente = st.selectbox("Cliente", sugestoes, index=None, placeholder="Digite para buscar",
                           disabled=visitante) if sugestoes else None

    st.markdown("---")
    st.subheader("Adicionar item ao carrinho")
    lista_fmt = opcao_produtos_fmt()
    sel = st.selectbox("Produto", lista_fmt, index=None, placeholder="Digite para buscar", disabled=visitante)
    qtd = st.number_input("Quantidade", min_value=1, step=1, value=1, disabled=visitante)
    preco_padrao = 0.0
    cod_sel = None
    if sel:
        cod_sel = parse_codigo_from_fmt(sel)
        if cod_sel in st.session_state.produtos:
            preco_padrao = st.session_state.produtos[cod_sel]["preco"]
    preco_venda = st.number_input("Preço desta venda", min_value=0.0, value=float(preco_padrao),
                                  step=0.10, format="%.2f", disabled=visitante)

    if st.button("Adicionar ao carrinho", disabled=visitante):
        if not cliente:
            st.warning("Selecione um cliente.")
        elif not cod_sel:
            st.warning("Selecione um produto.")
        else:
            nomep = st.session_state.produtos[cod_sel]["nome"]
            st.session_state.carrinho.append({
                "codigo": cod_sel,
                "nome": nomep,
                "quantidade": int(qtd),
                "preco": float(preco_venda),
            })
            st.success(f"Adicionado: {nomep} ({qtd}x)")

    # Carrinho com remover item
    st.markdown("### Carrinho")
    if not st.session_state.carrinho:
        st.info("Carrinho vazio.")
    else:
        total_cart = 0.0
        for i, item in enumerate(st.session_state.carrinho):
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(f"**{i+1}.** {item['nome']} ({item['quantidade']}x) - R$ {item['preco']:.2f} cada")
            with col2:
                if st.button("🗑️ Remover", key=f"rm_{i}", disabled=visitante):
                    st.session_state.carrinho.pop(i)
                    st.success("Item removido do carrinho.")
                    st.experimental_rerun()
            total_cart += item["quantidade"] * item["preco"]
        st.markdown(f"**Total do carrinho:** R$ {total_cart:.2f}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Limpar carrinho", disabled=visitante):
                st.session_state.carrinho = []
                st.rerun()
        with c2:
            if st.button("Finalizar venda", disabled=visitante):
                if not cliente:
                    st.warning("Selecione um cliente.")
                elif not st.session_state.carrinho:
                    st.warning("Carrinho vazio.")
                else:
                    st.session_state.clientes.setdefault(cliente, [])
                    st.session_state.clientes[cliente].extend(
                        [{"codigo": it["codigo"], "quantidade": it["quantidade"], "preco": it["preco"]}
                         for it in st.session_state.carrinho]
                    )
                    st.session_state.carrinho = []
                    save_db()
                    st.success("Venda registrada!")
                    st.rerun()

# ----------------- Tela Clientes (com adicionar produto direto) -----------------
def tela_clientes():
    visitante = is_visitante()
    st.header("👥 Clientes")
    aba_opcoes = ["Consultar cliente", "Cadastrar cliente"]
    aba = st.radio("Ação", aba_opcoes, horizontal=True, index=0 if visitante else 0)

    if visitante and aba == "Cadastrar cliente":
        st.info("🔒 Visitantes não podem cadastrar clientes.")
        return

    if aba == "Cadastrar cliente":
        nome = st.text_input("Nome do cliente").strip()
        if st.button("Salvar cliente"):
            if not nome:
                st.warning("Informe um nome.")
            elif nome in st.session_state.clientes:
                st.warning("Já existe cliente com esse nome.")
            else:
                st.session_state.clientes[nome] = []
                save_db()
                st.success("Cliente cadastrado!")
        return

    filtro = st.text_input("Buscar cliente (2+ letras)").strip()
    matches = filtrar_clientes(filtro)
    cliente = st.selectbox("Selecione o cliente", matches, index=None) if matches else None

    if cliente:
        st.markdown(f"### {cliente}")
        with st.expander("⋯ Ações do cliente", expanded=not visitante):
            col_a, col_b = st.columns(2)
            with col_a:
                novo_nome = st.text_input("Renomear cliente", value=cliente, key=f"rn_{cliente}", disabled=visitante)
                if not visitante and st.button("Salvar novo nome", key=f"btn_rn_{cliente}"):
                    renomear_cliente(cliente, novo_nome)
            with col_b:
                if not visitante and st.button("Apagar cliente", key=f"delcli_{cliente}"):
                    apagar_cliente(cliente)

        vendas = st.session_state.clientes.get(cliente, [])
        if not vendas:
            st.info("Sem vendas para este cliente.")
        else:
            total = 0.0
            for idx, v in enumerate(vendas):
                cod = v["codigo"]
                nomep = st.session_state.produtos.get(cod, {}).get("nome", f"Cód {cod}")
                preco = float(v.get("preco", st.session_state.produtos.get(cod, {}).get("preco", 0.0)))
                qtd = int(v.get("quantidade", 1))
                subtotal = preco * qtd
                total += subtotal
                with st.expander(f"{nomep} ({qtd}x) - R$ {preco:.2f} | Subtotal: R$ {subtotal:.2f}"):
                    nova_qtd = st.number_input("Quantidade", min_value=1, step=1, value=qtd, key=f"q_{cliente}_{idx}", disabled=visitante)
                    novo_preco = st.number_input("Preço", min_value=0.0, step=0.10, value=preco, format="%.2f", key=f"p_{cliente}_{idx}", disabled=visitante)
                    col1, col2 = st.columns(2)
                    with col1:
                        if not visitante and st.button("Salvar edição", key=f"save_{cliente}_{idx}"):
                            editar_venda(cliente, idx, nova_qtd, novo_preco)
                    with col2:
                        if not visitante and st.button("Apagar venda", key=f"del_{cliente}_{idx}"):
                            remover_venda(cliente, idx)
            st.markdown(f"**Total do cliente:** R$ {total:.2f}")

        # Nova seção: Adicionar produto diretamente para este cliente
        st.markdown("### ➕ Adicionar produto")
        lista_fmt = opcao_produtos_fmt()
        sel = st.selectbox("Produto", lista_fmt, index=None, placeholder="Selecione um produto")
        qtd = st.number_input("Quantidade", min_value=1, step=1, value=1, key=f"q_cli_{cliente}")
        preco_padrao = 0.0
        cod_sel = None
        if sel:
            cod_sel = parse_codigo_from_fmt(sel)
            if cod_sel in st.session_state.produtos:
                preco_padrao = st.session_state.produtos[cod_sel]["preco"]
        preco_venda = st.number_input("Preço desta venda", min_value=0.0, value=float(preco_padrao),
                                      step=0.10, format="%.2f", key=f"p_cli_{cliente}")

        if st.button("Adicionar produto ao cliente", key=f"btn_cli_{cliente}"):
            if cod_sel is None:
                st.warning("Selecione um produto válido.")
            else:
                st.session_state.clientes[cliente].append({
                    "codigo": cod_sel,
                    "quantidade": int(qtd),
                    "preco": float(preco_venda)
                })
                save_db()
                st.success("Produto adicionado ao cliente!")
                st.experimental_rerun()

# ----------------- Tela Produtos e Relatórios (mantidas suas funções originais) -----------------
# Aqui você mantém tela_produtos(), tela_relatorios(), tela_acessos() como no seu código

# ----------------- Sidebar melhorada -----------------
def bloco_backup_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧰 Backup & Estoque")
    db_json = json.dumps({
        "produtos": st.session_state.produtos,
        "clientes": st.session_state.clientes,
    }, ensure_ascii=False, indent=2)
    st.sidebar.download_button("⬇️ Exportar backup (.json)", data=db_json.encode("utf-8"),
                               file_name="backup_sistema_vendas.json")
    if not is_visitante():
        up = st.sidebar.file_uploader("⬆️ Restaurar backup (.json)", type=["json"])
        if up is not None:
            try:
                data = json.load(up)
                prods = {int(k): v for k, v in data.get("produtos", {}).items()}
                clis  = {k: v for k, v in data.get("clientes", {}).items()}
                st.session_state.produtos = prods
                st.session_state.clientes = clis
                save_db()
                st.sidebar.success("Backup restaurado!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Falha ao restaurar: {e}")

# ----------------- Barra lateral -----------------
def barra_lateral():
    st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario}")
    opcoes = ["Resumo", "Registrar venda", "Clientes", "Produtos", "Relatórios", "Sair"]
    if not is_visitante():
        opcoes.insert(-1, "Acessos")
    idx_atual = opcoes.index(st.session_state.menu) if st.session_state.menu in opcoes else 0
    menu = st.sidebar.radio("Menu", opcoes, index=idx_atual)
    st.session_state.menu = menu
    bloco_backup_sidebar()

# ----------------- Roteador -----------------
def roteador():
    if st.session_state.menu == "Resumo":
        tela_resumo()
    elif st.session_state.menu == "Registrar venda":
        tela_registrar_venda()
    elif st.session_state.menu == "Clientes":
        tela_clientes()
    elif st.session