# app.py
import streamlit as st
from datetime import datetime

# ===========================
# Configuração de login
# ===========================
USERS = {
    "Othavio": "122008",
    "Isabela": "122008",
}
ACESSOS_FILE = "acessos.log"

def registrar_acesso(nome, tipo):
    try:
        with open(ACESSOS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} — {tipo}: {nome}\n")
    except Exception:
        pass  # em ambiente restrito pode não permitir escrita

def do_login():
    st.title("🔒 Login no Sistema de Vendas")
    aba = st.radio("Escolha como entrar:", ["Usuário autorizado", "Entrar como visitante"])

    if aba == "Usuário autorizado":
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            ok = False
            for user, pwd in USERS.items():
                if u.strip().lower() == user.lower() and p.strip().lower() == pwd.lower():
                    ok = True
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    registrar_acesso(user, "USUÁRIO")
                    break
            if ok:
                st.success(f"Bem-vindo(a), {st.session_state.user}!")
                st.rerun()
            else:
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
            st.success(f"Bem-vindo(a), {nome_visitante.strip()}!")
            st.rerun()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ===========================
# Produtos (catálogo)
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
# Banco de dados (memória)
# ===========================
if "clientes" not in st.session_state:
    st.session_state.clientes = {}

def seed_inicial():
    """Carrega clientes e vendas que você me passou (somente 1x)."""
    if st.session_state.clientes:
        return
    add = lambda nome: st.session_state.clientes.setdefault(nome, {"vendas": []})

    def venda(nome, codigo, qtd, valor_unit):
        prod = produtos.get(codigo, {"nome": f"Código {codigo}"})
        st.session_state.clientes[nome]["vendas"].append({
            "codigo": codigo,
            "nome": prod["nome"],
            "quantidade": int(qtd),
            "valor": float(valor_unit),
        })

    # Clientes
    add("Tabata")
    add("Valquiria")
    add("Vanessa")
    add("Pamela")
    add("Elan")
    add("Claudinha")

    # TABATA (usando os valores informados por você; 4705 = 22,70)
    venda("Tabata", 4685, 1, 52.95)
    venda("Tabata", 4184, 1, 25.20)
    venda("Tabata", 4351, 1, 54.20)
    venda("Tabata", 3625, 1, 28.50)
    venda("Tabata", 4597, 2, 29.00)
    venda("Tabata", 3900, 3, 15.90)
    venda("Tabata", 4680, 1, 51.25)
    venda("Tabata", 4726, 1, 22.70)
    venda("Tabata", 4539, 1, 19.35)
    venda("Tabata", 4640, 1, 18.50)
    venda("Tabata", 3875, 1, 17.50)
    venda("Tabata", 4142, 1, 16.50)
    venda("Tabata", 4705, 1, 22.70)

    # VALQUIRIA (tot = 418,80)
    venda("Valquiria", 4702, 1, 58.40)
    venda("Valquiria", 4457, 1, 83.80)
    venda("Valquiria", 4493, 1, 25.50)
    venda("Valquiria", 4310, 1, 17.30)
    venda("Valquiria", 4705, 2, 27.70)
    venda("Valquiria", 3698, 3, 14.10)
    venda("Valquiria", 4494, 1, 65.10)
    venda("Valquiria", 4701, 1, 71.00)

    # VANESSA (tot = 141,15)
    venda("Vanessa", 4562, 1, 65.10)
    venda("Vanessa", 4699, 3, 18.90)
    venda("Vanessa", 4539, 1, 19.35)

    # PAMELA (usa 4681 = 11,20 como informado; tot = 141,90)
    venda("Pamela", 4681, 1, 11.20)
    venda("Pamela", 4459, 1, 19.75)
    venda("Pamela", 4497, 1, 27.15)
    venda("Pamela", 4673, 1, 83.80)

    # ELAN (tot = 59,20)
    venda("Elan", 4470, 2, 29.60)

    # CLAUDINHA (tot = 223,20)
    venda("Claudinha", 2750, 1, 24.90)
    venda("Claudinha", 4239, 2, 16.80)
    venda("Claudinha", 4142, 2, 16.50)
    venda("Claudinha", 4343, 1, 28.20)
    venda("Claudinha", 4122, 1, 103.50)

seed_inicial()

# ===========================
# Utilidades
# ===========================
def total_cliente(nome):
    return sum(v["quantidade"] * v["valor"] for v in st.session_state.clientes[nome]["vendas"])

def total_geral():
    return sum(total_cliente(n) for n in st.session_state.clientes)

def fmt_moeda(v):
    return f"R$ {v:.2f}"

def buscar_clientes(prefix):
    if len(prefix) < 2:
        return []
    prefix = prefix.lower().strip()
    return sorted([c for c in st.session_state.clientes if prefix in c.lower()], key=lambda x: x.lower())

def buscar_produtos(q):
    if len(q) < 2:
        return []
    ql = q.lower().strip()
    out = []
    for cod, p in produtos.items():
        if ql in p["nome"].lower() or ql in str(cod):
            out.append((cod, p["nome"], p["preco"]))
    out.sort(key=lambda x: x[1].lower())
    return out

