
---

# Detecção de Oportunidades de Sanduíche MEV via Grafo de Fluxo de Controle de Contratos Inteligentes

Este artefato contém a implementação da ferramenta de análise estática desenvolvida para detectar oportunidades de Sanduíche MEV em contratos inteligentes Ethereum, utilizando Grafos de Fluxo de Controle (CFG).

**Resumo do Artigo:** Estratégias do tipo Sanduı́che MEV exploram configurações inseguras de derrapagem de preço em trocas descentralizadas (DEXs), gerando perdas financeiras significativas. Enquanto mitigações atuais focam na camada
de rede, há uma lacuna em ferramentas preventivas de auditoria de código. Este trabalho propõe uma abordagem de análise estática baseada em Gráfico de Fluxo de Controle para detectar, em tempo de desenvolvimento, a ausência
de proteções de limite de preço em interações com AMMs. Nossa metodologia rastreia o código de contratos inteligentes que executam nas redes blockchain para identificar parâmetros inseguros ou não validados pelo usuário. Resultados preliminares indicam eficácia na detecção de oportunidades de Sanduı́che MEV por ferramentas tradicionais, contribuindo para a segurança preventiva no ecossistema DeFi.

# Estrutura do README.md

O repositório está organizado da seguinte forma:

* `detect_sandwich/`: Módulo principal contendo a lógica de detecção e análise de CFG.
* `smart_contracts_database/`: Banco de dados de contratos inteligentes utilizados para validação, incluindo contratos vulneráveis.
* `requirements.txt`: Lista de dependências Python necessárias.
* `run_tests.ipynb`: Notebook interativo para execução rápida de testes e visualização de resultados.
* `setup.py`: Script de instalação do pacote do detector na ferramenta Slither.
* `test.py`: Script de teste mínimo para verificação da instalação.

# Selos Considerados

Os autores solicitam a avaliação para os seguintes selos:

* **Disponíveis (SeloD):** O código está publicamente disponível e estruturado.
* **Funcionais (SeloF):** O artefato contém instruções de instalação e teste mínimo.
* **Sustentáveis (SeloS):** O código está modularizado e documentado.

# Informações básicas

O artefato foi desenvolvido para execução em sistemas Linux/macOS.

* **Requisitos de Software:** * Python 3.10 ou superior.
* Gerenciador de pacotes `pip`.
* (Opcional) Jupyter Notebook para executar o `run_tests.ipynb`.


* **Requisitos de Hardware:** * Mínimo de 4GB de RAM.
* 100MB de espaço em disco.



# Dependências

As principais dependências incluem bibliotecas do compilador da linguagem Solidity e o Analisador Estático Slither:

* `solc-select`: Para compilar contratos inteligentes Solidity.
* `slither-analyzer`: Para análise estática de contratos Solidity.
* Consulte `requirements.txt` para versões exatas e demais bibliotecas necessárias.

# Preocupações com segurança

A execução deste artefato é segura e não exige privilégios de administrador (root). A análise é puramente estática e não interage com redes blockchain reais (mainnet), operando apenas sobre arquivos locais ou bytecode fornecido.

# Instalação

Para configurar o ambiente, execute os seguintes comandos:

```bash
# Clone o repositório
git clone https://github.com/lesc-ufv/static-sandwich-mev-detector.git
cd static-sandwich-mev-detector

# Crie e ative um ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure o detector
python setup.py develop
```

# Teste mínimo

Para verificar se a instalação foi bem-sucedida, execute o script de teste básico que analisa um contrato de exemplo:

```bash
python3 test.py
```

**Resultado esperado:** O código deve imprimir no terminal a saída da ferramenta slither indicando a linha de código das oportunidades de Sanduíche MEV encontradas.

# Experimentos

Esta seção detalha como reproduzir os resultados apresentados nas tabelas de avaliação do artigo.

## Reivindicação #1: Análise de CFG em Contratos Complexos

O tempo de execução deve escalar linearmente com a complexidade do contrato.

* **Configuração:** Notebook `run_tests.ipynb`.
* **Comando:** Execute todas as células do notebook.
* **Resultado esperado:** Gráficos comparativos de tempo de execução, uso de memória RAM e tabela com resultados das detecções.

# LICENSE

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](https://github.com/lesc-ufv/static-sandwich-mev-detector/blob/main/LICENSE) para detalhes.
