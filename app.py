# ==========================
# Parte 1 - Configuração, Banco e Utilitários (com lembrar login)
# ==========================

import streamlit as st
from datetime import datetime
import json
import os
from PIL import Image
import pytesseract

# =============== Config página ===============
st.set_page_config(page_title="Sistema de Vendas", page_icon="🧾", layout="wide")

# =============== Arquivos ===============
LOG_FILE = "acessos.log"
DB_FILE = "db.json"
LOGIN_FILE = "login_salvo.json"  # arquivo para salvar login

# =============== Usuários ==================
USERS = {
    "othavio": "122008",
    "isabela": "122008",
}

# ================= Funções =================
def registrar_acesso(label: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {label}\n")
    except Exception:
        pass

def is_visitante():
    return bool(st.session_state.get("usuario")) and str(st.session_state.get("usuario")).startswith("visitante-")

# ================= Persistência JSON =================
def save_db():
    try:
        data = {
            "produtos": st.session_state.produtos,
            "clientes": st.session_state.clientes,
            "vendas": st.session_state.vendas,
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
            clis = {k: v for k, v in data.get("clientes", {}).items()}
            vendas = data.get("vendas", [])
            return prods, clis, vendas
        except Exception:
            pass
    return {}, {}, []

def save_login(usuario):
    try:
        with open(LOGIN_FILE, "w", encoding="utf-8") as f:
            json.dump({"usuario": usuario}, f)
    except:
        pass

def load_login():
    if os.path.exists(LOGIN_FILE):
        try:
            with open(LOGIN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("usuario", "")
        except:
            return ""
    return ""

# =============== Session state inicial =================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "produtos" not in st.session_state or "clientes" not in st.session_state or "vendas" not in st.session_state:
    p, c, v = load_db()
    st.session_state.produtos = p
    st.session_state.clientes = c
    st.session_state.vendas = v

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "filtro_cliente" not in st.session_state:
    st.session_state.filtro_cliente = ""
if "menu" not in st.session_state:
    st.session_state.menu = "Resumo"

# ================= Helpers =================
def total_cliente(nome: str) -> float:
    vendas = st.session_state.clientes.get(nome, [])
    return sum(v["preco"] * v["quantidade"] for v in vendas)

def total_geral() -> float:
    return sum(total_cliente(c) for c in st.session_state.clientes.keys())

# ================= Login =================
def tela_login():
    st.title("🔑 Login")

    usuario_salvo = load_login()

    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuário", value=usuario_salvo, key="usuario_input")
        senha = st.text_input("Senha", type="password", key="senha_input")
        lembrar = st.checkbox("Lembrar meu login")

        if st.button("Entrar"):
            if usuario.strip() in USERS and senha.strip() == USERS[usuario.strip()]:
                st.session_state.usuario = usuario.strip()
                st.session_state.logado = True
                registrar_acesso(f"Login - {usuario}")
                if lembrar:
                    save_login(usuario.strip())
                st.success(f"Bem-vindo {usuario}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos")

    with col2:
        st.write("Ou entre como visitante")
        if st.button("Entrar como visitante"):
            st.session_state.usuario = f"visitante-{int(datetime.now().timestamp())}"
            st.session_state.logado = True
            st.info("Você entrou como visitante (apenas leitura)")
            st.experimental_rerun()
# ========================== 
# ===============================
# PARTE 2 - Produtos e Vendas
# --------- Dependências necessárias (já presentes no seu app Parte 2) ----------
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import numpy as np
import cv2
import re
from datetime import datetime

# Ajuste (opcional) onde está o tesseract no ambiente:
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ----------------- Helpers de session-safe (compatibilidade db / produtos) -----------------
def _get_produtos_dict():
    # retorna dict onde keys são strings (seguro) -> {"4685": {"nome":..., "preco":...}, ...}
    if "produtos" in st.session_state and isinstance(st.session_state.produtos, dict):
        return {str(k): v for k, v in st.session_state.produtos.items()}
    if "db" in st.session_state and isinstance(st.session_state.db.get("produtos", {}), dict):
        return {str(k): v for k, v in st.session_state.db.get("produtos", {}).items()}
    return {}

def _save_produto(codigo_str, produto_obj):
    # salva em ambos lugares para compatibilidade
    if "produtos" in st.session_state and isinstance(st.session_state.produtos, dict):
        st.session_state.produtos[codigo_str] = produto_obj
    if "db" in st.session_state and isinstance(st.session_state.db.get("produtos", {}), dict):
        st.session_state.db["produtos"][codigo_str] = produto_obj
    # tente chamar save_db se estiver definido (Parte1)
    try:
        save_db()
    except Exception:
        # caso save_db não exista, ignore
        pass

def _append_venda(venda_obj):
    if "vendas" in st.session_state and isinstance(st.session_state.vendas, list):
        st.session_state.vendas.append(venda_obj)
    if "db" in st.session_state and isinstance(st.session_state.db.get("vendas", []), list):
        st.session_state.db.setdefault("vendas", []).append(venda_obj)
    try:
        save_db()
    except Exception:
        pass

# ----------------- Pré-processamento robusto -----------------
def _preprocess_for_ocr(pil_img, scale=2):
    # pil_img = PIL.Image
    img = pil_img.convert("RGB")
    # aumentar resolução
    w, h = img.size
    img = img.resize((int(w*scale), int(h*scale)), Image.BICUBIC)

    # converter para grayscale
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

    # filtro bilateral reduz ruído mantendo bordas
    gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    # equalizar contraste (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # tentativa de deskew (corrigir rotação leve)
    coords = np.column_stack(np.where(gray < 255))
    angle = 0.0
    if coords.size:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        # rotaciona somente se ângulo significativo
        if abs(angle) > 1:
            (h2, w2) = gray.shape
            center = (w2 // 2, h2 // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            gray = cv2.warpAffine(gray, M, (w2, h2), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # adaptive threshold (melhora fundo irregular)
    try:
        th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 15)
    except Exception:
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # pequeno closing para juntar letras quebradas
    kernel = np.ones((2,2), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)

    return Image.fromarray(th)

# ----------------- Função que tenta OCR com várias configs e retorna melhores candidatos ----------
def _ocr_attempts_and_candidates(pil_img):
    # retorna lista de tuples (config, text, data_dict)
    configs = [
        "--oem 3 --psm 6",   # assume um bloco de texto
        "--oem 3 --psm 11",  # sparse text
        "--oem 3 --psm 3",   # fully automatic
    ]
    results = []
    for cfg in configs:
        try:
            text = pytesseract.image_to_string(pil_img, lang="por", config=cfg)
            data = pytesseract.image_to_data(pil_img, lang="por", config=cfg, output_type=pytesseract.Output.DICT)
        except Exception as e:
            text = ""
            data = {"text":[],"conf":[]}
        results.append((cfg, text, data))
    # a seguir, extraímos candidatos analisando textos e tokens
    all_texts = " \n ".join([r[1] for r in results])
    # gather word-level candidates with confidences
    tokens = []
    for _, _, data in results:
        words = data.get("text", [])
        confs = data.get("conf", [])
        for w, c in zip(words, confs):
            try:
                conf_val = int(float(c))
            except:
                conf_val = -1
            tokens.append((w.strip(), conf_val))
    return results, all_texts, tokens

# ----------------- Extração robusta de código e preço -----------------
def _extract_ref_and_price(all_text, tokens):
    # Priorize 'Ref' no texto (ex: "Ref: 4685" ou "Ref 4685")
    ref = None
    m = re.search(r"Ref[:\s]*0*([0-9]{3,6})", all_text, re.IGNORECASE)
    if m:
        ref = m.group(1)
        # remove zeros à esquerda se quiser: ref = str(int(ref))
    # procurar padrão Sxxxx (S5295 -> 52.95)
    preco = None
    m2 = re.search(r"\bS\s*0*([0-9]{2,})([0-9]{2})\b", all_text, re.IGNORECASE)
    if m2:
        parte1 = m2.group(1)
        parte2 = m2.group(2)
        try:
            preco = float(f"{int(parte1)}.{int(parte2):02d}")
        except:
            preco = None
    # fallback: procurar valores com vírgula/ponto (ex: 52,95)
    if preco is None:
        m3 = re.search(r"(\d{1,3}[.,]\d{2})", all_text)
        if m3:
            preco = float(m3.group(1).replace(",", "."))
    # fallback tokens: procurar token "S5295" com alta confiança
    if preco is None:
        for tok, conf in tokens:
            if conf >= 50:
                m4 = re.match(r"^S\s*0*([0-9]{3,})([0-9]{2})$", tok, re.IGNORECASE)
                if m4:
                    preco = float(f"{int(m4.group(1))}.{int(m4.group(2))}")
                    break
    # se ainda não encontrou ref, tentar tokens numéricos com alta confiança (p.ex. '4685')
    if ref is None:
        for tok, conf in tokens:
            if conf >= 60 and re.fullmatch(r"\d{3,6}", tok):
                ref = tok
                break

    return ref, preco

# ----------------- Tela principal (substitua a sua atual) -----------------
def tela_registrar_venda_foto():
    st.title("📷 Registrar Venda por Foto (OCR melhorado)")

    # 1) selecionar / cadastrar cliente
    clientes_dict = st.session_state.get("clientes", {})
    nomes = list(clientes_dict.keys())
    modo = st.radio("Cliente:", ["Selecionar existente", "Cadastrar novo"], horizontal=True)
    cliente = None
    if modo == "Selecionar existente":
        if not nomes:
            st.info("Nenhum cliente cadastrado. Cadastre um novo.")
        else:
            cliente = st.selectbox("Selecione cliente", nomes)
    else:
        novo = st.text_input("Nome do novo cliente")
        if st.button("Cadastrar cliente"):
            if novo.strip():
                st.session_state.setdefault("clientes", {})[novo.strip()] = []
                st.success(f"Cliente {novo.strip()} cadastrado.")
                cliente = novo.strip()
                # evite rerun para manter upload etc.

    if cliente is None:
        st.info("Selecione ou cadastre um cliente antes de enviar fotos.")
        return

    st.write("---")
    uploaded_files = st.file_uploader("Envie até 10 fotos da etiqueta (prefira sem plástico/reflexo)", accept_multiple_files=True, type=["jpg","jpeg","png"])
    if not uploaded_files:
        return
    if len(uploaded_files) > 10:
        st.warning("Foram selecionadas mais de 10 fotos — apenas as 10 primeiras serão processadas.")
        uploaded_files = uploaded_files[:10]

    produtos = _get_produtos_dict()

    # carrinho temporário local
    carrinho_local = st.session_state.get("carrinho_foto", [])

    for idx, file in enumerate(uploaded_files):
        st.markdown(f"### Foto {idx+1}: {file.name}")
        pil_img = Image.open(file)
        st.image(pil_img, caption="Original", width=300)

        # Pré-processar
        proc = _preprocess_for_ocr(pil_img, scale=2)
        st.image(proc, caption="Pré-processada (para OCR)", width=300)

        # OCR várias tentativas
        results, all_text, tokens = _ocr_attempts_and_candidates(proc)

        # Mostrar resultados dos attempts (útil para debug)
        with st.expander("Resultados OCR (tentativas)"):
            for cfg, text, data in results:
                st.write(f"Config: {cfg}")
                st.text_area("Texto:", text, height=120)

        # Extrair candidatos
        codigo_cand, preco_cand = _extract_ref_and_price(all_text, tokens)

        st.info(f"Candidatos -> Código: {codigo_cand} | Preço: {preco_cand if preco_cand else 'não detectado'}")

        # Permitir seleção/correção manual
        codigo_input = st.text_input(f"Código detectado (Foto {idx+1})", value=codigo_cand if codigo_cand else "", key=f"cod_user_{idx}")
        preco_input = st.text_input(f"Preço detectado (R$) (Foto {idx+1})", value=f"{preco_cand:.2f}" if preco_cand else "", key=f"pre_user_{idx}")
        nome_input = st.text_input(f"Nome do produto (opcional) (Foto {idx+1})", value="", key=f"nome_user_{idx}")

        # Botão para adicionar ao carrinho local
        if st.button(f"Adicionar foto {idx+1} ao carrinho", key=f"add_btn_{idx}"):
            # validações básicas
            if not codigo_input:
                st.error("Informe um código antes de adicionar.")
            else:
                # normalizar código como string
                codigo_str = str(codigo_input).strip()
                # preço
                try:
                    preco_float = float(preco_input.replace(",", "."))
                except:
                    preco_float = None
                # se produto cadastrado, pegar nome/preço do cadastro (prioridade)
                produto_cadastrado = produtos.get(codigo_str)
                if produto_cadastrado:
                    nome_final = produto_cadastrado.get("nome", nome_input or produto_cadastrado.get("nome","Produto"))
                    preco_final = produto_cadastrado.get("preco", preco_float if preco_float else 0.0)
                else:
                    nome_final = nome_input if nome_input else f"Produto {codigo_str}"
                    if preco_float:
                        preco_final = preco_float
                    else:
                        st.error("Produto não cadastrado e preço não informado. Preencha o preço ou cadastre o produto.")
                        continue

                # se não cadastrado, guardar no produtos (opcional)
                if codigo_str not in produtos:
                    produtos[codigo_str] = {"nome": nome_final, "preco": preco_final}
                    _save_produto(codigo_str, produtos[codigo_str])
                    st.success(f"Produto {nome_final} cadastrado automaticamente.")

                # adicionar ao carrinho local
                item = {"codigo": codigo_str, "nome": nome_final, "preco": float(preco_final), "quantidade": 1}
                carrinho_local = st.session_state.get("carrinho_foto", [])
                carrinho_local.append(item)
                st.session_state.carrinho_foto = carrinho_local
                st.success(f"Item adicionado ao carrinho: {nome_final} - R$ {preco_final:.2f}")

    # Mostrar carrinho e permitir finalizar
    st.write("---")
    st.subheader("Carrinho (Fotos)")
    carrinho_local = st.session_state.get("carrinho_foto", [])
    if not carrinho_local:
        st.info("Carrinho vazio. Adicione itens das fotos acima.")
        return
    total = 0.0
    for i, it in enumerate(carrinho_local):
        st.write(f"{i+1}. {it['nome']} (Ref {it['codigo']}) - R$ {it['preco']:.2f} x {it.get('quantidade',1)}")
        total += it['preco'] * it.get('quantidade',1)
        if st.button(f"Remover item {i+1}", key=f"rem_cart_{i}"):
            carrinho_local.pop(i)
            st.session_state.carrinho_foto = carrinho_local
            st.experimental_rerun()

    st.write(f"**Total parcial: R$ {total:.2f}**")
    if st.button("Finalizar venda (itens do carrinho)"):
        venda = {
            "cliente": cliente,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "produtos": carrinho_local.copy(),
            "total": total
        }
        _append_venda(venda)
        st.session_state.carrinho_foto = []
        st.success("Venda registrada com sucesso!")
        st.experimental_rerun()
# ==========================
# Parte 3 - Barra lateral, login e roteamento
# ==========================

import streamlit as st

# ---------------- Função de login ----------------
def tela_login():
    st.title("🔐 Login")
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")
    visitante_input = st.checkbox("Entrar como visitante (somente leitura)")

    if st.button("Entrar"):
        if visitante_input:
            st.session_state.usuario = f"visitante-{datetime.now().strftime('%H%M%S')}"
            st.session_state.logado = True
            st.success("Entrou como visitante")
            registrar_acesso(f"Visitante entrou: {st.session_state.usuario}")
            st.rerun()
        elif usuario_input in USERS and USERS[usuario_input] == senha_input:
            st.session_state.usuario = usuario_input
            st.session_state.logado = True
            st.success(f"Bem-vindo {usuario_input}!")
            registrar_acesso(f"Login: {usuario_input}")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")


# ---------------- Barra lateral ----------------
def barra_lateral():
    st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario}")

    opcoes = [
        "Resumo",
        "Registrar venda por foto",
        "Clientes",
        "Produtos",
        "Relatórios",
        "Sair"
    ]
    if not is_visitante():
        opcoes.insert(-1, "Acessos")

    idx_atual = opcoes.index(st.session_state.menu) if st.session_state.menu in opcoes else 0
    st.session_state.menu = st.sidebar.radio("Menu", opcoes, index=idx_atual)


# ---------------- Função principal ----------------
def main():
    if "logado" not in st.session_state:
        st.session_state.logado = False
    if "menu" not in st.session_state:
        st.session_state.menu = "Resumo"

    if not st.session_state.logado:
        tela_login()
    else:
        barra_lateral()
        menu = st.session_state.menu

        if menu == "Resumo":
            tela_resumo()
        elif menu == "Registrar venda por foto":
            tela_registrar_venda_foto()
        elif menu == "Clientes":
            tela_clientes()
        elif menu == "Produtos":
            tela_produtos()
        elif menu == "Relatórios":
            tela_relatorios()
        elif menu == "Acessos" and not is_visitante():
            tela_acessos()
        elif menu == "Sair":
            st.session_state.logado = False
            st.session_state.usuario = None
            st.rerun()


# ----------------- Start App -----------------
if __name__ == "__main__":
    # Inicializar listas de vendas, produtos e clientes se não existirem
    if "vendas" not in st.session_state:
        st.session_state.vendas = []
    if "produtos" not in st.session_state:
        st.session_state.produtos = {}
    if "clientes" not in st.session_state:
        st.session_state.clientes = {}

    main()