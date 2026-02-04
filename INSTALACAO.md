# 🚀 BDR Hunter Pro - Guia de Instalação

## 📋 Requisitos

- Python 3.8+
- pip (gerenciador de pacotes)

## 🔧 Instalação Passo a Passo

### 1. Instalar Dependências

```bash
# Dependências obrigatórias
pip install streamlit pandas requests

# SDK OFICIAL do Google Gemini (para notícias)
pip install google-generativeai

# Opcional (para formatação Markdown)
pip install markdown
```

### 2. Obter Chave da API Gemini

1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada (formato: `AIza...`)

### 3. Configurar Secrets (IMPORTANTE)

Crie o arquivo `.streamlit/secrets.toml` na raiz do projeto:

```bash
mkdir .streamlit
touch .streamlit/secrets.toml
```

Edite o arquivo e adicione:

```toml
GEMINI_API_KEY = "AIza...sua_chave_aqui"
```

**⚠️ SEGURANÇA:**
- NUNCA commite `secrets.toml` no Git
- Adicione ao `.gitignore`:
  ```
  .streamlit/secrets.toml
  ```

### 4. Executar o Aplicativo

```bash
streamlit run bdr_hunter_sdk_oficial.py
```

## 🧪 Testar API Gemini (Isolado)

Antes de rodar o app completo, teste se a API está funcionando:

```python
import google.generativeai as genai

# Configure com sua chave
genai.configure(api_key="AIza...sua_chave")

# Teste simples
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Liste 3 empresas brasileiras do setor alimentício.")
print(response.text)
```

Se funcionar → tudo certo! ✅
Se der erro → verifique:
- Chave válida e ativa
- Quota disponível (free tier tem limites)
- Conexão com internet

## 📦 Deploy no Streamlit Cloud

1. Crie conta em: https://streamlit.io/cloud
2. Conecte seu repositório GitHub
3. Configure secrets:
   - Settings → Secrets
   - Cole: `GEMINI_API_KEY = "sua_chave"`
4. Deploy automático!

## 🛠️ Estrutura de Arquivos

```
projeto/
├── bdr_hunter_sdk_oficial.py    # App principal
├── .streamlit/
│   └── secrets.toml              # Chaves API (NÃO COMMITAR)
├── requirements.txt              # Dependências
└── .gitignore                    # Ignora secrets
```

## 📝 requirements.txt

Crie este arquivo para facilitar instalação:

```txt
streamlit>=1.28.0
pandas>=2.0.0
requests>=2.31.0
google-generativeai>=0.3.0
markdown>=3.5.0
```

Instalar tudo de uma vez:
```bash
pip install -r requirements.txt
```

## ⚠️ Solução de Problemas

### Erro: "Module 'google.generativeai' not found"
```bash
pip install google-generativeai --upgrade
```

### Erro: "API Key not found"
- Verifique se `.streamlit/secrets.toml` existe
- Confirme que a chave está entre aspas: `GEMINI_API_KEY = "..."`

### Erro 401/403 na API
- Chave inválida ou expirada
- Regenere em: https://aistudio.google.com/app/apikey

### Erro 429 (Rate Limit)
- Free tier: 60 requisições/minuto
- Aguarde 1 minuto ou upgrade para pago

### Notícias não aparecem
- Verifique logs no terminal
- Teste o script isolado (seção Teste acima)
- Confirme quota disponível

## 📊 Limites Free Tier (Gemini)

| Recurso | Limite |
|---------|--------|
| Requisições/minuto | 60 |
| Requisições/dia | 1.500 |
| Tokens/requisição | 32.000 |

## 🎯 Checklist Final

- [ ] Python 3.8+ instalado
- [ ] Todas dependências instaladas
- [ ] Chave API Gemini obtida
- [ ] Arquivo `secrets.toml` criado
- [ ] Chave adicionada corretamente
- [ ] Teste isolado funcionou
- [ ] App rodando sem erros

## 🆘 Suporte

Problemas? Verifique:
1. Versão do Python: `python --version`
2. Pacotes instalados: `pip list | grep -E "streamlit|google-generativeai"`
3. Logs do Streamlit (terminal)

## 🔐 Boas Práticas de Segurança

1. **NUNCA** hardcode API keys no código
2. Use `st.secrets` para todas chaves
3. Adicione `secrets.toml` ao `.gitignore`
4. Em produção, use variáveis de ambiente
5. Rotacione chaves periodicamente

---

**Desenvolvido por:** Gelson96
**Versão:** 2.0 (SDK Oficial)
**Última atualização:** Fevereiro 2025
