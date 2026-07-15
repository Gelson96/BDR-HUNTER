import streamlit as st
import pandas as pd
import requests
import re
import time
import math

# 1. Configuração da Página
st.set_page_config(page_title="BDR Hunter Pro | Gelson96", layout="wide", page_icon="🚀")

URL_LOGO = "https://static.wixstatic.com/media/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png/v1/fill/w_232,h_67,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png"

# --- CONFIGURAÇÃO DE APIs ---
HUNTER_API_KEY = "ade32d411c5065d4f61d89a27b4b80018b62647a"
APOLLO_API_KEY = "cSG2GJRmKBGpdGpNykMJuA"
SNOV_USER_ID = "3339dd3a641d4a40440040bdf815c895"
SNOV_API_SECRET = "66325b5f11c5e6708f2ffeb01d6f85e8"

# Cabeçalho usado nas chamadas HTTP (a BrasilAPI, em especial, costuma
# recusar/limitar requisições sem um User-Agent identificável)
HTTP_HEADERS = {
    "User-Agent": "BDR-Hunter-Pro/1.0 (+https://gelsonvallim.com)",
    "Accept": "application/json",
}

# --- CIDADE BASE (origem para cálculo de distância) ---
CIDADE_BASE_NOME = "Aguaí"
CIDADE_BASE_UF = "SP"
CIDADE_BASE_LAT = -22.0577
CIDADE_BASE_LON = -46.9739

# --- CSS COMPLETO ---
st.markdown(
    f"""
    <style>
    .centered-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; }}
    .centered-container img {{ width: 400px; margin-bottom: 10px; }}
    h1, h2, h3, .stSubheader {{ text-align: center !important; width: 100%; }}
    
    .potencial-box {{ 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 20px 0;
    }}
    .potencial-valor {{
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }}
    .sucesso-box {{
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }}
    .info-box {{
        background: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }}
    .alerta-box {{
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }}
    .erro-box {{
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }}
    
    /* Estilos Lusha */
    .contact-card {{
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .contact-card:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }}
    .contact-header {{
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 2px solid #f0f0f0;
    }}
    .contact-avatar {{
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        font-weight: bold;
        margin-right: 16px;
        flex-shrink: 0;
    }}
    .contact-info {{
        flex: 1;
    }}
    .contact-name {{
        font-size: 20px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0 0 4px 0;
    }}
    .contact-title {{
        font-size: 14px;
        color: #666;
        margin: 0;
    }}
    .contact-details {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin-top: 16px;
    }}
    .detail-item {{
        display: flex;
        align-items: center;
        padding: 12px;
        background: #f8f9fa;
        border-radius: 8px;
    }}
    .detail-icon {{
        font-size: 18px;
        margin-right: 12px;
    }}
    .detail-label {{
        font-size: 11px;
        color: #666;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 4px;
    }}
    .detail-value {{
        font-size: 14px;
        color: #1a1a1a;
        font-weight: 500;
    }}
    .confidence-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }}
    .source-badge {{
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        background: #e3f2fd;
        color: #1976d2;
        margin-left: 8px;
    }}
    .stats-container {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 24px 0;
    }}
    .stat-card {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }}
    .stat-number {{
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 8px;
    }}
    .stat-label {{
        font-size: 14px;
        opacity: 0.9;
    }}
    </style>
    <div class="centered-container"><img src="{URL_LOGO}"></div>
    """,
    unsafe_allow_html=True
)

st.title("BDR Hunter Pro")
st.subheader("Inteligência de Mercado & Prospecção Estratégica")
st.divider()

