# Projeto de Automação de Cotação com IA

Este projeto visa desenvolver uma aplicação funcional para um agente de IA que processa pedidos de materiais elétricos "bagunçados" e gera cotações automáticas. O sistema integra N8N para automação, um Model Context Protocol (MCP) para gerenciar o contexto dos prompts da IA, e uma base de dados de produtos em CSV.

## Estrutura do Projeto

- `project/data/`: Contém os arquivos CSV com a base de produtos e sinônimos.
- `project/n8n/`: Armazenará o workflow do N8N.
- `project/mcp/`: Contém a implementação do Model Context Protocol (MCP) em Python.
- `project/docs/`: Contém a documentação do projeto, relatórios e apresentações.
- `project/mcp_server.py`: O servidor Flask que expõe a funcionalidade do MCP como uma API.
- `project/test_mcp.py`: Script para testar a funcionalidade do MCP.
- `project/generate_test_orders.py`: Script para gerar pedidos fictícios para validação.
- `project/validate_system.py`: Script para validação completa do sistema.

## Como Usar

Instruções detalhadas sobre como configurar o ambiente, rodar o servidor MCP, importar o workflow do N8N e testar o sistema serão fornecidas na documentação `SETUP.md` dentro da pasta `docs`.

## Entregáveis

Todos os entregáveis do projeto serão compilados no arquivo `ENTREGAVEIS.md`.


