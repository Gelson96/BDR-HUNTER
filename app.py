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

def buscar_faturamento_web(nome_empresa, cnpj):
    """Busca faturamento na web para empresas grandes"""
    try:
        # Monta query de busca
        query = f"{nome_empresa} faturamento anual receita"
        url_search = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url_search, headers=headers, timeout=5)
        
        if response.status_code == 200:
            texto = response.text
            
            # Padrões de busca para faturamento
            padroes = [
                r'faturamento.*?R\$\s*([\d.,]+)\s*(bilh[õo]es?|milh[õo]es?)',
                r'receita.*?R\$\s*([\d.,]+)\s*(bilh[õo]es?|milh[õo]es?)',
                r'R\$\s*([\d.,]+)\s*(bilh[õo]es?|milh[õo]es?).*?faturamento',
                r'R\$\s*([\d.,]+)\s*(bilh[õo]es?|milh[õo]es?).*?receita'
            ]
            
            for padrao in padroes:
                match = re.search(padrao, texto, re.IGNORECASE)
                if match:
                    valor_str = match.group(1).replace('.', '').replace(',', '.')
                    try:
                        valor = float(valor_str)
                        unidade = match.group(2).lower()
                        
                        if 'bilh' in unidade:
                            return valor * 1_000_000_000, "WEB"
                        elif 'milh' in unidade:
                            return valor * 1_000_000, "WEB"
                    except:
                        continue
        
        return None, None
    except:
        return None, None

def processar_inteligencia_premium(d):
    porte_cod = d.get('porte')
    cap = d.get('capital_social', 0)
    fantasia = d.get('nome_fantasia') or d.get('razao_social')
    cnpj = d.get('cnpj', '')
    
    # Determina se é empresa grande para buscar faturamento real
    is_grande = False
    if porte_cod in [5, "05"] or cap > 10000000:
        is_grande = True
    
    # Tenta buscar faturamento real na web para empresas grandes
    faturamento_real = None
    fonte = "EST"
    
    if is_grande:
        fat_web, fonte_web = buscar_faturamento_web(fantasia, cnpj)
        if fat_web:
            faturamento_real = fat_web
            fonte = fonte_web
    
    # Se não encontrou faturamento real, usa estimativas
    if faturamento_real:
        if faturamento_real > 100_000_000:
            return "GRANDE", f"R$ {faturamento_real/1_000_000:.1f}M*", "500+*", faturamento_real, fonte
        elif faturamento_real > 10_000_000:
            return "MÉDIO-GRANDE", f"R$ {faturamento_real/1_000_000:.1f}M*", "100-500*", faturamento_real, fonte
        else:
            return "MÉDIO", f"R$ {faturamento_real/1_000_000:.1f}M*", "50-100*", faturamento_real, fonte
    
    # Estimativas padrão
    if porte_cod in [1, "01"]: 
        return "PEQUENO (ME)", "Até R$ 360k*", "1-9*", 360000, "EST"
    elif porte_cod in [3, "03"]: 
        return "PEQUENO (EPP)", "R$ 360k-4,8M*", "10-49*", 2400000, "EST"
    else:
        if cap > 10000000: 
            return "GRANDE", "100M+*", "500+*", 100000000, "EST"
        elif cap > 1000000: 
            return "MÉDIO", "10M-50M*", "100-250*", 30000000, "EST"
        else: 
            return "MÉDIO", "4,8M+*", "50+*", 10000000, "EST"

