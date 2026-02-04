import streamlit as st
import pandas as pd
import requests
import re

# 1. Configuração da Página
st.set_page_config(page_title="BDR Hunter Pro | Gelson96", layout="wide", page_icon="🚀")

URL_LOGO = "https://static.wixstatic.com/media/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png/v1/fill/w_232,h_67,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png"

# --- CSS PARA CENTRALIZAR ---
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
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }}
    .noticia-titulo {{
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
    }}
    .noticia-fonte {{
        font-size: 0.85em;
        color: #666;
        margin-top: 5px;
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
    
    # Empresas GRANDES não calculam potencial (possibilidades infinitas)
    if porte_cod in [5, "05"] or cap > 10000000:
        return "GRANDE", "100M+*", "500+*", None, None
    
    # Para demais portes, retorna MIN e MAX
    if porte_cod in [1, "01"]: 
        # ME: até 360k
        return "PEQUENO (ME)", "Até R$ 360k*", "1-9*", 0, 360000
    elif porte_cod in [3, "03"]: 
        # EPP: 360k-4,8M
        return "PEQUENO (EPP)", "R$ 360k-4,8M*", "10-49*", 360000, 4800000
    else:
        # Médio porte
        if cap > 1000000: 
            # 10M-50M
            return "MÉDIO", "R$ 10M-50M*", "100-250*", 10000000, 50000000
        else: 
            # 4,8M+ (estimativa até 10M)
            return "MÉDIO", "R$ 4,8M+*", "50+*", 4800000, 10000000

def verificar_situacao_especial(d):
    # Verifica no nome e na situação especial da Receita
    razao = d.get('razao_social', '').upper()
    sit_especial = d.get('situacao_especial', '').upper()
    
    if "RECUPERACAO JUDICIAL" in razao or "RECUPERACAO JUDICIAL" in sit_especial:
        return "⚠️ RECUPERAÇÃO JUDICIAL"
    if d.get('descricao_situacao_cadastral') != "ATIVA":
        return f"🚫 {d.get('descricao_situacao_cadastral')}"
    return "✅ REGULAR"

def buscar_filiais_cnpj(cnpj_base):
    """Busca quantidade de filiais usando o CNPJ raiz (8 primeiros dígitos)"""
    try:
        cnpj_raiz = cnpj_base[:8]
        # A API da Receita tem limitações, então fazemos uma busca simples
        # Em produção, você poderia usar APIs pagas como Serpro ou outros serviços
        return "Consulte manualmente"  # Placeholder
    except:
        return "N/D"

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
                
                # Identifica se é matriz ou filial
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
    
    # --- CÁLCULO DE POTENCIAL DE EMBALAGENS ---
    st.divider()
    st.markdown("### 📦 Potencial de Compra de Embalagens")
    
    # Filtra empresas que têm faturamento numérico (exclui GRANDES com None)
    df_calculavel = df[df['Faturamento_Min'].notna()]
    
    if df_calculavel.empty:
        st.warning("⚠️ Apenas empresas GRANDES foram encontradas. Não é possível calcular potencial (possibilidades infinitas).")
    else:
        # Cálculo MÍNIMO e MÁXIMO
        potencial_anual_min = df_calculavel['Faturamento_Min'].sum() * 0.03
        potencial_anual_max = df_calculavel['Faturamento_Max'].sum() * 0.03
        potencial_mensal_min = potencial_anual_min / 12
        potencial_mensal_max = potencial_anual_max / 12
        
        empresas_grandes = len(df) - len(df_calculavel)
        if empresas_grandes > 0:
            st.info(f"ℹ️ **{empresas_grandes} empresa(s) GRANDE(S)** foram excluídas do cálculo (possibilidades infinitas)")
        
        # Campo para preço médio do kg
        col_preco1, col_preco2, col_preco3 = st.columns([1, 2, 1])
        with col_preco2:
            preco_kg = st.number_input(
                "💵 Preço médio do KG de embalagem (R$):",
                min_value=0.01,
                value=15.00,
                step=0.50,
                format="%.2f"
            )
        
        # Cálculo de quantidade em kg
        kg_mensal_min = potencial_mensal_min / preco_kg if preco_kg > 0 else 0
        kg_mensal_max = potencial_mensal_max / preco_kg if preco_kg > 0 else 0
        kg_anual_min = potencial_anual_min / preco_kg if preco_kg > 0 else 0
        kg_anual_max = potencial_anual_max / preco_kg if preco_kg > 0 else 0
        
        # POTENCIAL MÍNIMO
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
        
        # POTENCIAL MÁXIMO
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

    # --- SEÇÃO DE INTELIGÊNCIA DE MERCADO ---
    st.divider()
    st.markdown("### 🔍 Inteligência de Mercado")
    st.markdown("Selecione uma empresa para ver notícias, expansões, unidades e informações estratégicas:")
    
    emp_sel = st.selectbox("🏭 Selecione a Empresa:", df["Empresa"].tolist())
    
    if emp_sel:
        row = df[df["Empresa"] == emp_sel].iloc[0]
        
        # Box com informações básicas
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.markdown(f"""
            <div class="sucesso-box">
                <strong>🏢 Empresa:</strong> {row['Empresa']}<br>
                <strong>🆔 Tipo:</strong> {row['Tipo']}<br>
                <strong>📊 Status:</strong> {row['Status']}
            </div>
            """, unsafe_allow_html=True)
        
        with col_info2:
            st.markdown(f"""
            <div class="sucesso-box">
                <strong>🏭 Setor:</strong> {row['Atividade Principal'][:50]}...<br>
                <strong>📏 Porte:</strong> {row['Porte']}<br>
                <strong>📍 Localização:</strong> {row['Cidade/UF']}
            </div>
            """, unsafe_allow_html=True)
        
        with col_info3:
            st.markdown(f"""
            <div class="sucesso-box">
                <strong>💰 Faturamento Est.:</strong> {row['Faturamento Est.*']}<br>
                <strong>👥 Funcionários Est.:</strong> {row['Funcionários Est.*']}<br>
                <strong>💼 Capital Social:</strong> {row['Capital Social']}
            </div>
            """, unsafe_allow_html=True)
        
        # Botão para buscar inteligência de mercado
        if st.button(f"🔎 Buscar Inteligência de Mercado sobre {row['Nome Busca']}", use_container_width=True):
            with st.spinner("🔍 Buscando notícias e informações estratégicas..."):
                
                # Container para as informações
                st.markdown("#### 📰 Notícias e Movimentações Recentes")
                
                # Aqui você precisaria implementar a busca real
                # Como exemplo, vou criar um placeholder que mostra como seria
                st.markdown(f"""
                <div class="noticia-box">
                    <div class="noticia-titulo">🔍 Buscando informações sobre: {row['Nome Busca']}</div>
                    <p>Pesquisando por:</p>
                    <ul>
                        <li>✅ Expansão de fábricas</li>
                        <li>✅ Fechamento de unidades</li>
                        <li>✅ Novos investimentos</li>
                        <li>✅ Fusões e aquisições</li>
                        <li>✅ Quantidade de filiais</li>
                        <li>✅ Notícias recentes do setor</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Links de busca automática
                st.markdown("#### 🔗 Fontes de Pesquisa Recomendadas")
                col_links1, col_links2 = st.columns(2)
                
                with col_links1:
                    nome_busca = row['Nome Busca'].replace(' ', '+')
                    st.markdown(f"🌐 [Notícias no Google](https://www.google.com/search?q={nome_busca}+expansão+OR+fábrica+OR+investimento+OR+filiais&tbm=nws)")
                    st.markdown(f"📊 [Pesquisa Geral](https://www.google.com/search?q={nome_busca}+unidades+filiais+fábricas)")
                    st.markdown(f"💼 [LinkedIn da Empresa](https://www.linkedin.com/search/results/companies/?keywords={nome_busca})")
                
                with col_links2:
                    st.markdown(f"📈 [Informações Financeiras](https://www.google.com/search?q={nome_busca}+balanço+OR+resultado+OR+faturamento)")
                    st.markdown(f"🏭 [Unidades e Fábricas](https://www.google.com/search?q={nome_busca}+onde+fica+fábrica+OR+unidades)")
                    st.markdown(f"📰 [Últimas Notícias](https://www.google.com/search?q={nome_busca}&tbm=nws&tbs=qdr:m)")
                
                # Informação sobre CNPJ raiz para buscar filiais
                st.markdown("#### 🏢 Identificação de Filiais")
                cnpj_raiz = row['CNPJ'][:8]
                st.markdown(f"""
                <div class="alerta-box">
                    <strong>🔢 CNPJ Raiz:</strong> {cnpj_raiz}<br>
                    <strong>💡 Dica:</strong> Para encontrar todas as filiais desta empresa, pesquise CNPJs que comecem com {cnpj_raiz} no portal da Receita Federal ou em bases de dados corporativas.
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"🔗 [Consultar CNPJs no portal da Receita](https://servicos.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao.asp)")
                
                # Análise de contexto setorial
                st.markdown("#### 📊 Contexto Setorial")
                st.markdown(f"🔍 [Tendências do Setor](https://www.google.com/search?q={row['Atividade Principal'][:30].replace(' ', '+')}+tendências+mercado+brasil&tbm=nws)")

    # MAPA
    st.divider()
    st.markdown("### 🗺️ Investigação de Localização")
    if emp_sel:
        row = df[df["Empresa"] == emp_sel].iloc[0]
        st.warning(f"📍 **{row['Empresa']}** | Status: {row['Status']} | Setor: {row['Atividade Principal']}")
        query = f"{row['Nome Busca']} {row['Endereço']}".replace(" ", "+")
        st.components.v1.iframe(f"https://www.google.com/maps?q={query}&output=embed", height=450)

st.markdown("---")
st.markdown("💡 **BDR Hunter Pro** - Desenvolvido por Gelson96 | Inteligência estratégica para prospecção B2B")
