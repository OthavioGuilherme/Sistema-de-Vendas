# app.py
import streamlit as st
from datetime import datetime

# =========================
# Configuração da página
# =========================
st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# =========================
# Helpers
# =========================
def money(v):
    try:
        return f"R$ {float(v):.2f}"
    except:
        return "R$ 0.00"

def log_acesso(usuario: str):
    try:
        with open("acessos.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {usuario}\n")
    except Exception:
        pass  # Em alguns ambientes pode não persistir; ignoramos erro.

def init_state():
    if "inited" in st.session_state:
        return

    # ---- Usuários (login) ----
    st.session_state.users = {
        "othavio": "122008",
        "isabela": "122008",
    }

    # ---- Produtos (catálogo) ----
    st.session_state.produtos = {
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
        4705: {"nome": "Tanga Ilma", "preco": 27.70},  # preço atual do catálogo
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

    # ---- Clientes e vendas (pré-registradas com preço da compra) ----
    st.session_state.clientes = {
        # Tabata - lista original com preço por item (inclui 4705 a 22,70 para Tabata)
        "Tabata": [
            {"codigo": 4685, "nome": "Soutien Francesca", "quantidade": 1, "preco_unit": 52.95},
            {"codigo": 4184, "nome": "Meia Masc Manhattan Kit", "quantidade": 1, "preco_unit": 25.20},
            {"codigo": 4351, "nome": "Soutien Soft Ribana", "quantidade": 1, "preco_unit": 54.20},
            {"codigo": 3625, "nome": "Cueca Boxe Carlos", "quantidade": 1, "preco_unit": 28.50},
            {"codigo": 4597, "nome": "Cueca Boxe Roger", "quantidade": 1, "preco_unit": 29.00},
            {"codigo": 3900, "nome": "Cueca Boxe Inf Animada", "quantidade": 1, "preco_unit": 15.90},
            {"codigo": 3900, "nome": "Cueca Boxe Inf Animada", "quantidade": 1, "preco_unit": 15.90},
            {"codigo": 3900, "nome": "Cueca Boxe Inf Animada", "quantidade": 1, "preco_unit": 15.90},
            {"codigo": 4597, "nome": "Cueca Boxe Roger", "quantidade": 1, "preco_unit": 29.00},
            {"codigo": 4680, "nome": "Samba Cançao Fernando", "quantidade": 1, "preco_unit": 51.25},
            {"codigo": 4726, "nome": "Tanga Mapola", "quantidade": 1, "preco_unit": 22.70},
            {"codigo": 4539, "nome": "Tanga Kamili", "quantidade": 1, "preco_unit": 19.35},
            {"codigo": 4640, "nome": "Tanga Import. Neon", "quantidade": 1, "preco_unit": 18.50},
            {"codigo": 3875, "nome": "Tanga Nazaré", "quantidade": 1, "preco_unit": 17.50},
            {"codigo": 4142, "nome": "Tanga Valdira", "quantidade": 1, "preco_unit": 16.50},
            {"codigo": 4705, "nome": "Tanga Ilma", "quantidade": 1, "preco_unit": 22.70},  # preço da compra da Tabata
        ],
        # Valquiria
        "Valquiria": [
            {"codigo": 4702, "nome": "Top Sueli032", "quantidade": 1, "preco_unit": 58.40},
            {"codigo": 4457, "nome": "Conjunto Verena", "quantidade": 1, "preco_unit": 83.80},
            {"codigo": 4493, "nome": "Meia Fem Analu Kit C/3", "quantidade": 1, "preco_unit": 25.50},
            {"codigo": 4310, "nome": "Tangao Nani Suede", "quantidade": 1, "preco_unit": 17.30},
            {"codigo": 4705, "nome": "Tanga Ilma", "quantidade": 1, "preco_unit": 27.70},
            {"codigo": 4705, "nome": "Tanga Ilma", "quantidade": 1, "preco_unit": 27.70},
            {"codigo": 3698, "nome": "Tanga Fio Cerejeira", "quantidade": 1, "preco_unit": 14.10},
            {"codigo": 3698, "nome": "Tanga Fio Cerejeira", "quantidade": 1, "preco_unit": 14.10},
            {"codigo": 3698, "nome": "Tanga Fio Cerejeira", "quantidade": 1, "preco_unit": 14.10},
            {"codigo": 4494, "nome": "Top Import Coração", "quantidade": 1, "preco_unit": 65.10},
            {"codigo": 4701, "nome": "Short Doll Brenda", "quantidade": 1, "preco_unit": 71.00},
        ],
        # Vanessa
        "Vanessa": [
            {"codigo": 4562, "nome": "Short Doll Analis", "quantidade": 1, "preco_unit": 65.10},
            {"codigo": 4699, "nome": "Tanga Bolívia", "quantidade": 1, "preco_unit": 18.90},
            {"codigo": 4699, "nome": "Tanga Bolívia", "quantidade": 1, "preco_unit": 18.90},
            {"codigo": 4699, "nome": "Tanga Bolívia", "quantidade": 1, "preco_unit": 18.90},
            {"codigo": 4539, "nome": "Tanga Kamili", "quantidade": 1, "preco_unit": 19.35},
        ],
        # Pamela (com 4681 a 11,20 conforme você informou)
        "Pamela": [
            {"codigo": 4681, "nome": "Short Doll Inf. Alcinha", "quantidade": 1, "preco_unit": 11.20},
            {"codigo": 4459, "nome": "Meia BB Pelucia Masc", "quantidade": 1, "preco_unit": 19.75},
            {"codigo": 4497, "nome": "Cueca Boxe Boss", "quantidade": 1, "preco_unit": 27.15},
            {"codigo": 4673, "nome": "Short Doll Alice Plus", "quantidade": 1, "preco_unit": 83.80},
        ],
        # Elan
        "Elan": [
            {"codigo": 4470, "nome": "Cueca Boxe Adidas", "quantidade": 1, "preco_unit": 29.60},
            {"codigo": 4470, "nome": "Cueca Boxe Adidas", "quantidade": 1, "preco_unit": 29.60},
        ],
        # Claudinha (com quantidades)
        "Claudinha": [
            {"codigo": 2750, "nome": "Calça Cós Laser", "quantidade": 1, "preco_unit": 24.90},
            {"codigo": 4239, "nome": "Tanga Fio Duplo Anelise", "quantidade": 2, "preco_unit": 16.80},
            {"codigo": 4142, "nome": "Tanga Valdira", "quantidade": 2, "preco_unit": 16.50},
            {"codigo": 4343, "nome": "Meia Sap Pompom Kit C/3", "quantidade": 1, "preco_unit": 28.20},
            {"codigo": 4122, "nome": "Calça Fem Mônica", "quantidade": 1, "preco_unit": 103.50},
        ],
    }

    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.inited = True

def total_cliente(nome: str) -> float:
    vendas = st.session_state.clientes.get(nome, [])
    return sum(v["quantidade"] * v["preco_unit"] for v in vendas)

def total_geral() -> float:
    return sum(total_cliente(c) for c in st.session_state.clientes.keys())

def sugestoes_clientes(query: str):
    if not query or len(query.strip()) < 2:
        return []
    q = query.strip().lower()
    return sorted([c for c in st.session_state.clientes.keys() if q in c.lower()])

def sugestoes_produtos(query: str):
    if not query or len(query.strip()) < 2:
        return []
    q = query.strip().lower()
    # retorna (codigo, nome, preco)
    items = []
    for cod, info in st.session_state.produtos.items():
        texto = f"{cod} - {info['nome']}".lower()
        if q in texto:
            items.append((cod, info["nome"], info["preco"]))
    items.sort(key=lambda x: (x[1].lower(), x[0]))
    return items

# =========================
# Telas
# =========================
def tela_login():
    st.title("🔐 Login")
    col1, col2 = st.columns([1,1])

    with col1:
        st.subheader("Usuário cadastrado")
        user = st.text_input("Usuário").strip().lower()
        senha = st.text_input("Senha", type="password").strip()
        if st.button("Entrar", type="primary", use_container_width=True):
            if user in st.session_state.users and st.session_state.users[user].lower() == senha.lower():
                st.session_state.logado = True
                st.session_state.usuario = user
                log_acesso(f"login::user::{user}")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with col2:
        st.subheader("Entrar como visitante")
        visitante = st.text_input("Seu nome (obrigatório)").strip()
        if st.button("Entrar como visitante", use_container_width=True):
            if visitante:
                st.session_state.logado = True
                st.session_state.usuario = f"visitante-{visitante}"
                log_acesso(f"login::visitante::{visitante}")
                st.rerun()
            else:
                st.warning("Informe um nome para entrar como visitante.")

def tela_home():
    st.title("📦 Sistema de Vendas")
    st.subheader("Resumo Geral de Vendas")

    total = total_geral()
    comissao = total * 0.40

    # Mostra totais por cliente (em ordem alfabética)
    with st.container(border=True):
        for c in sorted(st.session_state.clientes.keys(), key=lambda x: x.lower()):
            st.write(f"- **{c}**: {money(total_cliente(c))}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total geral", money(total))
    with col2:
        st.metric("Comissão (40%)", money(comissao))

def tela_clientes():
    st.header("👥 Clientes")
    aba = st.tabs(["Consultar / Editar", "Cadastrar"])[0]

    with st.expander("Buscar cliente (digite pelo menos 2 letras)", expanded=True):
        busca = st.text_input("Buscar", placeholder="Ex.: ta, va, pa ... (não precisa acento)").strip()
        sugest = sugestoes_clientes(busca)
        cliente_sel = None
        if sugest:
            cliente_sel = st.selectbox("Selecione o cliente", sugest, index=0)

    if cliente_sel:
        vendas = st.session_state.clientes.get(cliente_sel, [])
        st.subheader(f"Cliente: {cliente_sel}")
        st.caption("As vendas só aparecem depois que você seleciona o cliente.")
        if not vendas:
            st.info("Nenhuma venda registrada para este cliente.")
        else:
            # Lista de vendas com ações
            for idx, v in enumerate(vendas):
                cod = v["codigo"]
                nomep = v.get("nome") or st.session_state.produtos.get(cod, {}).get("nome", "Produto")
                preco = v["preco_unit"]
                qtd = v["quantidade"]
                with st.expander(f"{nomep} ({qtd}x) - {money(preco)} cada", expanded=False):
                    c1, c2, c3, c4 = st.columns([2,1,1,1])
                    with c1:
                        novo_nome = st.text_input("Nome do produto (venda)", value=nomep, key=f"vn_{cliente_sel}_{idx}")
                    with c2:
                        nova_qtd = st.number_input("Qtd", min_value=1, value=int(qtd), step=1, key=f"vq_{cliente_sel}_{idx}")
                    with c3:
                        novo_preco = st.number_input("Preço unit.", min_value=0.0, value=float(preco), step=0.10, format="%.2f", key=f"vp_{cliente_sel}_{idx}")
                    with c4:
                        if st.button("Salvar", key=f"vsave_{cliente_sel}_{idx}"):
                            v["nome"] = novo_nome
                            v["quantidade"] = int(nova_qtd)
                            v["preco_unit"] = float(novo_preco)
                            st.success("Venda atualizada!")
                            st.rerun()
                        if st.button("Apagar", key=f"vdel_{cliente_sel}_{idx}"):
                            st.session_state.clientes[cliente_sel].pop(idx)
                            st.warning("Venda removida.")
                            st.rerun()

            st.markdown(f"**Total do cliente:** {money(total_cliente(cliente_sel))}")

        st.divider()
        with st.expander("⋯ Ações do cliente"):
            colA, colB = st.columns(2)
            with colA:
                novo_nome_cli = st.text_input("Renomear cliente", value=cliente_sel, key=f"rn_{cliente_sel}")
                if st.button("Salvar novo nome", key=f"rnsave_{cliente_sel}"):
                    if novo_nome_cli and novo_nome_cli not in st.session_state.clientes:
                        st.session_state.clientes[novo_nome_cli] = st.session_state.clientes.pop(cliente_sel)
                        st.success("Cliente renomeado.")
                        st.rerun()
                    else:
                        st.warning("Informe um nome válido e que não exista.")
            with colB:
                if st.button("Apagar cliente", type="secondary", key=f"rmd_{cliente_sel}"):
                    st.session_state.clientes.pop(cliente_sel, None)
                    st.warning("Cliente apagado.")
                    st.rerun()

    # Aba: Cadastrar
    with st.tabs(["Consultar / Editar", "Cadastrar"])[1]:
        st.subheader("Cadastrar novo cliente")
        nome = st.text_input("Nome do cliente").strip()
        if st.button("Cadastrar cliente", type="primary"):
            if nome and nome not in st.session_state.clientes:
                st.session_state.clientes[nome] = []
                st.success("Cliente cadastrado!")
            else:
                st.warning("Nome inválido ou já existe.")

def tela_registrar_venda():
    st.header("🛒 Registrar venda")

    # Selecionar/filtrar cliente
    with st.expander("Cliente", expanded=True):
        busca = st.text_input("Buscar cliente (2+ letras)").strip()
        sugest = sugestoes_clientes(busca)
        cliente_sel = st.selectbox("Selecione o cliente", sugest, index=0) if sugest else None

        colc1, colc2 = st.columns([2,1])
        with colc1:
            novo_cliente = st.text_input("Ou cadastre um cliente novo (opcional)").strip()
        with colc2:
            if st.button("Cadastrar novo cliente aqui"):
                if novo_cliente and novo_cliente not in st.session_state.clientes:
                    st.session_state.clientes[novo_cliente] = []
                    st.success(f"Cliente '{novo_cliente}' cadastrado!")
                    cliente_sel = novo_cliente
                else:
                    st.warning("Informe um nome válido que não exista.")

    if not cliente_sel:
        st.info("Selecione ou cadastre um cliente para continuar.")
        return

    # Selecionar/filtrar produto
    with st.expander("Produto", expanded=True):
        qprod = st.text_input("Buscar produto por nome/código (2+ letras)").strip()
        sugest_p = sugestoes_produtos(qprod)
        opt_text = [f"{cod} - {nome} ({money(preco)})" for cod, nome, preco in sugest_p] if sugest_p else []
        sel_idx = st.selectbox("Selecione o produto", list(range(len(opt_text))), format_func=lambda i: opt_text[i] if opt_text else "Nenhum", index=0 if opt_text else None) if opt_text else None

        if sel_idx is not None:
            cod, nomep, preco_catalogo = sugest_p[sel_idx]
            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)
            preco_unit = st.number_input("Preço da venda (pode ajustar)", min_value=0.0, value=float(preco_catalogo), step=0.10, format="%.2f")
            if st.button("Adicionar à venda", type="primary"):
                st.session_state.clientes[cliente_sel].append({
                    "codigo": cod,
                    "nome": nomep,
                    "quantidade": int(qtd),
                    "preco_unit": float(preco_unit),
                })
                st.success("Item adicionado!")
                st.rerun()
        else:
            st.info("Digite para ver sugestões de produtos.")

    # Resumo da venda do cliente
    st.subheader(f"Carrinho / Itens do cliente: {cliente_sel}")
    vendas = st.session_state.clientes.get(cliente_sel, [])
    if not vendas:
        st.write("Nenhum item para este cliente.")
    else:
        for idx, v in enumerate(vendas):
            st.write(f"- {v['nome']} ({v['quantidade']}x) — {money(v['preco_unit'])} cada  → **{money(v['quantidade']*v['preco_unit'])}**")
        st.markdown(f"**Total do cliente:** {money(total_cliente(cliente_sel))}")

