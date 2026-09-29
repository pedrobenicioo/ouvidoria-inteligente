# 🏛️ Ouvidoria Inteligente — Triagem Semântica de Manifestações

Protótipo de triagem de manifestações cidadãs com embeddings de sentenças: comparação de representações, detecção de duplicatas, chunking de textos longos e app Streamlit.

## Executar

```bash
pip install -r requirements.txt
streamlit run app_ouvidoria.py
```

## Conteúdo

| Arquivo | Descrição |
|---|---|
| `analise_comparativa.ipynb` | Entrega 1 — BoW × TF-IDF × embeddings |
| `deteccao_duplicatas.ipynb` | Entrega 2 — `detectar_duplicatas`, heatmap, FP/FN, limiar |
| `chunking_manifestacoes.ipynb` | Entrega 3 — RecursiveCharacterTextSplitter, PCA/t-SNE |
| `app_ouvidoria.py` | Entrega 4 — app com busca, base, espaço vetorial e chunking |
| `ouvidoria_utils.py` | Funções compartilhadas |
| `manifestacoes.json` | 40 manifestações **sintéticas** (`gerar_dados.py`) |
| `duplicatas_reais.json` | Gabarito das duplicatas |
| `RELATORIO.pdf` | Relatório de decisões e aprendizados |

## Regenerar

```bash
python gerar_dados.py               # dados
python gerar_notebooks.py --executar  # notebooks com saídas
python gerar_relatorio.py           # PDF
```

## Notas

- O modelo `BAAI/bge-small-pt-v1.5` sugerido no enunciado estava inacessível; foi usado o `distiluse-base-multilingual-cased-v2`.
- A base de dados é sintética; substitua `manifestacoes.json` pela base real se disponível.

---
Autor: **PEDRO HENRIQUE BENICIO DE OLIVEIRA** — RGM: 33602697

