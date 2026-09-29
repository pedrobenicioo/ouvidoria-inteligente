# Autor: PEDRO HENRIQUE BENICIO DE OLIVEIRA | RGM: 33602697
"""Funções compartilhadas pelos notebooks e pelo app Streamlit da Ouvidoria Inteligente."""
import json
import os

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

AQUI = os.path.dirname(os.path.abspath(__file__))

MODELOS = {
    "paraphrase-multilingual-MiniLM-L12-v2": "paraphrase-multilingual-MiniLM-L12-v2",
    "distiluse-base-multilingual-cased-v2": "sentence-transformers/distiluse-base-multilingual-cased-v2",
    "intfloat/multilingual-e5-small": "intfloat/multilingual-e5-small",
}
MODELO_PADRAO = "paraphrase-multilingual-MiniLM-L12-v2"


def carregar_manifestacoes() -> pd.DataFrame:
    with open(os.path.join(AQUI, "manifestacoes.json"), encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))


def carregar_duplicatas_reais() -> set:
    """Gabarito: conjunto de pares (id_a, id_b) ordenados."""
    with open(os.path.join(AQUI, "duplicatas_reais.json"), encoding="utf-8") as f:
        return {tuple(sorted(p)) for p in json.load(f)}


def carregar_modelo(nome: str = MODELO_PADRAO):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(nome)


def codificar(modelo, textos, nome_modelo: str = MODELO_PADRAO) -> np.ndarray:
    """Embeddings normalizados. Modelos E5 exigem o prefixo 'query: '."""
    if "e5" in nome_modelo.lower():
        textos = ["query: " + t for t in textos]
    return modelo.encode(list(textos), normalize_embeddings=True, show_progress_bar=False)


def matriz_similaridade(emb: np.ndarray) -> np.ndarray:
    return cosine_similarity(emb)


def detectar_duplicatas(textos, limiar: float = 0.85, embeddings=None, modelo=None,
                        ids=None) -> list:
    """Retorna [(i, j, similaridade), ...] com i<j e similaridade >= limiar, ordenado do maior p/ menor.

    Recebe a lista de manifestações (textos). Se `embeddings` não for informado, gera com `modelo`
    (ou com o modelo padrão). `ids` opcional troca os índices por identificadores (ex.: 'M003')."""
    if embeddings is None:
        modelo = modelo or carregar_modelo()
        embeddings = codificar(modelo, textos)
    sim = cosine_similarity(embeddings)
    rotulos = ids if ids is not None else list(range(len(textos)))
    pares = [(rotulos[i], rotulos[j], float(sim[i, j]))
             for i in range(len(textos)) for j in range(i + 1, len(textos)) if sim[i, j] >= limiar]
    return sorted(pares, key=lambda p: -p[2])


def dividir_chunks(texto: str, chunk_size: int, chunk_overlap: int, estrategia: str = "Recursive") -> list:
    """Divide `texto` em chunks. Estratégias: 'Recursive' (RecursiveCharacterTextSplitter),
    'Caracteres' (janela fixa por caracteres, sem separadores) e 'Sentenças'."""
    if estrategia == "Recursive":
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                                                  separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
                                                  keep_separator="end")
        return splitter.split_text(texto)
    if estrategia == "Caracteres":
        passo = max(1, chunk_size - chunk_overlap)
        return [texto[i:i + chunk_size] for i in range(0, len(texto), passo) if texto[i:i + chunk_size].strip()]
    if estrategia == "Sentenças":
        import re
        sentencas = [s.strip() for s in re.split(r"(?<=[.!?])\s+", texto) if s.strip()]
        chunks, atual = [], ""
        for s in sentencas:
            if atual and len(atual) + len(s) + 1 > chunk_size:
                chunks.append(atual)
                # overlap: reaproveita o final do chunk anterior
                atual = (atual[-chunk_overlap:] + " " + s) if chunk_overlap else s
            else:
                atual = (atual + " " + s).strip()
        if atual:
            chunks.append(atual)
        return chunks
    raise ValueError(f"Estratégia desconhecida: {estrategia}")


def reduzir_2d(emb: np.ndarray, metodo: str = "PCA", seed: int = 42) -> np.ndarray:
    if metodo == "PCA":
        from sklearn.decomposition import PCA
        return PCA(n_components=2, random_state=seed).fit_transform(emb)
    from sklearn.manifold import TSNE
    perplexity = max(2, min(10, (len(emb) - 1) // 3))
    return TSNE(n_components=2, perplexity=perplexity, random_state=seed, init="pca").fit_transform(emb)

