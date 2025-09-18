# app.py (Parte 1/3)
import streamlit as st
from datetime import datetime
import json
import os
import io
import re

# Tentar importar bibliotecas de imagem / OCR
OCR_AVAILABLE = True
try:
    from PIL import Image
except Exception:
    OCR_AVAILABLE = False

try:
    import pytesseract
except Exception:
    OCR_AVAILABLE = False

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

# =============== Dados iniciais: produtos e vendas (exemplos) ===============
# Usei um conjunto razoável de produtos e algumas vendas iniciais.
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

VENDAS_INICIAIS = {
    "Tabata": [
        {"codigo": 4685, "quantidade": 1, "preco": 52.95},
        {"codigo": 4184, "quantidade": 1, "preco": 25.20},
        {"codigo": 4351, "quantidade": 1, "preco": 54.20},
        {"codigo": 3625, "quantidade": 1, "preco": 28.50},
        {"codigo": 4597, "quantidade": 1, "preco": 29.00},
        {"codigo": 3900, "quantidade": 1, "preco": 15.90},
    ],
    "Valquiria": [
        {"codigo": 4702, "quantidade": 1, "preco": 58.40},
        {"codigo": 4457, "quantidade": 1, "preco": 83.80},
        {"codigo": 4493, "quantidade": 1, "preco": 25.50},
    ],
    "Vanessa": [
        {"codigo": 4562, "quantidade": 1, "preco": 65.10},
        {"codigo": 4699, "quantidade": 2, "preco": 18.90},
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
            prods = {int(k): v for k, v in data.get("produtos", {}).items()}
            clis  = {k: v for k, v in data.get("clientes", {}).items()}
            return prods, clis
        except Exception:
            pass
    # se não existir db.json, retorna os iniciais
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

# =============== Helpers (início) ===============
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
# app.py (Parte 2/3)
# =============== Helpers (continuação) ===============
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
    except Exception:
        st.error("Não foi possível remover.")

def editar_venda(nome, idx, nova_qtd, novo_preco):
    try:
        st.session_state.clientes[nome][idx]["quantidade"] = int(nova_qtd)
        st.session_state.clientes[nome][idx]["preco"] = float(novo_preco)
        save_db()
        st.success("Venda atualizada.")
        st.rerun()
    except Exception:
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

# =============== OCR helper ===============
def extrair_texto_imagem(imagem_pil):
    """
    Recebe um PIL.Image e retorna texto com pytesseract (se disponível).
    """
    if not OCR_AVAILABLE:
        return "OCR não disponível no servidor. Instale pytesseract + tesseract."
    try:
        texto = pytesseract.image_to_string(imagem_pil, lang="por+eng")
        return texto
    except Exception as e:
        return f"Erro OCR: {e}"

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

# ----------------- Tela Resumo -----------------
def tela_resumo():
    st.header("📦 Sistema de Vendas - Resumo")
    tg = total_geral()
    st.markdown(f"**💰 Total geral:** R$ {tg:.2f}")
    st.markdown(f"**💸 Comissão (40%):** R$ {(tg*0.40):.2f}")
    st.markdown("---")
    st.subheader("Totais por cliente")
    for c in sorted(st.session_state.clientes.keys(), key=lambda x: x.lower()):
        st.write(f"- **{c}**: R$ {total_cliente(c):.2f}")

# ----------------- Tela Registrar Venda (manual, com carrinho) -----------------
def tela_registrar_venda():
    visitante = is_visitante()
    st.header("🛒 Registrar venda (manual)")

    if visitante:
        st.warning("🔒 Visitantes não podem registrar vendas. Os campos abaixo estão apenas para visualização.")

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
    sel = st.selectbox("Produto", lista_fmt, index=None, placeholder="Digite para buscar", disabled=visitante)
    qtd = st.number_input("Quantidade", min_value=1, step=1, value=1, disabled=visitante)
    preco_padrao = 0.0
    cod_sel = None
    if sel:
        cod_sel = parse_codigo_from_fmt(sel)
        if cod_sel in st.session_state.produtos:
            preco_padrao = st.session_state.produtos[cod_sel]["preco"]
    preco_venda = st.number_input("Preço desta venda (pode ajustar)", min_value=0.0, value=float(preco_padrao),
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
            st.success(f"Adicionado ao carrinho: {nomep} ({qtd}x)")

    st.markdown("### Carrinho")
    if not st.session_state.carrinho:
        st.info("Carrinho vazio.")
    else:
        total_cart = 0.0
        for i, item in enumerate(st.session_state.carrinho):
            col1, col2 = st.columns([5,1])
            with col1:
                st.write(f"**{i+1}.** {item['nome']} — {item['quantidade']}x — R$ {item['preco']:.2f} cada")
            with col2:
                if st.button("🗑️ Remover", key=f"rm_{i}", disabled=visitante):
                    st.session_state.carrinho.pop(i)
                    st.success("Item removido do carrinho.")
                    st.rerun()
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
                    # normaliza itens -> só manter codigo, quantidade, preco
                    for it in st.session_state.carrinho:
                        st.session_state.clientes[cliente].append({
                            "codigo": it["codigo"],
                            "quantidade": it["quantidade"],
                            "preco": it["preco"]
                        })
                    st.session_state.carrinho = []
                    save_db()
                    st.success("Venda registrada com sucesso!")
                    st.rerun()

# ----------------- Tela Clientes -----------------
def tela_clientes():
    visitante = is_visitante()
    st.header("👥 Clientes")
    aba_opcoes = ["Consultar cliente", "Cadastrar cliente"]
    aba = st.radio("Ação", aba_opcoes, horizontal=True)

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
                    novo_preco = st.number_input("Preço (desta venda)", min_value=0.0, step=0.10, value=preco, format="%.2f", key=f"p_{cliente}_{idx}", disabled=visitante)
                    col1, col2 = st.columns(2)
                    with col1:
                        if not visitante and st.button("Salvar edição", key=f"save_{cliente}_{idx}"):
                            editar_venda(cliente, idx, nova_qtd, novo_preco)
                    with col2:
                        if not visitante and st.button("Apagar venda", key=f"del_{cliente}_{idx}"):
                            remover_venda(cliente, idx)
            st.markdown(f"**Total do cliente:** R$ {total:.2f}")

        # Adicionar produto diretamente para este cliente
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
                st.rerun()

# ----------------- Tela Produtos -----------------
def tela_produtos():
    visitante = is_visitante()
    st.header("📦 Produtos")
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
            novo_preco = st.number_input("Preço", value=float(preco), step=0.10, format="%.2f", key=f"pp_{cod}", disabled=visitante)
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

# ----------------- Tela Relatórios -----------------
def tela_relatorios():
    st.header("📈 Relatórios")
    escolha = st.radio("Escolha um relatório", ["Geral", "Individual", "Comissão total"], horizontal=True)
    if escolha == "Geral":
        linhas = ["Relatório Geral", ""]
        for c in sorted(st.session_state.clientes.keys(), key=lambda x: x.lower()):
            linhas.append(f"- {c}: R$ {total_cliente(c):.2f}")
        linhas.append("")
        linhas.append(f"Total geral: R$ {total_geral():.2f}")
        st.code("\n".join(linhas))
        st.download_button("Baixar .txt", data="\n".join(linhas), file_name="relatorio_geral.txt")
    elif escolha == "Individual":
        filtro = st.text_input("Buscar cliente (2+ letras)").strip()
        matches = filtrar_clientes(filtro)
        cliente = st.selectbox("Cliente", matches, index=None) if matches else None
        if cliente:
            linhas = [f"Relatório de {cliente}", ""]
            vendas = st.session_state.clientes.get(cliente, [])
            if not vendas:
                linhas.append("Sem vendas")
            else:
                for v in vendas:
                    nomep = st.session_state.produtos.get(v["codigo"], {}).get("nome", f"Cód {v['codigo']}")
                    linhas.append(f"- {nomep} ({v['quantidade']}x): R$ {(v['preco']*v['quantidade']):.2f}")
            st.code("\n".join(linhas))
            st.download_button("Baixar .txt", data="\n".join(linhas), file_name=f"relatorio_{cliente}.txt")
        else:
            st.info("Digite ao menos 2 letras para buscar.")
    else:
        tg = total_geral()
        texto = f"Comissão total (40%): R$ {(tg*0.40):.2f}"
        st.code(texto)
        st.download_button("Baixar .txt", data=texto, file_name="relatorio_comissao.txt")

# ----------------- Tela Acessos -----------------
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
# app.py (Parte 3/3)
# ----------------- Backup / Sidebar -----------------
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
    else:
        st.sidebar.caption("🔒 Restauração disponível apenas para usuários logados.")

    # Inserir produto manual na sidebar (rápido)
    st.sidebar.markdown("---")
    st.sidebar.subheader("✍️ Inserir Produto Manualmente")
    if is_visitante():
        st.sidebar.caption("🔒 Apenas usuários logados podem inserir produtos.")
    else:
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
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Erro ao adicionar produto: {e}")

    # Zerar vendas (segurança)
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
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Falha ao zerar vendas: {e}")

# ----------------- Tela Registrar venda por foto (OCR) -----------------
def tela_registrar_venda_foto():
    visitante = is_visitante()
    st.header("📸 Registrar venda por foto")
    if visitante:
        st.info("🔒 Visitantes não podem registrar vendas por foto.")
    cliente = st.text_input("Nome do cliente (exato)", key="cli_foto")
    uploaded = st.file_uploader("Envie a foto da nota / produto (jpg, png)", type=["jpg","jpeg","png"], key="file_foto")
    if uploaded:
        if not OCR_AVAILABLE:
            st.warning("OCR não disponível: instale pytesseract + Pillow e o binário tesseract no servidor.")
        try:
            image = Image.open(uploaded).convert("RGB")
            st.image(image, caption="Imagem carregada", use_column_width=True)
        except Exception as e:
            st.error(f"Não foi possível abrir a imagem: {e}")
            return

        texto_detectado = extrair_texto_imagem(image)
        with st.expander("🔎 Texto detectado (OCR)"):
            st.text(texto_detectado)

        # tentativas de extrair preço e código por regex simples
        preco_detect = None
        codigo_detect = None
        # procurar padrões de preço, ex.: 123,45 ou 123.45
        preco_matches = re.findall(r'(\d{1,6}[.,]\d{2})', texto_detectado)
        if preco_matches:
            # pega primeiro (mais provável)
            preco_str = preco_matches[0].replace('.', '').replace(',', '.')
            try:
                preco_detect = float(preco_str)
            except:
                preco_detect = None
        # procurar códigos (números com 3-6 dígitos)
        cod_matches = re.findall(r'\b(\d{3,6})\b', texto_detectado)
        if cod_matches:
            # pega primeiro que existe nos produtos, se possível
            for c in cod_matches:
                ci = int(c)
                if ci in st.session_state.produtos:
                    codigo_detect = ci
                    break
            if not codigo_detect:
                codigo_detect = int(cod_matches[0]) if cod_matches else None

        st.markdown("### Ajuste / confirme os campos (se necessário)")
        codigo_input = st.text_input("Código do produto (se detectado, corrija aqui)", value=str(codigo_detect) if codigo_detect else "")
        nome_input = st.text_input("Nome do produto (se possível preencher)", value=st.session_state.produtos.get(codigo_detect, {}).get("nome", "") if codigo_detect else "")
        preco_input = st.number_input("Preço unitário", min_value=0.0, value=float(preco_detect) if preco_detect else 0.0, step=0.01, format="%.2f")
        qtd_input = st.number_input("Quantidade", min_value=1, value=1, step=1)

        if st.button("Adicionar venda a este cliente"):
            if not cliente:
                st.warning("Informe o nome do cliente.")
            else:
                # valida código
                cod_final = None
                if codigo_input:
                    try:
                        cod_final = int(str(codigo_input).strip())
                    except:
                        cod_final = None
                if cod_final is None:
                    # gera novo código next
                    cod_final = max(list(st.session_state.produtos.keys()) + [0]) + 1
                # se produto não existe, cria com o nome e preço informados
                if cod_final not in st.session_state.produtos:
                    st.session_state.produtos[cod_final] = {"nome": nome_input.strip() or f"Cod {cod_final}", "preco": float(preco_input)}
                # registra venda
                st.session_state.clientes.setdefault(cliente, [])
                st.session_state.clientes[cliente].append({
                    "codigo": cod_final,
                    "quantidade": int(qtd_input),
                    "preco": float(preco_input)
                })
                save_db()
                st.success("Venda registrada com sucesso!")
                registrar_acesso(f"venda_por_foto: {st.session_state.usuario} - cliente:{cliente} - cod:{cod_final}")
                st.rerun()

# ----------------- Barra lateral (com menu) -----------------
def barra_lateral():
    st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario}")
    opcoes = ["Resumo", "Registrar venda", "Registrar venda por foto", "Clientes", "Produtos", "Relatórios", "Sair"]
    # adicionar Acessos só para não-visitante
    if not is_visitante():
        opcoes.insert(-1, "Acessos")
    idx_atual = opcoes.index(st.session_state.menu) if st.session_state.menu in opcoes else 0
    st.session_state.menu = st.sidebar.radio("Menu", opcoes, index=idx_atual)
    bloco_backup_sidebar()

# ----------------- Roteador principal e main -----------------
def main():
    if not st.session_state.logado:
        # exibe somente a tela de login
        tela_login()
        return
    # se logado
    barra_lateral()
    menu = st.session_state.menu
    if menu == "Resumo":
        tela_resumo()
    elif menu == "Registrar venda":
        tela_registrar_venda()
    elif menu == "Registrar venda por foto":
        tela_registrar_venda_foto()
    elif menu == "Clientes":
        tela_clientes()
    elif menu == "Produtos":
        tela_produtos()
    elif menu == "Relatórios":
        tela_relatorios()
    elif menu == "Acessos":
        # proteger acessos para visitantes
        if not is_visitante():
            tela_acessos()
        else:
            st.error("Acesso negado.")
    elif menu == "Sair":
        # limpa sessão do usuário e volta ao login
        st.session_state.logado = False
        st.session_state.usuario = None
        st.rerun()

if __name__ == "__main__":
    main()

