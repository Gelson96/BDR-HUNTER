import streamlit as st
import pandas as pd
import requests
import re
import time

# 1. Configuração da Página
st.set_page_config(page_title="BDR Hunter Pro | Gelson96", layout="wide", page_icon="🚀")

URL_LOGO = "https://static.wixstatic.com/media/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png/v1/fill/w_232,h_67,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png"

# --- CONFIGURAÇÃO DE APIs DE ENRIQUECIMENTO ---
HUNTER_API_KEY = "ade32d411c5065d4f61d89a27b4b80018b62647a"
APOLLO_API_KEY = "cSG2GJRmKBGpdGpNykMJuA"
SNOV_USER_ID = "3339dd3a641d4a40440040bdf815c895"
SNOV_API_SECRET = "66325b5f11c5e6708f2ffeb01d6f85e8"

# --- CSS ---
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
    </style>
    <div class="centered-container"><img src="{URL_LOGO}"></div>
    """,
    unsafe_allow_html=True
)

st.title("BDR Hunter")
st.subheader("Inteligência de Mercado & Prospecção Estratégica")
st.divider()

# --- FUNÇÕES ---
def limpar_nome_empresa(nome):
    if not nome: return ""
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def buscar_emails_hunter(empresa_domain):
    """Busca emails usando Hunter.io"""
    if not HUNTER_API_KEY:
        return []
    
    try:
        url = f"https://api.hunter.io/v2/domain-search"
        params = {
            'domain': empresa_domain,
            'api_key': HUNTER_API_KEY,
            'limit': 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            emails = []
            
            for email_data in data.get('data', {}).get('emails', [])[:5]:
                emails.append({
                    'email': email_data.get('value'),
                    'nome': f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip(),
                    'cargo': email_data.get('position', 'N/D'),
                    'confidence': email_data.get('confidence', 0),
                    'fonte': 'Hunter.io'
                })
            
            return emails
        return []
    except:
        return []

def buscar_contatos_apollo(empresa_nome):
    """Busca contatos usando Apollo.io"""
    if not APOLLO_API_KEY:
        return []
    
    try:
        url = "https://api.apollo.io/v1/mixed_people/search"
        
        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        
        payload = {
            'api_key': APOLLO_API_KEY,
            'q_organization_name': empresa_nome,
            'page': 1,
            'per_page': 5,
            'person_titles': ['comprador', 'suprimentos', 'procurement', 'buyer', 'purchasing']
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            contatos = []
            
            for person in data.get('people', [])[:5]:
                contatos.append({
                    'nome': person.get('name', 'N/D'),
                    'cargo': person.get('title', 'N/D'),
                    'email': person.get('email', 'N/D'),
                    'telefone': person.get('phone_numbers', [{}])[0].get('raw_number', 'N/D') if person.get('phone_numbers') else 'N/D',
                    'linkedin': person.get('linkedin_url', ''),
                    'fonte': 'Apollo.io'
                })
            
            return contatos
        return []
    except:
        return []

def buscar_contatos_snov(empresa_domain):
    """Busca contatos usando Snov.io"""
    if not SNOV_USER_ID or not SNOV_API_SECRET:
        return []
    
    try:
        # Primeiro, autentica
        auth_url = "https://api.snov.io/v1/get-user-id"
        auth_data = {
            'client_id': SNOV_USER_ID,
            'client_secret': SNOV_API_SECRET
        }
        
        auth_response = requests.post(auth_url, json=auth_data, timeout=10)
        
        if auth_response.status_code != 200:
            return []
        
        access_token = auth_response.json().get('access_token')
        
        # Busca emails por domínio
        search_url = "https://api.snov.io/v1/get-domain-emails-with-info"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        search_data = {
            'domain': empresa_domain,
            'limit': 5
        }
        
        response = requests.post(search_url, json=search_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            contatos = []
            
            for email_info in data.get('emails', [])[:5]:
                contatos.append({
                    'nome': f"{email_info.get('firstName', '')} {email_info.get('lastName', '')}".strip(),
                    'cargo': email_info.get('position', 'N/D'),
                    'email': email_info.get('email', 'N/D'),
                    'telefone': 'N/D',
                    'linkedin': email_info.get('social', {}).get('linkedin', ''),
                    'fonte': 'Snov.io'
                })
            
            return contatos
        return []
    except:
        return []

def extrair_dominio_empresa(razao_social, cnpj=None):
    """Tenta deduzir o domínio web da empresa"""
    # Remove caracteres especiais e espaços
    nome_limpo = limpar_nome_empresa(razao_social).lower()
    nome_limpo = re.sub(r'[^a-z0-9\s]', '', nome_limpo)
    
    # Pega a primeira palavra significativa (geralmente o nome principal)
    palavras = nome_limpo.split()
    if palavras:
        dominio = palavras[0] + '.com.br'
        return dominio
    
    return None

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

def verificar_situacao_especial(d):
    razao = d.get('razao_social', '').upper()
    sit_especial = d.get('situacao_especial', '').upper()
    
    if "RECUPERACAO JUDICIAL" in razao or "RECUPERACAO JUDICIAL" in sit_especial:
        return "⚠️ RECUPERAÇÃO JUDICIAL"
    if d.get('descricao_situacao_cadastral') != "ATIVA":
        return f"🚫 {d.get('descricao_situacao_cadastral')}"
    return "✅ REGULAR"

def processar_lista(lista_cnpjs):
    dados_finais = []
    progresso = st.progress(0)
    status_text = st.empty()
    
    for i, cnpj_bruto in enumerate(lista_cnpjs):
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        try:
            status_text.text(f"🔍 Processando {i+1}/{len(lista_cnpjs)}...")
            res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            if res.status_code == 200:
                d = res.json()
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
            time.sleep(0.3)
        except: 
            continue
        progresso.progress((i + 1) / len(lista_cnpjs))
    
    status_text.text("✅ Análise concluída!")
    return pd.DataFrame(dados_finais)

# --- INTERFACE ---
col_in1, col_in2, col_in3 = st.columns([1, 4, 1])
with col_in2:
    entrada = st.text_area("Insira os CNPJs para análise de risco e porte:", height=150)
    if st.button("🚀 Iniciar Análise", use_container_width=True):
        if entrada:
            cnpjs = re.findall(r'\d+', entrada)
            if cnpjs: 
                st.session_state.df_resultado = processar_lista(cnpjs)

if 'df_resultado' in st.session_state and not st.session_state.df_resultado.empty:
    df = st.session_state.df_resultado
    
    # Tabela Principal
    st.dataframe(
        df.drop(columns=['Endereço', 'Nome Busca', 'Faturamento_Min', 'Faturamento_Max', 'Razão Social', 'CNPJ']),
        column_config={
            "LinkedIn": st.column_config.LinkColumn("Pessoas"), 
            "WhatsApp": st.column_config.LinkColumn("Zap")
        },
        hide_index=True, 
        use_container_width=True
    )
    
    # Download do Relatório
    st.download_button(
        "📥 Baixar Relatório", 
        data=df.to_csv(index=False).encode('utf-8-sig'), 
        file_name="bdr_hunter_risk.csv", 
        use_container_width=True
    )

    # --- MAPA DE LOCALIZAÇÃO ---
    st.divider()
    st.markdown("### 🗺️ Investigação de Localização")
    
    emp_sel = st.selectbox("🏭 Selecione a Empresa:", df["Empresa"].tolist())
    
    if emp_sel:
        row = df[df["Empresa"] == emp_sel].iloc[0]
        
        # Informações da Empresa Selecionada
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.markdown(f"""
            <div class="sucesso-box">
                <strong>🏢 Razão Social:</strong> {row['Razão Social']}<br>
                <strong>🏷️ Nome Fantasia:</strong> {row['Empresa']}<br>
                <strong>🆔 CNPJ:</strong> {row['CNPJ']}
            </div>
            """, unsafe_allow_html=True)
        
        with col_info2:
            st.markdown(f"""
            <div class="sucesso-box">
                <strong>📊 Status:</strong> {row['Status']}<br>
                <strong>🏭 Tipo:</strong> {row['Tipo']}<br>
                <strong>📏 Porte:</strong> {row['Porte']}
            </div>
            """, unsafe_allow_html=True)
        
        with col_info3:
            st.markdown(f"""
            <div class="sucesso-box">
                <strong>💰 Faturamento Est.:</strong> {row['Faturamento Est.*']}<br>
                <strong>👥 Funcionários Est.:</strong> {row['Funcionários Est.*']}<br>
                <strong>📍 Localização:</strong> {row['Cidade/UF']}
            </div>
            """, unsafe_allow_html=True)
        
        # Mapa
        st.info(f"📍 **{row['Empresa']}** | {row['Endereço']}")
        query = f"{row['Razão Social']} {row['Endereço']}".replace(" ", "+")
        st.components.v1.iframe(f"https://www.google.com/maps?q={query}&output=embed", height=450)
        
        # --- BUSCA DE CONTATOS ---
        st.divider()
        st.markdown("### 📞 Busca de Contatos")
        
        if st.button("🔍 Buscar Emails e Telefones", use_container_width=True, type="primary"):
            with st.spinner("🔎 Buscando contatos via APIs..."):
                
                # Tenta extrair domínio
                dominio = extrair_dominio_empresa(row['Razão Social'], row['CNPJ'])
                
                todos_contatos = []
                apis_usadas = []
                
                # Busca no Hunter.io (emails por domínio)
                if HUNTER_API_KEY:
                    with st.status(f"🔍 Buscando em Hunter.io (domínio: {dominio})...") as status:
                        emails_hunter = buscar_emails_hunter(dominio)
                        if emails_hunter:
                            todos_contatos.extend(emails_hunter)
                            apis_usadas.append(f"Hunter.io: {len(emails_hunter)} contato(s)")
                            status.update(label=f"✅ Hunter.io: {len(emails_hunter)} encontrado(s)", state="complete")
                        else:
                            status.update(label="⚠️ Hunter.io: Nenhum resultado", state="complete")
                
                # Busca no Apollo.io (contatos completos)
                if APOLLO_API_KEY:
                    with st.status(f"🔍 Buscando em Apollo.io...") as status:
                        contatos_apollo = buscar_contatos_apollo(row['Razão Social'])
                        if contatos_apollo:
                            todos_contatos.extend(contatos_apollo)
                            apis_usadas.append(f"Apollo.io: {len(contatos_apollo)} contato(s)")
                            status.update(label=f"✅ Apollo.io: {len(contatos_apollo)} encontrado(s)", state="complete")
                        else:
                            status.update(label="⚠️ Apollo.io: Nenhum resultado", state="complete")
                
                # Busca no Snov.io
                if SNOV_USER_ID and SNOV_API_SECRET:
                    with st.status(f"🔍 Buscando em Snov.io (domínio: {dominio})...") as status:
                        contatos_snov = buscar_contatos_snov(dominio)
                        if contatos_snov:
                            todos_contatos.extend(contatos_snov)
                            apis_usadas.append(f"Snov.io: {len(contatos_snov)} contato(s)")
                            status.update(label=f"✅ Snov.io: {len(contatos_snov)} encontrado(s)", state="complete")
                        else:
                            status.update(label="⚠️ Snov.io: Nenhum resultado", state="complete")
                
                if todos_contatos:
                    st.success(f"✅ **{len(todos_contatos)} contato(s) encontrado(s)!**")
                    st.info(f"🔍 Fontes consultadas: {' | '.join(apis_usadas)}")
                    
                    # Exibe em cards
                    for idx, contato in enumerate(todos_contatos, 1):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            nome = contato.get('nome', 'N/D')
                            cargo = contato.get('cargo', 'N/D')
                            email = contato.get('email', 'N/D')
                            telefone = contato.get('telefone', 'N/D')
                            linkedin = contato.get('linkedin', '')
                            fonte = contato.get('fonte', 'API')
                            confidence = contato.get('confidence', 0)
                            
                            confianca_texto = f"| 🎯 Confiança: {confidence}%" if confidence > 0 else ""
                            
                            st.markdown(f"""
                            <div class="sucesso-box">
                                <strong>👤 {nome}</strong><br>
                                <strong>💼 Cargo:</strong> {cargo}<br>
                                <strong>✉️ Email:</strong> {email}<br>
                                <strong>📱 Telefone:</strong> {telefone}<br>
                                <small>🔍 Fonte: {fonte} {confianca_texto}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_b:
                            if linkedin:
                                st.link_button("🔗 LinkedIn", linkedin, use_container_width=True)
                            if email != 'N/D':
                                st.link_button("✉️ Email", f"mailto:{email}", use_container_width=True)
                    
                    # Botão para salvar contatos
                    df_contatos = pd.DataFrame(todos_contatos)
                    csv_contatos = df_contatos.to_csv(index=False).encode('utf-8-sig')
                    
                    st.download_button(
                        "📥 Baixar Todos os Contatos (CSV)",
                        data=csv_contatos,
                        file_name=f"contatos_{limpar_nome_empresa(row['Empresa'])}.csv",
                        use_container_width=True
                    )
                    
                else:
                    st.warning("⚠️ Nenhum contato encontrado nas APIs consultadas.")
                    
                    st.markdown("""
                    <div class="alerta-box">
                        <strong>💡 Possíveis motivos:</strong><br>
                        • Domínio da empresa não foi identificado corretamente<br>
                        • Empresa não possui dados públicos disponíveis<br>
                        • Limite de créditos das APIs atingido<br>
                        • APIs podem não ter cobertura desta empresa específica
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("💡 **BDR Hunter Pro** - Desenvolvido por Gelson Vallim | Inteligência estratégica para prospecção B2B")
