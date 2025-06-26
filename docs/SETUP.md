# Instruções para Configuração e Uso do Sistema

## Pré-requisitos

### Software Necessário
- **Python 3.9+**: Para executar o MCP e scripts de teste
- **Node.js 18+**: Para executar o N8N
- **VSCode** (opcional): Para edição de código

### Instalação das Dependências

1. **Instalar Python e dependências**:
```bash
# Verificar versão do Python
python3 --version

# Instalar dependências Python (se necessário)
pip3 install csv difflib json re time
```

2. **Instalar N8N**:
```bash
# Instalar N8N globalmente
npm install -g n8n

# OU instalar localmente no projeto
npm install n8n
```

3. **Configurar API da OpenAI** (opcional):
```bash
# Definir variável de ambiente com sua chave da API
export OPENAI_API_KEY="sua_chave_aqui"
```

## Estrutura do Projeto

```
project/
├── data/
│   ├── produtos.csv          # Base de dados de 100 produtos
│   ├── sinonimos.csv         # Mapeamento de sinônimos
│   ├── pedidos_teste.csv     # 10 casos de teste
│   └── pedidos_validacao.csv # 50 pedidos para validação
├── mcp/
│   └── mcp.py               # Implementação do Model Context Protocol
├── n8n/
│   └── workflow.json        # Workflow do N8N
├── docs/
│   ├── README.md
│   └── relatorio_validacao.json
├── test_mcp.py              # Script de teste do MCP
├── generate_test_orders.py  # Gerador de pedidos fictícios
├── validate_system.py       # Validação completa do sistema
└── README.md
```

## Como Usar o Sistema

### 1. Testar o MCP Isoladamente

```bash
cd project
python3 mcp/mcp.py
```

Este comando testa o MCP com um pedido de exemplo e mostra:
- Produtos identificados
- Produtos não identificados
- Prompt gerado para a OpenAI

### 2. Executar Testes com Casos Predefinidos

```bash
cd project
python3 test_mcp.py
```

Executa os 10 casos de teste e mostra:
- Taxa de sucesso por caso
- Produtos identificados vs. não identificados
- Total das cotações

### 3. Gerar Pedidos Fictícios para Validação

```bash
cd project
python3 generate_test_orders.py
```

Gera 50 pedidos fictícios realistas para teste de validação.

### 4. Executar Validação Completa

```bash
cd project
python3 validate_system.py
```

Processa 50 pedidos e mede:
- Taxa de sucesso (meta: 80%+)
- Tempo de processamento (meta: <30s)
- Relatório detalhado em JSON

### 5. Configurar e Usar o N8N

#### Iniciar o N8N:
```bash
# Se instalado globalmente
n8n

# Se instalado localmente
npx n8n
```

#### Importar o Workflow:
1. Acesse http://localhost:5678
2. Vá em "Workflows" > "Import from File"
3. Selecione o arquivo `n8n/workflow.json`
4. Configure as credenciais da OpenAI (se necessário)

#### Testar o Workflow:
1. Ative o workflow
2. Use o webhook endpoint para enviar pedidos
3. Exemplo de requisição:
```bash
curl -X POST http://localhost:5678/webhook/processar-pedido \
  -H "Content-Type: application/json" \
  -d '{"pedido": "preciso de 10 metros de cabo flexivel 2.5 e 5 disjuntores 16a"}'
```

## Configuração do MCP

O Model Context Protocol (MCP) é implementado como uma biblioteca Python que:

1. **Carrega dados**: Lê produtos.csv e sinonimos.csv
2. **Normaliza texto**: Remove acentos, pontuação e padroniza
3. **Extrai quantidades**: Identifica números, unidades e produtos
4. **Busca sinônimos**: Usa correspondência exata e similaridade
5. **Gera prompts**: Cria contexto otimizado para OpenAI

### Personalizar Sinônimos

Edite o arquivo `data/sinonimos.csv` para adicionar novos sinônimos:

```csv
termo_original,sinonimo,codigo_produto
cabo 2.5,cabo flexível 2,5mm²,P001
fio 2.5,cabo flexível 2,5mm²,P001
```

### Adicionar Produtos

Edite o arquivo `data/produtos.csv` para adicionar novos produtos:

```csv
codigo,descricao,preco
P101,Novo Produto,99.90
```

## Limitações e Melhorias

### Limitações Atuais
- Taxa de sucesso de ~63% (abaixo da meta de 80%)
- Dificuldade com pedidos complexos (múltiplos produtos)
- Sinônimos limitados (apenas 47 mapeamentos)

### Sugestões de Melhoria
1. **Expandir sinônimos**: Adicionar mais variações de escrita
2. **Melhorar extração**: Usar NLP mais avançado
3. **Integrar OpenAI**: Implementar chamadas reais à API
4. **Feedback loop**: Aprender com erros para melhorar

## Suporte e Troubleshooting

### Problemas Comuns

1. **Erro de CSV**: Verificar encoding UTF-8 e vírgulas nas descrições
2. **N8N não inicia**: Verificar se a porta 5678 está livre
3. **MCP não encontra produtos**: Verificar caminhos dos arquivos CSV

### Logs e Debug

Para debug detalhado, modifique o MCP para incluir mais logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Contato

Para suporte adicional, consulte a documentação do projeto ou entre em contato com a equipe de desenvolvimento.

