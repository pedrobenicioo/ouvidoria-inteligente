# Autor: PEDRO HENRIQUE BENICIO DE OLIVEIRA | RGM: 33602697
"""Ouvidoria Inteligente — triagem semântica de manifestações cidadãs.
Execução: streamlit run app_ouvidoria.py"""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import ouvidoria_utils as u

st.set_page_config(page_title="Ouvidoria Inteligente", page_icon="🏛️", layout="wide")


# ----------------------------------------------------------------------------
# Cache: modelo (recurso) e embeddings (dados)
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Carregando modelo de embeddings...")
def get_modelo(nome_modelo: str):
    return u.carregar_modelo(u.MODELOS[nome_modelo])


@st.cache_data(show_spinner="Gerando embeddings da base...")
def get_embeddings_base(nome_modelo: str) -> np.ndarray:
    df = u.carregar_manifestacoes()
    return u.codificar(get_modelo(nome_modelo), df["texto"].tolist(), u.MODELOS[nome_modelo])


@st.cache_data(show_spinner=False)
def get_projecao(nome_modelo: str, metodo: str) -> np.ndarray:
    return u.reduzir_2d(get_embeddings_base(nome_modelo), metodo)


def cor_score(s: float) -> tuple[str, str]:
    if s > 0.7:
        return "🟢", "#d4edda"
    if s > 0.5:
        return "🟡", "#fff3cd"
    return "🔴", "#f8d7da"


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
df = u.carregar_manifestacoes()
with st.sidebar:
    st.title("⚙️ Configurações")
    nome_modelo = st.selectbox("Modelo de embedding", list(u.MODELOS), index=0)
    top_k = st.slider("Top-k resultados", 1, 15, 5)
    st.caption(f"Base: {len(df)} manifestações")
    st.divider()
    st.markdown("**Legenda de similaridade**\n\n🟢 > 0,7 &nbsp; 🟡 > 0,5 &nbsp; 🔴 demais")
    if "e5" in nome_modelo:
        st.warning("O e5 concentra os scores em ~0,8–0,9; as cores perdem poder discriminativo.")

emb_base = get_embeddings_base(nome_modelo)
modelo = get_modelo(nome_modelo)

st.title("🏛️ Ouvidoria Inteligente")
st.caption("Triagem semântica de manifestações cidadãs com embeddings de sentenças")

tab_busca, tab_base, tab_espaco, tab_chunk = st.tabs(
    ["🔍 Busca Semântica", "📋 Base Completa", "🌐 Espaço Vetorial", "🧩 Chunking"])

# ----------------------------------------------------------------------------
# 🔍 Busca semântica
# ----------------------------------------------------------------------------
with tab_busca:
    consulta = st.text_area("Descreva o problema:", height=100,
                            placeholder="Ex.: a rua está cheia de buracos e os carros estão quebrando")
    if st.button("Buscar", type="primary") and consulta.strip():
        q = u.codificar(modelo, [consulta], u.MODELOS[nome_modelo])
        scores = (emb_base @ q.T).ravel()
        for pos in np.argsort(-scores)[:top_k]:
            r, s = df.iloc[pos], float(scores[pos])
            icone, bg = cor_score(s)
            st.markdown(
                f"<div style='background:{bg};color:#222;padding:10px 14px;border-radius:8px;margin-bottom:8px'>"
                f"<b>{icone} {r['id']}</b> · {r['categoria_oficial']} · {r['data']} · "
                f"<b>score {s:.3f}</b><br>{r['texto']}</div>", unsafe_allow_html=True)
    elif not consulta.strip():
        st.info("Digite uma descrição livre para encontrar manifestações semelhantes.")

# ----------------------------------------------------------------------------
# 📋 Base completa
# ----------------------------------------------------------------------------
with tab_base:
    filtro = st.multiselect("Filtrar por categoria", sorted(df.categoria_oficial.unique()))
    vis = df[df.categoria_oficial.isin(filtro)] if filtro else df
    st.dataframe(vis, use_container_width=True, hide_index=True)
    if st.button("Gerar matriz de similaridade"):
        S = u.matriz_similaridade(emb_base)
        fig = px.imshow(S, x=df.id, y=df.id, color_continuous_scale="Viridis", zmin=0, zmax=1,
                        aspect="auto", height=700, labels=dict(color="cosseno"))
        st.plotly_chart(fig, use_container_width=True)
        iu = np.triu_indices(len(df), 1)
        top = pd.DataFrame({"id_a": df.id.values[iu[0]], "id_b": df.id.values[iu[1]], "similaridade": S[iu]})
        st.subheader("Pares mais similares (candidatos a duplicata)")
        st.dataframe(top.sort_values("similaridade", ascending=False).head(10), hide_index=True)