def tela_produtos():
    st.header("📦 Produtos")
    with st.expander("Adicionar produto", expanded=False):
        ncod = st.text_input("Código (número)").strip()
        nnome = st.text_input("Nome do produto").strip()
        npreco = st.number_input("Preço", min_value=0.0, value=0.0, step=0.10, format="%.2f")
        if st.button("Adicionar produto", type="primary"):
            if not ncod.isdigit():
                st.warning("Código deve ser numérico.")
            else:
                icod = int(ncod)
                if icod in st.session_state.produtos:
                    st.warning("Já existe produto com este código.")
                elif not nnome:
                    st.warning("Informe o nome do produto.")
                else:
                    st.session_state.produtos[icod] = {"nome": nnome, "preco": float(npreco)}
                    st.success("Produto cadastrado!")

    # Buscar produto
    q = st.text_input("Buscar produto (nome/código, 2+ letras)").strip()
    lista = list(st.session_state.produtos.items())
    if len(q) >= 2:
        ql = q.lower()
        lista = [(c, p) for c, p in lista if ql in f"{c} - {p['nome']}".lower()]
    lista.sort(key=lambda x: (x[1]["nome"].lower(), x[0]))

    # Listagem com edição
    for cod, info in lista:
        with st.expander(f"{cod} - {info['nome']} ({money(info['preco'])})", expanded=False):
            nnome = st.text_input("Nome", value=info["nome"], key=f"p_nome_{cod}")
            npreco = st.number_input("Preço", value=float(info["preco"]), step=0.10, format="%.2f", key=f"p_preco_{cod}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Salvar alterações", key=f"p_save_{cod}"):
                    st.session_state.produtos[cod]["nome"] = nnome
                    st.session_state.produtos[cod]["preco"] = float(npreco)
                    st.success("Produto atualizado.")
                    st.rerun()
            with c2:
                if st.button("Apagar produto", key=f"p_del_{cod}"):
                    st.session_state.produtos.pop(cod, None)
                    st.warning("Produto apagado.")
                    st.rerun()

