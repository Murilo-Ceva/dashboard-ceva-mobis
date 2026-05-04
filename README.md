# 📊 Dashboard CEVA - Guia de Uso

## 🎯 Como Funciona Agora?

### 1. **Um CSV Base para Tudo**
O arquivo `BASE OTD.csv` alimenta **TODAS as páginas** do dashboard automaticamente.

```
BASE OTD.csv (5.944 NFs)
      ↓
Parser Python (parse_base_otd.py)
      ↓
dashboard_data.json
      ↓
Dashboard (todas as 8 páginas atualizam)
```

### 2. **Cada Página Tem Seu "Upload CSV"**
- **Visão Geral**: Botão "📊 Importar CSV"
- **OTD por Transportadora**: Botão "📊 Importar CSV"
- **OTD por Dealer**: Botão "📊 Importar CSV"
- **OTD por UF**: Botão "📊 Importar CSV"
- **OTD por Dia**: Botão "📊 Importar CSV"
- **Ocorrências/Drivers**: Botão "📊 Importar CSV"
- **Network Design**: Botão "📊 Importar CSV"
- **Resumo TSP**: Botão "📊 Importar CSV"

Quando você clica em qualquer um, **TODOS os dados são atualizados** simultaneamente.

---

## 🚀 Passo a Passo para Usar

### **Passo 1: Ter o servidor rodando**
```powershell
cd "c:\Users\AnjosM\Downloads\Dashboard - CEVA"
python server.py
```

### **Passo 2: Abrir o dashboard**
Acesse no navegador:
```
http://localhost:8000/mobis_dashboard.html
```

### **Passo 3: Importar CSV (Opcional)**
Se tiver um novo CSV `BASE OTD.csv`, clique em **"📊 Importar CSV"** em qualquer página e selecione o arquivo.

> **OBS**: Os dados já estão carregados! Se não mudou o CSV, não precisa importar de novo.

---

## ✅ O que Funciona Agora?

| Recurso | Status | Descrição |
|---------|--------|-----------|
| **Visão Geral** | ✅ | Resume OTD, volumes, NFs |
| **OTD por TSP** | ✅ | Ranking das transportadoras |
| **OTD por Dealer** | ✅ | Performance de cada dealer |
| **OTD por UF** | ✅ | Por estado de destino |
| **OTD por Dia** | ✅ | Evolução diária |
| **Ocorrências** | ✅ | Problemas de entrega |
| **Network** | ✅ | Estrutura de dealers |
| **Resumo TSP** | ✅ | Consolidado por transportadora |
| **Filtros** | ⏳ | Em desenvolvimento (compatível com dados) |
| **Logo** | ✅ | Embutido em base64 |
| **Avatar** | ✅ | Foto Murilo carregada |
| **Email** | ✅ | EXT.Murilo.Anjos@cevalogistics.com |

---

## 📊 Dados Disponíveis

Depois do upload, você tem acesso a:

### **Por Transportadora (11)**
- TERMACO: 98.6% OTD
- CARVALIMA: 98.3% OTD
- BVLOG: 97.4% OTD
- TRANSTRY: 92.7% OTD
- CAMILO: 91.9% OTD
- RISSO: 88.4% OTD
- *(e mais 5...)*

### **Por Dealer (147)**
Todos os dealers com OTD individual

### **Por UF (27)**
Todos os estados com performance

### **Por Dia (31)**
Evolução de 1º a 31 de abril/2026

### **Ocorrências (25 tipos)**
- Avaria: 22
- Extravio: 16
- Feriado municipal: 12
- Recusa: 8
- *(e mais 21...)*

---

## 🔄 Como Atualizar Dados?

### **Opção 1: Clique em "Importar CSV"**
1. Em qualquer página, clique **"📊 Importar CSV"**
2. Selecione um novo arquivo `BASE OTD.csv`
3. Dashboard recarrega com novos dados

### **Opção 2: Usar Terminal (mais rápido)**
```powershell
cd "c:\Users\AnjosM\Downloads\Dashboard - CEVA"
python parse_base_otd.py
# Depois abra o dashboard e recarregue (F5)
```

---

## 🎨 Sobre os Filtros

Os filtros **"Período", "Região", "Transportadora"** estão implementados no HTML.

**Status**: Podem ser ativados quando precisar filtrar visualizações específicas.

**Como funcionam**:
- **Período**: Filtra por mês (Abril, Março, Fevereiro)
- **Região**: Mapeia UF para região (Sudeste, Sul, Nordeste, etc)
- **Transportadora**: Filtra por TSP (RISSO, TERMACO, etc)

---

## 🐛 Se Algo Não Funcionar

### **1. Dashboard não abre?**
- Verifique se o servidor está rodando: `python server.py`
- Acesse: `http://localhost:8000/mobis_dashboard.html`

### **2. Dados não carregam?**
- Verifique se `dashboard_data.json` existe na pasta
- Se não, execute: `python parse_base_otd.py`

### **3. Upload não funciona?**
- Abra o console do navegador (F12)
- Verifique mensagens de erro
- Certifique-se que o servidor está ativo

### **4. Preciso resetar tudo?**
```powershell
# Delete arquivo de dados
rm dashboard_data.json

# Processe BASE OTD novamente
python parse_base_otd.py

# Recarregue o navegador (F5)
```

---

## 📞 Próximos Passos

Você quer que eu:
- [ ] Ative os filtros para funcionar 100%?
- [ ] Crie visualizações por período/região?
- [ ] Adicione mais métricas (ex: custo, KPIs)?
- [ ] Implemente gráficos dinâmicos?

---

## 📝 Resumo

✅ **Um CSV alimenta tudo**
✅ **147 dealers, 11 transportadoras, 27 UFs**
✅ **5.944 NFs analisadas**
✅ **91,6% de OTD geral**
✅ **Logo e avatar personalizados**
✅ **Pronto para filtros**

**Teste agora!** Abra o navegador e vá para `http://localhost:8000/mobis_dashboard.html`
