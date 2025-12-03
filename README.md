# Otimização de serviços com simplex

Este projeto fornece um dashboard interativo (Dash/Plotly) que usa Programação Linear (simplex via `scipy.optimize.linprog`) para sugerir a melhor distribuição de serviços a fim de maximizar o lucro, respeitando o tempo total disponível e limites mínimos/máximos por serviço. Opcionalmente, você pode carregar os serviços já realizados no mês para comparar com o plano otimizado.

Os dados de serviço usados nos exemplos foram extraídos de um prestador de serviço que trabalha com lavagem de carros a domicílio.

## Requisitos
- Python 3.9+ (recomendado 3.10 ou superior)
- Sistema operacional: Windows, macOS ou Linux
- Pacotes Python:
  - `dash`
  - `plotly`
  - `pandas`
  - `scipy`
  - `openpyxl` (leitura de `.xlsx`)

## Instalação
1. Crie e ative um ambiente virtual (Windows PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   Em macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Atualize o `pip` e instale as dependências:
   ```bash
   python -m pip install -U pip
   pip install dash plotly pandas scipy openpyxl
   ```

## Execução
1. Na raiz do projeto, execute:
   ```bash
   python app.py
   ```
2. O navegador abrirá automaticamente em `http://127.0.0.1:8050`. Se não abrir, acesse manualmente esse endereço.

## Estrutura do Projeto
- `app.py`: aplicação Dash, layout, callbacks e orquestração do fluxo.
- `data_manager.py`: leitura/parse de arquivos (CSV/Excel), limpeza e consolidação de dados.
- `optimizer.py`: modelo de otimização linear (simplex) e cálculo das métricas de meta/real.
- `components.py`: componentes visuais, gráficos e tabela detalhada.
- `assets/style.css`: estilos globais do dashboard.
- `templates/`: exemplos de arquivos de entrada.

## Formato dos Arquivos de Entrada
### Template de metas (obrigatório)
Arquivo com os serviços a otimizar. Pode ser `.xlsx`, `.xls` ou `.csv`.
- Colunas obrigatórias (lowercase, sem espaços extras):
  - `servico`, `tempo`, `custo`, `venda`, `minimo`, `maximo`
- Notas:
  - Valores monetários podem conter `R$` e vírgulas; o sistema limpa automaticamente.
  - `tempo=0` é ajustado para `0.01` internamente para evitar divisão por zero.

Exemplo: `templates/serviços.xlsx`.

### Dados realizados (opcional)
Arquivo com o que já foi feito no mês, para comparação.
- Colunas esperadas:
  - `servico`, `quantidade`
- Se não estiver presente, o sistema considera `quantidade=0` para todos.

Exemplos: `templates/servicos_feitos.xlsx`, `templates/servicos_feitos_2.xlsx`.

## Como Usar o Dashboard
1. Na barra lateral:
   - Use "Carregar template" para escolher o arquivo de metas (obrigatório).
   - Use "Carregar mês atual" para enviar os realizados (opcional).
   - Informe "Horas disponíveis no mês" (por padrão `360`).
2. Clique em `CALCULAR OTIMIZAÇÃO`.
3. Interprete os resultados:
   - Sem realizados:
     - KPIs: lucro máximo possível, faturamento esperado, tempo planejado, valor da hora.
     - Gráficos: Pareto de lucratividade e distribuição do tempo.
   - Com realizados:
     - Gauges de comparação: lucro, faturamento e tempo real vs meta.
     - Gráficos: comparativo financeiro e waterfall de ganhos/perdas.
   - Tabela detalhada: mostra `Qtd Ideal` (plano), `Qtd Feita` (real), `Lucro Ideal`, `Lucro Real` e `Diferença`.

## Modelo de Otimização
- Objetivo: maximizar o lucro total.
- Restrição de tempo: soma(`tempo` × `qtd`) ≤ `horas disponíveis`.
- Limites por serviço: `minimo` ≤ `qtd` ≤ `maximo`.
- Solver: `scipy.optimize.linprog(..., method="highs")`.
- Quantidades sugeridas são arredondadas para inteiro (pode haver pequena diferença de tempo total por arredondamento).
- Ordenação de exibição por `rentabilidade_hora`.

Mensagens de inviabilidade:
- Se soma dos tempos mínimos exigidos exceder as horas disponíveis, o sistema informa o déficit.

## Boas Práticas para Preparar os Arquivos
- Garanta que os nomes dos serviços coincidam entre o template e realizado.
- Use o formato decimal consistente (`,` em CSV é suportado; o sistema converte vírgulas para ponto).
- Revise `minimo`/`maximo` e `tempo` por serviço; valores inválidos afetam o plano.

## Exemplos Rápidos
- Template: `templates/serviços.xlsx`.
- Realizado: `templates/servicos_feitos.xlsx`.
- Passos:
  1. Execute `python app.py`.
  2. Carregue os dois arquivos e defina as horas.
  3. Clique em `CALCULAR OTIMIZAÇÃO` para ver o plano e comparativos.

## Resolução de Problemas
- "INVIÁVEL": aumente as horas disponíveis ou reduza `minimo` em serviços com grande tempo.
- Erro de leitura: confirme extensão (`.csv`, `.xlsx`, `.xls`) e se há cabeçalhos corretos.
- Gráficos vazios: ocorre quando nenhum realizado foi informado; é normal.
- Performance: para bases muito grandes, considere manter tipos numéricos limpos e evitar células formatadas com símbolos.

## Desenvolvimento
- O projeto está organizado em módulos simples; alterações comuns:
  - Regras/visualizações: `components.py`.
  - Regras de limpeza/consolidação: `data_manager.py`.
  - Restrições/objetivo da otimização: `optimizer.py`.
  - Layout e callbacks: `app.py`.
- Para suporte a quantidades estritamente inteiras no solver, considere migrar para um solver de programação inteira (ex.: PuLP/OR-Tools).

---

Qualquer dúvida ou melhoria desejada (novas restrições de negócio, exportação de plano para Excel/CSV, etc.), entre em contato ou abra uma issue.