# ===========================
# Páginas / Ações
# ===========================
def pagina_resumo():
    st.header("📦 Sistema de Vendas")
    tg = total_geral()
    st.subheader(f"💰 Total geral: {fmt_moeda(tg)}")
    st.subheader(f"💸 Comissão (40%): {fmt_moeda(tg * 0.40)}")

def pagina_cadastrar_cliente():
    st.header("👤 Cadastrar cliente")
    nome = st.text_input("Nome do cliente")
    if st.button("Cadastrar", use_container_width=True):
        if not nome.strip():
            st.warning("Digite um nome.")
            return
        if nome.strip() in st.session_state.clientes:
            st.error("Já existe um cliente com esse nome.")
            return
        st.session_state.clientes[nome.strip()] = {"vendas": []}
        st.success(f"Cliente {nome.strip()} cadastrado!")

def pagina_registrar_venda():
    st.header("🛒 Registrar venda")

    # Buscar cliente
    busca_cli = st.text_input("Busque o cliente (digite ao menos 2 letras)")
    sugestoes = buscar_clientes(busca_cli)
    cliente = st.selectbox("Selecione o cliente", [""] + sugestoes, index=0)
    if not cliente:
        st.info("Digite ao menos 2 letras para buscar o cliente.")
        return

    # Buscar produto
    q = st.text_input("Busque o produto por nome ou código (min. 2 letras/números)")
    matches = buscar_produtos(q)
    if matches:
        label = [f"{cod} — {nome} — {fmt_moeda(preco)}" for cod, nome, preco in matches]
        escolha = st.selectbox("Escolha o produto", label)
        idx = label.index(escolha)
        cod, nome_prod, preco_cat = matches[idx]
    else:
        st.info("Digite ao menos 2 caracteres para ver sugestões de produtos.")
        return

    qtd = st.number_input("Quantidade", min_value=1, step=1, value=1)
    alterar_preco = st.checkbox("Alterar preço desta venda?")
    if alterar_preco:
        preco_uso = st.number_input("Preço unitário (R$)", min_value=0.0, step=0.10, value=float(preco_cat))
    else:
        preco_uso = float(preco_cat)

    if st.button("Adicionar à venda", use_container_width=True):
        st.session_state.clientes[cliente]["vendas"].append({
            "codigo": int(cod),
            "nome": nome_prod,
            "quantidade": int(qtd),
            "valor": float(preco_uso),
        })
        st.success(f"Adicionado: {qtd}x {nome_prod} para {cliente} ({fmt_moeda(preco_uso)} cada).")

def pagina_consultar_cliente():
    st.header("🔎 Consultar cliente")
    busca_cli = st.text_input("Busque o cliente (digite ao menos 2 letras)")
    sugestoes = buscar_clientes(busca_cli)
    cliente = st.selectbox("Selecione o cliente", [""] + sugestoes, index=0)
    if not cliente:
        st.info("Digite ao menos 2 letras e selecione um cliente.")
        return

    # Cabeçalho com ações do cliente
    cols = st.columns([1, 0.15])
    with cols[0]:
        st.subheader(f"Vendas de {cliente}")
    with cols[1]:
        with st.popover("⋯", use_container_width=True):
            novo_nome = st.text_input("Renomear cliente", value=cliente, key=f"ren_{cliente}")
            if st.button("Salvar nome", key=f"save_ren_{cliente}", use_container_width=True):
                if not novo_nome.strip():
                    st.warning("Nome não pode ser vazio.")
                elif novo_nome.strip() in st.session_state.clientes and novo_nome.strip() != cliente:
                    st.error("Já existe um cliente com esse nome.")
                else:
                    st.session_state.clientes[novo_nome.strip()] = st.session_state.clientes.pop(cliente)
                    st.success("Cliente renomeado!")
                    st.rerun()
            st.divider()
            if st.button("Apagar cliente", type="primary", key=f"del_{cliente}", use_container_width=True):
                st.session_state.clientes.pop(cliente, None)
                st.success("Cliente apagado.")
                st.rerun()

    # Lista de vendas com menu ⋯
    vendas = st.session_state.clientes[cliente]["vendas"]
    if not vendas:
        st.info("Nenhuma venda registrada.")
        return

    total = 0.0
    for i, v in enumerate(vendas):
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.write(f"**{i+1}.** {v['nome']} — {v['quantidade']}x — {fmt_moeda(v['valor'])} cada")
        with col2:
            with st.popover("⋯", key=f"pop_{cliente}_{i}", use_container_width=True):
                qtd = st.number_input("Quantidade", min_value=1, value=int(v["quantidade"]), step=1, key=f"q_{cliente}_{i}")
                preco = st.number_input("Preço unit.", min_value=0.0, value=float(v["valor"]), step=0.10, key=f"p_{cliente}_{i}")
                if st.button("Salvar", key=f"save_{cliente}_{i}", use_container_width=True):
                    v["quantidade"] = int(qtd)
                    v["valor"] = float(preco)
                    st.success("Venda atualizada!")
                    st.rerun()
                st.divider()
                if st.button("Apagar item", key=f"delitem_{cliente}_{i}", use_container_width=True):
                    vendas.pop(i)
                    st.success("Item removido.")
                    st.rerun()
        total += v["quantidade"] * v["valor"]

    st.markdown(f"**Total do cliente: {fmt_moeda(total)}**")