# ----------------------------------------------------------------------------
# 🌐 Espaço vetorial
# ----------------------------------------------------------------------------
with tab_espaco:
    metodo = st.radio("Redução de dimensionalidade", ["PCA", "t-SNE"], horizontal=True)
    xy = get_projecao(nome_modelo, metodo)
    plot = df.assign(x=xy[:, 0], y=xy[:, 1], trecho=df.texto.str.slice(0, 90) + "…")
    fig = px.scatter(plot, x="x", y="y", color="categoria_oficial", hover_name="id",
                     hover_data={"trecho": True, "x": False, "y": False}, height=600)
    fig.update_traces(marker=dict(size=11, line=dict(width=0.5, color="white")))
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("💬 Os clusters semânticos coincidem com as categorias oficiais?", expanded=True):
        st.markdown("""
**Parcialmente.** Medição com o MiniLM multilíngue: em 80% das manifestações o vizinho mais próximo (cosseno)
tem a mesma categoria oficial. *Saúde* é a mais coesa (100%), seguida de *educação* e *infraestrutura* (88% cada);
*meio ambiente* (67%) e *segurança* (57%) são as que mais se misturam. O silhouette global é baixo (≈ 0,09), ou seja,
as categorias não formam blocos bem separados. Exemplos de confusão: semáforo desligado (segurança) e poste apagado
(infraestrutura); esgoto/rio poluído (meio ambiente) próximo a reclamações de ruas alagadas (infraestrutura);
manifestações longas e multi-assunto ficam entre vários grupos. Os embeddings agrupam por **tema/vocabulário**,
enquanto a categoria oficial reflete a **secretaria responsável**, um critério administrativo.
O PCA de 2 componentes retém só ~26% da variância, então sobreposições visuais podem ser artefato da projeção;
o t-SNE evidencia melhor os agrupamentos locais. (Valores para o modelo padrão; podem mudar com outro modelo.)
""")

# ----------------------------------------------------------------------------
# 🧩 Chunking
# ----------------------------------------------------------------------------
with tab_chunk:
    longas = df.assign(n=df.texto.str.len()).nlargest(5, "n")
    if st.checkbox("Carregar exemplo (manifestação longa da base)"):
        exemplo = st.selectbox("Exemplo", longas.id, format_func=lambda i: f"{i} ({longas.set_index('id').n[i]} caracteres)")
        st.session_state["texto_longo"] = df.set_index("id").texto[exemplo]
    texto = st.text_area("Cole uma manifestação longa:", key="texto_longo", height=180)
    c1, c2, c3 = st.columns(3)
    estrategia = c1.selectbox("Estratégia", ["Recursive", "Sentenças", "Caracteres"])
    chunk_size = c2.slider("chunk_size", 50, 800, 400, 10)
    overlap = c3.slider("chunk_overlap", 0, max(0, chunk_size - 10), min(100, chunk_size // 3), 10)

    if texto.strip():
        chunks = u.dividir_chunks(texto, chunk_size, overlap, estrategia)
        st.markdown(f"**{len(chunks)} chunks** gerados (tamanho médio {np.mean([len(c) for c in chunks]):.0f} caracteres)")
        emb_ch = u.codificar(modelo, chunks, u.MODELOS[nome_modelo])
        tabela = pd.DataFrame({"chunk": range(len(chunks)), "caracteres": [len(c) for c in chunks],
                               "texto": chunks,
                               "embedding (8 primeiras dims)": [np.round(e[:8], 3).tolist() for e in emb_ch]})
        for i, c in enumerate(chunks):
            with st.container(border=True):
                st.markdown(f"**Chunk {i}** · {len(c)} caracteres")
                st.write(c)
        with st.expander("Embeddings"):
            st.dataframe(tabela, hide_index=True, use_container_width=True)
            st.caption(f"Dimensão de cada embedding: {emb_ch.shape[1]}")
        if len(chunks) > 1:
            S = u.matriz_similaridade(emb_ch)
            consec = [S[i, i + 1] for i in range(len(chunks) - 1)]
            st.metric("Similaridade média entre chunks consecutivos", f"{np.mean(consec):.3f}")
            fig = px.imshow(S, text_auto=".2f", color_continuous_scale="Viridis", zmin=0, zmax=1,
                            labels=dict(x="chunk", y="chunk", color="cosseno"), height=450)
            st.plotly_chart(fig, use_container_width=True)
        if len(chunks) >= 3:
            xy_ch = u.reduzir_2d(emb_ch, "PCA")
            fig = px.scatter(x=xy_ch[:, 0], y=xy_ch[:, 1], text=[str(i) for i in range(len(chunks))],
                             title="Chunks no espaço 2D (PCA)", height=420)
            fig.update_traces(textposition="top center", marker=dict(size=12))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cole um texto ou carregue um exemplo para ver os chunks.")

