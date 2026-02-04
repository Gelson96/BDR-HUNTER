import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime
import time

# 1. Configuração da Página
st.set_page_config(page_title="BDR Hunter Pro | Gelson96", layout="wide", page_icon="🚀")

URL_LOGO = "https://static.wixstatic.com/media/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png/v1/fill/w_232,h_67,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png"

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
    .noticia-box {{
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-left: 5px solid #667eea;
        padding: 18px;
        margin: 12px 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .noticia-titulo {{
        font-weight: bold;
        color: #1a1a1a;
        margin-bottom: 10px;
        font-size: 1.15em;
        line-height: 1.4;
    }}
    .noticia-conteudo {{
        color: #444;
        line-height: 1.7;
        margin: 10px 0;
        font-size: 0.95em;
    }}
    .noticia-fonte {{
        font-size: 0.82em;
        color: #888;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid #f0f0f0;
        font-style: italic;
    }}
    .alerta-box {{
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
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
    .destaque-box {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        text-align: center;
    }}
    .destaque-numero {{
        font-size: 3em;
        font-weight: bold;
        margin: 10px 0;
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

def buscar_quantidade_filiais(cnpj):
    """
    Busca a quantidade total de estabelecimentos (matriz + filiais) usando CNPJ raiz
    Utiliza a API da ReceitaWS como alternativa
    """
    try:
        cnpj_raiz = cnpj[:8]
        
        # Método 1: Tentar via BrasilAPI (pode não ter essa funcionalidade)
        # Método 2: Usar ReceitaWS (mais completo)
        url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # A ReceitaWS retorna informações, mas não lista todas filiais
            # Vamos buscar informações adicionais
            qsa_count = len(data.get('qsa', [])) if data.get('qsa') else 0
            
            # Informação básica
            info = {
                'cnpj_raiz': cnpj_raiz,
                'razao_social': data.get('nome', 'N/D'),
                'tipo': 'MATRIZ' if data.get('tipo', '') == 'MATRIZ' else 'FILIAL',
                'qtd_filiais_estimada': 'Consultar Receita Federal',  # Placeholder
                'capital_social': data.get('capital_social', '0'),
                'socios': qsa_count
            }
            return info
        else:
            # Se ReceitaWS falhar, retorna info básica
            return {
                'cnpj_raiz': cnpj_raiz,
                'razao_social': 'N/D',
                'tipo': 'N/D',
                'qtd_filiais_estimada': 'Não disponível',
                'capital_social': '0',
                'socios': 0
            }
            
    except Exception as e:
        return {
            'cnpj_raiz': cnpj[:8] if len(cnpj) >= 8 else cnpj,
            'razao_social': 'Erro na consulta',
            'tipo': 'N/D',
            'qtd_filiais_estimada': f'Erro: {str(e)}',
            'capital_social': '0',
            'socios': 0
        }

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
            time.sleep(0.3)  # Evitar rate limit
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
            if cnpjs: st.session_state.df_resultado = processar_lista(cnpjs)

if 'df_resultado' in st.session_state and not st.session_state.df_resultado.empty:
    df = st.session_state.df_resultado
    
    st.dataframe(
        df.drop(columns=['Endereço', 'Nome Busca', 'Faturamento_Min', 'Faturamento_Max', 'Razão Social', 'CNPJ']),
        column_config={
            "LinkedIn": st.column_config.LinkColumn("Pessoas"), 
            "WhatsApp": st.column_config.LinkColumn("Zap")
        },
        hide_index=True, use_container_width=True
    )
    
    # --- POTENCIAL DE EMBALAGENS ---
    st.divider()
    st.markdown("### 📦 Potencial de Compra de Embalagens")
    
    df_calculavel = df[df['Faturamento_Min'].notna()]
    
    if df_calculavel.empty:
        st.warning("⚠️ Apenas empresas GRANDES foram encontradas. Não é possível calcular potencial (possibilidades infinitas).")
    else:
        potencial_anual_min = df_calculavel['Faturamento_Min'].sum() * 0.03
        potencial_anual_max = df_calculavel['Faturamento_Max'].sum() * 0.03
        potencial_mensal_min = potencial_anual_min / 12
        potencial_mensal_max = potencial_anual_max / 12
        
        empresas_grandes = len(df) - len(df_calculavel)
        if empresas_grandes > 0:
            st.info(f"ℹ️ **{empresas_grandes} empresa(s) GRANDE(S)** foram excluídas do cálculo (possibilidades infinitas)")
        
        col_preco1, col_preco2, col_preco3 = st.columns([1, 2, 1])
        with col_preco2:
            preco_kg = st.number_input(
                "💵 Preço médio do KG de embalagem (R$):",
                min_value=0.01,
                value=15.00,
                step=0.50,
                format="%.2f"
            )
        
        kg_mensal_min = potencial_mensal_min / preco_kg if preco_kg > 0 else 0
        kg_mensal_max = potencial_mensal_max / preco_kg if preco_kg > 0 else 0
        kg_anual_min = potencial_anual_min / preco_kg if preco_kg > 0 else 0
        kg_anual_max = potencial_anual_max / preco_kg if preco_kg > 0 else 0
        
        st.markdown("#### 📉 Potencial MÍNIMO")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""
                <div class="potencial-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div style="font-size: 1.2em;">💰 Anual Mínimo</div>
                    <div class="potencial-valor">R$ {potencial_anual_min:,.2f}</div>
                    <div style="font-size: 1.1em; margin-top: 10px;">⚖️ {kg_anual_min:,.2f} kg</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div class="potencial-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div style="font-size: 1.2em;">📅 Mensal Mínimo</div>
                    <div class="potencial-valor">R$ {potencial_mensal_min:,.2f}</div>
                    <div style="font-size: 1.1em; margin-top: 10px;">⚖️ {kg_mensal_min:,.2f} kg</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div class="potencial-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div style="font-size: 1.2em;">📊 Preço/KG</div>
                    <div class="potencial-valor">R$ {preco_kg:,.2f}</div>
                    <div style="font-size: 1.1em; margin-top: 10px;">💼 Configurado</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("#### 📈 Potencial MÁXIMO")
        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown(
                f"""
                <div class="potencial-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <div style="font-size: 1.2em;">💰 Anual Máximo</div>
                    <div class="potencial-valor">R$ {potencial_anual_max:,.2f}</div>
                    <div style="font-size: 1.1em; margin-top: 10px;">⚖️ {kg_anual_max:,.2f} kg</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col5:
            st.markdown(
                f"""
                <div class="potencial-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <div style="font-size: 1.2em;">📅 Mensal Máximo</div>
                    <div class="potencial-valor">R$ {potencial_mensal_max:,.2f}</div>
                    <div style="font-size: 1.1em; margin-top: 10px;">⚖️ {kg_mensal_max:,.2f} kg</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col6:
            st.markdown(
                f"""
                <div class="potencial-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <div style="font-size: 1.2em;">📊 Preço/KG</div>
                    <div class="potencial-valor">R$ {preco_kg:,.2f}</div>
                    <div style="font-size: 1.1em; margin-top: 10px;">💼 Configurado</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.info(f"💡 **Cálculo baseado em:** 3% do faturamento estimado de **{len(df_calculavel)} empresa(s)** | Mínimo: limite inferior | Máximo: limite superior")
    
    st.download_button("📥 Baixar Relatório", data=df.to_csv(index=False).encode('utf-8-sig'), file_name="bdr_hunter_risk.csv", use_container_width=True)

    # --- INTELIGÊNCIA DE MERCADO REFORMULADA ---
    st.divider()
    st.markdown("### 🔍 Inteligência de Mercado")
    st.markdown("**Análise completa:** Estrutura corporativa + Notícias atuais")
    
    emp_sel = st.selectbox("🏭 Selecione a Empresa para Análise:", df["Empresa"].tolist())
    
    if emp_sel:
        row = df[df["Empresa"] == emp_sel].iloc[0]
        
        # Informações Básicas
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
        
        # Botão de Análise Completa
        if st.button(f"🚀 BUSCAR INTELIGÊNCIA COMPLETA", use_container_width=True, type="primary"):
            
            # SEÇÃO 1: ESTRUTURA CORPORATIVA (FILIAIS)
            st.markdown("---")
            st.markdown("### 🏢 Estrutura Corporativa - Matriz e Filiais")
            
            with st.spinner("📊 Consultando estrutura da empresa..."):
                info_filiais = buscar_quantidade_filiais(row['CNPJ'])
                cnpj_raiz = row['CNPJ'][:8]
                
                col_fil1, col_fil2 = st.columns(2)
                
                with col_fil1:
                    st.markdown(f"""
                    <div class="destaque-box">
                        <div style="font-size: 1.3em;">🔢 CNPJ RAIZ</div>
                        <div class="destaque-numero">{cnpj_raiz}</div>
                        <div style="font-size: 0.9em; margin-top: 10px;">Use este número para buscar todas as unidades</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_fil2:
                    st.markdown(f"""
                    <div class="destaque-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                        <div style="font-size: 1.3em;">🏭 TIPO DE ESTABELECIMENTO</div>
                        <div class="destaque-numero">{row['Tipo']}</div>
                        <div style="font-size: 0.9em; margin-top: 10px;">Classificação do CNPJ consultado</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="info-box">
                    <strong>💡 Como encontrar TODAS as filiais:</strong><br><br>
                    1️⃣ Acesse: <a href="https://solucoes.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp" target="_blank">Portal da Receita Federal</a><br>
                    2️⃣ Busque por CNPJs que começam com: <strong>{cnpj_raiz}</strong><br>
                    3️⃣ Ou use serviços pagos como Serasa, Boa Vista, ou API da Serpro<br><br>
                    <strong>📍 Endereço desta unidade:</strong> {row['Endereço']}<br>
                    <strong>🏭 Setor de Atuação:</strong> {row['Atividade Principal']}
                </div>
                """, unsafe_allow_html=True)
            
            # SEÇÃO 2: NOTÍCIAS ATUAIS
            st.markdown("---")
            st.markdown("### 📰 Notícias e Informações Atuais")
            
            with st.spinner("🔍 Buscando notícias recentes da empresa..."):
                
                # Aqui você deve implementar a busca real via API
                # Exemplo de estrutura de resposta esperada
                
                st.markdown(f"""
                <div class="alerta-box">
                    <strong>🔎 Buscando notícias sobre:</strong> {row['Razão Social']}<br>
                    <strong>📅 Período:</strong> Últimos 6 meses<br>
                    <strong>🌐 Fontes:</strong> Google News, portais setoriais, imprensa especializada
                </div>
                """, unsafe_allow_html=True)
                
                # SIMULAÇÃO DE NOTÍCIAS (substituir por busca real)
                # Use Google News API, NewsAPI, ou scraping
                
                noticias_encontradas = [
                    {
                        "titulo": f"Aguardando integração com API de notícias",
                        "conteudo": f"Para ver notícias reais sobre {row['Razão Social']}, integre com Google News API, NewsAPI.org ou similar. O sistema está pronto para receber e exibir as notícias assim que a API for configurada.",
                        "fonte": "Sistema BDR Hunter",
                        "data": "Hoje",
                        "categoria": "info",
                        "relevancia": "alta"
                    }
                ]
                
                # Links de busca manual enquanto a API não está integrada
                st.markdown("#### 🔗 Busca Manual de Notícias (Temporário)")
                
                col_news1, col_news2, col_news3 = st.columns(3)
                
                nome_busca = row['Razão Social'].replace(' ', '+')
                
                with col_news1:
                    st.markdown(f"""
                    **Notícias Gerais:**
                    - [Google News - Geral](https://www.google.com/search?q={nome_busca}&tbm=nws)
                    - [Google News - Últimos 30 dias](https://www.google.com/search?q={nome_busca}&tbm=nws&tbs=qdr:m)
                    """)
                
                with col_news2:
                    st.markdown(f"""
                    **Expansão e Investimentos:**
                    - [Expansão/Fábricas](https://www.google.com/search?q={nome_busca}+expansão+OR+fábrica+OR+investimento&tbm=nws)
                    - [Novos Projetos](https://www.google.com/search?q={nome_busca}+projeto+OR+inauguração&tbm=nws)
                    """)
                
                with col_news3:
                    st.markdown(f"""
                    **Dados Corporativos:**
                    - [Resultados Financeiros](https://www.google.com/search?q={nome_busca}+balanço+OR+resultado&tbm=nws)
                    - [Unidades/Filiais](https://www.google.com/search?q={nome_busca}+filiais+OR+unidades)
                    """)
                
                # Exibir notícias formatadas
                st.markdown("#### 📋 Notícias Encontradas")
                
                for idx, noticia in enumerate(noticias_encontradas, 1):
                    
                    # Definir cores por categoria
                    if noticia["categoria"] == "expansao":
                        cor_borda = "#28a745"
                        icone = "🏭"
                    elif noticia["categoria"] == "investimento":
                        cor_borda = "#007bff"
                        icone = "💰"
                    elif noticia["categoria"] == "crise":
                        cor_borda = "#dc3545"
                        icone = "⚠️"
                    elif noticia["categoria"] == "mercado":
                        cor_borda = "#6f42c1"
                        icone = "📊"
                    else:
                        cor_borda = "#667eea"
                        icone = "📌"
                    
                    st.markdown(f"""
                    <div class="noticia-box" style="border-left: 5px solid {cor_borda};">
                        <div class="noticia-titulo">{icone} {noticia['titulo']}</div>
                        <p class="noticia-conteudo">{noticia['conteudo']}</p>
                        <div class="noticia-fonte">
                            📰 {noticia['fonte']} | 📅 {noticia['data']} | 
                            🎯 Relevância: <strong>{noticia['relevancia'].upper()}</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Instruções para integração
                st.markdown("---")
                st.info("""
                **💡 Para ativar busca automática de notícias:**
                
                1. Cadastre-se em uma API de notícias:
                   - NewsAPI.org (gratuito até 100 req/dia)
                   - Google News API
                   - Bing News Search API
                
                2. Adicione sua chave API no código
                
                3. As notícias aparecerão automaticamente aqui
                """)
            
            # SEÇÃO 3: CONTEXTO SETORIAL
            st.markdown("---")
            st.markdown("### 📊 Análise do Setor")
            
            st.markdown(f"""
            <div class="info-box">
                <strong>🏭 Atividade Principal:</strong> {row['Atividade Principal']}<br>
                <strong>📈 Classificação de Porte:</strong> {row['Porte']}<br>
                <strong>🌎 Região de Operação:</strong> {row['Cidade/UF']}<br>
                <strong>💼 Capital Social Declarado:</strong> {row['Capital Social']}
            </div>
            """, unsafe_allow_html=True)
            
            # Links setoriais
            setor_busca = row['Atividade Principal'][:40].replace(' ', '+')
            st.markdown(f"🔍 [Tendências do Setor no Google](https://www.google.com/search?q={setor_busca}+mercado+brasil+2024+2025&tbm=nws)")

    # MAPA
    st.divider()
    st.markdown("### 🗺️ Localização da Empresa")
    if emp_sel:
        row = df[df["Empresa"] == emp_sel].iloc[0]
        st.info(f"📍 **{row['Empresa']}** | {row['Endereço']}")
        query = f"{row['Razão Social']} {row['Endereço']}".replace(" ", "+")
        st.components.v1.iframe(f"https://www.google.com/maps?q={query}&output=embed", height=450)

st.markdown("---")
st.markdown("💡 **BDR Hunter Pro** - Desenvolvido por Gelson Vallim | Inteligência estratégica para prospecção B2B")