# --- FUNÇÕES CNPJ ---
def extrair_cnpjs(texto):
    """Extrai CNPJs do texto, com ou sem pontuação"""
    cnpjs = []
    
    # Padrão 1: CNPJ formatado (XX.XXX.XXX/XXXX-XX)
    formatados = re.findall(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', texto)
    for cnpj in formatados:
        # Remove pontuação
        cnpj_limpo = re.sub(r'\D', '', cnpj)
        if len(cnpj_limpo) == 14:
            cnpjs.append(cnpj_limpo)
    
    # Padrão 2: CNPJ sem formatação (14 dígitos seguidos)
    sem_formatacao = re.findall(r'\b\d{14}\b', texto)
    for cnpj in sem_formatacao:
        if cnpj not in cnpjs:  # Evita duplicatas
            cnpjs.append(cnpj)
    
    return cnpjs

def limpar_nome_empresa(nome):
    if not nome: return ""
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def processar_inteligencia_premium(d):
    porte_cod = d.get('porte')
    cap = d.get('capital_social', 0)
    
    if porte_cod in [5, "05"] or cap > 10000000:
        return "GRANDE", "100M+*", "500+*", None, None
    
    if porte_cod in [1, "01"]: 
        return "PEQUENO (ME)", "Até R$ 360k*", "1-9*", 0, 360000
    elif porte_cod in [3, "03"]: 
        return "PEQUENO (EPP)", "R$ 360k-4,8M*", "10-49*", 360000, 4800000
    else:
        if cap > 1000000: 
            return "MÉDIO", "R$ 10M-50M*", "100-250*", 10000000, 50000000
        else: 
            return "MÉDIO", "R$ 4,8M+*", "50+*", 4800000, 10000000

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def geocodificar_cidade(municipio, uf, pais="Brasil"):
    """
    Geocodifica uma cidade brasileira usando a Nominatim (OpenStreetMap), que é
    gratuita e não exige chave de API. Resultado é cacheado por 24h para evitar
    requisições repetidas para a mesma cidade (respeitando o limite de uso da
    Nominatim de ~1 requisição por segundo).
    Retorna (lat, lon) ou (None, None) se não encontrar.
    """
    if not municipio:
        return None, None
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "city": municipio,
            "state": uf,
            "country": pais,
            "format": "json",
            "limit": 1,
        }
        res = requests.get(url, params=params, headers=HTTP_HEADERS, timeout=10)
        if res.status_code == 200:
            resultados = res.json()
            if resultados:
                return float(resultados[0]["lat"]), float(resultados[0]["lon"])
        return None, None
    except Exception:
        return None, None