def verificar_situacao_especial(d):
    # Verifica no nome e na situação especial da Receita
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
                porte, fat, func, fat_anual, fonte = processar_inteligencia_premium(d)
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                status_emp = verificar_situacao_especial(d)
                
                # Indica se o faturamento foi buscado na web
                fat_display = fat
                if fonte == "WEB":
                    fat_display = f"{fat} 🌐"
                
                dados_finais.append({
                    "Empresa": fantasia,
                    "Status": status_emp,
                    "Atividade Principal": d.get('cnae_fiscal_descricao', 'N/I'),
                    "Porte": porte,
                    "Faturamento Est.*": fat_display,
                    "Funcionários Est.*": func,
                    "Capital Social": f"R$ {float(d.get('capital_social',0)):,.2f}",
                    "Cidade/UF": f"{d.get('municipio')}/{d.get('uf')}",
                    "LinkedIn": f"https://www.linkedin.com/search/results/people/?keywords={limpar_nome_empresa(fantasia).replace(' ', '%20')}%20(Comprador%20OR%20Suprimentos)",
                    "WhatsApp": f"https://www.google.com.br/search?q=whatsapp+telefone+setor+compras+{fantasia.replace(' ', '+')}",
                    "Endereço": f"{d.get('logradouro')}, {d.get('numero')} - {d.get('municipio')}",
                    "Nome Busca": limpar_nome_empresa(fantasia),
                    "Faturamento_Numerico": fat_anual,
                    "Fonte": fonte
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
    
    # Inicializar faturamento real se não existir
    if 'faturamento_real' not in st.session_state:
        st.session_state.faturamento_real = {}
    
    st.dataframe(
        df.drop(columns=['Endereço', 'Nome Busca', 'Faturamento_Numerico']),
        column_config={
            "LinkedIn": st.column_config.LinkColumn("Pessoas"), 
            "WhatsApp": st.column_config.LinkColumn("Zap"),
            "Fonte": st.column_config.TextColumn("📊 Fonte", help="EST=Estimativa | WEB=Busca Web")
        },
        hide_index=True, use_container_width=True
    )
    
    # --- SEÇÃO PARA INSERIR FATURAMENTO REAL ---
    st.divider()
    st.markdown("### 💼 Faturamento Real (Opcional)")
    st.info("💡 **Dica:** Se você possui o faturamento real de alguma empresa, insira abaixo para um cálculo mais preciso. Caso contrário, usaremos as estimativas.")
    
    col_fat1, col_fat2 = st.columns(2)
    with col_fat1:
        empresa_selecionada = st.selectbox(
            "Selecione a empresa:",
            [""] + df["Empresa"].tolist(),
            key="select_empresa_fat"
        )
    
    with col_fat2:
        if empresa_selecionada:
            faturamento_input = st.number_input(
                "Faturamento Anual Real (R$):",
                min_value=0.0,
                value=float(st.session_state.faturamento_real.get(empresa_selecionada, 0)),
                step=10000.0,
                format="%.2f",
                key="input_fat"
            )
            
            if st.button("💾 Salvar Faturamento Real"):
                st.session_state.faturamento_real[empresa_selecionada] = faturamento_input
                st.success(f"✅ Faturamento salvo para {empresa_selecionada}!")
                st.rerun()
    
    # Atualizar dataframe com faturamentos reais
    for empresa, fat_real in st.session_state.faturamento_real.items():
        if fat_real > 0:
            df.loc[df["Empresa"] == empresa, "Faturamento_Numerico"] = fat_real
    
    # Mostrar empresas com faturamento real cadastrado
    if st.session_state.faturamento_real:
        empresas_com_fat_real = {k: v for k, v in st.session_state.faturamento_real.items() if v > 0}
        if empresas_com_fat_real:
            st.success(f"✅ **{len(empresas_com_fat_real)} empresa(s)** com faturamento real cadastrado:")
            for emp, fat in empresas_com_fat_real.items():
                st.write(f"• {emp}: **R$ {fat:,.2f}**")
    
    # Mostrar quantas empresas tiveram faturamento buscado na web
    empresas_web = df[df['Fonte'] == 'WEB']
    if not empresas_web.empty:
        st.info(f"🌐 **{len(empresas_web)} empresa(s) grande(s)** tiveram faturamento buscado automaticamente na web (indicadas com 🌐)")
    
    # --- CÁLCULO DE POTENCIAL DE EMBALAGENS ---
    st.divider()
    st.markdown("### 📦 Potencial de Compra de Embalagens")
    
    potencial_anual_total = df['Faturamento_Numerico'].sum() * 0.03
    potencial_mensal_total = potencial_anual_total / 12
    
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
    kg_mensal = potencial_mensal_total / preco_kg if preco_kg > 0 else 0
    kg_anual = potencial_anual_total / preco_kg if preco_kg > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="potencial-box">
                <div style="font-size: 1.2em;">💰 Potencial Anual</div>
                <div class="potencial-valor">R$ {potencial_anual_total:,.2f}</div>
                <div style="font-size: 1.1em; margin-top: 10px;">⚖️ {kg_anual:,.2f} kg</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="potencial-box">
                <div style="font-size: 1.2em;">📅 Potencial Mensal</div>
                <div class="potencial-valor">R$ {potencial_mensal_total:,.2f}</div>
                <div style="font-size: 1.1em; margin-top: 10px;">⚖️ {kg_mensal:,.2f} kg</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="potencial-box">
                <div style="font-size: 1.2em;">📊 Preço/KG</div>
                <div class="potencial-valor">R$ {preco_kg:,.2f}</div>
                <div style="font-size: 1.1em; margin-top: 10px;">💼 Valor configurado</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.info("💡 **Estimativa baseada em:** 3% do faturamento anual médio estimado de todas as empresas analisadas.")
    
    st.download_button("📥 Baixar Relatório", data=df.to_csv(index=False).encode('utf-8-sig'), file_name="bdr_hunter_risk.csv", use_container_width=True)

    # MAPA
    st.divider()
    emp_sel = st.selectbox("Investigar Fachada:", df["Empresa"].tolist())
    if emp_sel:
        row = df[df["Empresa"] == emp_sel].iloc[0]
        st.warning(f"Status: {row['Status']} | Setor: {row['Atividade Principal']}")
        query = f"{row['Nome Busca']} {row['Endereço']}".replace(" ", "+")
        st.components.v1.iframe(f"https://www.google.com/maps?q={query}&output=embed", height=450)
