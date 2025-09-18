# app.py
import streamlit as st
from datetime import datetime
import json
import os

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

# =============== Dados iniciais e vendas ===============
PRODUTOS_INICIAIS = {
    1: {"nome": "Produto A", "preco": 10.0},
    2: {"nome": "Produto B", "preco": 20.0},
    3: {"nome": "Produto C", "preco": 15.5},
}

VENDAS_INICIAIS = {
    "Cliente 1": [{"codigo": 1, "quantidade": 2, "preco": 10.0}],
    "Cliente 2": [{"codigo": 2, "quantidade": 1, "preco": 20.0}],
}

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
        st.experimental_rerun()
    except:
        st.error("Não foi possível remover.")

def editar_venda(nome, idx, nova_qtd, novo_preco):
    try:
        st.session_state.clientes[nome][idx]["quantidade"] = int(nova_qtd)
        st.session_state.clientes[nome][idx]["preco"] = float(novo_preco)
        save_db()
        st.success("Venda atualizada.")
        st.experimental_rerun()
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
    st.experimental_rerun()

def apagar_cliente(nome):
    st.session_state.clientes.pop(nome, None)
    save_db()
    st.success("Cliente apagado.")
    st.experimental_rerun()

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

# =============== Telas principais ===============
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
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        nome = st.text_input("Digite seu nome para entrar como visitante").strip()
        if st.button("Entrar como visitante"):
            if nome:
                st.session_state.logado = True
                st.session_state.usuario = f"visitante-{nome}"
                registrar_acesso(f"login-visitante: {nome}")
                st.experimental_rerun()
            else:
                st.warning("Por favor, digite um nome.")

def tela_resumo():
    st.header("📊 Resumo")
    st.write(f"Total geral das vendas: R$ {total_geral():.2f}")

def tela_registrar_venda():
    visitante = is_visitante()
    st.header("🛒 Registrar venda")
    if visitante:
        st.warning("🔒 Visitantes não podem registrar vendas.")

    st.session_state.filtro_cliente = st.text_input(
        "Buscar cliente (2+ letras):",
        value=st.session_state.filtro_cliente,
        disabled=visitante
    )
    sugestoes = filtrar_clientes(st.session_state.filtro_cliente)
    cliente = st.selectbox("Cliente", sugestoes, index=None, placeholder="Digite para buscar",
                           disabled=visitante) if sugestoes else None

    st.markdown("---")
    lista_fmt = opcao_produtos_fmt()
    sel = st.selectbox("Produto", lista_fmt, index=None, placeholder="Selecione produto", disabled=visitante)
    qtd = st.number_input("Quantidade", min_value=1, step=1, value=1, disabled=visitante)
    preco_padrao = 0.0
    cod_sel = None
    if sel:
        cod_sel = parse_codigo_from_fmt(sel)
        if cod_sel in st.session_state.produtos:
            preco_padrao = st.session_state.produtos[cod_sel]["preco"]
    preco_venda = st.number_input("Preço unitário", min_value=0.0, value=float(preco_padrao),
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

    st.markdown("### Carrinho")
    if not st.session_state.carrinho:
        st.info("Carrinho vazio.")
    else:
        total_cart = 0.0
        for i, item in enumerate(st.session_state.carrinho):
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(f"{i+1}. {item['nome']} ({item['quantidade']}x) - R$ {item['preco']:.2f}")
            with col2:
                if st.button("🗑️", key=f"rm_{i}", disabled=visitante):
                    st.session_state.carrinho.pop(i)
                    st.experimental_rerun()
            total_cart += item["quantidade"] * item["preco"]
        st.markdown(f"**Total do carrinho:** R$ {total_cart:.2f}")
        if st.button("Finalizar venda", disabled=visitante):
            if cliente and st.session_state.carrinho:
                st.session_state.clientes.setdefault(cliente, [])
                st.session_state.clientes[cliente].extend(st.session_state.carrinho)
                st.session_state.carrinho = []
                save_db()
                st.success("Venda registrada!")
                st.experimental_rerun()

def tela_clientes():
    visitante = is_visitante()
    st.header("👥 Clientes")
    filtro = st.text_input("Buscar cliente (2+ letras)").strip()
    matches = filtrar_clientes(filtro)
    cliente = st.selectbox("Selecione o cliente", matches, index=None) if matches else None
    if cliente:
        st.subheader(f"Vendas de {cliente}")
        vendas = st.session_state.clientes.get(cliente, [])
        total = 0.0
        for idx, v in enumerate(vendas):
            cod = v["codigo"]
            nomep = st.session_state.produtos.get(cod, {}).get("nome", f"Cód {cod}")
            preco = float(v["preco"])
            qtd = int(v["quantidade"])
            subtotal = preco * qtd
            total += subtotal
            st.write(f"{idx+1}. {nomep} - {qtd}x - R$ {preco:.2f} = R$ {subtotal:.2f}")
        st.markdown(f"**Total do cliente:** R$ {total:.2f}")

def tela_produtos():
    st.header("📦 Produtos")
    for cod, p in st.session_state.produtos.items():
        st.write(f"{cod} - {p['nome']} - R$ {p['preco']:.2f}")

def tela_relatorios():
    st.header("📄 Relatórios")
    st.write("Funcionalidade de relatórios em construção.")

def tela_acessos():
    st.header("📝 Acessos")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.read()
        st.text(logs)
    else:
        st.info("Nenhum acesso registrado.")

# =============== Sidebar e navegação ===============
def bloco_backup_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧰 Backup")
    db_json = json.dumps({
        "produtos": st.session_state.produtos,
        "clientes": st.session_state.clientes,
    }, ensure_ascii=False, indent=2)
    st.sidebar.download_button("⬇️ Exportar backup", data=db_json.encode("utf-8"),
                               file_name="backup.json")
    up = st.sidebar.file_uploader("⬆️ Restaurar backup", type=["json"])
    if up is not None:
        try:
            data = json.load(up)
            st.session_state.produtos = {int(k): v for k, v in data.get("produtos", {}).items()}
            st.session_state.clientes = {k: v for k, v in data.get("clientes", {}).items()}
            save_db()
            st.sidebar.success("Backup restaurado!")
            st.experimental_rerun()
        except Exception as e:
            st.sidebar.error(f"Erro: {e}")

def barra_lateral():
    st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario}")
    opcoes = ["Resumo", "Registrar venda", "Clientes", "Produtos", "Relatórios", "Sair"]
    if not is_visitante():
        opcoes.insert(-1, "Acessos")
    idx_atual = opcoes.index(st.session_state.menu) if st.session_state.menu in opcoes else 0
    st.session_state.menu = st.sidebar.radio("Menu", opcoes, index=idx_atual)
    bloco_backup_sidebar()

def main():
    if not st.session_state.logado:
        tela_login()
    else:
        barra_lateral()
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
            tela_acessos()
        elif st.session_state.menu == "Sair":
            st.session_state.logado = False
            st.session_state.usuario = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()