import streamlit as st
import pandas as pd
import requests
import re

st.set_page_config(page_title="BDR Hunter Pro - Inteligência Completa", layout="wide")

st.title("🤖 BDR Hunter - Inteligência de Mercado")
st.markdown("### Classificação Completa: Porte, Faturamento e Equipe")

def limpar_nome_empresa(nome):
    if not nome: return ""
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except:
        return "N/D"

def classificar_inteligencia(dado_api):
    porte_cod = str(dado_api.get('porte', ''))
    capital = float(dado_api.get('capital_social', 0))
    
    # Lógica de Porte Detalhado
    if porte_cod in ["01", "1", "03", "3"]:
        porte_real = "PEQUENA (ME/EPP)"
        fat_est = "Até R$ 4,8 Milhões/ano"
        func_est = "1 a 20 funcionários"
    elif porte_cod in ["05", "5"]:
        if capital >= 5000000:
            porte_real = "GRANDE EMPRESA"
            fat_est = "Acima de R$ 300 Milhões/ano"
            func_est = "Mais de 500 funcionários"
        else:
            porte_real = "MÉDIA EMPRESA"
            fat_est = "R$ 4,8 mi a R$ 300 Milhões/ano"
            func_est = "20 a 500 funcionários"
    else:
        porte_real = "NÃO INFORMADO"
        fat_est = "Consultar Capital Social"
        func_est = "N/D"
        
    return porte_real, fat_est, func_est

def processar_lista(lista_cnpjs):
    dados_finais = []
    progresso = st.progress(0)
    
    for i, cnpj_bruto in enumerate(lista_cnpjs):
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        try:
            res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            if res.status_code == 200:
                d = res.json()
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                nome_busca = limpar_nome_empresa(fantasia)
                
                # Obtém classificação inteligente
                porte, faturamento, funcionarios = classificar_inteligencia(d)
                
                # Links de Prospecção
                l_link = f"https://www.linkedin.com/search/results/people/?keywords={nome_busca.replace(' ', '%20')}%20(Comprador%20OR%20Suprimentos)"
                g_link = f"https://www.google.com.br/search?q=whatsapp+compras+{nome_busca.replace(' ', '+')}"
                
                dados_finais.append({
                    "Empresa": fantasia,
                    "PORTE": porte,
                    "Faturamento Estimado": faturamento,
                    "Equipe Estimada": funcionarios,
                    "Capital Social": formatar_moeda(d.get('capital_social')),
                    "LinkedIn": l_link,
                    "WhatsApp (Busca)": g_link,
                    "Cidade/UF": f"{d.get('municipio')}/{d.get('uf')}"
                })
        except:
            continue
        progresso.progress((i + 1) / len(lista_cnpjs))
        
    return pd.DataFrame(dados_finais)

entrada = st.text_area("Cole os CNPJs aqui:", height=150)

if st.button("🚀 Gerar Inteligência de Mercado"):
    if entrada:
        cnpjs = re.findall(r'\d+', entrada)
        df = processar_lista(cnpjs)
        
        if not df.empty:
            st.success("Busca Finalizada!")
            st.dataframe(
                df,
                column_config={
                    "LinkedIn": st.column_config.LinkColumn("Pessoas"),
                    "WhatsApp (Busca)": st.column_config.LinkColumn("Google")
                },
                hide_index=True
            )
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Baixar Planilha Inteligente", data=csv, file_name="leads_completos.csv")
