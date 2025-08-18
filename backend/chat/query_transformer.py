import asyncio
import pprint
import aiohttp
import logging
import json
from collections import Counter

from document_processor.vector_store import vector_store
from langchain.load import loads, dumps


class OllamaModelRouter:
    def __init__(self):
        self.model_endpoints = {
            "multi_query": "http://localhost:11434/api/generate",
            "decomposition": "http://localhost:11435/api/generate",
            "hyde": "http://localhost:11436/api/generate",
            "step_back": "http://localhost:11437/api/generate"
        }
        self.semaphore = asyncio.Semaphore(6)

    async def make_llm_call(self, task: str, prompt: str, model: str, timeout=15):
        if task not in self.model_endpoints:
            raise ValueError(f"Unknown task: {task}")
        url = self.model_endpoints[task]
        payload = {"model": model, "prompt": prompt}

        async with self.semaphore, aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=timeout) as r:
                r.raise_for_status()
                combined_text = ""
                async for line in r.content:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        combined_text += chunk.get("response", "")
                    except json.JSONDecodeError:
                        continue
                return combined_text


# Initialize components
ollamaModelRouter = OllamaModelRouter()
retriever = vector_store.as_retriever()

def reciprocal_rank_fusion(results: list[list], k=60):
    """Reciprocal Rank Fusion that intelligently combines multiple ranked lists"""
    fused_scores = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            fused_scores[doc_str] += 1 / (rank + k)

    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
    return reranked_results


async def generate_multiple_queries(user_prompt: str):
    system_prompt = f"""You are an AI language model assistant. Your task is to generate five
    different versions of the given user question to retrieve relevant documents from a vector
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search.
    Provide these alternative questions separated by newlines.
    OUTPUT FORMAT: Just output the sentences in new lines, nothing else
    Original question: {user_prompt}"""

    alt_queries = await ollamaModelRouter.make_llm_call(
        task="multi_query",
        prompt=system_prompt,
        model="gemma3:1b"
    )
    alt_queries += f"\n{user_prompt}"
    queries = [q.strip() for q in alt_queries.splitlines() if q.strip()]
    print(alt_queries)

    docs_per_query = [retriever.invoke(query) for query in queries]
    print(f"Total re-ranked documents retrieved: {len(docs_per_query)} for # of {len(queries)}")

    ranked_docs = reciprocal_rank_fusion(docs_per_query, k=60)
    print(f"Total re-ranked documents retrieved: {len(ranked_docs)}")
    return queries, docs_per_query, ranked_docs


async def decomposition(user_prompt: str):
    system_prompt = f"""You are a helpful assistant that breaks down the input into sub-questions.
    Generate three related sub-questions to: {user_prompt}.
    OUTPUT FORMAT: Just output the generated sub questions in new lines, do not include any other irrelevant text."""

    sub_queries = await ollamaModelRouter.make_llm_call(
        task="decomposition",
        prompt=system_prompt,
        model="gemma3:1b"
    )
    print("Sub queries from decomposition:", sub_queries, "\n")

    queries = [q.strip() for q in sub_queries.splitlines() if q.strip()]
    docs_per_query = [retriever.invoke(query) for query in queries]
    ranked_docs = reciprocal_rank_fusion(docs_per_query, k=60)
    return queries, docs_per_query, ranked_docs


async def step_back(user_prompt: str):
    system_prompt = f"""Given the user's question, generate 3 broader questions that provide context before answering.
    Original: {user_prompt}.
    OUTPUT FORMAT: Just output the generated sub questions in new lines, do not include any other irrelevant text"""

    alt_queries = await ollamaModelRouter.make_llm_call(
        task="step_back",
        prompt=system_prompt,
        model="tinyllama:latest"
    )
    print("Step back queries:", alt_queries, "\n")

    queries = [q.strip() for q in alt_queries.splitlines() if q.strip()]
    docs_per_query = [retriever.invoke(query) for query in queries]
    ranked_docs = reciprocal_rank_fusion(docs_per_query, k=60)
    return queries, docs_per_query, ranked_docs


async def hyde(user_prompt: str):
    system_prompt = f"""Generate a hypothetical answer to the following question.
    Question: {user_prompt}.
    OUTPUT STRUCTURE: Just output the generated sub questions in new lines, do not include any other irrelevant text"""

    alt_queries = await ollamaModelRouter.make_llm_call(
        task="hyde",
        prompt=system_prompt,
        model="gemma3:1b"
    )
    print("HydE queries:", alt_queries)

    queries = [q.strip() for q in alt_queries.splitlines() if q.strip()]
    docs_per_query = [retriever.invoke(query) for query in queries]
    ranked_docs = reciprocal_rank_fusion(docs_per_query, k=60)
    return queries, docs_per_query, ranked_docs


async def trigger_query_transformation_pipeline(user_prompt: str):
    results = await asyncio.gather(
        generate_multiple_queries(user_prompt),
        decomposition(user_prompt),
        step_back(user_prompt),
        hyde(user_prompt)
    )

    all_docs = []
    for _, docs_per_query, _ in results:
        for docs in docs_per_query:
            all_docs.extend(dumps(doc) for doc in docs)

    doc_counts = Counter(all_docs)
    top_3 = doc_counts.most_common(3)
    top_3_docs = [(loads(doc_str), count) for doc_str, count in top_3]

    print("\nTop 3 most frequent docs across all strategies:")
    pprint.pprint(top_3_docs)
    return top_3_docs


def run_query_transformation(user_prompt: str):
    return asyncio.run(trigger_query_transformation_pipeline(user_prompt=user_prompt))


if __name__ == "__main__":
    run_query_transformation("How to get a driver license in the state of Maryland")