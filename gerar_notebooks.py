# Autor: PEDRO HENRIQUE BENICIO DE OLIVEIRA | RGM: 33602697
"""Gera os 3 notebooks (.ipynb) do desafio. Uso: python gerar_notebooks.py [--executar]
Com --executar, roda cada notebook (nbconvert) e grava as saídas dentro do .ipynb."""
import os
import sys

import nbformat as nbf

AQUI = os.path.dirname(os.path.abspath(__file__))
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell


def salvar(nome, celulas):
    nb = nbf.v4.new_notebook()
    nb.cells = [md('**Autor:** PEDRO HENRIQUE BENICIO DE OLIVEIRA — **RGM:** 33602697')] + celulas
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nbf.write(nb, os.path.join(AQUI, nome))
    print("gerado", nome)


SETUP = '''import os, warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, seaborn as sns
import ouvidoria_utils as u

df = u.carregar_manifestacoes()
textos = df["texto"].tolist()
idx = {i: k for k, i in enumerate(df["id"])}   # id -> posição na matriz
print(f"{len(df)} manifestações | categorias: {df.categoria_oficial.value_counts().to_dict()}")
df.head()'''

# ---------------------------------------------------------------------------
# Notebook 1 — Análise comparativa
# ---------------------------------------------------------------------------
nb1 = [
    md("""# Entrega 1 — Análise Comparativa de Representações
**Ouvidoria Inteligente • NLP Aplicado**

Comparamos representações **esparsas** (BoW, TF-IDF) e **densas** (embeddings de sentenças) nas 40 manifestações,
avaliando a similaridade de cosseno em três pares-chave:

| Par | Relação esperada |
|---|---|
| M003 × M017 | mesmo problema (buraco/asfalto esburacado), palavras diferentes |
| M008 × M022 | mesmo problema (posto de saúde sem médico / PSF sem atendimento) |
| M008 × M031 | temas sem relação (saúde × iluminação) |"""),
    code(SETUP),
    md("## 1. Gerando as representações"),
    code('''from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODELOS = {
    "MiniLM-L12 (multilíngue)": "paraphrase-multilingual-MiniLM-L12-v2",
    "distiluse (multilíngue)": "sentence-transformers/distiluse-base-multilingual-cased-v2",
    "multilingual-e5-small": "intfloat/multilingual-e5-small",
}

X_bow = CountVectorizer().fit_transform(textos)
X_tfidf = TfidfVectorizer().fit_transform(textos)
print("BoW    :", X_bow.shape, f"| esparsidade {1 - X_bow.nnz / np.prod(X_bow.shape):.1%}")
print("TF-IDF :", X_tfidf.shape)

sims = {"BoW": cosine_similarity(X_bow), "TF-IDF": cosine_similarity(X_tfidf)}
for rotulo, nome in MODELOS.items():
    modelo = u.carregar_modelo(nome)
    emb = u.codificar(modelo, textos, nome)
    sims[rotulo] = cosine_similarity(emb)
    print(f"{rotulo:26s}: embeddings {emb.shape}")'''),
    md("## 2. Similaridade de cosseno nos pares solicitados"),
    code('''pares = [("M003", "M017", "buraco Av. Brasil × asfalto esburacado"),
         ("M008", "M022", "posto sem médico × falta atendimento PSF"),
         ("M008", "M031", "posto sem médico × lâmpada queimada")]

tabela = pd.DataFrame(
    {rep: [S[idx[a], idx[b]] for a, b, _ in pares] for rep, S in sims.items()},
    index=[f"{a} × {b} — {desc}" for a, b, desc in pares])
tabela.style.format("{:.3f}").background_gradient(cmap="RdYlGn", axis=None, vmin=0, vmax=1)'''),
    code('''# Textos dos pares, para conferência qualitativa
for a, b, _ in pares:
    print(f"{a}: {textos[idx[a]]}\\n{b}: {textos[idx[b]]}\\n")'''),
    md("""## 3. Escala dos scores: a similaridade média muda de modelo para modelo
Um mesmo valor de cosseno significa coisas diferentes em cada representação. Comparamos a distribuição
das similaridades entre **todos** os pares de manifestações distintas."""),
    code('''iu = np.triu_indices(len(df), k=1)
resumo = pd.DataFrame({rep: pd.Series(S[iu]).describe() for rep, S in sims.items()}).T[["mean", "std", "min", "50%", "max"]]
display(resumo.round(3))

fig, ax = plt.subplots(figsize=(9, 3.6))
for rep, S in sims.items():
    sns.kdeplot(S[iu], label=rep, ax=ax, clip=(0, 1))
ax.set(title="Distribuição das similaridades par-a-par (780 pares)", xlabel="cosseno")
ax.legend(); plt.tight_layout(); plt.show()'''),
    md("## 4. Vocabulário compartilhado nos pares (por que BoW/TF-IDF falham?)"),
    code('''import re
def vocab(t):  # palavras (sem stopword curtas) do texto
    return {w for w in re.findall(r"\\w+", t.lower()) if len(w) > 3}
for a, b, desc in pares:
    print(f"{a} × {b}: palavras em comum (>3 letras) = {sorted(vocab(textos[idx[a]]) & vocab(textos[idx[b]]))}")'''),
]
nb1.append(md("""## 5. Discussão e conclusão

**Resultados (execução de referência).**

| Par | BoW | TF-IDF | MiniLM-L12 | distiluse | e5-small |
|---|---|---|---|---|---|
| M003 × M017 (duplicata) | 0,00 | 0,00 | 0,48 | 0,25 | 0,87 |
| M008 × M022 (duplicata) | 0,16 | 0,07 | 0,80 | 0,56 | 0,90 |
| M008 × M031 (sem relação) | 0,00 | 0,00 | 0,10 | 0,14 | 0,89 |

* **BoW e TF-IDF** só enxergam sobreposição *literal* de palavras. M003 e M017 descrevem o mesmo problema sem
  compartilhar nenhuma palavra de conteúdo ("buraco" × "esburacado", "Av. Brasil" × "avenida principal"), por isso o
  cosseno é exatamente 0 — idêntico ao de um par sem qualquer relação (M008 × M031). No par M008 × M022 a única
  palavra em comum é "saúde" e o score fica baixíssimo (0,16 e 0,07). São vetores de ~540 dimensões com 95% de zeros:
  não capturam sinônimos, flexões, siglas (PSF = posto de saúde) nem contexto. O TF-IDF melhora a *ponderação*
  (reduz o peso de palavras comuns), mas não resolve o descasamento de vocabulário.
* **Embeddings densos** aproximam significados: o MiniLM dá 0,80 para posto sem médico × PSF sem atendimento e 0,10 para
  saúde × iluminação — separação clara. O par do buraco recebeu apenas 0,48: acima do não relacionado, mas abaixo do
  esperado, pois M003 traz detalhes específicos (número, acidentes com motos, urgência) que M017 não tem.
  O distiluse produz a mesma ordenação, com scores menores.
* **Cuidado com a escala.** O `multilingual-e5-small` dá 0,87–0,90 a *todos* os pares (média 0,87, desvio 0,02):
  o espaço é muito "anisotrópico" e o cosseno só discrimina com calibração própria — nele o par sem relação (0,89) ficou
  acima de uma duplicata (0,87). Um mesmo limiar (por exemplo 0,85) não é transferível entre modelos.

**Limitações.** *BoW/TF-IDF*: rápidos, interpretáveis e sem GPU, ótimos para termos exatos, mas cegos a sinônimos e
paráfrases. *Embeddings*: capturam semântica e paráfrases, porém são caixas-pretas, dependem do modelo e do domínio
(nenhum foi treinado em português jurídico/administrativo), têm scores não calibrados e podem confundir textos do
mesmo *tema* mas de *problemas diferentes* (ex.: duas reclamações de iluminação em locais distintos). Na prática,
uma abordagem híbrida (léxica + semântica) tende a ser a mais robusta.
"""))
salvar("analise_comparativa.ipynb", nb1)

