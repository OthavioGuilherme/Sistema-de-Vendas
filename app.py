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

# =============== Controle de acesso ===============
def is_visitante():
    return bool(st.session_state.get("usuario")) and str(st.session_state.get("usuario")).startswith("visitante-")

# =============== Dados iniciais: Produtos ===============
PRODUTOS_INICIAIS = {
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

# =============== Vendas iniciais (preço da VENDA) ===============
VENDAS_INICIAIS = {
    "Tabata": [
        {"codigo": 4685, "quantidade": 1, "preco": 52.95},
        {"codigo": 4184, "quantidade": 1, "preco": 25.20},
        {"codigo": 4351, "quantidade": 1, "preco": 54.20},
        {"codigo": 3625, "quantidade": 1, "preco": 28.50},
        {"codigo": 4597, "quantidade": 1, "preco": 29.00},
        {"codigo": 3900, "quantidade": 1, "preco": 15.90},
        {"codigo": 3900, "quantidade": 1, "preco": 15.90},
        {"codigo": 3900, "quantidade": 1, "preco": 15.90},
        {"codigo": 4597, "quantidade": 1, "preco": 29.00},
        {"codigo": 4680, "quantidade": 1, "preco": 51.25},
        {"codigo": 4726, "quantidade": 1, "preco": 22.70},
        {"codigo": 4539, "quantidade": 1, "preco": 19.35},
        {"codigo": 4640, "quantidade": 1, "preco": 18.50},
        {"codigo": 3875, "quantidade": 1, "preco": 17.50},
        {"codigo": 4142, "quantidade": 1, "preco": 16.50},
        {"codigo": 4705, "quantidade": 1, "preco": 22.70},
    ],
    "Valquiria": [
        {"codigo": 4702, "quantidade": 1, "preco": 58.40},
        {"codigo": 4457, "quantidade": 1, "preco": 83.80},
        {"codigo": 4493, "quantidade": 1, "preco": 25.50},
        {"codigo": 4310, "quantidade": 1, "preco": 17.30},
        {"codigo": 4705, "quantidade": 1, "preco": 27.70},
        {"codigo": 4705, "quantidade": 1, "preco": 27.70},
        {"codigo": 3698, "quantidade": 1, "preco": 14.10},
        {"codigo": 3698, "quantidade": 1, "preco": 14.10},
        {"codigo": 3698, "quantidade": 1, "preco": 14.10},
        {"codigo": 4494, "quantidade": 1, "preco": 65.10},
        {"codigo": 4701, "quantidade": 1, "preco": 71.00},
    ],
    "Vanessa": [
        {"codigo": 4562, "quantidade": 1, "preco": 65.10},
        {"codigo": 4699, "quantidade": 1, "preco": 18.90},
        {"codigo": 4699, "quantidade": 1, "preco": 18.90},
        {"codigo": 4699, "quantidade": 1, "preco": 18.90},
        {"codigo": 4539, "quantidade": 1, "preco": 19.35},
    ],
    "Pamela": [
        {"codigo": 4681, "quantidade": 1, "preco": 11.20},  # override do preço
        {"codigo": 4459, "quantidade": 1, "preco": 19.75},
        {"codigo": 4497, "quantidade": 1, "preco": 27.15},
        {"codigo": 4673, "quantidade": 1, "preco": 83.80},
    ],
    "Elan": [
        {"codigo": 4470, "quantidade": 1, "preco": 29.60},
        {"codigo": 4470, "quantidade": 1, "preco": 29.60},
    ],
    "Claudinha": [
        {"codigo": 2750, "quantidade": 1, "preco": 24.90},
        {"codigo": 4239, "quantidade": 2, "preco": 16.80},
        {"codigo": 4142, "quantidade": 2, "preco": 16.50},
        {"codigo": 4343, "quantidade": 1, "preco": 28.20},
        {"codigo": 4122, "quantidade": 1, "preco": 103.50},
    ],
}

# =============== Persistência (JSON) ===============
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
            # produtos (chaves podem vir como string)
            prods = {int(k): v for k, v in data.get("produtos", {}).items()}
            clis  = {k: v for k, v in data.get("clientes", {}).items()}
            return prods, clis
        except Exception:
            pass
    # caso não exista/erro, retorna iniciais
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
            cod = v["codigo"]; preco = v["preco"]
            chave = (cod, preco)
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

# =============== Novas funcionalidades: leitura PDF / inserção manual / zerar vendas ===============
def substituir_estoque_pdf(uploaded_file):
    """
    Lê o PDF enviado e extrai linhas no formato:
      <quantidade> <codigo> <nome do produto ...> <valor unitário>
    Substitui o mapa st.session_state.produtos pelos produtos encontrados (codigo -> {nome, preco}).
    """
    # ler bytes do upload (UploadedFile do Streamlit)
    try:
        data = uploaded_file.read()
        if not data:
            raise ValueError("Arquivo vazio")
        stream = io.BytesIO(data)
    except Exception as e:
        raise ValueError(f"Falha ao ler arquivo: {e}")

    novos_produtos = {}
    # regex para capturar: quantidade, código (com zeros), nome (texto), preço (com , decimal e possivelmente . como separador de milhar)
    linha_regex = re.compile(r'^\s*(\d+)\s+0*(\d{1,6})\s+(.+?)\s+((?:\d{1,3}(?:[.\,]\d{3})*|\d+)[\.,]\d{2})\s*$')

    try:
        with pdfplumber.open(stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                for raw_linha in text.splitlines():
                    linha = raw_linha.strip()
                    if not linha:
                        continue
                    m = linha_regex.match(linha)
                    if m:
                        qtd_s, codigo_s, nome_raw, preco_s = m.groups()
                        try:
                            codigo = int(codigo_s)
                        except:
                            continue
                        # normaliza preço: remove pontos de milhar e troca vírgula por ponto
                        preco_norm = preco_s.replace('.', '').replace(',', '.')
                        try:
                            preco = float(preco_norm)
                        except:
                            preco = 0.0
                        nome = nome_raw.strip().title()  # converte para Title Case pra ficar parecido com seu padrão
                        # guarda produto (mantemos apenas nome e preco no dicionário de produtos)
                        novos_produtos[codigo] = {"nome": nome, "preco": preco}
    except Exception as e:
        raise ValueError(f"Falha ao processar PDF: {e}")

    if not novos_produtos:
        raise ValueError("Nenhum produto válido encontrado no PDF. Verifique o arquivo.")

    # Substitui totalmente o estoque atual (produtos)
    st.session_state.produtos = novos_produtos
    save_db()

def adicionar_produto_manual(codigo, nome, quantidade, preco_unitario):
    """
    Adiciona/atualiza um produto no mapa de produtos (mantendo o padrão {cod: {'nome','preco'}}).
    Não gravamos quantidade no produto por compatibilidade com o formato atual do sistema.
    A quantidade e o total são apenas mostrados na UI conforme solicitado.
    """
    try:
        cod = int(codigo)
    except:
        raise ValueError("Código inválido")
    st.session_state.produtos[cod] = {"nome": nome.strip(), "preco": float(preco_unitario)}
    save_db()

def zerar_todas_vendas():
    """
    Substitui a lista de vendas de cada cliente por lista vazia.
    """
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

    st.markdown("### Carrinho")
    if not st.session_state.carrinho:
        st.info("Carrinho vazio.")
    else:
        total_cart = 0.0
        for i, item in enumerate(st.session_state.carrinho):
            st.write(f"**{i+1}.** {item['nome']} ({item['quantidade']}x) - R$ {item['preco']:.2f} cada")
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
                if not visitante:
                    if st.button("Salvar novo nome", key=f"btn_rn_{cliente}"):
                        renomear_cliente(cliente, novo_nome)
                else:
                    st.caption("🔒 Disponível apenas para usuários logados.")
            with col_b:
                if not visitante:
                    if st.button("Apagar cliente", key=f"delcli_{cliente}"):
                        apagar_cliente(cliente)
                else:
                    st.button("Apagar cliente", key=f"delcli_{cliente}", disabled=True)

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
                    col1, col2 = st.columns(2)
                    with col1:
                        if not visitante:
                            if st.button("Salvar edição", key=f"save_{cliente}_{idx}"):
                                editar_venda(cliente, idx, nova_qtd, novo_preco)
                        else:
                            st.button("Salvar edição", key=f"save_{cliente}_{idx}", disabled=True)
                    with col2:
                        if not visitante:
                            if st.button("Apagar venda", key=f"del_{cliente}_{idx}"):
                                remover_venda(cliente, idx)
                        else:
                            st.button("Apagar venda", key=f"del_{cliente}_{idx}", disabled=True)

            st.markdown(f"**Total do cliente:** R$ {total:.2f}")

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
                    if visitante:
                        st.button("Salvar", key=f"s_{cod}", disabled=True)
                    else:
                        if st.button("Salvar", key=f"s_{cod}"):
                            st.session_state.produtos[cod]["nome"] = novo_nome
                            st.session_state.produtos[cod]["preco"] = float(novo_preco)
                            save_db()
                            st.success("Produto atualizado.")
                with c2:
                    if visitante:
                        st.button("Apagar", key=f"d_{cod}", disabled=True)
                    else:
                        if st.button("Apagar", key=f"d_{cod}"):
                            st.session_state.produtos.pop(cod, None)
                            save_db()
                            st.success("Produto apagado.")
                            st.rerun()

def tela_relatorios():
    st.header("📈 Relatórios")
    escolha = st.radio("Escolha um relatório", ["Geral", "Individual", "Comissão total"], horizontal=True)

    if escolha == "Geral":
        texto = wh_ts_geral()
        st.subheader("Prévia")
        st.code(texto)
        st.download_button("Baixar .txt", data=texto, file_name="relatorio_geral.txt")

    elif escolha == "Individual":
        filtro = st.text_input("Buscar cliente (2+ letras)").strip()
        matches = filtrar_clientes(filtro)
        cliente = st.selectbox("Cliente", matches, index=None) if matches else None
        if cliente:
            texto = wh_ts_individual(cliente)
            st.subheader("Prévia")
            st.code(texto)
            st.download_button("Baixar .txt", data=texto, file_name=f"relatorio_{cliente}.txt")
        else:
            st.info("Digite ao menos 2 letras para buscar.")

    else:
        texto = wh_ts_comissao()
        st.subheader("Prévia")
        st.code(texto)
        st.download_button("Baixar .txt", data=texto, file_name="relatorio_comissao.txt")

def tela_acessos():
    st.header("📜 Histórico de acessos")
    if not os.path.exists(LOG_FILE):
        st.info("Nenhum acesso registrado ainda.")
        return
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        linhas = f.readlines()
    st.caption("Mostrando os acessos mais recentes (últimos 200):")
    for linha in reversed(linhas[-200:]):
        st.text(linha.strip())

# =============== Layout principal ===============
def bloco_backup_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧰 Backup")
    db_json = json.dumps({
        "produtos": st.session_state.produtos,
        "clientes": st.session_state.clientes,
    }, ensure_ascii=False, indent=2)
    st.sidebar.download_button("⬇️ Exportar backup (.json)", data=db_json.encode("utf-8"),
                               file_name="backup_sistema_vendas.json")
    # Restaurar backup: apenas para usuários logados
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
    else:
        st.sidebar.caption("🔒 Restauração disponível apenas para usuários logados.")

    # === NOVO: Importar estoque via PDF ===
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Importar Estoque via PDF")
    if is_visitante():
        st.sidebar.caption("🔒 Apenas usuários logados podem importar PDF.")
    else:
        pdf_file = st.sidebar.file_uploader("Carregar PDF da Nota", type=["pdf"], key="pdf_estoque")
        if pdf_file is not None:
            st.sidebar.caption("Após enviar o PDF, clique em 'Substituir estoque pelo PDF' para confirmar.")
            if st.sidebar.button("Substituir estoque pelo PDF"):
                try:
                    substituir_estoque_pdf(pdf_file)
                    st.sidebar.success("Estoque substituído com sucesso.")
                    registrar_acesso(f"substituir_estoque_pdf: {st.session_state.usuario}")
                    st.experimental_rerun()
                except Exception as e:
                    st.sidebar.error(f"Falha ao substituir o estoque: {e}")

    # === NOVO: Inserir produto manualmente (1 por vez) ===
    st.sidebar.markdown("---")
    st.sidebar.subheader("✍️ Inserir Produto Manualmente")
    if is_visitante():
        st.sidebar.caption("🔒 Apenas usuários logados podem inserir produtos.")
    else:
        # inputs separados com keys para evitar conflito com outros widgets
        cod_manual = st.sidebar.number_input("Código", min_value=1, step=1, key="cod_manual")
        nome_manual = st.sidebar.text_input("Nome do produto", key="nome_manual")
        qtd_manual = st.sidebar.number_input("Quantidade", min_value=1, step=1, value=1, key="qtd_manual")
        preco_manual = st.sidebar.number_input("Preço Unitário", min_value=0.0, step=0.10, format="%.2f", key="preco_manual")
        total_manual = qtd_manual * preco_manual
        st.sidebar.markdown(f"**Valor Total:** R$ {total_manual:.2f}")
        if st.sidebar.button("Adicionar Produto", key="btn_add_manual"):
            if not str(nome_manual).strip():
                st.sidebar.warning("Informe o nome do produto.")
            else:
                try:
                    adicionar_produto_manual(cod_manual, nome_manual, qtd_manual, preco_manual)
                    st.sidebar.success("Produto adicionado com sucesso.")
                    registrar_acesso(f"adicionar_produto_manual: {st.session_state.usuario} - cod:{cod_manual}")
                    st.experimental_rerun()
                except Exception as e:
                    st.sidebar.error(f"Erro ao adicionar produto: {e}")

    # === Zerar vendas (mantém clientes) ===
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗑️ Zerar Vendas")
    if is_visitante():
        st.sidebar.caption("🔒 Apenas usuários logados podem zerar vendas.")
    else:
        confirmar_zerar = st.sidebar.checkbox("Confirmo que quero zerar todas as vendas", key="conf_zerar")
        if st.sidebar.button("Zerar vendas"):
            if not confirmar_zerar:
                st.sidebar.warning("Marque a confirmação antes de zerar vendas.")
            else:
                try:
                    zerar_todas_vendas()
                    st.sidebar.success("Todas as vendas foram zeradas.")
                    registrar_acesso(f"zerar_vendas: {st.session_state.usuario}")
                    st.experimental_rerun()
                except Exception as e:
                    st.sidebar.error(f"Falha ao zerar vendas: {e}")

def barra_lateral():
    st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario}")
    opcoes = ["Resumo", "Registrar venda", "Clientes", "Produtos", "Relatórios", "Sair"]
    if not is_visitante():
        opcoes.insert(-1, "Acessos")  # adiciona antes do "Sair"
    # Ajusta índice caso a opção anterior não exista (ex.: visitante não tem "Acessos")
    idx_atual = opcoes.index(st.session_state.menu) if st.session_state.menu in opcoes else 0
    menu = st.sidebar.radio("Menu", opcoes, index=idx_atual)
    st.session_state.menu = menu
    bloco_backup_sidebar()

def roteador():
    if st.session_state.menu == "Resumo":
        tela_resumo()
    elif st.session_state.menu == "Registrar venda":
        tela_registrar_venda()
    elif st.session_state.menu == "Clientes":
        tela_clientes()
    elif st.session_state.menu == "Produtos":
        tela_produtos()
    elif st.session_state.menu == "Relatórios":
        tela_relatorios()
    elif st.session_state.menu == "Acessos":
        # segurança extra: só mostra se não for visitante
        if not is_visitante():
            tela_acessos()
        else:
            st.error("Acesso negado.")
    elif st.session_state.menu == "Sair":
        st.session_state.clear()
        st.rerun()

# =============== Main ===============
def main():
    if not st.session_state.logado:
        tela_login()
        return
    barra_lateral()
    roteador()

if __name__ == "__main__":
    main()