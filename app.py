import streamlit as st
import pandas as pd
import requests
import re

# 1. Configuração da Página
st.set_page_config(page_title="BDR Hunter Pro | Gelson96", layout="wide", page_icon="🚀")

# Link da sua logo
URL_LOGO = "https://static.wixstatic.com/media/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png/v1/fill/w_232,h_67,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png"

# --- CSS PARA CENTRALIZAR TUDO ---
st.markdown(
    f"""
    <style>
    /* Centraliza o Logo */
    .centered-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
    }}
    .centered-container img {{
        width: 450px; /* Tamanho do logo */
        margin-bottom: 10px;
    }}
    /* Centraliza Títulos nativos do Streamlit */
    h1, h2, h3, .stSubheader {{
        text-align: center !important;
        width: 100%;
    }}
    /* Ajusta largura da área de texto */
    .stTextArea {{
        max-width: 1000px;
        margin: 0 auto;
    }}
    </style>
    
    <div class="centered-container">
        <img src="{URL_LOGO}">
    </div>
    """,
    unsafe_allow_html=True
)

# --- TÍTULOS CENTRALIZADOS ---
st.title("BDR Hunter")
st.subheader("Inteligência de Mercado & Prospecção Estratégica")

st.divider()

# --- FUNÇÕES DE LÓGICA ---
def limpar_nome_empresa(nome):
    if not nome: return ""
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def processar_inteligencia_premium(d):
    porte_cod = d.get('porte')
    cap = d.get('capital_social', 0)
    
    if porte_cod in [1, "01"]:
        porte, fat, func = "PEQUENO (ME)", "Até R$ 360.000*", "1 a 9*"
    elif porte_cod in [3, "03"]:
        porte, fat, func = "PEQUENO (EPP)", "R$ 360k a R$ 4,8 Milhões*", "10 a 49*"
    else:
        porte = "MÉDIO OU GRANDE"
        if cap > 10000000:
            fat, func = "Acima de R$ 100 Milhões*", "500+*"
        elif cap > 1000000:
            fat, func = "R$ 10M a R$ 50 Milhões*", "100 a 250*"
        else:
            fat, func = "Acima de R$ 4,8 Milhões*", "50+*"
    return porte, fat, func

def processar_lista(lista_cnpjs):
    dados_finais = []
    progresso = st.progress(0)
    for i, cnpj_bruto in enumerate(lista_cnpjs):
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        try:
            res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            if res.status_code == 200:
                d = res.json()
                porte, fat, func = processar_inteligencia_premium(d)
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                nome_limpo = limpar_nome_empresa(fantasia)
                
                l_link = f"https://www.linkedin.com/search/results/people/?keywords={nome_limpo.replace(' ', '%20')}%20(Comprador%20OR%20Suprimentos%20OR%20Compras)"
                g_link = f"https://www.google.com.br/search?q=whatsapp+telefone+setor+compras+{nome_limpo.replace(' ', '+')}"

                dados_finais.append({
                    "Empresa": fantasia,
                    "Porte Real": porte,
                    "Faturamento Est.*": fat,
                    "Funcionários Est.*": func,
                    "LinkedIn (Decisor)": l_link,
                    "Google (WhatsApp)": g_link,
                    "Telefone (Receita)": d.get('ddd_telefone_1', 'N/D'),
                    "Cidade/UF": f"{d.get('municipio')}/{d.get('uf')}",
                    "Capital Social": f"R$ {float(d.get('capital_social',0)):,.2f}"
                })
        except: continue
        progresso.progress((i + 1) / len(lista_cnpjs))
    return pd.DataFrame(dados_finais)

# --- ÁREA CENTRALIZADA DE INPUT ---
col_in1, col_in2, col_in3 = st.columns([1, 4, 1])
with col_in2:
    entrada = st.text_area("Cole os CNPJs para análise completa:", height=150)
    
    # Botão Centralizado na coluna do meio
    if st.button("🚀 Iniciar Prospecção Inteligente", use_container_width=True):
        if entrada:
            cnpjs = re.findall(r'\d+', entrada)
            if cnpjs:
                df = processar_lista(cnpjs)
                if not df.empty:
                    st.success(f"Análise de {len(df)} empresas concluída!")
                    
                    # Exibição da Tabela em largura total
                    st.dataframe(
                        df, 
                        column_config={
                            "LinkedIn (Decisor)": st.column_config.LinkColumn("Pessoas"), 
                            "Google (WhatsApp)": st.column_config.LinkColumn("Buscar Zap")
                        }, 
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Baixar Planilha Unificada", data=csv, file_name="leads_bdr.csv", use_container_width=True)
            else:
                st.error("Nenhum CNPJ detectado.")
        else:
            st.warning("Por favor, cole os CNPJs.")
