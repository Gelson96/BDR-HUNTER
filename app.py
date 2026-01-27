import streamlit as st
import pandas as pd
import requests
import re

# 1. Configuração da Página (Wide mode para usar toda a tela)
st.set_page_config(page_title="BDR Hunter Pro | Gelson96", layout="wide", page_icon="🚀")

# Link da sua logo
URL_LOGO = "https://static.wixstatic.com/media/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png/v1/fill/w_232,h_67,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png"

# --- CSS PARA CENTRALIZAR E AMPLIAR O LOGO ---
st.markdown(
    f"""
    <style>
    .centered-logo {{
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }}
    .centered-logo img {{
        width: 400px; /* Aumentei o tamanho aqui */
    }}
    .stTitle {{
        text-align: center;
    }}
    .stSubheader {{
        text-align: center;
    }}
    </style>
    <div class="centered-logo">
        <img src="{URL_LOGO}">
    </div>
    """,
    unsafe_allow_html=True
)

# --- CABEÇALHO CENTRALIZADO ---
st.title("BDR Hunter")
st.markdown("<h3 style='text-align: center; color: gray;'>Inteligência de Mercado & Prospecção</h3>", unsafe_allow_html=True)

st.divider()

# --- FUNÇÕES DE INTELIGÊNCIA ---
def limpar_nome_empresa(nome):
    if not nome: return ""
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def processar_inteligencia_premium(d):
    porte_cod = d.get('porte')
    cap = d.get('capital_social', 0)
    
    if porte_cod in [1, "01"]:
        porte, faturamento, funcionarios = "PEQUENO (ME)", "Até R$ 360.000*", "1 a 9*"
    elif porte_cod in [3, "03"]:
        porte, faturamento, funcionarios = "PEQUENO (EPP)", "R$ 360k a R$ 4,8 Milhões*", "10 a 49*"
    else:
        porte = "MÉDIO OU GRANDE"
        if cap > 10000000:
            faturamento, funcionarios = "Acima de R$ 100 Milhões*", "500+*"
        elif cap > 1000000:
            faturamento, funcionarios = "R$ 10M a R$ 50 Milhões*", "100 a 250*"
        else:
            faturamento, funcionarios = "Acima de R$ 4,8 Milhões*", "50+*"
            
    return porte, faturamento, funcionarios

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
        except:
            continue
        progresso.progress((i + 1) / len(lista_cnpjs))
        
    return pd.DataFrame(dados_finais)

# --- INTERFACE DE ENTRADA (OCUPANDO TODA A LARGURA) ---
entrada = st.text_area("Cole os CNPJs para análise completa:", height=150, placeholder="Ex: 00.000.000/0001-00")

# Centralizar o botão
col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
with col_btn2:
    botao_clicado = st.button("🚀 Iniciar Prospecção", use_container_width=True)

if botao_clicado:
    if entrada:
        cnpjs_encontrados = re.findall(r'\d+', entrada)
        if cnpjs_encontrados:
            df = processar_lista(cnpjs_encontrados)
            
            if not df.empty:
                st.success(f"Análise de {len(df)} empresas concluída!")
                
                # Tabela em largura total
                st.dataframe(
                    df,
                    column_config={
                        "LinkedIn (Decisor)": st.column_config.LinkColumn("Ver Pessoas"),
                        "Google (WhatsApp)": st.column_config.LinkColumn("Buscar Zap")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Baixar Planilha Unificada", data=csv, file_name="leads_bdr_premium.csv", use_container_width=True)
        else:
            st.error("Nenhum CNPJ encontrado.")
    else:
        st.warning("Por favor, cole os CNPJs.")
