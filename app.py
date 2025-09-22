# ================== PARTE 1 ==================
# Imports e Configuração
import streamlit as st
from datetime import datetime
import json
import os
import io
import re

# Se você usa importação de PDF, deixe a linha abaixo (requer pdfplumber instalado)
try:
    import pdfplumber
except Exception:
    pdfplumber = None

st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# ================== Usuários (login) ==================
USERS = {"othavio": "122008", "isabela": "122008"}  # usuários e senhas em texto (simples)
LOG_FILE = "acessos.log"
DB_FILE = "db.json"

# ================== Registro de acesso ==================
def registrar_acesso(usuario: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {usuario}\n")
    except:
        pass

# ================== Helpers: salvar/carregar DB ==================
def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "produtos": st.session_state.get("produtos", {}),
                "clientes": st.session_state.get("clientes", {}),
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Falha ao salvar DB: {e}")

def load_db():
    # retorna (produtos_dict, clientes_dict)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            prods = {}
            for k, v in data.get("produtos", {}).items():
                try:
                    prods[int(k)] = v
                except:
                    prods[k] = v
            clis = {k: v for k, v in data.get("clientes", {}).items()}
            return prods, clis
        except Exception:
            pass
    # default (se não existir DB)
    default_clients = {
        "Tabata": [],
        "Valquiria": [],
        "Vanessa": [],
        "Pamela": [],
        "Elan": [],
        "Claudinha": [],
    }
    return {}, default_clients

# ================== Session State inicial ==================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "produtos" not in st.session_state or not st.session_state["produtos"]:
    prods_loaded, clients_loaded = load_db()
    # se DB vazio, load_db já retornou defaults
    st.session_state["produtos"] = prods_loaded or {}
    st.session_state["clientes"] = clients_loaded or {
        "Tabata": [], "Valquiria": [], "Vanessa": [], "Pamela": [], "Elan": [], "Claudinha": []
    }
if "menu" not in st.session_state:
    st.session_state["menu"] = "Resumo 📊"
# flag auxiliar (não necessária, mas mantida para compatibilidade)
if "recarregar" not in st.session_state:
    st.session_state["recarregar"] = False

# ================== Função: is_visitante ==================
def is_visitante():
    u = st.session_state.get("usuario")
    return isinstance(u, str) and u.startswith("visitante-")

# ================== PARTE 2 ==================
# ================== Login ==================
def login():
    st.title("🔐 Login")
    escolha = st.radio("Como deseja entrar?", ["Usuário cadastrado", "Visitante"], horizontal=True)

    if escolha == "Usuário cadastrado":
        usuario = st.text_input("Usuário", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar"):
            if usuario in USERS and USERS[usuario] == senha:
                st.session_state["usuario"] = usuario
                registrar_acesso(f"login-usuario:{usuario}")
                st.success(f"Bem-vindo(a), {usuario}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        nome = st.text_input("Digite seu nome para entrar como visitante", key="login_visitante")
        if st.button("Entrar como visitante"):
            if nome.strip():
                st.session_state["usuario"] = f"visitante-{nome.strip()}"
                registrar_acesso(f"login-visitante:{nome.strip()}")
                st.success(f"Bem-vindo(a), visitante {nome.strip()}!")
                st.rerun()

# ================== Tela de Resumo ==================
def tela_resumo():
    st.header("📊 Resumo de Vendas")
    visitante = is_visitante()
    total_geral = 0.0
    for cliente, vendas in st.session_state["clientes"].items():
        total_cliente = sum((v.get("preco", 0.0) * v.get("quantidade", 0)) for v in vendas)
        total_geral += total_cliente
    comissao = total_geral * 0.25
    if visitante:
        st.metric("💰 Total Geral de Vendas", "R$ *****")
        st.metric("🧾 Comissão (25%)", "R$ *****")
    else:
        st.metric("💰 Total Geral de Vendas", f"R$ {total_geral:.2f}")
        st.metric("🧾 Comissão (25%)", f"R$ {comissao:.2f}")

# ================== PDF (opcional) ==================
def tela_pdf():
    st.header("📄 Importar Estoque via Nota Fiscal (PDF)")
    if is_visitante():
        st.info("🔒 Apenas usuários logados podem importar PDF.")
        return
    if pdfplumber is None:
        st.warning("A biblioteca pdfplumber não está disponível no ambiente.")
        return
    pdf_file = st.file_uploader("Selecione o PDF da nota fiscal", type=["pdf"])
    if pdf_file is not None:
        if st.button("Substituir estoque pelo PDF"):
            substituir_estoque_pdf(pdf_file)

def substituir_estoque_pdf(uploaded_file):
    data = uploaded_file.read()
    stream = io.BytesIO(data)
    novos_produtos = {}
    # Regex adaptável (depende do layout do PDF)
    linha_regex = re.compile(r'^\s*(\d+)\s+0*(\d{1,6})\s+(.+?)\s+([\d.,]+)\s*$')
    try:
        with pdfplumber.open(stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                for linha in text.splitlines():
                    m = linha_regex.match(linha.strip())
                    if m:
                        _, cod_s, nome, preco_s = m.groups()
                        try:
                            cod = int(cod_s)
                        except:
                            cod = int(cod_s) if cod_s.isdigit() else None
                        try:
                            preco = float(preco_s.replace('.', '').replace(',', '.'))
                        except:
                            preco = 0.0
                        if cod is not None:
                            novos_produtos[cod] = {"nome": nome.title(), "preco": preco}
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
        return

    if not novos_produtos:
        st.error("Nenhum produto válido encontrado no PDF.")
        return
    st.session_state["produtos"] = novos_produtos
    save_db()
    st.success("Estoque atualizado a partir do PDF!")

# ================== Produtos ==================
def adicionar_produto_manual(cod, nome, preco):
    cod = int(cod)
    st.session_state["produtos"][cod] = {"nome": nome.strip(), "preco": float(preco)}
    save_db()
    st.success(f"Produto {nome} adicionado/atualizado!")

def tela_produtos():
    st.header("📦 Produtos")
    visitante = is_visitante()
    acao = st.radio("Ação", ["Listar/Buscar", "Adicionar"], horizontal=True)

    if acao == "Adicionar":
        if visitante:
            st.info("🔒 Visitantes não podem adicionar produtos.")
            return
        cod = st.number_input("Código", min_value=1, step=1, key="cod_produto")
        nome = st.text_input("Nome do produto", key="nome_produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.10, format="%.2f", key="preco_produto")
        if st.button("Salvar produto"):
            if cod in st.session_state["produtos"]:
                st.warning("Código já existe.")
            elif not nome.strip():
                st.warning("Informe um nome válido.")
            else:
                adicionar_produto_manual(cod, nome, preco)
    else:
        termo = st.text_input("Buscar por nome ou código", key="buscar_produto").lower()
        st.subheader("Lista de Produtos")
        for cod, dados in sorted(st.session_state["produtos"].items(), key=lambda x: str(x[0])):
            if termo in str(cod) or termo in dados["nome"].lower() or termo == "":
                st.write(f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f})")

# ================== PARTE 3 ==================
# ================== Clientes ==================
def tela_clientes():
    st.header("👥 Clientes")
    visitante = is_visitante()
    aba = st.radio("Ação", ["Consultar cliente", "Cadastrar cliente"], horizontal=True)

    # Bloquear cadastro de cliente para visitante
    if visitante and aba == "Cadastrar cliente":
        st.info("🔒 Visitantes não podem cadastrar clientes.")
        return

    if aba == "Cadastrar cliente":
        nome = st.text_input("Nome do cliente", key="nome_cliente")
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

    # Consultar clientes
    filtro = st.text_input("Buscar cliente (2+ letras)", key="buscar_cliente").lower()
    matches = [c for c in st.session_state["clientes"] if filtro in c.lower()]
    cliente = st.selectbox("Selecione o cliente", matches) if matches else None

    if cliente:
        st.subheader(f"{cliente}")
        vendas = st.session_state["clientes"].get(cliente, [])

        # ➕ Adicionar Venda
        st.markdown("### ➕ Adicionar Venda")
        if visitante:
            st.info("🔒 Visitantes não podem adicionar vendas.")
        else:
            produto_input = st.text_input("Digite código ou nome do produto", key=f"venda_produto_{cliente}")
            opcoes_produtos = [
                f"{cod} - {p['nome']}" for cod, p in st.session_state["produtos"].items()
                if produto_input.lower() in str(cod) or produto_input.lower() in p["nome"].lower()
            ]
            produto_selecionado = st.selectbox("Escolha o produto", opcoes_produtos, key=f"select_venda_produto_{cliente}") if opcoes_produtos else None
            quantidade = st.number_input("Quantidade", min_value=1, step=1, key=f"quantidade_venda_{cliente}")
            if st.button("Adicionar venda", key=f"btn_add_venda_{cliente}"):
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

            # Bloquear edição e exclusão para visitante
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

        # Apagar cliente (corrigido) - checkbox antes do botão
        if not visitante:
            confirmar = st.checkbox(f"Confirme que deseja apagar o cliente {cliente}", key=f"confirm_apagar_{cliente}")
            if confirmar:
                if st.button(f"🗑️ Apagar cliente {cliente}"):
                    st.session_state["clientes"].pop(cliente, None)
                    save_db()
                    st.success(f"Cliente {cliente} apagado!")
                    st.rerun()

# ================== Relatórios ==================
def relatorio_geral():
    st.header("📋 Relatório Geral")
    visitante = is_visitante()
    linhas = ["📋 Relatório Geral de Vendas", ""]
    for c, vendas in st.session_state["clientes"].items():
        total = sum(v.get("preco", 0.0) * v.get("quantidade", 0) for v in vendas)
        if visitante:
            linhas.append(f"- {c}: R$ *****")
        else:
            linhas.append(f"- {c}: R$ {total:.2f}")

    total_geral = sum(sum(v.get("preco", 0.0) * v.get("quantidade", 0) for v in vendas) for vendas in st.session_state["clientes"].values())
    if visitante:
        linhas.append(f"\n💰 Total geral: R$ *****")
    else:
        linhas.append(f"\n💰 Total geral: R$ {total_geral:.2f}")

    st.code("\n".join(linhas))
    st.download_button("Baixar .txt", data="\n".join(linhas), file_name="relatorio_geral.txt")

# ================== Menu lateral ==================
def bloco_backup_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧰 Backup")
    db_json = json.dumps({"produtos": st.session_state["produtos"], "clientes": st.session_state["clientes"]}, ensure_ascii=False, indent=2)
    st.sidebar.download_button("⬇️ Exportar backup (.json)", data=db_json.encode("utf-8"), file_name="backup_sistema_vendas.json")
    if not is_visitante():
        up = st.sidebar.file_uploader("⬆️ Restaurar backup (.json)", type=["json"])
        if up is not None:
            try:
                data = json.load(up)
                prods = {int(k): v for k, v in data.get("produtos", {}).items()}
                clis = {k: v for k, v in data.get("clientes", {}).items()}
                st.session_state["produtos"] = prods
                st.session_state["clientes"] = clis
                save_db()
                st.sidebar.success("Backup restaurado!")
            except Exception as e:
                st.sidebar.error(f"Falha ao restaurar: {e}")
    else:
        st.sidebar.caption("🔒 Restauração apenas para usuários logados.")

def barra_lateral():
    st.sidebar.markdown(f"**Usuário:** {st.session_state.get('usuario', '')}")
    opcoes = {
        "Resumo 📊": tela_resumo,
        "Upload PDF 📄": tela_pdf,
        "Clientes 👥": tela_clientes,
        "Produtos 📦": tela_produtos,
        "Relatórios 📋": relatorio_geral,
    }
    if not is_visitante():
        opcoes["Backup 🗂️"] = bloco_backup_sidebar

    # Prevent selectbox index error if menu not in keys
    opcoes_lista = list(opcoes.keys())
    menu_atual = st.session_state.get("menu", "Resumo 📊")
    try:
        idx = opcoes_lista.index(menu_atual)
    except ValueError:
        idx = 0

    menu_selecionado = st.sidebar.selectbox("Menu", opcoes_lista, index=idx)
    st.session_state["menu"] = menu_selecionado
    func = opcoes.get(menu_selecionado)
    if func:
        func()
    elif menu_selecionado == "Sair 🚪":
        # não usamos essa rota por padrão; há botão abaixo
        pass

    st.sidebar.markdown("---")
    # Botão sair (seguro)
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.session_state["usuario"] = None
        st.rerun()

# ================== Main ==================
def main():
    if st.session_state.get("usuario") is None:
        login()
        st.stop()
    barra_lateral()

if __name__ == "__main__":
    main()