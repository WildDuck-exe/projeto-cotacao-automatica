"""
Model Context Protocol (MCP) para Processamento de Pedidos de Materiais Elétricos

Este módulo implementa a lógica para interpretar pedidos de clientes, identificar produtos
e extrair quantidades, utilizando uma base de dados de produtos e sinônimos.
"""
import csv
import re
import unicodedata

def remover_acentos(texto):
    """Remove acentos de uma string."""
    nfkd_form = unicodedata.normalize(\'NFKD\', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalizar_texto(texto):
    """Normaliza o texto: minúsculas, sem acentos e remove caracteres especiais exceto números e letras."""
    texto = remover_acentos(texto.lower())
    texto = re.sub(r\'[^a-z0-9\\s.]\', \'\', texto) # Mantém pontos para mm² e afins
    texto = re.sub(r\'\\s+\', \' \', texto).strip() # Remove espaços extras
    return texto

class ModelContextProtocol:
    def __init__(self, arquivo_produtos, arquivo_sinonimos):
        self.produtos = self._carregar_produtos(arquivo_produtos)
        self.sinonimos = self._carregar_sinonimos(arquivo_sinonimos)
        self.historico_pedidos = [] # Para futuras implementações de contexto

    def _carregar_produtos(self, arquivo_produtos):
        """Carrega a base de dados de produtos do arquivo CSV."""
        produtos_db = {}
        try:
            with open(arquivo_produtos, mode=\'r\', encoding=\'utf-8\') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    # Normaliza a descrição para busca
                    row[\'descricao_normalizada\'] = normalizar_texto(row[\'Descrição\'])
                    produtos_db[row[\'Código\']] = row
        except FileNotFoundError:
            print(f"Erro: Arquivo de produtos não encontrado em {arquivo_produtos}")
            return {}
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
            return {}
        return produtos_db

    def _carregar_sinonimos(self, arquivo_sinonimos):
        """Carrega os sinônimos do arquivo CSV."""
        sinonimos_db = {}
        try:
            with open(arquivo_sinonimos, mode=\'r\', encoding=\'utf-8\') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    termo_normalizado = normalizar_texto(row[\'termo_original\'])
                    sinonimos_db[termo_normalizado] = row[\'codigo_produto\']
        except FileNotFoundError:
            print(f"Erro: Arquivo de sinônimos não encontrado em {arquivo_sinonimos}")
            return {}
        except Exception as e:
            print(f"Erro ao carregar sinônimos: {e}")
            return {}
        return sinonimos_db

    def _extrair_quantidades(self, texto_pedido_normalizado, termo_produto_normalizado):
        """Tenta extrair a quantidade antes ou depois do termo do produto."""
        # Padrão para encontrar números (inteiros ou decimais) antes do termo
        # Ex: "10 metros cabo", "2.5 pecas disjuntor"
        padrao_antes = r\'(\\d+\\.?\\d*|\\d+)\\s*(?:pecas?|pcs?|unidades?|unid?|metros?|mts?|m|cm)?\\s*\' + re.escape(termo_produto_normalizado)
        match_antes = re.search(padrao_antes, texto_pedido_normalizado)
        if match_antes:
            try:
                return float(match_antes.group(1).replace(\'\', \'.\'))
            except ValueError:
                pass
        
        # Padrão para encontrar números (inteiros ou decimais) depois do termo (menos comum para quantidades)
        # Ex: "cabo 10 metros", "disjuntor 2 pecas"
        padrao_depois = re.escape(termo_produto_normalizado) + r\'\\s*(\\d+\\.?\\d*|\\d+)\\s*(?:pecas?|pcs?|unidades?|unid?|metros?|mts?|m|cm)?\'
        match_depois = re.search(padrao_depois, texto_pedido_normalizado)
        if match_depois:
            try:
                return float(match_depois.group(1).replace(\'\', \'.\'))
            except ValueError:
                pass
        return 1 # Quantidade padrão se não encontrada

    def identificar_produto(self, trecho_pedido):
        """Identifica um produto no trecho do pedido, usando sinônimos e a base de produtos."""
        trecho_normalizado = normalizar_texto(trecho_pedido)

        # 1. Tenta correspondência direta com sinônimos
        for termo_sinonimo, codigo_produto in self.sinonimos.items():
            if termo_sinonimo in trecho_normalizado:
                if codigo_produto in self.produtos:
                    quantidade = self._extrair_quantidades(trecho_normalizado, termo_sinonimo)
                    return {"codigo": codigo_produto, "descricao": self.produtos[codigo_produto][\'Descrição\'], "quantidade": quantidade, "preco_unitario": float(self.produtos[codigo_produto][\'Preço\'])}

        # 2. Tenta correspondência com descrições normalizadas dos produtos
        # Ordena por comprimento da descrição para priorizar correspondências mais longas/específicas
        descricoes_ordenadas = sorted(self.produtos.values(), key=lambda x: len(x[\'descricao_normalizada\']), reverse=True)
        for produto_info in descricoes_ordenadas:
            if produto_info[\'descricao_normalizada\'] in trecho_normalizado:
                quantidade = self._extrair_quantidades(trecho_normalizado, produto_info[\'descricao_normalizada\'])
                return {"codigo": produto_info[\'Código\'], "descricao": produto_info[\'Descrição\'], "quantidade": quantidade, "preco_unitario": float(produto_info[\'Preço\'])}
        
        return None

    def processar_pedido(self, texto_pedido):
        """Processa o texto completo do pedido para identificar múltiplos produtos e suas quantidades."""
        self.historico_pedidos.append(texto_pedido) # Adiciona ao histórico
        texto_pedido_normalizado = normalizar_texto(texto_pedido)
        
        produtos_identificados = []
        texto_restante = texto_pedido_normalizado

        # Tenta identificar produtos usando sinônimos primeiro, dos mais longos para os mais curtos
        sinonimos_ordenados = sorted(self.sinonimos.keys(), key=len, reverse=True)
        for termo_sinonimo in sinonimos_ordenados:
            if termo_sinonimo in texto_restante:
                codigo_produto = self.sinonimos[termo_sinonimo]
                if codigo_produto in self.produtos:
                    quantidade = self._extrair_quantidades(texto_restante, termo_sinonimo)
                    produto_info = self.produtos[codigo_produto]
                    produtos_identificados.append({
                        "codigo": codigo_produto,
                        "descricao": produto_info[\'Descrição\'],
                        "quantidade": quantidade,
                        "preco_unitario": float(produto_info[\'Preço\']),
                        "preco_total_item": quantidade * float(produto_info[\'Preço\'])
                    })
                    # Remove o trecho identificado para evitar re-identificação
                    # Tenta remover de forma mais robusta, considerando a quantidade
                    padrao_remocao = r\'(\\d+\\.?\\d*|\\d+)?\\s*(?:pecas?|pcs?|unidades?|unid?|metros?|mts?|m|cm)?\\s*\' + re.escape(termo_sinonimo)
                    texto_restante = re.sub(padrao_remocao, \'\', texto_restante, 1).strip()
                    texto_restante = re.sub(r\'\\s*e\\s*|\\s*,\\s*\', \' \', texto_restante).strip() # Limpa conectivos

        # Tenta identificar produtos restantes usando descrições diretas
        descricoes_ordenadas = sorted(self.produtos.values(), key=lambda x: len(x[\'descricao_normalizada\']), reverse=True)
        for produto_info_db in descricoes_ordenadas:
            desc_norm = produto_info_db[\'descricao_normalizada\']
            if desc_norm in texto_restante:
                # Verifica se este produto já não foi identificado por um sinônimo mais específico
                ja_identificado = False
                for p_id in produtos_identificados:
                    if p_id[\'codigo\'] == produto_info_db[\'Código\']:
                        ja_identificado = True
                        break
                if ja_identificado:
                    continue

                quantidade = self._extrair_quantidades(texto_restante, desc_norm)
                produtos_identificados.append({
                    "codigo": produto_info_db[\'Código\'],
                    "descricao": produto_info_db[\'Descrição\'],
                    "quantidade": quantidade,
                    "preco_unitario": float(produto_info_db[\'Preço\']),
                    "preco_total_item": quantidade * float(produto_info_db[\'Preço\'])
                })
                padrao_remocao = r\'(\\d+\\.?\\d*|\\d+)?\\s*(?:pecas?|pcs?|unidades?|unid?|metros?|mts?|m|cm)?\\s*\' + re.escape(desc_norm)
                texto_restante = re.sub(padrao_remocao, \'\', texto_restante, 1).strip()
                texto_restante = re.sub(r\'\\s*e\\s*|\\s*,\\s*\', \' \', texto_restante).strip()

        total_pedido = sum(p[\'preco_total_item\'] for p in produtos_identificados)
        
        return {
            "pedido_original": texto_pedido,
            "produtos_identificados": produtos_identificados,
            "total_pedido": round(total_pedido, 2),
            "texto_nao_identificado": texto_restante if texto_restante else None
        }

    def gerar_prompt_openai(self, texto_pedido_nao_processado):
        """Gera um prompt otimizado para a OpenAI com base no que não foi identificado."""
        # Esta é uma implementação básica. Pode ser expandida para incluir mais contexto.
        prompt = f"Por favor, ajude a identificar os seguintes itens de um pedido de material elétrico que não puderam ser reconhecidos automaticamente: \'{texto_pedido_nao_processado}\'. "
        prompt += "Liste os produtos e suas quantidades. Se possível, sugira códigos de produtos de uma base de dados fictícia onde os códigos são como \'P001\', \'P002\', etc. "
        prompt += "Exemplo de resposta esperada: [{\'codigo_sugerido\': \'PXXX\', \'descricao\': \'Nome do Produto\', \'quantidade\': Y}, ...]."
        
        # Adicionar exemplos de produtos da base para dar contexto à IA
        if self.produtos:
            prompt += "\\n\\nAlguns exemplos de produtos existentes na base são:"
            count = 0
            for codigo, info_produto in self.produtos.items():
                prompt += f"\\n- {info_produto[\'Descrição\']} (Código: {codigo})"
                count += 1
                if count >= 5: # Limita a 5 exemplos para não exceder o prompt
                    break
        return prompt

# Exemplo de uso (para teste direto do script)
if __name__ == \'__main__\':
    # Caminhos relativos à pasta \'project\' onde o script mcp.py estaria
    # Se mcp.py está em project/mcp/, então os dados estão em ../data/
    arquivo_produtos_exemplo = \'../data/produtos.csv\'
    arquivo_sinonimos_exemplo = \'../data/sinonimos.csv\'

    mcp = ModelContextProtocol(arquivo_produtos_exemplo, arquivo_sinonimos_exemplo)

    if not mcp.produtos or not mcp.sinonimos:
        print("MCP não pôde ser inicializado corretamente devido a erros nos arquivos de dados.")
    else:
        print(f"MCP Inicializado. {len(mcp.produtos)} produtos, {len(mcp.sinonimos)} sinônimos.")
        pedidos_exemplo = [
            "preciso de 10 metros de cabo flexivel 2.5 e 5 disjuntores 16a",
            "me ve 2 lampadas led e 1 interruptor simples",
            "quanto custa 3 tomadas 2p+t e 1 fita isolante",
            "quero 1 eletroduto rigido 3/4 e 2 caixas de passagem 4x2",
            "preciso de 4 conectores wago 3 vias e 1 conector sindal 2.5mm2",
            "20m cabo pp e 3 disjuntor 20 amperes",
            "5 fita isolante e 100m cabo de rede cat5e",
            "um timer digital e duas lampada vapor metalico 150w",
            "quero 15m de cabo coaxial rg6, 2 disjuntores tripolar 20a e 1 sensor de presença",
            "30 abraçadeira de nylon, 1 barramento neutro e 1 quadro de distribuição para 12 disjuntores"
        ]

        for pedido in pedidos_exemplo:
            resultado = mcp.processar_pedido(pedido)
            print(f"\\nPedido: {resultado[\'pedido_original\']}")
            if resultado[\'produtos_identificados\']:
                for produto in resultado[\'produtos_identificados\']:
                    print(f"  - Produto: {produto[\'descricao\']} (Cod: {produto[\'codigo\']}), Qtd: {produto[\'quantidade\']}, Preço Unit.: {produto[\'preco_unitario\']:.2f}, Total Item: {produto[\'preco_total_item\']:.2f}")
                print(f"  Total do Pedido: {resultado[\'total_pedido\']:.2f}")
            if resultado[\'texto_nao_identificado\']:
                print(f"  Texto não identificado: {resultado[\'texto_nao_identificado\']}")
                # print(f"  Prompt OpenAI sugerido: {mcp.gerar_prompt_openai(resultado[\'texto_nao_identificado\'])}")
            print("-" * 30)


