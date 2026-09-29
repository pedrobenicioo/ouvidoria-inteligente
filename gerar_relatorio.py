# Autor: PEDRO HENRIQUE BENICIO DE OLIVEIRA | RGM: 33602697
"""Gera RELATORIO.pdf (até 5 páginas). Uso: python gerar_relatorio.py"""
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

AQUI = os.path.dirname(os.path.abspath(__file__))
ss = getSampleStyleSheet()
corpo = ParagraphStyle("c", parent=ss["BodyText"], fontSize=10, leading=13.5, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=13, spaceBefore=8, spaceAfter=4)
P = lambda t, s=corpo: Paragraph(t, s)


def tabela(dados, larguras):
    t = Table(dados, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                           ("FONTSIZE", (0, 0), (-1, -1), 8.5), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


el = [
    P("Ouvidoria Inteligente — Triagem Semântica de Manifestações", ss["Title"]),
    P("<b>Autor: PEDRO HENRIQUE BENICIO DE OLIVEIRA — RGM: 33602697</b>", corpo),
    P("Relatório de decisões, dificuldades e aprendizados • Desafio Prático de NLP Aplicado", corpo),

    P("1. Visão geral", h2),
    P("O protótipo substitui a busca por palavras-chave por representações vetoriais para (i) medir similaridade entre "
      "manifestações, (ii) detectar duplicatas, (iii) tratar textos longos com chunking e (iv) oferecer busca e visualização "
      "em um app Streamlit. O código compartilhado fica em <b>ouvidoria_utils.py</b> (carga de dados, embeddings, "
      "<i>detectar_duplicatas</i>, chunking, redução 2D) e é reutilizado pelos três notebooks e pelo app. "
      "Como o arquivo <i>manifestacoes.json</i> não acompanhava o enunciado, foi gerado um conjunto sintético de 40 "
      "manifestações (<i>gerar_dados.py</i>) seguindo a especificação: 5 categorias, 3 pares de duplicatas semânticas "
      "(6 manifestações = 15%) registrados em <i>duplicatas_reais.json</i> como gabarito, e 5 textos com 620–682 caracteres "
      "e vários assuntos cada."),

    P("2. Entrega 1 — Representações esparsas × densas", h2),
    P("Comparamos BoW e TF-IDF (scikit-learn, 542 termos, 95% de esparsidade) com três modelos do sentence-transformers: "
      "paraphrase-multilingual-MiniLM-L12-v2, distiluse-base-multilingual-cased-v2 e multilingual-e5-small. "
      "O modelo <i>BAAI/bge-small-pt-v1.5</i> sugerido no enunciado não estava acessível no Hugging Face (erro 401) e foi "
      "substituído pelo distiluse."),
    tabela([["Par", "BoW", "TF-IDF", "MiniLM", "distiluse", "e5-small"],
            ["M003 × M017 (duplicata)", "0,00", "0,00", "0,48", "0,25", "0,87"],
            ["M008 × M022 (duplicata)", "0,16", "0,07", "0,80", "0,56", "0,90"],
            ["M008 × M031 (sem relação)", "0,00", "0,00", "0,10", "0,14", "0,89"]],
           [5.5*cm, 2*cm, 2*cm, 2.3*cm, 2.3*cm, 2.3*cm]),
    Spacer(1, 6),
    P("Os modelos esparsos não distinguem uma duplicata sem palavras em comum de um par sem relação (ambos 0), pois "
      "\"buraco\" e \"esburacado\" são tokens distintos. Os embeddings densos separam bem o par de saúde (0,80 × 0,10 no MiniLM), "
      "mas o par do buraco ficou em 0,48, porque M003 tem detalhes que M017 não tem. O e5-small comprime todos os scores em "
      "0,81–0,93 (média 0,87), tornando o cosseno pouco discriminativo sem recalibração: <b>o limiar não é transferível "
      "entre modelos</b>."),

    P("3. Entrega 2 — Duplicatas", h2),
    P("A função <i>detectar_duplicatas(textos, limiar=0.85)</i> calcula a matriz de cosseno e retorna os pares acima do "
      "limiar. Com 0,85 e o MiniLM, apenas M012×M035 (0,89) é encontrado: precisão 100%, revocação 33% (2 falsos negativos: "
      "M008×M022 com 0,80 e M003×M017 com 0,48). O melhor F1 (0,67) ocorre perto de 0,775, com 1 falso positivo (M017×M020, "
      "mesmo tema de asfalto, mas manifestações diferentes). Nenhum limiar separa perfeitamente as classes: o maior cosseno entre "
      "não duplicatas (0,80) é maior que o menor entre duplicatas (0,48). Decisão: <b>0,85 para fusão automática</b> (evita "
      "descartar manifestações legítimas) e <b>0,75–0,78 como fila de revisão humana</b>. O percentil 99 da distribuição "
      "(0,67) serve como limiar dinâmico para ordenar candidatos. O gabarito tem só 3 pares, então as métricas são instáveis."),

    P("4. Entrega 3 — Chunking", h2),
    P("Usamos <i>RecursiveCharacterTextSplitter</i> com a hierarquia de separadores parágrafo, linha, frase, ponto e vírgula, "
      "vírgula e espaço, mantendo o separador ao fim do trecho. Testamos quatro configurações nas 5 manifestações mais longas:"),
    tabela([["chunk_size / overlap", "nº chunks", "sim. consecutivos", "sim. não vizinhos", "vizinho na mesma manifestação"],
            ["200 / 0", "25", "0,355", "0,326", "52%"],
            ["200 / 50", "25", "0,355", "0,326", "52%"],
            ["400 / 0", "11", "0,514", "0,382", "82%"],
            ["400 / 150", "14", "0,655", "0,500", "93%"]],
           [3.6*cm, 2.2*cm, 3.4*cm, 3.4*cm, 4.4*cm]),
    Spacer(1, 6),
    P("Achado importante: o overlap só tem efeito quando cabe pelo menos uma unidade de corte (uma frase de ~125 caracteres) "
      "dentro dele e do chunk; por isso 200/50 é idêntico a 200/0. A configuração <b>400/150</b> preservou melhor o sentido: "
      "a frase de fronteira aparece nos dois chunks, mantendo ligados problemas encadeados (bueiros entupidos → alagamento) e "
      "elevando a coesão entre vizinhos (0,51 → 0,65). O custo é cerca de 27% mais chunks. No espaço 2D (PCA e t-SNE), chunks "
      "da mesma manifestação tendem a ficar próximos, mas não em clusters compactos, pois os textos são multi-assunto."),

    P("5. Entrega 4 — App Streamlit", h2),
    P("<b>app_ouvidoria.py</b> tem sidebar com seleção de modelo e top-k, e quatro abas: <b>Busca Semântica</b> (top-k com "
      "cores 🟢 &gt; 0,7, 🟡 &gt; 0,5, 🔴 demais); <b>Base Completa</b> (tabela filtrável e botão que gera o heatmap e os pares "
      "mais similares); <b>Espaço Vetorial</b> (PCA/t-SNE por categoria, com a discussão dos clusters); <b>Chunking</b> "
      "(texto livre ou exemplo, estratégia Recursive/Sentenças/Caracteres, parâmetros, chunks, embeddings, matriz e projeção). "
      "O modelo usa <i>st.cache_resource</i> e os embeddings, <i>st.cache_data</i>. Medimos que, com o MiniLM, o vizinho mais próximo "
      "tem a mesma categoria oficial em 80% dos casos (saúde 100%, segurança 57%): os clusters coincidem apenas em parte, pois "
      "os embeddings agrupam por tema, e a categoria oficial reflete a secretaria responsável."),

    P("6. Dificuldades", h2),
    P("• Dados ausentes: o JSON foi recriado de forma sintética, então os resultados numéricos valem para este conjunto. "
      "• Modelo bge-small-pt inacessível: substituído. • Scores do e5 comprimidos: exigem prefixo <i>query:</i> e calibração. "
      "• O overlap do splitter recursivo não age em qualquer combinação de parâmetros. • Gabarito pequeno (3 pares): "
      "precisão e revocação variam muito com um único par."),

    P("7. Aprendizados", h2),
    P("1) Embeddings resolvem o problema de vocabulário, mas exigem calibração de limiar por modelo. 2) Mesmo tema não é o "
      "mesmo problema: duplicatas devem ser confirmadas por humanos ou por regras adicionais (local, data). "
      "3) A escolha de chunking deve seguir a estrutura do texto (frases) e não apenas números arbitrários. "
      "4) Métricas quantitativas (vizinho mais próximo, silhouette, F1) são mais confiáveis do que a inspeção visual de "
      "projeções 2D. 5) Próximos passos: avaliar modelos maiores (bge-m3), busca híbrida BM25 + vetorial e um gabarito maior."),

    P("8. Como executar", h2),
    P("<font face='Courier'>pip install -r requirements.txt</font> → <font face='Courier'>streamlit run app_ouvidoria.py</font>. "
      "Notebooks: <i>analise_comparativa</i>, <i>deteccao_duplicatas</i> e <i>chunking_manifestacoes</i>. "
      "<font face='Courier'>python gerar_notebooks.py --executar</font> os regenera."),
]

SimpleDocTemplate(os.path.join(AQUI, "RELATORIO.pdf"), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                  topMargin=1.8*cm, bottomMargin=1.8*cm, title="Relatório — Ouvidoria Inteligente").build(el)
print("RELATORIO.pdf gerado")