# ---------------------------------------------------------------------------
# Notebook 2 — Duplicatas
# ---------------------------------------------------------------------------
nb2 = [
    md("""# Entrega 2 — Detecção de Duplicatas Semânticas
Implementamos `detectar_duplicatas(textos, limiar=0.85)` (em `ouvidoria_utils.py`), avaliamos com o
gabarito (`duplicatas_reais.json`) e discutimos a escolha do limiar."""),
    code(SETUP + '''
import inspect'''),
    md("## 1. A função"),
    code('''print(inspect.getsource(u.detectar_duplicatas))'''),
    md("## 2. Embeddings e matriz de similaridade completa"),
    code('''NOME = "paraphrase-multilingual-MiniLM-L12-v2"
modelo = u.carregar_modelo(NOME)
emb = u.codificar(modelo, textos, NOME)
S = u.matriz_similaridade(emb)

fig, ax = plt.subplots(figsize=(13, 11))
sns.heatmap(S, xticklabels=df.id, yticklabels=df.id, cmap="viridis", vmin=0, vmax=1, ax=ax,
            cbar_kws={"label": "similaridade de cosseno"})
ax.set_title(f"Matriz de similaridade — {NOME}")
plt.xticks(fontsize=7, rotation=90); plt.yticks(fontsize=7); plt.tight_layout(); plt.show()'''),
    md("## 3. Pares duplicados com o limiar padrão (0,85)"),
    code('''pares85 = u.detectar_duplicatas(textos, limiar=0.85, embeddings=emb, ids=df.id.tolist())
pd.DataFrame(pares85, columns=["id_a", "id_b", "similaridade"]) if pares85 else "Nenhum par ≥ 0,85"'''),
    md("""## 4. Justificando o limiar
Não há um limiar universal: depende do modelo e do custo de errar. Varremos vários limiares e comparamos com o
gabarito (precisão, revocação e F1). Também avaliamos um **limiar dinâmico** pelo percentil 99 da distribuição
(cerca de 8 dos 780 pares)."""),
    code('''real = u.carregar_duplicatas_reais()
print("Duplicatas reais (gabarito):", sorted(real))

def avaliar(limiar):
    pred = {tuple(sorted((a, b))) for a, b, _ in u.detectar_duplicatas(textos, limiar, emb, ids=df.id.tolist())}
    tp, fp, fn = len(pred & real), len(pred - real), len(real - pred)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return dict(limiar=round(limiar, 3), previstos=len(pred), VP=tp, FP=fp, FN=fn, precisão=p, revocação=r, F1=f1), pred

iu = np.triu_indices(len(df), 1)
p99 = float(np.percentile(S[iu], 99))
limiares = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, round(p99, 3)]
varredura = pd.DataFrame([avaliar(l)[0] for l in limiares]).sort_values("limiar", ascending=False)
print(f"Percentil 99 da distribuição = {p99:.3f}")
varredura.style.format({"precisão": "{:.2f}", "revocação": "{:.2f}", "F1": "{:.2f}"})'''),
    code('''fig, ax = plt.subplots(figsize=(8, 3.5))
grade = np.arange(0.5, 0.96, 0.025)
res = pd.DataFrame([avaliar(l)[0] for l in grade])
ax.plot(res.limiar, res["precisão"], label="precisão"); ax.plot(res.limiar, res["revocação"], label="revocação")
ax.plot(res.limiar, res["F1"], "k--", label="F1"); ax.axvline(0.85, color="gray", ls=":", label="limiar 0,85")
ax.set(xlabel="limiar", ylim=(0, 1.05), title="Trade-off precisão × revocação"); ax.legend(); plt.tight_layout(); plt.show()
melhor = res.loc[res.F1.idxmax()]
print(f"Melhor F1 = {melhor.F1:.2f} com limiar ≈ {melhor.limiar:.3f}")'''),
    md("## 5. Falsos positivos e falsos negativos (limiar 0,85 e limiar de melhor F1)"),
    code('''def relatorio(limiar):
    m, pred = avaliar(limiar)
    print(f"\\n=== limiar {limiar:.3f} === VP={m['VP']} FP={m['FP']} FN={m['FN']}")
    for titulo, conj in [("Verdadeiros positivos", pred & real), ("FALSOS POSITIVOS", pred - real), ("FALSOS NEGATIVOS", real - pred)]:
        print(f"-- {titulo}")
        for a, b in sorted(conj):
            print(f"   {a} × {b}  (cos={S[idx[a], idx[b]]:.3f})\\n      {a}: {textos[idx[a]][:110]}\\n      {b}: {textos[idx[b]][:110]}")
relatorio(0.85)
relatorio(float(melhor.limiar))'''),
    md("## 6. Comparação entre modelos no mesmo gabarito"),
    code('''linhas = []
for nome in ["paraphrase-multilingual-MiniLM-L12-v2", "sentence-transformers/distiluse-base-multilingual-cased-v2", "intfloat/multilingual-e5-small"]:
    E = u.codificar(u.carregar_modelo(nome), textos, nome)
    M = u.matriz_similaridade(E)
    sim_real = [M[idx[a], idx[b]] for a, b in real]
    nao_dup = np.array([M[i, j] for i, j in zip(*iu) if (df.id[i], df.id[j]) not in real])
    linhas.append(dict(modelo=nome.split("/")[-1], sim_media_duplicatas=np.mean(sim_real),
                       sim_media_nao_dup=nao_dup.mean(), maior_nao_dup=nao_dup.max(),
                       menor_dup=min(sim_real), separável=min(sim_real) > nao_dup.max()))
pd.DataFrame(linhas).round(3)'''),
]
nb2.append(md("""## 7. Análise e justificativa do limiar

**Gabarito:** 3 pares de duplicatas reais (M003×M017, M008×M022, M012×M035) em 780 pares possíveis.

| Limiar | Previstos | VP | FP | FN | Comentário |
|---|---|---|---|---|---|
| 0,85 (padrão) | 1 | 1 | 0 | 2 | precisão 100%, revocação 33% |
| ≈ 0,775 (melhor F1) | 3 | 2 | 1 | 1 | precisão 67%, revocação 67%, F1 = 0,67 |

* **Falsos negativos (0,85):** M008×M022 (cos = 0,797) — mesmo problema, mas a linguagem coloquial e a sigla "PSF" reduzem a
  similaridade — e M003×M017 (cos = 0,484), em que M003 traz informações extras (endereço, acidentes) e M017 usa outras palavras.
* **Falso positivo (0,775):** M017×M020 (cos = 0,803): ambas falam de asfalto ruim, mas M020 é uma reclamação longa e multi-assunto
  de outra rua. Mesmo *tema* ≠ mesma *manifestação*.
* **Não há limiar que separe perfeitamente** as classes com este modelo: a maior similaridade entre não duplicatas (0,80)
  supera a menor entre duplicatas (0,48). Com e5-small a situação é pior (ver tabela da seção 6) por causa da compressão de scores.
* **Limiar dinâmico:** o percentil 99 da distribuição (0,67 aqui) equivale a "os ~8 pares mais parecidos"; é útil para
  *ordenar candidatos* e se adapta a cada modelo, mas não sabe quantas duplicatas realmente existem.

**Decisão.** Manter **0,85** como limiar de *fusão automática* (nenhum falso positivo: não se descarta manifestação
legítima) e usar **0,75–0,78** como limiar de *sugestão para revisão humana*, aceitando alguns falsos positivos em troca de
revocação. Ressalva: com só 3 pares no gabarito as métricas são instáveis; em produção o limiar deve ser calibrado
em uma amostra maior rotulada por atendentes. Para melhorar M003×M017, seria possível pré-processar (normalizar
"Av."/"avenida"), comparar por *chunks* ou usar um modelo maior (ex.: bge-m3).
"""))
salvar("deteccao_duplicatas.ipynb", nb2)

