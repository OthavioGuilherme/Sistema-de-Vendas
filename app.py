# app.py - Parte 1
import streamlit as st
from datetime import datetime
import json
import os
import io
import re
import pdfplumber

# =================== Configuração da página ===================
st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# =================== Usuários ===================
USERS = {
    "othavio": "122008",
    "isabela": "122008",
}

LOG_FILE = "acessos.log"
DB_FILE  = "db.json"

def registrar_acesso(label: str):
    """Registra log de acesso"""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {label}\n")
    except Exception:
        pass

# =================== Controle de acesso ===================
def is_visitante():
    """Retorna True se o usuário for visitante"""
    return bool(st.session_state.get("usuario")) and str(st.session_state.get("usuario")).startswith("visitante-")

# =================== Dados iniciais ===================
PRODUTOS_INICIAIS = {
    3900: {"nome": "Cueca Boxe Inf Animada", "preco": 15.90},
    4416: {"nome": "Calcinha Inf Canelada", "preco": 13.00},
    4497: {"nome": "Cueca Boxe Boss", "preco": 27.15},
    # ... mantenha todos os produtos iniciais aqui
}

VENDAS_INICIAIS = {
    "Tabata": [
        {"codigo": 4685, "quantidade": 1, "preco": 52.95},
        # ... mantenha todas as vendas iniciais
    ],
    # outros clientes
}

# =================== Persistência ===================
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
    """Carrega produtos e clientes. Retorna iniciais caso falhe"""
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

# =================== Session State ===================
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
if "carrinho_undo" not in st.session_state:
    st.session_state.carrinho_undo = []
if "filtro_cliente" not in st.session_state:
    st.session_state.filtro_cliente = ""
if "menu" not in st.session_state:
    st.session_state.menu = "Resumo"

# =================== Helpers ===================
def total_cliente(nome: str) -> float:
    vendas = st.session_state.clientes.get(nome, [])
    return sum(v["preco"] * v["quantidade"] for v in vendas)

def total_geral() -> float:
    return sum(total_cliente(c) for c in st.session_state.clientes.keys())

def wh_ts_geral() -> str:
    linhas = ["📋 *Relatório Geral de Vendas*", ""]
    for c in sorted(st.session_state.clientes.keys(), key=lambda x: x.lower()):
        linhas.append(f"- {c}: R$ {total_cliente(c):.2f}")
    linhas += ["", f"💰 *Total geral*: R$ {total_geral():.2f}",
               f"💸 *Comissão (40%)*: R$ {(total_geral()*0.40):.2f}"]
    return "\n".join(linhas)

def wh_ts_individual(nome: str) -> str:
    vendas = st.session_state.clientes.get(nome, [])
    linhas = [f"📋 *Relatório de {nome}*", ""]
    if not vendas:
        linhas.append("_Sem vendas._")
    else:
        agrup = {}
        for v in vendas:
            chave = (v["codigo"], v["preco"])
            agrup.setdefault(chave, 0)
            agrup[chave] += v["quantidade"]
        for (cod, preco), qtd in sorted(
            agrup.items(),
            key=lambda x: st.session_state.produtos.get(x[0][0], {}).get("nome", f"Cód {x[0][0]}").lower()
        ):
            nomep = st.session_state.produtos.get(cod, {}).get("nome", f"Cód {cod}")
            linhas.append(f"- {nomep} ({qtd}x): R$ {(preco*qtd):.2f}")
        linhas += ["", f"💰 *Total do cliente*: R$ {total_cliente(nome):.2f}"]
    return "\n".join(linhas)

def wh_ts_comissao() -> str:
    tg = total_geral()
    return f"💸 *Comissão total (40%)*: R$ {(tg*0.40):.2f}"

def opcao_produtos_fmt():
    items = [f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f})"
             for cod, dados in st.session_state.produtos.items()]
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
    
# app.py - Parte 2

# =================== Tela Login ===================
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

# =================== Tela Resumo ===================
def tela_resumo():
    st.title("📦 Sistema de Vendas")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Resumo Geral de Vendas")
        tg = total_geral()
        st.markdown(f"**💰 Total geral:** R$ {tg:.2f}")
    with col2:
        st.subheader("Comissão")
        st.markdown(f"**💸 Comissão (40%):** R$ {(tg*0.40):.2f}")

# =================== Tela Registrar Venda ===================
def tela_registrar_venda():
    visitante = is_visitante()
    st.header("🛒 Registrar venda")

    if visitante:
        st.warning("🔒 Visitantes não podem registrar vendas. Os campos abaixo estão apenas para visualização.")

    # Busca/seleção de cliente
    st.session_state.filtro_cliente = st.text_input(
        "Buscar/selecionar cliente (digite ao menos 2 letras):",
        value=st.session_state.filtro_cliente,
        disabled=visitante
    )
    sugestoes = filtrar_clientes(st.session_state.filtro_cliente)
    cliente = st.selectbox("Cliente", sugestoes, index=None, placeholder="Digite para buscar",
                           disabled=visitante) if sugestoes else None

    st.markdown("---")
    st.subheader("Adicionar item ao carrinho")
    lista_fmt = opcao_produtos_fmt()
    sel = st.selectbox("Produto", lista_fmt, index=None, placeholder="Digite para buscar por nome ou código",
                       disabled=visitante)
    qtd = st.number_input("Quantidade", min_value=1, step=1, value=1, disabled=visitante)
    preco_padrao = 0.0
    cod_sel = None
    if sel:
        cod_sel = parse_codigo_from_fmt(sel)
        if cod_sel in st.session_state.produtos:
            preco_padrao = st.session_state.produtos[cod_sel]["preco"]
    preco_venda = st.number_input("Preço desta venda (pode ajustar)", min_value=0.0,
                                  value=float(preco_padrao), step=0.10, format="%.2f", disabled=visitante)

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

    # Carrinho
    st.markdown("### Carrinho")
    if not st.session_state.carrinho:
        st.info("Carrinho vazio.")
    else:
        total_cart = 0.0
        for i, item in enumerate(st.session_state.carrinho):
            st.write(f"**{i+1}.** {item['nome']} ({item['quantidade']}x) - R$ {item['preco']:.2f} cada")
            total_cart += item["quantidade"] * item["preco"]
        st.markdown(f"**Total do carrinho:** R$ {total_cart:.2f}")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Limpar carrinho", disabled=visitante):
                st.session_state.carrinho_undo = st.session_state.carrinho.copy()
                st.session_state.carrinho = []
                st.rerun()
        with c2:
            if st.button("Desfazer último carrinho"):
                st.session_state.carrinho = st.session_state.carrinho_undo.copy()
                st.success("Carrinho restaurado.")
                st.rerun()
        with c3:
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
                    st.session_state.carrinho_undo = st.session_state.carrinho.copy()
                    st.session_state.carrinho = []
                    save_db()
                    st.success("Venda registrada!")
                    st.rerun()

