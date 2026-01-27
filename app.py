import streamlit as st
import pandas as pd
import requests
import re

# Configuração da Página
st.set_page_config(page_title="BDR Hunter Pro - Unificado", layout="wide")

st.title("🚀 BDR Hunter - Unificado")
st.markdown("### Inteligência de Mercado + Busca de Decisores")

def limpar_nome_empresa(nome):
    if not nome: return ""
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def processar_inteligencia_premium(d):
    """Aplica a lógica de faturamento e funcionários da sua planilha premium"""
    porte_cod = d.get('porte')
    cap = d.get('capital_social', 0)
    
    if porte_cod == 1 or porte_cod == "01":
        porte = "ME (Microempresa)"
        faturamento = "Até R$ 360.000*"
        funcionarios = "1 a 9*"
    elif porte_cod == 3 or porte_cod == "03":
        porte = "EPP (Pequeno Porte)"
        faturamento = "R$ 360k a R$ 4,8 Milhões*"
        funcionarios = "10 a 49*"
    else:
        porte = "Demais (Médio/Grande)"
        if cap > 10000000:
            faturamento = "Acima de R$ 100 Milhões*"
            funcionarios = "500+*"
        elif cap > 1000000:
            faturamento = "R$ 10M a R$ 50 Milhões*"
            funcionarios = "100 a 250*"
        else:
            faturamento = "Acima de R$ 4,8 Milhões*"
            funcionarios = "50+*"
            
    return porte, faturamento, funcionarios

def processar_lista(lista_cnpjs):
    dados_finais = []
    progresso = st.progress(0)
    
    for i, cnpj_bruto in enumerate(lista_cnpjs):
        # Garante 14 dígitos com zeros à esquerda
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        
        try:
            res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            if res.status_code == 200:
                d = res.json()
                
                # 1. Obtém Dados da Planilha Premium
                porte, fat, func = processar_inteligencia_premium(d)
                
                # 2. Prepara Busca de Contatos
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                nome_limpo = limpar_nome_empresa(fantasia)
                
                # Links de Prospecção (Do primeiro código que você gostou)
                l_link = f"https://www.linkedin.com/search/results/people/?keywords={nome_limpo.replace(' ', '%20')}%20(Comprador%20OR%20Suprimentos%20OR%20Compras)"
                g_link = f"https://www.google.com.br/search?q=whatsapp+telefone+setor+compras+{nome_limpo.replace(' ', '+')}"

                dados_finais.append({
                    "Empresa": fantasia,
                    "Porte": porte,
                    "Faturamento Est.*": fat,
                    "Funcionários Est.*": func,
                    "LinkedIn (Decisor)": l_link,
                    "Google (WhatsApp)": g_link,
                    "Telefone (Receita)": d.get('ddd_telefone_1', 'N/D'),
                    "Cidade/UF": f"{d.get('municipio')}/{d.get('uf')}",
                    "Atividade": d.get('cnae_fiscal_descricao')
                })
        except:
            continue
        progresso.progress((i + 1) / len(lista_cnpjs))
        
    return pd.DataFrame(dados_finais)

# --- INTERFACE ---
entrada = st.text_area("Cole os CNPJs para análise completa:", height=150)

if st.button("🚀 Iniciar Prospecção Inteligente"):
    if entrada:
        cnpjs_encontrados = re.findall(r'\d+', entrada)
        if cnpjs_encontrados:
            df = processar_lista(cnpjs_encontrados)
            
            if not df.empty:
                st.success(f"Análise de {len(df)} empresas concluída!")
                
                # Exibe a tabela com links clicáveis
                st.dataframe(
                    df,
                    column_config={
                        "LinkedIn (Decisor)": st.column_config.LinkColumn("Ver Pessoas"),
                        "Google (WhatsApp)": st.column_config.LinkColumn("Buscar Zap")
                    },
                    hide_index=True
                )
                
                # Exportação
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Baixar Planilha Unificada (CSV)", data=csv, file_name="prospeccao_unificada.csv")
        else:
            st.error("Nenhum CNPJ encontrado no texto.")
    else:
        st.warning("Por favor, cole os CNPJs.")