def calcular_distancia_km(lat1, lon1, lat2, lon2):
    """Distância em linha reta (haversine) entre duas coordenadas, em km.
    Usada apenas como fallback quando o cálculo de rota (OSRM) falha."""
    R = 6371  # raio médio da Terra em km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def calcular_distancia_rodoviaria_km(lat1, lon1, lat2, lon2):
    """
    Calcula a distância rodoviária (por estrada) entre dois pontos usando o
    OSRM (Open Source Routing Machine), servidor público de demonstração,
    gratuito e sem necessidade de chave de API. O resultado é bem mais
    próximo do que o Google Maps mostra do que uma distância em linha reta.
    Retorna (distancia_km, duracao_horas) ou (None, None) se a rota falhar.
    """
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
        params = {"overview": "false"}
        res = requests.get(url, params=params, headers=HTTP_HEADERS, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == "Ok" and data.get("routes"):
                rota = data["routes"][0]
                distancia_km = rota["distance"] / 1000
                duracao_horas = rota["duration"] / 3600
                return distancia_km, duracao_horas
        return None, None
    except Exception:
        return None, None

def verificar_situacao_especial(d):
    razao = d.get('razao_social', '').upper()
    sit_especial = d.get('situacao_especial', '').upper()
    
    if "RECUPERACAO JUDICIAL" in razao or "RECUPERACAO JUDICIAL" in sit_especial:
        return "⚠️ RECUPERAÇÃO JUDICIAL"
    if d.get('descricao_situacao_cadastral') != "ATIVA":
        return f"🚫 {d.get('descricao_situacao_cadastral')}"
    return "✅ REGULAR"

def _requisitar(url, timeout=15):
    """Executa um GET simples e devolve (json, status_code, erro_de_conexao)."""
    try:
        res = requests.get(url, headers=HTTP_HEADERS, timeout=timeout)
    except requests.exceptions.Timeout:
        return None, None, "timeout"
    except requests.exceptions.ConnectionError:
        return None, None, "connection_error"
    except requests.exceptions.RequestException as e:
        return None, None, f"request_error: {e}"

    if res.status_code == 200:
        try:
            return res.json(), 200, None
        except ValueError:
            return None, 200, "invalid_json"
    return None, res.status_code, None


def _consultar_brasilapi(cnpj, tentativas=3):
    """
    Consulta a BrasilAPI com retry automático (com espera progressiva) para
    erros transitórios do servidor (500/502/503/504), que são comuns nessa API
    pois ela faz proxy da base da Receita Federal.
    Retorna (dados, motivo_erro).
    """
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    ultimo_status = None
    ultimo_erro = None

    for tentativa in range(1, tentativas + 1):
        dados, status, erro_conexao = _requisitar(url)

        if dados is not None:
            return dados, None

        ultimo_status = status
        ultimo_erro = erro_conexao

        # Erros permanentes: não adianta tentar de novo
        if status == 404:
            return None, "CNPJ não encontrado na base da Receita Federal"
        if status == 429:
            return None, "Limite de requisições da BrasilAPI atingido (aguarde alguns segundos e tente novamente)"

        # Erros transitórios (5xx) ou de conexão/timeout: espera e tenta de novo
        if tentativa < tentativas:
            time.sleep(1.5 * tentativa)  # espera progressiva: 1.5s, 3s, ...

    if ultimo_erro == "timeout":
        return None, "Tempo de resposta esgotado (timeout) na BrasilAPI, mesmo após novas tentativas"
    if ultimo_erro == "connection_error":
        return None, "Falha de conexão com a BrasilAPI após novas tentativas"
    if ultimo_erro == "invalid_json":
        return None, "A BrasilAPI retornou uma resposta que não é um JSON válido"
    if ultimo_status:
        return None, f"BrasilAPI retornou status HTTP {ultimo_status} (mesmo após {tentativas} tentativas)"
    return None, "Falha desconhecida ao consultar a BrasilAPI"


def _consultar_minhareceita(cnpj):
    """
    Fallback: minhareceita.org usa a mesma estrutura de campos da BrasilAPI
    (ambas derivam dos dados públicos da Receita Federal), então serve como
    alternativa quando a BrasilAPI está instável.
    """
    url = f"https://minhareceita.org/{cnpj}"
    dados, status, erro_conexao = _requisitar(url, timeout=20)

    if dados is not None:
        return dados, None
    if status == 404:
        return None, "CNPJ não encontrado (minhareceita.org)"
    if erro_conexao:
        return None, f"minhareceita.org também falhou ({erro_conexao})"
    if status:
        return None, f"minhareceita.org também retornou status HTTP {status}"
    return None, "Falha desconhecida ao consultar minhareceita.org"


def _normalizar_cnpjws(d):
    """Converte a resposta do publica.cnpj.ws para o mesmo formato usado pela BrasilAPI."""
    est = d.get('estabelecimento') or {}
    ativ_principal = est.get('atividade_principal') or {}
    estado = est.get('estado') or {}
    cidade = est.get('cidade') or {}
    porte = d.get('porte') or {}

    return {
        'razao_social': d.get('razao_social'),
        'nome_fantasia': est.get('nome_fantasia'),
        'porte': porte.get('id'),
        'capital_social': float(d.get('capital_social') or 0),
        'cnae_fiscal_descricao': ativ_principal.get('descricao', 'N/I'),
        'municipio': cidade.get('nome'),
        'uf': estado.get('sigla'),
        'logradouro': est.get('logradouro'),
        'numero': est.get('numero'),
        'identificador_matriz_filial': 1 if est.get('tipo') == 'Matriz' else 2,
        'descricao_situacao_cadastral': (est.get('situacao_cadastral') or '').upper(),
        'situacao_especial': est.get('situacao_especial') or '',
    }


def _consultar_cnpjws(cnpj):
    """Fallback adicional: API pública do cnpj.ws (limite de 3 consultas/min)."""
    url = f"https://publica.cnpj.ws/cnpj/{cnpj}"
    dados, status, erro_conexao = _requisitar(url, timeout=20)

    if dados is not None:
        try:
            return _normalizar_cnpjws(dados), None
        except Exception as e:
            return None, f"cnpj.ws retornou dados em formato inesperado: {e}"
    if status == 404:
        return None, "CNPJ não encontrado (cnpj.ws)"
    if status == 429:
        return None, "Limite de requisições do cnpj.ws atingido (3/min)"
    if erro_conexao:
        return None, f"cnpj.ws também falhou ({erro_conexao})"
    if status:
        return None, f"cnpj.ws também retornou status HTTP {status}"
    return None, "Falha desconhecida ao consultar cnpj.ws"


_MAPA_PORTE_OPENCNPJ = {
    "microempresa (me)": "01",
    "empresa de pequeno porte (epp)": "03",
    "demais": "05",
}

def _normalizar_opencnpj(d):
    """Converte a resposta do OpenCNPJ (schema real: snake_case, capital_social
    com vírgula decimal, porte como texto) para o mesmo formato usado pela BrasilAPI."""
    capital_str = str(d.get('capital_social') or '0').replace('.', '').replace(',', '.')
    try:
        capital = float(capital_str)
    except ValueError:
        capital = 0.0

    porte_texto = (d.get('porte_empresa') or '').strip().lower()
    porte_cod = _MAPA_PORTE_OPENCNPJ.get(porte_texto)  # None se não reconhecido

    return {
        'razao_social': d.get('razao_social'),
        'nome_fantasia': d.get('nome_fantasia') or d.get('razao_social'),
        'porte': porte_cod,
        'capital_social': capital,
        'cnae_fiscal_descricao': d.get('cnae_principal_descricao', 'N/I'),
        'municipio': d.get('municipio'),
        'uf': d.get('uf'),
        'logradouro': d.get('logradouro', ''),
        'numero': d.get('numero', ''),
        'identificador_matriz_filial': 1 if d.get('matriz_filial', '').upper() == 'MATRIZ' else 2,
        'descricao_situacao_cadastral': (d.get('situacao_cadastral') or '').upper(),
        'situacao_especial': d.get('situacao_especial') or '',
    }


def _consultar_opencnpj(cnpj):
    """Último fallback: OpenCNPJ — projeto open source, base atualizada
    mensalmente a partir dos dados públicos da Receita Federal, sem
    autenticação e com limite de até 50 requisições/segundo por IP."""
    url = f"https://api.opencnpj.org/{cnpj}"
    dados, status, erro_conexao = _requisitar(url, timeout=20)

    if dados is not None:
        try:
            return _normalizar_opencnpj(dados), None
        except Exception as e:
            return None, f"OpenCNPJ retornou dados em formato inesperado: {e}"
    if status == 404:
        return None, "CNPJ não encontrado (OpenCNPJ)"
    if erro_conexao:
        return None, f"OpenCNPJ também falhou ({erro_conexao})"
    if status:
        return None, f"OpenCNPJ também retornou status HTTP {status}"
    return None, "Falha desconhecida ao consultar OpenCNPJ"


def consultar_cnpj(cnpj):
    """
    Consulta um CNPJ tentando, em ordem, múltiplas fontes públicas até uma
    responder com sucesso:
    1. BrasilAPI (com retry para erros 5xx transitórios)
    2. minhareceita.org
    3. cnpj.ws (API pública)
    4. OpenCNPJ

    Isso é necessário porque BrasilAPI e minhareceita.org compartilham a mesma
    base de dados de origem — se um registro específico causa erro em uma,
    frequentemente causa o mesmo erro na outra. cnpj.ws e OpenCNPJ usam
    pipelines de dados independentes e servem como fallback real nesses casos.

    Retorna (dados, None) em sucesso ou (None, motivo_do_erro) em falha total.
    """
    if len(cnpj) != 14 or not cnpj.isdigit():
        return None, "CNPJ inválido (deve conter 14 dígitos numéricos)"

    fontes = [
        ("BrasilAPI", lambda: _consultar_brasilapi(cnpj)),
        ("minhareceita.org", lambda: _consultar_minhareceita(cnpj)),
        ("cnpj.ws", lambda: _consultar_cnpjws(cnpj)),
        ("OpenCNPJ", lambda: _consultar_opencnpj(cnpj)),
    ]

    erros_acumulados = []
    for nome_fonte, funcao in fontes:
        dados, erro = funcao()
        if dados is not None:
            return dados, None

        # "Não encontrado" é um resultado definitivo — mas só paramos por aqui
        # se pelo menos duas fontes concordarem, já que uma fonte isolada
        # pode simplesmente estar desatualizada.
        erros_acumulados.append(f"{nome_fonte}: {erro}")

    return None, " | ".join(erros_acumulados)

def processar_lista(lista_cnpjs):
    dados_finais = []
    erros = []
    progresso = st.progress(0)
    status_text = st.empty()
    
    for i, cnpj_bruto in enumerate(lista_cnpjs):
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        status_text.text(f"🔍 Processando {i+1}/{len(lista_cnpjs)}...")

        d, motivo_erro = consultar_cnpj(cnpj)

        if d is not None:
            try:
                porte, fat, func, fat_min, fat_max = processar_inteligencia_premium(d)
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                status_emp = verificar_situacao_especial(d)
                tipo_estabelecimento = "🏢 MATRIZ" if d.get('identificador_matriz_filial') == 1 else "🏪 FILIAL"
                
                dados_finais.append({
                    "Empresa": fantasia,
                    "Razão Social": d.get('razao_social'),
                    "CNPJ": cnpj,
                    "Tipo": tipo_estabelecimento,
                    "Status": status_emp,
                    "Atividade Principal": d.get('cnae_fiscal_descricao', 'N/I'),
                    "Porte": porte,
                    "Faturamento Est.*": fat,
                    "Funcionários Est.*": func,
                    "Capital Social": f"R$ {float(d.get('capital_social',0)):,.2f}",
                    "Cidade/UF": f"{d.get('municipio')}/{d.get('uf')}",
                    "LinkedIn": f"https://www.linkedin.com/search/results/people/?keywords={limpar_nome_empresa(fantasia).replace(' ', '%20')}%20(Comprador%20OR%20Suprimentos)",
                    "WhatsApp": f"https://www.google.com.br/search?q=whatsapp+telefone+setor+compras+{fantasia.replace(' ', '+')}",
                    "Endereço": f"{d.get('logradouro')}, {d.get('numero')} - {d.get('municipio')}",
                    "Nome Busca": limpar_nome_empresa(fantasia),
                    "Faturamento_Min": fat_min,
                    "Faturamento_Max": fat_max
                })
            except Exception as e:
                erros.append((cnpj, f"Erro ao processar os dados retornados: {e}"))
        else:
            erros.append((cnpj, motivo_erro))

        time.sleep(0.3)
        progresso.progress((i + 1) / len(lista_cnpjs))
    
    status_text.text("✅ Análise concluída!")

    # Mostra claramente qualquer CNPJ que não pôde ser processado, em vez de
    # simplesmente sumir sem explicação.
    if erros:
        with st.expander(f"⚠️ {len(erros)} CNPJ(s) não processado(s) — clique para ver detalhes", expanded=len(dados_finais) == 0):
            for cnpj_err, motivo in erros:
                st.markdown(
                    f"""<div class="erro-box"><strong>CNPJ:</strong> {cnpj_err}<br>
                    <strong>Motivo:</strong> {motivo}</div>""",
                    unsafe_allow_html=True
                )

    if not dados_finais:
        st.error("❌ Nenhuma empresa pôde ser processada. Veja os detalhes dos erros acima.")

    return pd.DataFrame(dados_finais)

# --- FUNÇÕES LUSHA ---
def buscar_email_hunter(first_name, last_name, domain):
    if not HUNTER_API_KEY:
        return None
    try:
        url = "https://api.hunter.io/v2/email-finder"
        params = {
            'domain': domain,
            'first_name': first_name,
            'last_name': last_name,
            'api_key': HUNTER_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            email_data = data.get('data', {})
            if email_data.get('email'):
                return {
                    'email': email_data.get('email'),
                    'confidence': email_data.get('score', 0),
                    'verified': email_data.get('verification', {}).get('value') == 'valid'
                }
        return None
    except:
        return None

def buscar_perfil_apollo(nome, empresa):
    if not APOLLO_API_KEY:
        return None
    try:
        url = "https://api.apollo.io/v1/people/match"
        headers = {'Content-Type': 'application/json'}
        nome_partes = nome.split()
        payload = {
            'api_key': APOLLO_API_KEY,
            'first_name': nome_partes[0] if nome_partes else nome,
            'last_name': nome_partes[-1] if len(nome_partes) > 1 else '',
            'organization_name': empresa
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            person = data.get('person', {})
            if person:
                phones = person.get('phone_numbers', [])
                return {
                    'email': person.get('email'),
                    'telefone': phones[0].get('raw_number') if phones else None,
                    'cargo': person.get('title'),
                    'empresa': person.get('organization', {}).get('name'),
                    'linkedin': person.get('linkedin_url')
                }
        return None
    except:
        return None

def buscar_por_empresa_apollo(empresa, limit=10):
    if not APOLLO_API_KEY:
        return []
    try:
        url = "https://api.apollo.io/v1/mixed_people/search"
        
        # Lista de cargos focados APENAS em compras
        titulos_compras = [
            'comprador', 'compradora', 'buyer', 'purchasing',
            'suprimentos', 'procurement', 'supply chain',
            'gerente de compras', 'coordenador de compras', 'analista de compras',
            'diretor de compras', 'supervisor de compras', 'assistente de compras',
            'gestão de suprimentos', 'abastecimento', 'sourcing',
            'gerente de suprimentos', 'coordenador de suprimentos',
            'analista de suprimentos', 'supply manager'
        ]
        
        contatos_unicos = {}
        
        # Busca em até 3 páginas para garantir resultados
        for pagina in range(1, 4):
            payload = {
                'api_key': APOLLO_API_KEY,
                'q_organization_name': empresa,
                'page': pagina,
                'per_page': 25,
                'person_titles': titulos_compras
            }
            
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                pessoas = data.get('people', [])
                
                if not pessoas:  # Se não há mais resultados, para
                    break
                
                for person in pessoas:
                    cargo = person.get('title', '').lower()
                    email = person.get('email', 'N/D')
                    
                    # Filtro duplo: cargo deve conter palavras-chave de compras
                    keywords_compras = [
                        'compra', 'buyer', 'purchasing', 'procurement',
                        'suprimento', 'supply', 'sourcing', 'abastecimento'
                    ]
                    
                    if any(keyword in cargo for keyword in keywords_compras):
                        # Evita duplicatas por email
                        if email not in contatos_unicos or email == 'N/D':
                            phones = person.get('phone_numbers', [])
                            contatos_unicos[email if email != 'N/D' else person.get('name', '')] = {
                                'nome': person.get('name', 'N/D'),
                                'cargo': person.get('title', 'N/D'),
                                'email': email,
                                'telefone': phones[0].get('raw_number') if phones else 'N/D',
                                'linkedin': person.get('linkedin_url', ''),
                                'empresa': empresa,
                                'confidence': 95,
                                'sources': ['Apollo.io']
                            }
                    
                    # Para quando atingir o limite
                    if len(contatos_unicos) >= limit:
                        break
            
            if len(contatos_unicos) >= limit:
                break
        
        return list(contatos_unicos.values())[:limit]
    except Exception as e:
        st.error(f"Erro na busca: {str(e)}")
        return []

def enriquecer_contato(nome, empresa, domain=None):
    resultado = {
        'nome': nome,
        'empresa': empresa,
        'cargo': None,
        'email': None,
        'telefone': None,
        'linkedin': None,
        'confidence': 0,
        'sources': []
    }
    apollo_data = buscar_perfil_apollo(nome, empresa)
    if apollo_data:
        resultado.update({k: v for k, v in apollo_data.items() if v})
        resultado['sources'].append('Apollo.io')
    if not resultado['email'] and domain:
        nome_partes = nome.split()
        if len(nome_partes) >= 2:
            hunter_data = buscar_email_hunter(nome_partes[0], nome_partes[-1], domain)
            if hunter_data:
                resultado['email'] = hunter_data['email']
                resultado['confidence'] = hunter_data['confidence']
                resultado['sources'].append('Hunter.io')
    return resultado

def renderizar_contact_card(contato):
    nome = contato.get('nome', 'N/D')
    cargo = contato.get('cargo', 'N/D')
    email = contato.get('email', 'N/D')
    telefone = contato.get('telefone', 'N/D')
    empresa = contato.get('empresa', 'N/D')
    linkedin = contato.get('linkedin', '')
    confidence = contato.get('confidence', 0)
    sources = contato.get('sources', [])
    
    iniciais = ''.join([p[0].upper() for p in nome.split()[:2]])
    
    if confidence >= 90:
        conf_color, conf_text = "#d4edda", "#155724"
    elif confidence >= 70:
        conf_color, conf_text = "#fff3cd", "#856404"
    else:
        conf_color, conf_text = "#f8d7da", "#721c24"
    
    html = f"""
    <div class="contact-card">
        <div class="contact-header">
            <div class="contact-avatar">{iniciais}</div>
            <div class="contact-info">
                <div class="contact-name">{nome}</div>
                <div class="contact-title">{cargo} @ {empresa}</div>
            </div>
            <div>
                <span class="confidence-badge" style="background: {conf_color}; color: {conf_text};">
                    {confidence}% confiança
                </span>
                {''.join([f'<span class="source-badge">{s}</span>' for s in sources])}
            </div>
        </div>
        <div class="contact-details">
            <div class="detail-item">
                <span class="detail-icon">✉️</span>
                <div>
                    <div class="detail-label">Email</div>
                    <div class="detail-value">{email}</div>
                </div>
            </div>
            <div class="detail-item">
                <span class="detail-icon">📱</span>
                <div>
                    <div class="detail-label">Telefone</div>
                    <div class="detail-value">{telefone}</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if email != 'N/D':
            st.link_button("📧 Email", f"mailto:{email}", use_container_width=True)
    with col2:
        if linkedin:
            st.link_button("🔗 LinkedIn", linkedin, use_container_width=True)
    with col3:
        if telefone != 'N/D':
            st.link_button("📞 WhatsApp", f"https://wa.me/{telefone.replace('+', '').replace(' ', '')}", use_container_width=True)

# === INTERFACE COM TABS ===
tab1, tab2, tab3 = st.tabs(["🏢 Análise de Empresas (CNPJ)", "🔍 Busca de Contatos", "📊 Histórico"])

# TAB 1: ANÁLISE CNPJ
with tab1:
    col_in1, col_in2, col_in3 = st.columns([1, 4, 1])
    with col_in2:
        entrada = st.text_area(
            "Insira os CNPJs para análise:", 
            height=150,
            placeholder="Você pode inserir com ou sem pontuação:\n09.560.231/0001-24\n09560231000124\n\nVários CNPJs (um por linha ou separados por vírgula)"
        )
        if st.button("🚀 Iniciar Análise", use_container_width=True, key="btn_cnpj"):
            if entrada:
                cnpjs = extrair_cnpjs(entrada)
                if cnpjs:
                    st.info(f"📋 {len(cnpjs)} CNPJ(s) identificado(s)")
                    st.session_state.df_resultado = processar_lista(cnpjs)
                else:
                    st.error("❌ Nenhum CNPJ válido encontrado. Verifique o formato.")
            else:
                st.error("❌ Insira ao menos um CNPJ antes de iniciar a análise.")

    if 'df_resultado' in st.session_state and not st.session_state.df_resultado.empty:
        df = st.session_state.df_resultado
        
        st.dataframe(
            df.drop(columns=['Endereço', 'Nome Busca', 'Faturamento_Min', 'Faturamento_Max', 'Razão Social', 'CNPJ']),
            column_config={
                "LinkedIn": st.column_config.LinkColumn("Pessoas"), 
                "WhatsApp": st.column_config.LinkColumn("Zap")
            },
            hide_index=True, 
            use_container_width=True
        )
        
        st.download_button(
            "📥 Baixar Relatório", 
            data=df.to_csv(index=False).encode('utf-8-sig'), 
            file_name="bdr_hunter_empresas.csv", 
            use_container_width=True
        )

        st.divider()
        st.markdown("### 🗺️ Investigação de Localização")
        
        emp_sel = st.selectbox("🏭 Selecione a Empresa:", df["Empresa"].tolist(), key="select_empresa_mapa")
        
        if emp_sel:
            row = df[df["Empresa"] == emp_sel].iloc[0]
            
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.markdown(f"""
                <div class="sucesso-box">
                    <strong>🏢 Razão Social:</strong> {row['Razão Social']}<br>
                    <strong>🆔 CNPJ:</strong> {row['CNPJ']}
                </div>
                """, unsafe_allow_html=True)
            
            with col_info2:
                st.markdown(f"""
                <div class="sucesso-box">
                    <strong>📊 Status:</strong> {row['Status']}<br>
                    <strong>🏭 Tipo:</strong> {row['Tipo']}
                </div>
                """, unsafe_allow_html=True)
            
            with col_info3:
                st.markdown(f"""
                <div class="sucesso-box">
                    <strong>💰 Faturamento:</strong> {row['Faturamento Est.*']}<br>
                    <strong>📍 Cidade:</strong> {row['Cidade/UF']}
                </div>
                """, unsafe_allow_html=True)
            
            st.info(f"📍 **{row['Empresa']}** | {row['Endereço']}")

            # --- Distância a partir de Aguaí - SP ---
            cidade_uf = row['Cidade/UF'] or ""
            municipio_empresa, _, uf_empresa = cidade_uf.partition("/")
            municipio_empresa = municipio_empresa.strip()
            uf_empresa = uf_empresa.strip()

            col_mapa, col_distancia = st.columns([3, 1])

            with col_distancia:
                if municipio_empresa:
                    with st.spinner("📏 Calculando distância..."):
                        lat_empresa, lon_empresa = geocodificar_cidade(municipio_empresa, uf_empresa)

                    if lat_empresa is not None:
                        distancia_rodoviaria, duracao_horas = calcular_distancia_rodoviaria_km(
                            CIDADE_BASE_LAT, CIDADE_BASE_LON, lat_empresa, lon_empresa
                        )

                        if distancia_rodoviaria is not None:
                            horas = int(duracao_horas)
                            minutos = int((duracao_horas - horas) * 60)
                            st.markdown(f"""
                            <div class="potencial-box" style="margin-top:0;">
                                <div style="font-size: 0.9em;">🚗 Distância de {CIDADE_BASE_NOME}-{CIDADE_BASE_UF}</div>
                                <div class="potencial-valor">{distancia_rodoviaria:,.0f} km</div>
                                <div style="font-size: 0.8em; opacity: 0.85;">até {municipio_empresa}/{uf_empresa}</div>
                                <div style="font-size: 0.75em; opacity: 0.85; margin-top: 4px;">⏱️ ≈ {horas}h{minutos:02d}min de carro</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Fallback: se o OSRM falhar, mostra linha reta com aviso claro
                            distancia_reta = calcular_distancia_km(
                                CIDADE_BASE_LAT, CIDADE_BASE_LON, lat_empresa, lon_empresa
                            )
                            st.markdown(f"""
                            <div class="alerta-box" style="margin-top:0;">
                                <div style="font-size: 0.9em;">📍 Distância (linha reta) de {CIDADE_BASE_NOME}-{CIDADE_BASE_UF}</div>
                                <div class="potencial-valor" style="color:#856404; font-size:1.8em;">~{distancia_reta:,.0f} km</div>
                                <div style="font-size: 0.75em;">até {municipio_empresa}/{uf_empresa}</div>
                                <div style="font-size: 0.7em; margin-top: 4px;">⚠️ Rota rodoviária indisponível no momento; valor aproximado por linha reta (menor que a distância real por estrada).</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning(f"⚠️ Não foi possível localizar '{municipio_empresa}/{uf_empresa}' para calcular a distância.")
                else:
                    st.info("Cidade da empresa não identificada.")

            with col_mapa:
                query = f"{row['Razão Social']} {row['Endereço']}".replace(" ", "+")
                st.components.v1.iframe(f"https://www.google.com/maps?q={query}&output=embed", height=450)

# TAB 2: BUSCA DE CONTATOS
with tab2:
    subtab1, subtab2 = st.tabs(["👤 Buscar Pessoa", "🏢 Buscar por Empresa"])
    
    with subtab1:
        st.markdown("#### Buscar dados de um profissional")
        col1, col2 = st.columns(2)
        with col1:
            nome_pessoa = st.text_input("👤 Nome completo", placeholder="João Silva", key="nome_pessoa")
            empresa_pessoa = st.text_input("🏢 Empresa", placeholder="Empresa LTDA", key="empresa_pessoa")
        with col2:
            domain_pessoa = st.text_input("🌐 Domínio (opcional)", placeholder="empresa.com.br", key="domain_pessoa")
        
        if st.button("🔍 Buscar Contato", use_container_width=True, type="primary", key="btn_buscar_pessoa"):
            if nome_pessoa and empresa_pessoa:
                with st.spinner("🔎 Enriquecendo dados..."):
                    contato = enriquecer_contato(nome_pessoa, empresa_pessoa, domain_pessoa)
                    if contato['email'] or contato['telefone']:
                        st.success("✅ Contato encontrado!")
                        renderizar_contact_card(contato)
                        if 'historico' not in st.session_state:
                            st.session_state.historico = []
                        st.session_state.historico.append(contato)
                    else:
                        st.warning("⚠️ Não encontramos dados para este contato.")
            else:
                st.error("❌ Preencha Nome e Empresa")
    
    with subtab2:
        st.markdown("#### Buscar contatos da área de compras de uma empresa")
        
        st.info("""
        🎯 **Foco em Compras**: Esta busca retorna apenas profissionais com os seguintes cargos:
        - 🛒 Comprador / Buyer / Purchasing
        - 📦 Suprimentos / Supply Chain / Procurement
        - 👔 Gerente/Coordenador/Analista/Diretor de Compras
        - 🔄 Sourcing / Abastecimento
        """)
        
        empresa_busca = st.text_input("🏢 Nome da empresa", placeholder="Ambev, Natura...", key="empresa_busca")
        num_contatos = st.slider("📊 Número de contatos", 5, 20, 10, key="num_contatos")
        
        if st.button("🔍 Buscar Equipe de Compras", use_container_width=True, type="primary", key="btn_buscar_empresa"):
            if empresa_busca:
                with st.spinner(f"🔎 Buscando profissionais de compras em {empresa_busca}..."):
                    contatos = buscar_por_empresa_apollo(empresa_busca, num_contatos)
                    if contatos:
                        # Stats
                        st.success(f"✅ Encontrados {len(contatos)} profissional(is) da área de compras!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🛒 Contatos de Compras", len(contatos))
                        with col2:
                            emails_validos = sum(1 for c in contatos if c.get('email') and c['email'] != 'N/D')
                            st.metric("✉️ Emails Válidos", emails_validos)
                        with col3:
                            telefones_validos = sum(1 for c in contatos if c.get('telefone') and c['telefone'] != 'N/D')
                            st.metric("📱 Telefones", telefones_validos)
                        
                        st.divider()
                        
                        # Agrupa por cargo para melhor visualização
                        st.markdown("##### 👥 Profissionais Encontrados:")
                        for contato in contatos:
                            renderizar_contact_card(contato)
                        
                        df = pd.DataFrame(contatos)
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            "📥 Baixar Lista de Contatos de Compras",
                            data=csv,
                            file_name=f"equipe_compras_{empresa_busca.replace(' ', '_')}.csv",
                            use_container_width=True
                        )
                        
                        if 'historico' not in st.session_state:
                            st.session_state.historico = []
                        st.session_state.historico.extend(contatos)
                    else:
                        st.warning("""
                        ⚠️ **Nenhum profissional de compras encontrado**
                        
                        Possíveis motivos:
                        - A empresa pode não ter esses cargos cadastrados publicamente
                        - Tente variações do nome da empresa
                        - A empresa pode usar nomenclaturas diferentes (ex: "Procurement", "Supply Chain")
                        """)
            else:
                st.error("❌ Digite o nome da empresa")

# TAB 3: HISTÓRICO
with tab3:
    st.markdown("### 📊 Histórico de Buscas")
    if 'historico' in st.session_state and st.session_state.historico:
        st.info(f"📈 Total: {len(st.session_state.historico)} contatos")
        for contato in st.session_state.historico:
            renderizar_contact_card(contato)
        
        df_historico = pd.DataFrame(st.session_state.historico)
        csv_historico = df_historico.to_csv(index=False).encode('utf-8-sig')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Baixar Histórico", data=csv_historico, file_name="historico.csv", use_container_width=True)
        with col2:
            if st.button("🗑️ Limpar", use_container_width=True):
                st.session_state.historico = []
                st.rerun()
    else:
        st.info("📭 Nenhuma busca realizada ainda")

st.markdown("---")
st.markdown("💡 **BDR Hunter Pro** - Powered by APIs | Desenvolvido por Gelson Vallim")