# =================== Tela Clientes ===================
def tela_clientes():
    visitante = is_visitante()
    st.header("👥 Clientes")
    aba_opcoes = ["Consultar cliente", "Cadastrar cliente"]
    aba = st.radio("Ação", aba_opcoes, horizontal=True, index=0)

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

    # Consultar cliente
    filtro = st.text_input("Buscar cliente (digite ao menos 2 letras)").strip()
    matches = filtrar_clientes(filtro)
    cliente = st.selectbox("Selecione o cliente", matches, index=None) if matches else None

    if cliente:
        st.markdown(f"### {cliente}")
        with st.expander("⋯ Ações do cliente", expanded=not visitante):
            col_a, col_b = st.columns(2)
            with col_a:
                novo_nome = st.text_input("Renomear cliente", value=cliente, key=f"rn_{cliente}",
                                          disabled=visitante)
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
                    nova_qtd = st.number_input("Quantidade", min_value=1, step=1, value=qtd,
                                               key=f"q_{cliente}_{idx}", disabled=visitante)
                    novo_preco = st.number_input("Preço (desta venda)", min_value=0.0, step=0.10, value=preco,
                                                 format="%.2f", key=f"p_{cliente}_{idx}", disabled=visitante)
                    c1, c2 = st.columns(2)
                    with c1:
                        if not visitante and st.button("Salvar edição", key=f"save_{cliente}_{idx}"):
                            editar_venda(cliente, idx, nova_qtd, novo_preco)
                    with c2:
                        if not visitante and st.button("Apagar venda", key=f"del_{cliente}_{idx}"):
                            remover_venda(cliente, idx)

            st.markdown(f"**Total do cliente:** R$ {total:.2f}")
            
# ================= PARTE 3 ===========================
# =================== Tela Produtos (continuação) ===================
def tela_produtos():
    visitante = is_visitante()
    st.header("📦 Produtos")
    sub = st.radio("Ação", ["Listar/Buscar", "Adicionar"], horizontal=True, index=0)

    if sub == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar produtos.")
            return
        col1, col2 = st.columns([1,2])
        with col1:
            cod = st.number_input("Código", min_value=1, step=1)
        with col2:
            nomep = st.text_input("Nome do produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.10, format="%.2f")

        if st.button("Salvar produto"):
            cod = int(cod)
            if cod in st.session_state.produtos:
                st.warning("Já existe produto com esse código.")
            elif not nomep.strip():
                st.warning("Informe um nome válido.")
            else:
                st.session_state.produtos[cod] = {"nome": nomep.strip(), "preco": float(preco)}
                save_db()
                st.success("Produto cadastrado!")

    else:
        termo = st.text_input("Buscar por nome ou código").strip().lower()
        itens = []
        for cod, dados in st.session_state.produtos.items():
            nome = dados["nome"]; preco = dados["preco"]
            texto = f"{cod} - {nome} (R$ {preco:.2f})"
            if not termo or (termo in nome.lower() or termo in str(cod)):
                itens.append((cod, nome, preco, texto))

        for cod, nome, preco, texto in sorted(itens, key=lambda x: x[1].lower()):
            with st.expander(texto):
                novo_nome = st.text_input("Nome", value=nome, key=f"pn_{cod}", disabled=visitante)
                novo_preco = st.number_input("Preço", value=float(preco), step=0.10, format="%.2f",
                                             key=f"pp_{cod}", disabled=visitante)
                c1, c2 = st.columns(2)
                with c1:
                    if not visitante:
                        if st.button("Salvar", key=f"s_{cod}"):
                            st.session_state.produtos[cod]["nome"] = novo_nome.strip()
                            st.session_state.produtos[cod]["preco"] = float(novo_preco)
                            save_db()
                            st.success("Produto atualizado.")
                    else:
                        st.button("Salvar", key=f"s_{cod}", disabled=True)
                with c2:
                    if not visitante:
                        if st.button("Apagar", key=f"d_{cod}"):
                            st.session_state.produtos.pop(cod, None)
                            save_db()
                            st.success("Produto apagado.")
                            st.experimental_rerun()
                    else:
                        st.button("Apagar", key=f"d_{cod}", disabled=True)

# =================== Loop principal do app ===================
def main():
    if "logado" not in st.session_state:
        st.session_state.logado = False
    if "usuario" not in st.session_state:
        st.session_state.usuario = None
    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []
    if "filtro_cliente" not in st.session_state:
        st.session_state.filtro_cliente = ""

    if not st.session_state.logado:
        tela_login()
        return

    barra_lateral()
    roteador()

if __name__ == "__main__":
    main()