def tela_relatorios():
    st.header("📊 Relatórios")
    escolha = st.radio("Escolha:", ["Relatório geral", "Relatório de um cliente", "Comissão total"], horizontal=True)

    if escolha == "Relatório geral":
        linhas = ["📋 *Relatório Geral de Vendas*", ""]
        tot_geral = 0.0
        for c in sorted(st.session_state.clientes.keys(), key=lambda x: x.lower()):
            t = total_cliente(c)
            tot_geral += t
            linhas.append(f"- {c}: {money(t)}")
        linhas.append("")
        linhas.append(f"💰 *Total geral*: {money(tot_geral)}")
        linhas.append(f"💸 *Comissão (40%)*: {money(tot_geral*0.40)}")

        texto = "\n".join(linhas)
        st.text_area("Copie e cole no WhatsApp:", value=texto, height=220)

    elif escolha == "Relatório de um cliente":
        busca = st.text_input("Buscar cliente (2+ letras)").strip()
        sugest = sugestoes_clientes(busca)
        cliente_sel = st.selectbox("Selecione o cliente", sugest) if sugest else None
        if cliente_sel:
            vendas = st.session_state.clientes.get(cliente_sel, [])
            linhas = [f"📋 *Relatório de {cliente_sel}*", ""]
            total_c = 0.0
            # Agrupar por produto (somar quantidades iguais)
            # Como os registros podem se repetir, vamos consolidar por (codigo, nome, preco_unit)
            from collections import defaultdict
            agg = defaultdict(lambda: {"qtd":0, "preco":0.0, "nome":""})
            for v in vendas:
                key = (v["codigo"], v.get("nome",""), float(v["preco_unit"]))
                agg[key]["qtd"] += int(v["quantidade"])
                agg[key]["preco"] = float(v["preco_unit"])
                agg[key]["nome"] = v.get("nome","")

            for (cod, nomep, preco), val in sorted(agg.items(), key=lambda k: k[0][1].lower()):
                subtotal = val["qtd"] * val["preco"]
                total_c += subtotal
                linhas.append(f"- {nomep} ({val['qtd']}x): {money(subtotal)}")

            linhas.append("")
            linhas.append(f"💰 Total do cliente: {money(total_c)}")
            st.text_area("Copie e cole no WhatsApp:", value="\n".join(linhas), height=220)
        else:
            st.info("Digite para ver sugestões e selecione o cliente.")

    else:  # Comissão total
        t = total_geral()
        st.metric("💸 Comissão total (40%)", money(t*0.40))

# =========================
# Layout principal
# =========================
def main():
    init_state()
    if not st.session_state.logado:
        tela_login()
        return

    # Menu lateral
    with st.sidebar:
        st.markdown(f"**Usuário:** {st.session_state.usuario}")
        pagina = st.radio(
            "Menu",
            ["Início", "Clientes", "Registrar venda", "Produtos", "Relatórios", "Sair"],
            index=0
        )

    if pagina == "Início":
        tela_home()
    elif pagina == "Clientes":
        tela_clientes()
    elif pagina == "Registrar venda":
        tela_registrar_venda()
    elif pagina == "Produtos":
        tela_produtos()
    elif pagina == "Relatórios":
        tela_relatorios()
    else:
        # Sair
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    main()
