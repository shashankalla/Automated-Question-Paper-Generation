# similarity.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def remove_similar_questions(questions, threshold=0.85):
    texts = [q["question"] for q in questions]
    embeddings = model.encode(texts)
    
    keep = []
    
    for i in range(len(embeddings)):
        is_similar = False
        for j in keep:
            sim = cosine_similarity(
                [embeddings[i]], [embeddings[j]]
            )[0][0]
            
            if sim > threshold:
                is_similar = True
                break
        
        if not is_similar:
            keep.append(i)
    
    return [questions[i] for i in keep]