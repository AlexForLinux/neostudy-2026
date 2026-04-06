import os
import faiss
import numpy as np

class RecipeRetrieverService:
    def __init__(self, path2faiss, emded_model, recipeRepo):
        self.__path2faiss = path2faiss
        self.__embed_model = emded_model
        self.__recipeRepo = recipeRepo

        if (not os.path.exists(path2faiss)):
            self._create_db()
        else:
            self._load_db()

    def _load_batches(self, batch_size=64):
        batch = []
        for rid, recipe in self.__recipeRepo.read_all_recipes():
            batch.append((rid, recipe))

            if (len(batch) >= batch_size):
                yield batch
                batch = []

        if batch:
            yield batch

    def _extract_info(self, recipe):
        return f"""
        Название: {recipe['name']}
        Описание: {recipe['description']}
        Ингредиенты: {', '.join([row['product']['name'] for row in recipe['ingredients']])}
        Утварь: {', '.join(recipe['utensils'])}
        """.strip()

    def _create_db(self):
        index = None
        batch_size = 64
        
        for batch in self._load_batches(batch_size):
            extracts = []
            ids = []

            for rid, recipe in batch:
                ids.append(rid)
                extracts.append(self._extract_info(recipe))
                
            embeddings = self.__embed_model.encode(
                extracts,
                batch_size=batch_size,
                normalize_embeddings=True
            ).astype('float32')

            if index is None:
                dim = embeddings.shape[1]
                index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))

            index.add_with_ids(embeddings, np.array(ids, dtype='int64'))

        faiss.write_index(index, self.__path2faiss)
        self.__index = index

    def _load_db(self):
        self.__index = faiss.read_index(self.__path2faiss)

    def retrieve(self, query, top_k=3):   
        query_emb = self.__embed_model.encode(
            [query],
            normalize_embeddings=True
        )

        scores, ids = self.__index.search(query_emb, top_k)
        rids = ids[0].tolist()
        rscores = scores[0].tolist()

        docs = self.__recipeRepo.read_recipes_by_ids(rids)
        return [(rid, score, docs[rid]) for score, rid in zip(rscores, rids)]