# ---------------------------------------------------------------------------
# Notebook 3 — Chunking
# ---------------------------------------------------------------------------
nb3 = [
    md("""# Entrega 3 — Chunking de Manifestações Longas
As 5 manifestações mais longas são divididas com `RecursiveCharacterTextSplitter` (LangChain) em
diferentes configurações `(chunk_size, chunk_overlap)`. Avaliamos a coesão entre chunks consecutivos e
a proximidade dos chunks de uma mesma manifestação no espaço 2D."""),
    code(SETUP),
    code('''NOME = "paraphrase-multilingual-MiniLM-L12-v2"
modelo = u.carregar_modelo(NOME)

longas = df.assign(n=df.texto.str.len()).nlargest(5, "n")
print(longas[["id", "categoria_oficial", "n"]].to_string(index=False))'''),
    md("## 1. Configurações testadas"),
    code('''CONFIGS = {
    "A: 200 / 0":   (200, 0),     # pequeno, sem overlap
    "B: 200 / 50":  (200, 50),    # pequeno, overlap menor que uma frase (sem efeito prático)
    "C: 400 / 0":   (400, 0),     # grande, sem overlap
    "D: 400 / 150": (400, 150),   # grande, overlap de ~1 frase
}

chunks = []   # todos os chunks de todas as configs
for cfg, (size, ov) in CONFIGS.items():
    for _, r in longas.iterrows():
        for k, c in enumerate(u.dividir_chunks(r.texto, size, ov, "Recursive")):
            chunks.append(dict(config=cfg, id=r["id"], chunk=k, texto=c, tam=len(c)))
ch = pd.DataFrame(chunks)
ch["emb_idx"] = range(len(ch))
E = u.codificar(modelo, ch.texto.tolist(), NOME)
ch.groupby("config").agg(n_chunks=("chunk", "size"), tam_medio=("tam", "mean")).round(1)'''),
    md("## 2. Exemplo: manifestação M020 nas configurações A e D"),
    code('''for cfg in ["A: 200 / 0", "D: 400 / 150"]:
    print(f"\\n########## {cfg}")
    for _, r in ch[(ch.config == cfg) & (ch.id == "M020")].iterrows():
        print(f"[{r.chunk}] ({r.tam} chars) {r.texto!r}")'''),
    md("""## 3. Overlap e coesão entre chunks consecutivos
Medimos o cosseno médio entre chunks **consecutivos** da mesma manifestação (maior = transição mais coesa) e o
cosseno médio entre chunks **não vizinhos** (linha de base)."""),
    code('''from sklearn.metrics.pairwise import cosine_similarity
linhas = []
for cfg in CONFIGS:
    viz, nviz = [], []
    for mid in longas.id:
        sub = ch[(ch.config == cfg) & (ch.id == mid)]
        S = cosine_similarity(E[sub.emb_idx.values])
        n = len(sub)
        viz += [S[i, i + 1] for i in range(n - 1)]
        nviz += [S[i, j] for i in range(n) for j in range(i + 2, n)]
    linhas.append(dict(config=cfg, sim_consecutivos=np.mean(viz), sim_nao_vizinhos=np.mean(nviz), diferença=np.mean(viz) - np.mean(nviz)))
coesao = pd.DataFrame(linhas).set_index("config").round(3)
coesao'''),
    code('''# Quantos chunks terminam/começam no meio de uma frase? (proxy de "sentido preservado")
def corta_frase(t):
    return (not t.rstrip().endswith((".", "!", "?"))) or t[0].islower()
ch["corte_no_meio"] = ch.texto.map(corta_frase)
ch.groupby("config").corte_no_meio.mean().mul(100).round(1).rename("% chunks com início/fim no meio de frase")'''),
    md("## 4. Espaço 2D (PCA e t-SNE) — chunks da mesma manifestação ficam próximos?"),
    code('''from sklearn.metrics import silhouette_score
def plotar(cfg, metodo, ax):
    sub = ch[ch.config == cfg]
    xy = u.reduzir_2d(E[sub.emb_idx.values], metodo)
    for mid, g in sub.groupby("id"):
        pos = [list(sub.index).index(i) for i in g.index]
        ax.scatter(xy[pos, 0], xy[pos, 1], label=mid, s=45)
        for k, p in zip(g.chunk, pos):
            ax.annotate(str(k), xy[p], fontsize=6, xytext=(2, 2), textcoords="offset points")
    ax.set_title(f"{metodo} — {cfg}")

fig, axes = plt.subplots(2, 2, figsize=(13, 10))
for ax, (cfg, metodo) in zip(axes.ravel(), [("A: 200 / 0", "PCA"), ("D: 400 / 150", "PCA"), ("A: 200 / 0", "t-SNE"), ("D: 400 / 150", "t-SNE")]):
    plotar(cfg, metodo, ax)
axes[0, 0].legend(title="manifestação"); plt.tight_layout(); plt.show()

# Métrica objetiva: silhouette usando a manifestação de origem como rótulo (no espaço original)
sil = {cfg: silhouette_score(E[g.emb_idx.values], g.id) for cfg, g in ch.groupby("config")}
pd.Series(sil, name="silhouette (rótulo = manifestação de origem)").round(3)'''),
    code('''# Dentro-vs-fora: vizinho mais próximo de cada chunk pertence à mesma manifestação?
linhas = []
for cfg, g in ch.groupby("config"):
    S = cosine_similarity(E[g.emb_idx.values]); np.fill_diagonal(S, -1)
    viz = S.argmax(axis=1)
    linhas.append(dict(config=cfg, acerto_vizinho_mais_proximo=(g.id.values[viz] == g.id.values).mean()))
pd.DataFrame(linhas).set_index("config").round(3)'''),
]
nb3.append(md("""## 5. Conclusões

**Efeito do overlap na coesão.** A similaridade média entre chunks consecutivos subiu de 0,51 (400/0) para
0,65 (400/150), enquanto a dos não vizinhos foi de 0,38 para 0,50: o overlap repete a frase de fronteira nos dois chunks,
e por isso os vizinhos "herdam" contexto comum. O ganho é real, mas parte dele é *repetição literal*, não coesão
temática pura — daí acompanhar também a diferença consecutivos − não vizinhos (0,13 → 0,16).
Observação importante: no `RecursiveCharacterTextSplitter` o overlap só existe quando as unidades de corte (aqui, frases de
~120–130 caracteres) cabem dentro do overlap **e** do chunk. Por isso as configs 200/0 e 200/50 são idênticas: com
overlap de 50 caracteres nenhuma frase inteira é repetida, e com chunk_size de 200 não cabem duas frases. Para o overlap agir,
`chunk_size` precisa ser ≥ ~3× o tamanho de uma frase e `chunk_overlap` ≈ 1 frase.

**Melhor configuração: 400/150.** (1) Preserva o sentido das denúncias: com chunks de 200 caracteres cada frase vira um chunk isolado
(ex.: "Três postes estão sem lâmpada…" sem saber que se trata da Rua Sete de Setembro); com 400/150 a frase de fronteira
aparece nos dois chunks e a queixa das bocas de lobo entupidas continua ligada a "a rua vira um rio" e ao alagamento.
(2) É a que mais recupera a origem do chunk: o vizinho mais próximo de um chunk pertence à mesma manifestação em 93% dos casos
(52% para 200/0, 82% para 400/0) e o silhouette (rótulo = manifestação) é o maior (0,19). (3) O custo é ~27% mais chunks
(14 × 11) e algum conteúdo duplicado no índice. Em todas as configs 0% dos chunks começam/terminam no meio de frase,
graças à hierarquia de separadores (`\\n\\n`, `\\n`, `. `, `; `, `, `, ` `).

**Espaço 2D.** Os chunks de uma mesma manifestação tendem a ficar próximos, mas não formam clusters compactos: os textos
são *multi-assunto* (M020 mistura buracos, alagamento, iluminação e sinalização; M027 mistura assaltos, casa abandonada e
velocidade), então chunks de temas iguais em manifestações diferentes (ex.: iluminação em M020 e M027) se aproximam entre
si. PCA (2 componentes) preserva pouca variância de embeddings de 384 dimensões e mostra a separação apenas de forma grosseira;
o t-SNE separa melhor localmente, mas suas distâncias globais não são interpretáveis. Por isso a métrica quantitativa
(vizinho mais próximo e silhouette) é mais confiável do que a inspeção visual.
"""))
salvar("chunking_manifestacoes.ipynb", nb3)

if "--executar" in sys.argv:
    import subprocess
    for nome in ["analise_comparativa", "deteccao_duplicatas", "chunking_manifestacoes"]:
        subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                        "--ExecutePreprocessor.timeout=900", os.path.join(AQUI, nome + ".ipynb")], check=True, cwd=AQUI)



