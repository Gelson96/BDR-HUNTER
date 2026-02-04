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

def processar_inteligencia_premium(d):
    porte_cod = d.get('porte')
    cap = d.get('capital_social', 0)
    if porte_cod in [1, "01"]: 
        return "PEQUENO (ME)", "Até R$ 360k*", "1-9*", 360000
    elif porte_cod in [3, "03"]: 
        return "PEQUENO (EPP)", "R$ 360k-4,8M*", "10-49*", 2400000  # Média
    else:
        if cap > 10000000: 
            return "GRANDE", "100M+*", "500+*", 100000000
        elif cap > 1000000: 
            return "MÉDIO", "10M-50M*", "100-250*", 30000000  # Média
        else: 
            return "MÉDIO", "4,8M+*", "50+*", 10000000

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
    for i, cnpj_bruto in enumerate(lista_cnpjs):
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        try:
            res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            if res.status_code == 200:
                d = res.json()
                porte, fat, func, fat_anual = processar_inteligencia_premium(d)
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                status = verificar_situacao_especial(d)
                
                dados_finais.append({
                    "Empresa": fantasia,
                    "Status": status,
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
                    "Faturamento_Numerico": fat_anual
                })
        except: continue
        progresso.progress((i + 1) / len(lista_cnpjs))
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
        df.drop(columns=['Endereço', 'Nome Busca', 'Faturamento_Numerico']),
        column_config={"LinkedIn": st.column_config.LinkColumn("Pessoas"), "WhatsApp": st.column_config.LinkColumn("Zap")},
        hide_index=True, use_container_width=True
    )
    
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
