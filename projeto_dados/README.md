
## Perguntas de negocio

Este dashboard responde as seguintes perguntas:

1. Qual mes gera mais receita?
2. Qual categoria gera mais receita?
3. Qual e o ticket medio por venda?
4. Quantas vendas e quantos itens foram vendidos no periodo?
5. Quais produtos mais contribuem para a receita?

## Metricas oficiais

Regra de modelagem:
- Grao da tabela fato: 1 linha = 1 item de uma venda.

### 1) Receita Total
- Definicao: soma da receita de todos os itens vendidos.
- Formula: `SUM(sales_fact[revenue])`
- Interpretacao: valor total faturado no periodo filtrado.

### 2) Quantidade de Itens
- Definicao: soma das quantidades vendidas por item.
- Formula: `SUM(sales_fact[quantity])`
- Interpretacao: volume total de itens vendidos.

### 3) Quantidade de Vendas
- Definicao: contagem unica de vendas.
- Formula: `DISTINCTCOUNT(sales_fact[sale_id])`
- Interpretacao: numero total de pedidos/vendas.

### 4) Ticket Medio
- Definicao: receita media por venda.
- Formula: `DIVIDE([Receita Total], [Quantidade de Vendas])`
- Interpretacao: quanto, em media, cada venda gera de receita.

### 5) Preco Medio
- Definicao: media do preco unitario dos itens.
- Formula: `AVERAGE(sales_fact[unit_price])`
- Interpretacao: referencia de preco medio dos produtos vendidos.

### 6) Receita por Mes
- Definicao: receita agregada por ano-mes da `sale_date`.
- Formula: `SUM(sales_fact[revenue])` (com agrupamento por mes no visual)
- Interpretacao: sazonalidade e desempenho mensal.

### 7) Receita por Categoria
- Definicao: receita agregada por `category`.
- Formula: `SUM(sales_fact[revenue])` (com agrupamento por categoria no visual)
- Interpretacao: categorias que mais contribuem para o faturamento.

## Medidas DAX (Power BI)

```DAX
Receita Total = SUM(sales_fact[revenue])
Qtd Itens = SUM(sales_fact[quantity])
Qtd Vendas = DISTINCTCOUNT(sales_fact[sale_id])
Ticket Medio = DIVIDE([Receita Total], [Qtd Vendas])
Preco Medio = AVERAGE(sales_fact[unit_price])
```

## Valores de validacao (dataset atual)

Use estes numeros para validar se o Power BI esta calculando corretamente:

- Receita Total: `4691.27`
- Qtd Itens: `42`
- Qtd Vendas: `7`
- Ticket Medio: `670.18`
- Mes com maior receita: `2020-01` (`3018.50`)
- Categoria com maior receita: `men's clothing` (`2646.44`)
