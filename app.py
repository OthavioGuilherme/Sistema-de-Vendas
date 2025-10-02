# ======== Parte 1: Ajustes no Backend/Conexão =================

# =================================================================
# CONFIGURAÇÕES (JÁ AJUSTADO PARA SEU NOME DA PLANILHA)
# =================================================================
PLANILHA_NOME = "Sistema de vendas"
ABA_VENDAS = "Vendas"                             
ABA_CLIENTES = "Clientes"                         
ABA_PRODUTOS = "Produtos" 
# ... (restante dos imports e configs) ...

# ================== Conexão Google Sheets & Sincronização ==================
GSHEETS_CONECTADO = False
gc = None

# FUNÇÃO 1: SINCRONIZAÇÃO DE DADOS PARA O SHEETS (GRAVAÇÃO)
def sync_to_gsheet(aba_nome: str, data: list):
    """Grava uma lista de dados no Sheets."""
    if not GSHEETS_CONECTADO:
        st.warning(f"Não conectado ao Google Sheets. Dados de {aba_nome} salvos apenas localmente.")
        return
    try:
        sh = gc.open(PLANILHA_NOME)
        aba = sh.worksheet(aba_nome)
        
        # Lógica de gravação:
        if aba_nome == ABA_VENDAS:
            # Vendas: Adiciona uma nova linha
            aba.append_row(data, value_input_option='USER_ENTERED')
        elif aba_nome == ABA_PRODUTOS:
            # Produtos: Limpa a aba e reescreve todos (mais simples para este modelo)
            aba.clear()
            # Define o cabeçalho
            aba.append_row(["Código", "Nome", "Preço", "Estoque"])
            # Formata os dados para escrita
            produtos_list = [[cod, p['nome'], p['preco'], p['quantidade']] 
                             for cod, p in st.session_state["produtos"].items()]
            aba.append_rows(produtos_list, value_input_option='USER_ENTERED')
        
    except SpreadsheetNotFound:
        st.error(f"❌ Planilha '{PLANILHA_NOME}' não encontrada no seu Drive.")
    except WorksheetNotFound:
        st.error(f"❌ Aba '{aba_nome}' não encontrada na planilha.")
    except Exception as e:
        st.error(f"❌ ERRO ao salvar no Sheets ({aba_nome}): {e}")

# FUNÇÃO 2: SINCRONIZAÇÃO DE DADOS DO SHEETS (LEITURA)
def sync_from_gsheet():
    """Carrega dados iniciais do Sheets para o session_state."""
    if not GSHEETS_CONECTADO:
        return
    try:
        sh = gc.open(PLANILHA_NOME)
        
        # Carregar Produtos
        aba_produtos = sh.worksheet(ABA_PRODUTOS)
        dados_produtos = aba_produtos.get_all_records()
        produtos = {}
        for row in dados_produtos:
            # Assume que as colunas são "Código", "Nome", "Preço", "Estoque"
            try:
                cod = int(row.get("Código"))
                produtos[cod] = {
                    "nome": str(row.get("Nome")).strip().title(),
                    "preco": float(row.get("Preço", 0.0)),
                    "quantidade": int(row.get("Estoque", 0))
                }
            except Exception:
                continue # Pula linhas inválidas ou cabeçalho
        
        if produtos:
             st.session_state["produtos"] = produtos
             st.success("✅ Produtos carregados do Google Sheets!")
        
    except Exception as e:
        st.warning(f"⚠️ Falha ao carregar dados do Sheets: {e}")

def connect_gsheet():
    global gc, GSHEETS_CONECTADO
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_info(dict(creds_dict), scopes=scopes)
        gc = gspread.authorize(credentials)
        GSHEETS_CONECTADO = True
        
        # CHAMA A SINCRONIZAÇÃO APÓS A CONEXÃO
        sync_from_gsheet() 
        
    except KeyError:
        st.error("❌ Chave 'gcp_service_account' não encontrada nos Secrets")
        st.info("Rodando apenas localmente.")
    except Exception as e:
        st.error(f"❌ ERRO FATAL AO CONECTAR: {type(e).__name__} - {e}")
        st.info("Verifique o JSON e permissões da Conta de Serviço.")

connect_gsheet() # Chama a conexão e a sincronização inicial
# ... (restante do código até o início da Parte 2) ...

# ... (Funções anteriores) ...

def adicionar_produto_manual(cod, nome, preco, qtd=10):
    cod = int(cod)
    produto_data = {
        "nome": nome.strip(),
        "preco": float(preco),
        "quantidade": qtd
    }
    st.session_state["produtos"][cod] = produto_data
    save_db() # Salva localmente
    
    # 🌟 CORREÇÃO 1: Salvar Produtos no Sheets
    sync_to_gsheet(ABA_PRODUTOS, []) # Usa a função que reescreve todos
    
    st.success(f"Produto {nome} adicionado/atualizado!")

# ... (Função tela_produtos - sem alteração significativa) ...

# ... (Funções de Clientes) ...

