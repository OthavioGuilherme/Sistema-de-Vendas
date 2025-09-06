# app.py
import streamlit as st
import json, os
from typing import Dict, List, Any
from collections import defaultdict

# =========================
# Configurações visuais
# =========================
st.set_page_config(page_title="Sistema de Vendas", layout="wide")

# =========================
# Arquivos (persistência local)
# =========================
CLIENTES_FILE = "clientes.json"
VENDAS_FILE   = "vendas.json"
PRODUTOS_FILE = "produtos.json"

COMISSAO = 0.40  # 40%

# =========================
# Utilidades
# =========================
def brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def salvar_json(caminho: str, dados: Any):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def carregar_json(caminho: str, padrao: Any) -> Any:
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return padrao

def normalizar_vendas(vendas: List[Dict]) -> List[Dict]:
    # Junta vendas duplicadas (mesmo cliente+codigo) somando quantidades
    cache = defaultdict(int)
    for v in vendas:
        k = (v["cliente"], int(v["codigo"]))
        cache[k] += int(v.get("quantidade", 1))
    saida = []
    for (cliente, codigo), qtd in cache.items():
        saida.append({"cliente": cliente, "codigo": int(codigo), "quantidade": int(qtd)})
    # ordenar por cliente, depois por código
    saida.sort(key=lambda x: (x["cliente"].lower(), x["codigo"]))
    return saida

def total_por_cliente(vendas: List[Dict], produtos: Dict[int, Dict]) -> Dict[str, float]:
    tot = defaultdict(float)
    for v in vendas:
        info = produtos.get(int(v["codigo"]))
        if not info:
            continue
        tot[v["cliente"]] += info["preco"] * int(v["quantidade"])
    return dict(tot)

def total_geral(vendas: List[Dict], produtos: Dict[int, Dict]) -> float:
    return sum(
        produtos.get(int(v["codigo"]), {}).get("preco", 0.0) * int(v["quantidade"])
        for v in vendas
    )

def sugestoes_clientes(clientes: List[str], termo: str) -> List[str]:
    t = termo.strip().lower()
    if len(t) < 2:
        return []
    return sorted([c for c in clientes if t in c.lower()], key=lambda x: x.lower())

def produto_opcao_display(codigo: int, info: Dict) -> str:
    return f"{codigo} - {info['nome']} ({brl(info['preco'])})"