def pagina_relatorios():
    st.header("📑 Relatórios")
    escolha = st.radio("Escolha o relatório:", ["Relatório geral", "Relatório de um cliente", "Comissão total"])

    if escolha == "Relatório geral":
        tg = total_geral()
        linhas = ["📋 *Relatório Geral de Vendas*", ""]
        for nome in sorted(st.session_state.clientes.keys(), key=lambda x: x.lower()):
            linhas.append(f"- {nome}: {fmt_moeda(total_cliente(nome))}")
        linhas.append("")
        linhas.append(f"💰 *Total geral*: {fmt_moeda(tg)}")
        linhas.append(f"💸 *Comissão (40%)*: {fmt_moeda(tg*0.40)}")
        texto = "\n".join(linhas)
        st.text_area("Copie e cole no WhatsApp", value=texto, height=260)

    elif escolha == "Relatório de um cliente":
        busca_cli = st.text_input("Busque o cliente (min. 2 letras)")
        sugestoes = buscar_clientes(busca_cli)
        cliente = st.selectbox("Selecione o cliente", [""] + sugestoes)
        if cliente:
            vendas = st.session_state.clientes[cliente]["vendas"]
            tot = total_cliente(cliente)
            linhas = [f"📋 *Relatório de {cliente}*", ""]
            for v in vendas:
                linhas.append(f"- {v['nome']} ({v['quantidade']}x): {fmt_moeda(v['quantidade']*v['valor'])}")
            linhas.append("")
            linhas.append(f"💰 Total do cliente: {fmt_moeda(tot)}")
            st.text_area("Copie e cole no WhatsApp", value="\n".join(linhas), height=260)
        else:
            st.info("Selecione um cliente para gerar o relatório.")

    else:  # Comissão total
        tg = total_geral()
        st.subheader(f"💸 Comissão total (40%): {fmt_moeda(tg*0.40)}")

def pagina_produtos():
    st.header("🧰 Produtos")
    # Buscar
    q = st.text_input("Buscar produto por nome ou código (min. 2 caracteres)")
    results = buscar_produtos(q) if len(q) >= 2 else []
    if results:
        for cod, nome, preco in results:
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                st.write(f"**{cod}** — {nome} — {fmt_moeda(preco)}")
            with c2:
                with st.popover("⋯", key=f"pp_{cod}", use_container_width=True):
                    novo_nome = st.text_input("Nome", value=nome, key=f"pn_{cod}")
                    novo_preco = st.number_input("Preço (R$)", min_value=0.0, value=float(preco), step=0.10, key=f"ppp_{cod}")
                    if st.button("Salvar", key=f"ps_{cod}", use_container_width=True):
                        produtos[cod]["nome"] = novo_nome.strip() or nome
                        produtos[cod]["preco"] = float(novo_preco)
                        st.success("Produto atualizado!")
                        st.rerun()
                    st.divider()
                    if st.button("Apagar produto", key=f"pd_{cod}", use_container_width=True):
                        produtos.pop(cod, None)
                        st.success("Produto removido.")
                        st.rerun()
    else:
        st.info("Digite ao menos 2 caracteres para buscar.")

    st.markdown("---")
    st.subheader("Adicionar novo produto")
    nc = st.text_input("Código (numérico)")
    nn = st.text_input("Nome")
    np = st.number_input("Preço (R$)", min_value=0.0, step=0.10)
    if st.button("Adicionar produto", use_container_width=True):
        if not nc.isdigit():
            st.warning("Código deve ser numérico.")
            return
        cod = int(nc)
        if cod in produtos:
            st.error("Já existe produto com esse código.")
            return
        if not nn.strip():
            st.warning("Digite um nome para o produto.")
            return
        produtos[cod] = {"nome": nn.strip(), "preco": float(np)}
        st.success("Produto adicionado!")
        st.rerun()

# ===========================
# Fluxo principal
# ===========================
if not st.session_state.logged_in:
    do_login()
    st.stop()

st.sidebar.caption(f"👤 {st.session_state.user}")
menu = st.sidebar.radio(
    "Menu",
    ["Resumo", "Cadastrar cliente", "Registrar venda", "Consultar cliente", "Relatórios", "Produtos"],
    index=0
)

if menu == "Resumo":
    pagina_resumo()
elif menu == "Cadastrar cliente":
    pagina_cadastrar_cliente()
elif menu == "Registrar venda":
    pagina_registrar_venda()
elif menu == "Consultar cliente":
    pagina_consultar_cliente()
elif menu == "Relatórios":
    pagina_relatorios()
elif menu == "Produtos":
    pagina_produtos()