def registrar_venda(cliente, codigo, quantidade):
    produtos = st.session_state["produtos"]
    if codigo not in produtos:
        st.error("Produto não encontrado.")
        return
    # ... (verificação de estoque e outras lógicas) ...
    
    venda_data = {
        "codigo": codigo,
        "nome": produtos[codigo]["nome"],
        "preco": produtos[codigo]["preco"],
        "quantidade": quantidade,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    produtos[codigo]["quantidade"] -= quantidade
    st.session_state["clientes"][cliente].append(venda_data)
    save_db() # Salva localmente
    
    # 🌟 CORREÇÃO 1: Salvar Vendas no Sheets
    # Formato da linha para o Sheets: [Cliente, Código, Nome, Preço, Quantidade, Data]
    linha_venda = [cliente, codigo, venda_data["nome"], venda_data["preco"], 
                   venda_data["quantidade"], venda_data["data"]]
    sync_to_gsheet(ABA_VENDAS, linha_venda) 
    
    # 🌟 Sincroniza a atualização de estoque (Produto)
    sync_to_gsheet(ABA_PRODUTOS, [])
    
    st.success("Venda registrada!")

# Função para filtrar produtos (CORREÇÃO 3)
def autocomplete_vendas(input_cod):
    """Filtra a lista de produtos com base no código digitado."""
    input_cod = str(input_cod).strip()
    if len(input_cod) < 2: # 🌟 CORREÇÃO 3: Inicia a busca após 2 dígitos
        return []

    opcoes_encontradas = []
    for cod, dados in st.session_state["produtos"].items():
        cod_str = str(cod)
        # Filtra se o código digitado for o início do código do produto
        if cod_str.startswith(input_cod):
            # Formata a string de exibição: "CÓDIGO - NOME (R$ PREÇO)"
            opcoes_encontradas.append(f"{cod} - {dados['nome']} (R$ {dados['preco']:.2f})")
    return opcoes_encontradas


def tela_vendas():
    st.header("🛒 Vendas")
    if not st.session_state["clientes"]:
        st.warning("Cadastre um cliente primeiro.")
        return
    if not st.session_state["produtos"]:
        st.warning("Cadastre produtos primeiro.")
        return

    # 🌟 CORREÇÃO 3: Alteração para autocompletar dinâmico (Input + Select)
    cliente = st.selectbox("Selecione o cliente", list(st.session_state["clientes"].keys()))
    
    col1, col2 = st.columns([3, 1])
    
    # Entrada de texto para buscar o código
    codigo_input = col1.text_input("Digite o Código do produto (mín. 2 dígitos)", key="venda_cod_input")

    # Obtém as opções filtradas
    opcoes = autocomplete_vendas(codigo_input)
    
    # Se encontrou opções, mostra o SelectBox (o usuário deve selecionar)
    if opcoes:
        produto_selecionado_str = col1.selectbox("Selecione o produto", opcoes, key="venda_produto_select")
        # Extrai o código (o primeiro número da string)
        try:
            codigo = int(produto_selecionado_str.split(' - ')[0])
        except:
            codigo = None # Caso a string não esteja formatada
    else:
        produto_selecionado_str = None
        codigo = None # Nenhum código válido selecionado ou encontrado

    # Quantidade na coluna 2
    quantidade = col2.number_input("Quantidade", min_value=1, step=1)
    
    # ----------------------------------------------------------------------

    if st.button("Registrar venda"):
        if codigo is None:
            st.error("Por favor, digite um código válido e selecione o produto na lista.")
        else:
            registrar_venda(cliente, codigo, quantidade)

    # ... (Histórico de vendas) ...

# ... (Relatórios) ...

# 🌟 CORREÇÃO 2: Alteração do Menu (Lateral para Superior)
def menu():
    # 🌟 Substitui st.sidebar.radio por st.tabs() para menu superior
    opcoes = ["Resumo 📊", "Produtos 📦", "Clientes 👥", "Vendas 🛒", "Relatórios 📑", "Sair 🚪"]
    
    # Cria o menu superior como abas
    aba_resumo, aba_produtos, aba_clientes, aba_vendas, aba_relatorios, aba_sair = st.tabs(opcoes)

    with aba_resumo:
        tela_resumo()
    with aba_produtos:
        tela_produtos()
    with aba_clientes:
        tela_clientes()
    with aba_vendas:
        tela_vendas()
    with aba_relatorios:
        tela_relatorios()
    with aba_sair:
        st.header("Sair do Sistema")
        if st.button("Confirmar saída"):
            st.session_state.clear()
            st.rerun()

# ================== Main ==================
def main():
    init_db()
    
    # Move a exibição do usuário para o topo, antes do menu
    if st.session_state.get("usuario"):
        st.sidebar.title("📌 Sistema de Vendas")
        st.sidebar.write(f"👤 **Logado:** {st.session_state['usuario']}")
        
    if not st.session_state.get("usuario"):
        login()
    else:
        # 🌟 O menu agora é superior
        menu()

if __name__ == "__main__":
    main()
