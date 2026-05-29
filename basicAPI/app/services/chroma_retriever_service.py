import os
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from typing import TypeVar, Generic, List, Tuple,  Generator
from app.repo.retriever_repo_protocol import ReadableRepo
from app.my_schemas.identified import Identified
from app.my_schemas.summarizable import Summarizable

class EmbeddingAdapter(Embeddings):
    def __init__(self, embed_model):
        self.embed_model = embed_model

    def embed_documents(self, texts):
        return self.embed_model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()

    def embed_query(self, text):
        return self.embed_model.encode(
            [text],
            normalize_embeddings=True
        )[0].tolist()
    
T = TypeVar('T', bound=Summarizable)

class ChromaRetrieverService(Generic[T]):
    def __init__(self, collection_name : str, path2chroma : str, readable_repo: ReadableRepo, embedding_model):
        self.__readable_repo = readable_repo

        self.__vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=EmbeddingAdapter(embedding_model),
            persist_directory=path2chroma
        )

        if self.__is_empty():
            self._create_db()

            self.__is_empty()

    def __is_empty(self) -> bool:
        data = self.__vectorstore.get()

        if not data:
            return True

        return len(data.get("ids", [])) == 0

        
    def _load_batches(self, batch_size=64) -> Generator[List[Identified[T]]]:
        batch = []

        for doc in self.__readable_repo.get_all():
            batch.append((doc.id, doc.data))

            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch
    
    def _create_db(self):
        batch_size = 64

        for batch in self._load_batches(batch_size):

            texts = []
            ids = []

            for rid, data in batch:
                texts.append(data.summarize())
                ids.append(str(rid))

            self.__vectorstore.add_texts(
                texts=texts,
                ids=ids,
            )


    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[int, float, T]]:

        results = self.__vectorstore.similarity_search_with_score(
            query,
            k=top_k
        )

        id_score_mapping = {int(doc.id): score for doc, score in results}
        doc_ids = tuple(id_score_mapping.keys())
        full_docs = self.__readable_repo.get_by_ids(doc_ids)

        retrieved_data  = [
            (full_doc.id, id_score_mapping[full_doc.id], full_doc.data) for full_doc in full_docs
        ]

        return retrieved_data