def carregar_produtos_iniciais() -> Dict[int, Dict]:
    # Lista completa que você forneceu
    d = {
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
    # converter chaves para str ao salvar e de volta para int ao carregar
    return {int(k): {"nome": v["nome"], "preco": float(v["preco"])} for k, v in d.items()}

def iniciar_banco_local():
    # PRODUTOS
    produtos = carregar_json(PRODUTOS_FILE, None)
    if not produtos:
        produtos = carregar_produtos_iniciais()
        salvar_json(PRODUTOS_FILE, {str(k): v for k, v in produtos.items()})
    else:
        # garantir int nas chaves
        produtos = {int(k): v for k, v in produtos.items()}

    # CLIENTES iniciais
    clientes_padrao = [
        "Tabata", "Valquiria", "Vanessa", "Pamela", "Elan", "Claudinha"
    ]
    clientes = carregar_json(CLIENTES_FILE, None)
    if not clientes:
        clientes = sorted(clientes_padrao, key=lambda x: x.lower())
        salvar_json(CLIENTES_FILE, clientes)
    else:
        clientes = sorted(list(dict.fromkeys(clientes)), key=lambda x: x.lower())

    # VENDAS iniciais
    vendas_padrao = [
        # Tabata
        {"cliente":"Tabata","codigo":4685,"quantidade":1},
        {"cliente":"Tabata","codigo":4184,"quantidade":1},
        {"cliente":"Tabata","codigo":4351,"quantidade":1},
        {"cliente":"Tabata","codigo":3625,"quantidade":1},
        {"cliente":"Tabata","codigo":4597,"quantidade":2},
        {"cliente":"Tabata","codigo":3900,"quantidade":3},
        {"cliente":"Tabata","codigo":4680,"quantidade":1},
        {"cliente":"Tabata","codigo":4726,"quantidade":1},
        {"cliente":"Tabata","codigo":4539,"quantidade":1},
        {"cliente":"Tabata","codigo":4640,"quantidade":1},
        {"cliente":"Tabata","codigo":3875,"quantidade":1},
        {"cliente":"Tabata","codigo":4142,"quantidade":1},
        {"cliente":"Tabata","codigo":4705,"quantidade":1},
        # Valquiria
        {"cliente":"Valquiria","codigo":4702,"quantidade":1},
        {"cliente":"Valquiria","codigo":4457,"quantidade":1},
        {"cliente":"Valquiria","codigo":4493,"quantidade":1},
        {"cliente":"Valquiria","codigo":4310,"quantidade":1},
        {"cliente":"Valquiria","codigo":4705,"quantidade":2},
        {"cliente":"Valquiria","codigo":3698,"quantidade":3},
        {"cliente":"Valquiria","codigo":4494,"quantidade":1},
        {"cliente":"Valquiria","codigo":4701,"quantidade":1},
        # Vanessa
        {"cliente":"Vanessa","codigo":4562,"quantidade":1},
        {"cliente":"Vanessa","codigo":4699,"quantidade":3},
        {"cliente":"Vanessa","codigo":4539,"quantidade":1},
        # Pamela
        {"cliente":"Pamela","codigo":4681,"quantidade":1},
        {"cliente":"Pamela","codigo":4459,"quantidade":1},
        {"cliente":"Pamela","codigo":4497,"quantidade":1},
        {"cliente":"Pamela","codigo":4673,"quantidade":1},
        # Elan
        {"cliente":"Elan","codigo":4470,"quantidade":2},
        # Claudinha
        {"cliente":"Claudinha","codigo":2750,"quantidade":1},
        {"cliente":"Claudinha","codigo":4239,"quantidade":2},
        {"cliente":"Claudinha","codigo":4142,"quantidade":2},
        {"cliente":"Claudinha","codigo":4343,"quantidade":1},
        {"cliente":"Claudinha","codigo":4122,"quantidade":1},
    ]
    vendas = carregar_json(VENDAS_FILE, None)
    if not vendas:
        vendas = normalizar_vendas(vendas_padrao)
        salvar_json(VENDAS_FILE, vendas)
    else:
        # garantir tipos
        for v in vendas:
            v["codigo"] = int(v["codigo"])
            v["quantidade"] = int(v.get("quantidade", 1))
        vendas = normalizar_vendas(vendas)

    return produtos, clientes, vendas

# =========================
# Carregar base
# =========================
produtos, clientes, vendas = iniciar_banco_local()

# =========================
# Barra lateral (menu)
# =========================
st.sidebar.title("📦 Sistema de Vendas")
pagina = st.sidebar.radio(
    "Menu",
    ["Visão Geral", "Clientes", "Vendas", "Produtos", "Relatórios"],
    index=0
)

# =========================
# VISÃO GERAL
# =========================
if pagina == "Visão Geral":
    st.markdown("## 📊 Resumo Geral de Vendas")

    total = total_geral(vendas, produtos)
    comissao = total * COMISSAO

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total geral", brl(total))
    with col2:
        st.metric("Comissão (40%)", brl(comissao))

    # Lista por cliente (valores), sem mostrar comissão por cliente — apenas total geral
    st.markdown("### Por cliente")
    tot_cli = total_por_cliente(vendas, produtos)
    if not tot_cli:
        st.info("Sem vendas cadastradas.")
    else:
        for nome in sorted(tot_cli.keys(), key=lambda x: x.lower()):
            st.write(f"- **{nome}**: {brl(tot_cli[nome])}")

    st.divider()
    if st.button("Gerar texto para WhatsApp"):
        linhas = ["📋 *Relatório Geral de Vendas*"]
        for nome in sorted(tot_cli.keys(), key=lambda x: x.lower()):
            linhas.append(f"- {nome}: {brl(tot_cli[nome])}")
        linhas.append("")
        linhas.append(f"💰 *Total geral*: {brl(total)}")
        linhas.append(f"💸 *Comissão (40%)*: {brl(comissao)}")
        st.text_area("Copie e cole no WhatsApp", "\n".join(linhas), height=220)

# =========================
# CLIENTES (buscar → ver → ações)
# =========================
elif pagina == "Clientes":
    st.markdown("## 👤 Clientes")

    # Cadastrar novo cliente
    with st.expander("➕ Cadastrar cliente"):
        novo = st.text_input("Nome do cliente (novo)")
        if st.button("Salvar cliente"):
            n = novo.strip()
            if not n:
                st.warning("Digite um nome.")
            elif n in clientes:
                st.warning("Esse cliente já existe.")
            else:
                clientes.append(n)
                clientes = sorted(list(dict.fromkeys(clientes)), key=lambda x: x.lower())
                salvar_json(CLIENTES_FILE, clientes)
                st.success(f"Cliente '{n}' cadastrado!")

    st.markdown("### Buscar cliente (digite ≥ 2 letras)")
    termo = st.text_input("Nome (busca)", placeholder="ex.: ta, va, pa...")
    sugest = sugestoes_clientes(clientes, termo)
    escolha = st.selectbox("Resultados", options=["(selecione)"] + sugest, index=0)

    if escolha != "(selecione)":
        st.markdown(f"### {escolha}")

        # Editar nome do cliente
        with st.expander("✏️ Editar cliente"):
            novo_nome = st.text_input("Nome", value=escolha, key=f"ed_{escolha}")
            cols = st.columns(2)
            with cols[0]:
                if st.button("Salvar alterações", key=f"salvar_{escolha}"):
                    novo_nome2 = novo_nome.strip()
                    if not novo_nome2:
                        st.warning("Nome inválido.")
                    elif novo_nome2 != escolha and novo_nome2 in clientes:
                        st.warning("Já existe um cliente com esse nome.")
                    else:
                        # Atualiza na lista de clientes
                        clientes = [novo_nome2 if c == escolha else c for c in clientes]
                        clientes = sorted(list(dict.fromkeys(clientes)), key=lambda x: x.lower())
                        salvar_json(CLIENTES_FILE, clientes)
                        # Atualiza nas vendas
                        for v in vendas:
                            if v["cliente"] == escolha:
                                v["cliente"] = novo_nome2
                        vendas = normalizar_vendas(vendas)
                        salvar_json(VENDAS_FILE, vendas)
                        st.success("Cliente atualizado! Recarregue a busca para ver o novo nome.")
            with cols[1]:
                if st.button("🗑️ Excluir cliente", key=f"del_{escolha}"):
                    # Verifica se tem vendas
                    tem_vendas = any(v["cliente"] == escolha for v in vendas)
                    if tem_vendas:
                        st.warning("Não é possível excluir: o cliente possui vendas. Apague as vendas primeiro.")
                    else:
                        clientes = [c for c in clientes if c != escolha]
                        salvar_json(CLIENTES_FILE, clientes)
                        st.success("Cliente excluído.")

        # Registrar venda para esse cliente
        with st.expander("🛒 Registrar venda"):
            # Select de produtos com busca
            opcoes_prod = {produto_opcao_display(c, info): c for c, info in produtos.items()}
            display_escolhido = st.selectbox("Produto", options=sorted(opcoes_prod.keys(), key=lambda x: x.lower()))
            codigo_sel = opcoes_prod[display_escolhido]
            qtd = st.number_input("Quantidade", min_value=1, step=1, value=1)
            if st.button("Adicionar"):
                vendas.append({"cliente": escolha, "codigo": int(codigo_sel), "quantidade": int(qtd)})
                vendas[:] = normalizar_vendas(vendas)
                salvar_json(VENDAS_FILE, vendas)
                st.success("Venda adicionada!")

        # Mostrar compras (apenas após selecionar cliente)
        st.markdown("#### Compras desse cliente")
        itens = [v for v in vendas if v["cliente"] == escolha]
        if not itens:
            st.info("Nenhuma compra.")
        else:
            # Tabela/linhas com ação de editar quantidade ou apagar item
            total_cli = 0.0
            for v in sorted(itens, key=lambda x: x["codigo"]):
                cod = int(v["codigo"])
                info = produtos.get(cod)
                if not info:
                    st.error(f"Código {cod} não cadastrado.")
                    continue
                nome = info["nome"]
                preco = info["preco"]
                qtd_atual = int(v["quantidade"])
                subtotal = preco * qtd_atual
                total_cli += subtotal

                c1, c2, c3, c4, c5 = st.columns([4,2,2,2,2])
                with c1:
                    st.write(f"**{cod} - {nome}**")
                with c2:
                    st.write(f"Preço: {brl(preco)}")
                with c3:
                    nova_qtd = st.number_input("Qtd", min_value=0, step=1, value=qtd_atual, key=f"q_{escolha}_{cod}")
                with c4:
                    if st.button("Salvar", key=f"sv_{escolha}_{cod}"):
                        if nova_qtd == 0:
                            # Apaga item
                            vendas[:] = [x for x in vendas if not (x["cliente"] == escolha and int(x["codigo"]) == cod)]
                            salvar_json(VENDAS_FILE, normalizar_vendas(vendas))
                            st.success("Item removido.")
                        else:
                            # Atualiza quantidade
                            for x in vendas:
                                if x["cliente"] == escolha and int(x["codigo"]) == cod:
                                    x["quantidade"] = int(nova_qtd)
                            salvar_json(VENDAS_FILE, normalizar_vendas(vendas))
                            st.success("Quantidade atualizada.")
                with c5:
                    if st.button("🗑️ Apagar", key=f"rm_{escolha}_{cod}"):
                        vendas[:] = [x for x in vendas if not (x["cliente"] == escolha and int(x["codigo"]) == cod)]
                        salvar_json(VENDAS_FILE, normalizar_vendas(vendas))
                        st.success("Item removido.")

            st.markdown(f"**Total do cliente:** {brl(total_cli)}")

# =========================
# VENDAS (geral)
# =========================
elif pagina == "Vendas":
    st.markdown("## 🛒 Registrar Vendas")

    if not clientes:
        st.info("Cadastre clientes primeiro.")
    else:
        # Cliente (autocomplete embutido do selectbox + ordenado)
        cli = st.selectbox("Cliente", options=sorted(clientes, key=lambda x: x.lower()))
        # Produto
        opcoes_prod = {produto_opcao_display(c, info): c for c, info in produtos.items()}
        display_escolhido = st.selectbox("Produto", options=sorted(opcoes_prod.keys(), key=lambda x: x.lower()))
        codigo_sel = opcoes_prod[display_escolhido]
        qtd = st.number_input("Quantidade", min_value=1, step=1, value=1)

        if st.button("Adicionar venda"):
            vendas.append({"cliente": cli, "codigo": int(codigo_sel), "quantidade": int(qtd)})
            vendas[:] = normalizar_vendas(vendas)
            salvar_json(VENDAS_FILE, vendas)
            st.success("Venda registrada!")

    st.divider()
    st.markdown("### Extrato geral")
    tot_cli = total_por_cliente(vendas, produtos)
    total = total_geral(vendas, produtos)
    comissao = total * COMISSAO

    for nome in sorted(tot_cli.keys(), key=lambda x: x.lower()):
        st.write(f"- **{nome}**: {brl(tot_cli[nome])}")
    st.write(f"**Total geral:** {brl(total)}")
    st.write(f"**Comissão (40%)**: {brl(comissao)}")

# =========================
# PRODUTOS (gerenciar)
# =========================
elif pagina == "Produtos":
    st.markdown("## 📦 Produtos")

    # Adicionar/atualizar produto
    with st.expander("➕ Adicionar/Atualizar produto"):
        colp = st.columns([1,3,2])
        with colp[0]:
            codigo = st.number_input("Código", min_value=1, step=1, value=3900)
        with colp[1]:
            nomep = st.text_input("Nome do produto")
        with colp[2]:
            precop = st.number_input("Preço (R$)", min_value=0.0, step=0.10, value=0.0, format="%.2f")

        if st.button("Salvar produto"):
            if not nomep.strip() or precop <= 0:
                st.warning("Preencha nome e preço.")
            else:
                produtos[int(codigo)] = {"nome": nomep.strip(), "preco": float(precop)}
                salvar_json(PRODUTOS_FILE, {str(k): v for k, v in produtos.items()})
                st.success("Produto salvo/atualizado!")

    st.markdown("### Lista de produtos")
    # ordenar por nome
    for cod in sorted(produtos.keys(), key=lambda k: produtos[k]["nome"].lower()):
        info = produtos[cod]
        c1, c2, c3 = st.columns([5,2,1])
        with c1:
            st.write(f"**{cod} - {info['nome']}**")
        with c2:
            st.write(brl(info["preco"]))
        with c3:
            if st.button("🗑️", key=f"delp_{cod}"):
                # bloquear exclusão se houver vendas com esse produto
                if any(int(v["codigo"]) == int(cod) for v in vendas):
                    st.warning("Não é possível excluir: existe venda com esse código.")
                else:
                    produtos.pop(cod, None)
                    salvar_json(PRODUTOS_FILE, {str(k): v for k, v in produtos.items()})
                    st.success("Produto excluído.")

# =========================
# RELATÓRIOS
# =========================
elif pagina == "Relatórios":
    st.markdown("## 📑 Relatórios")

    opc = st.radio("Escolha", ["Geral", "Por cliente", "Comissão total"])

    if opc == "Geral":
        st.markdown("### Relatório geral (com produtos e quantidades)")
        # Agrupar por cliente e produto
        agrup = defaultdict(lambda: defaultdict(int))
        for v in vendas:
            agrup[v["cliente"]][int(v["codigo"])] += int(v["quantidade"])

        linhas = ["📋 *Relatório Geral de Vendas*"]
        total = 0.0
        for cliente in sorted(agrup.keys(), key=lambda x: x.lower()):
            linhas.append(f"\n*{cliente}*")
            subtotal_cli = 0.0
            for cod, qtd in sorted(agrup[cliente].items()):
                info = produtos.get(cod)
                if not info: 
                    continue
                linhas.append(f"- {info['nome']} ({qtd}x): {brl(info['preco']*qtd)}")
                subtotal_cli += info["preco"]*qtd
            linhas.append(f"Total do cliente: {brl(subtotal_cli)}")
            total += subtotal_cli

        linhas.append(f"\n💰 Total geral: {brl(total)}")
        linhas.append(f"💸 Comissão (40%): {brl(total*COMISSAO)}")
        st.text_area("Copie e cole no WhatsApp", "\n".join(linhas), height=420)

    elif opc == "Por cliente":
        if not clientes:
            st.info("Sem clientes.")
        else:
            cli = st.selectbox("Cliente", options=sorted(clientes, key=lambda x: x.lower()))
            itens = [v for v in vendas if v["cliente"] == cli]
            if not itens:
                st.info("Esse cliente não possui vendas.")
            else:
                # agrupar por produto
                agrup = defaultdict(int)
                for v in itens:
                    agrup[int(v["codigo"])] += int(v["quantidade"])
                total_cli = 0.0
                linhas = [f"📋 *Relatório de {cli}*"]
                for cod, qtd in sorted(agrup.items()):
                    info = produtos.get(cod)
                    if not info: 
                        continue
                    linhas.append(f"- {info['nome']} ({qtd}x): {brl(info['preco']*qtd)}")
                    total_cli += info["preco"]*qtd
                linhas.append(f"\n💰 Total do cliente: {brl(total_cli)}")
                st.text_area("Copie e cole no WhatsApp", "\n".join(linhas), height=350)

    else:  # Comissão total
        total = total_geral(vendas, produtos)
        st.metric("💸 Comissão (40%)", brl(total * COMISSAO))

