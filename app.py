import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import time

# 1. Configuração da Página
st.set_page_config(page_title="BDR Hunter Pro | Gelson96", layout="wide", page_icon="🚀")

URL_LOGO = "https://static.wixstatic.com/media/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png/v1/fill/w_232,h_67,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png"
GEMINI_API_KEY = "AIzaSyBpzFNt13y2t1AB8aSXQAfyoWVpOvLbvFw"

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
        padding: 20px;
        margin: 15px 0;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }}
    .noticia-titulo {{
        font-weight: bold;
        color: #1a1a1a;
        margin-bottom: 12px;
        font-size: 1.2em;
        line-height: 1.5;
    }}
    .noticia-conteudo {{
        color: #444;
        line-height: 1.8;
        margin: 12px 0;
        font-size: 0.98em;
    }}
    .noticia-fonte {{
        font-size: 0.85em;
        color: #888;
        margin-top: 12px;
        padding-top: 10px;
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

def buscar_noticias_gemini(empresa_nome):
    """Busca notícias detalhadas usando Google Gemini API"""
    try:
        nome_limpo = limpar_nome_empresa(empresa_nome)
        
        prompt = f"""
Busque notícias RECENTES E RELEVANTES sobre a empresa "{empresa_nome}".

Foque especificamente em:
1. Expansão de fábricas, novas unidades ou plantas industriais
2. Investimentos significativos ou aportes de capital
3. Aquisições, fusões ou parcerias estratégicas
4. Lançamento de novos produtos ou linhas de produção
5. Resultados financeiros e balanços divulgados
6. Mudanças na diretoria ou estrutura societária
7. Prêmios, certificações ou reconhecimentos
8. Crises, fechamentos ou recuperação judicial
9. Contratações em massa ou demissões
10. Inaugurações ou eventos corporativos importantes

Para cada notícia encontrada, retorne em formato JSON (SEM markdown, SEM ```json, apenas o JSON puro):

{{"noticias": [
  {{
    "titulo": "título completo e descritivo da notícia",
    "conteudo": "descrição detalhada em 3-5 frases explicando o contexto, impacto e relevância para negócios",
    "fonte": "nome do veículo ou site",
    "data": "mês/ano ou período aproximado",
    "categoria": "expansao ou investimento ou crise ou financeiro ou geral",
    "relevancia": "alta ou média ou baixa"
  }}
]}}

IMPORTANTE:
- Retorne ATÉ 8 notícias mais relevantes
- Priorize notícias dos últimos 2 anos
- Se não encontrar notícias, retorne: {{"noticias": []}}
- NÃO invente informações - apenas notícias verificáveis
- Seja específico sobre valores, datas e locais quando disponível
"""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 4096,
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            
            try:
                texto_resposta = data['candidates'][0]['content']['parts'][0]['text']
                texto_resposta = texto_resposta.strip()
                
                # Remove markdown se presente
                if '```json' in texto_resposta:
                    texto_resposta = texto_resposta.split('```json')[1].split('```')[0].strip()
                elif '```' in texto_resposta:
                    texto_resposta = texto_resposta.split('```')[1].split('```')[0].strip()
                
                import json
                resultado = json.loads(texto_resposta)
                
                noticias_formatadas = []
                
                for noticia in resultado.get('noticias', []):
                    categoria = noticia.get('categoria', 'geral').lower()
                    
                    # Define ícone e cor por categoria
                    if categoria == "expansao":
                        icone = "🏭"
                        cor = "#28a745"
                    elif categoria == "investimento":
                        icone = "💰"
                        cor = "#007bff"
                    elif categoria == "crise":
                        icone = "⚠️"
                        cor = "#dc3545"
                    elif categoria == "financeiro":
                        icone = "📊"
                        cor = "#6f42c1"
                    else:
                        icone = "📰"
                        cor = "#667eea"
                    
                    noticias_formatadas.append({
                        'titulo': noticia.get('titulo', 'Sem título'),
                        'conteudo': noticia.get('conteudo', 'Sem descrição'),
                        'fonte': noticia.get('fonte', 'Fonte não identificada'),
                        'data': noticia.get('data', 'Data não disponível'),
                        'categoria': categoria,
                        'relevancia': noticia.get('relevancia', 'média'),
                        'icone': icone,
                        'cor': cor
                    })
                
                return noticias_formatadas
                
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                st.error(f"❌ Erro ao processar resposta da API: {str(e)}")
                return []
        else:
            st.error(f"❌ Erro na API Gemini (código {response.status_code})")
            return []
            
    except Exception as e:
        st.error(f"❌ Erro ao buscar notícias: {str(e)}")
        return []

def buscar_noticias_setor(atividade):
    """Busca notícias sobre o setor de atuação"""
    try:
        # Extrai palavras-chave da atividade
        palavras_chave = atividade[:50]
        
        prompt = f"""
Busque notícias e tendências RECENTES do setor: "{palavras_chave}".

Foque em:
- Tendências de mercado e inovações
- Regulamentações ou mudanças legais
- Crescimento ou retração do setor
- Principais desafios e oportunidades
- Novas tecnologias ou processos

Retorne JSON puro (sem markdown):

{{"noticias": [
  {{
    "titulo": "título da notícia setorial",
    "conteudo": "descrição em 2-3 frases",
    "fonte": "fonte",
    "data": "período",
    "relevancia": "alta ou média"
  }}
]}}

Máximo 4 notícias. Se não encontrar: {{"noticias": []}}
"""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
            }
        }
        
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            texto_resposta = data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            if '```json' in texto_resposta:
                texto_resposta = texto_resposta.split('```json')[1].split('```')[0].strip()
            elif '```' in texto_resposta:
                texto_resposta = texto_resposta.split('```')[1].split('```')[0].strip()
            
            import json
            resultado = json.loads(texto_resposta)
            
            noticias = []
            for n in resultado.get('noticias', []):
                noticias.append({
                    'titulo': n.get('titulo', ''),
                    'conteudo': n.get('conteudo', ''),
                    'fonte': n.get('fonte', ''),
                    'data': n.get('data', ''),
                    'relevancia': n.get('relevancia', 'média'),
                    'icone': '📊',
                    'cor': '#6f42c1'
                })
            
            return noticias
        
        return []
        
    except:
        return []

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

    # --- INTELIGÊNCIA DE MERCADO (AUTOMÁTICA) ---
    st.divider()
    st.markdown("### 🔍 Inteligência de Mercado")
    
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
        
        # Estrutura Corporativa
        st.markdown("---")
        cnpj_raiz = row['CNPJ'][:8]
        st.markdown(f"""
        <div class="info-box">
            <strong>🏢 Estrutura Corporativa</strong><br><br>
            <strong>📋 CNPJ Raiz:</strong> {cnpj_raiz}<br>
            <strong>🏭 Tipo do Estabelecimento:</strong> {row['Tipo']}<br>
            <strong>📍 Endereço:</strong> {row['Endereço']}<br><br>
            <strong>💡 Como verificar filiais:</strong> Consulte o portal da <a href="https://solucoes.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp" target="_blank">Receita Federal</a> 
            usando o CNPJ raiz <strong>{cnpj_raiz}</strong> ou utilize serviços especializados (Serasa, Boa Vista, Serpro).
        </div>
        """, unsafe_allow_html=True)
        
        # NOTÍCIAS DA EMPRESA (AUTOMÁTICO)
        st.markdown("---")
        st.markdown("### 📰 Notícias e Informações Atuais da Empresa")
        
        with st.spinner(f"🔍 Buscando notícias sobre {row['Razão Social']}..."):
            noticias_empresa = buscar_noticias_gemini(row['Razão Social'])
            
            if noticias_empresa:
                for idx, noticia in enumerate(noticias_empresa, 1):
                    st.markdown(f"""
                    <div class="noticia-box" style="border-left: 5px solid {noticia['cor']};">
                        <div class="noticia-titulo">{noticia['icone']} {noticia['titulo']}</div>
                        <p class="noticia-conteudo">{noticia['conteudo']}</p>
                        <div class="noticia-fonte">
                            📰 <strong>{noticia['fonte']}</strong> | 📅 {noticia['data']} | 🎯 Relevância: {noticia['relevancia'].upper()}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ Nenhuma notícia recente encontrada sobre esta empresa.")
        
        # ANÁLISE DO SETOR (AUTOMÁTICO)
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
        
        with st.spinner("📊 Buscando tendências do setor..."):
            noticias_setor = buscar_noticias_setor(row['Atividade Principal'])
            
            if noticias_setor:
                st.markdown("#### 📈 Notícias do Setor")
                for noticia in noticias_setor:
                    st.markdown(f"""
                    <div class="noticia-box" style="border-left: 5px solid {noticia['cor']};">
                        <div class="noticia-titulo">{noticia['icone']} {noticia['titulo']}</div>
                        <p class="noticia-conteudo">{noticia['conteudo']}</p>
                        <div class="noticia-fonte">
                            📰 {noticia['fonte']} | 📅 {noticia['data']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # MAPA
    st.divider()
    st.markdown("### 🗺️ Localização da Empresa")
    if emp_sel:
        row = df[df["Empresa"] == emp_sel].iloc[0]
        st.info(f"📍 **{row['Empresa']}** | {row['Endereço']}")
        query = f"{row['Razão Social']} {row['Endereço']}".replace(" ", "+")
        st.components.v1.iframe(f"https://www.google.com/maps?q={query}&output=embed", height=450)

st.markdown("---")
st.markdown("💡 **BDR Hunter Pro** - Desenvolvido por Gelson96 | Inteligência estratégica para prospecção B2B")
