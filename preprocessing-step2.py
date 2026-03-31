# preprocessing.py

import spacy
import re
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9., ]', '', text)
    return text.lower().strip()

def extract_concepts(text, top_n=15):
    doc = nlp(text)
    
    nouns = [token.text for token in doc 
             if token.pos_ in ["NOUN", "PROPN"] 
             and not token.is_stop]

    freq = Counter(nouns)
    keywords = [word for word, count in freq.most_common(top_n)]
    
    return keywords

def preprocess_syllabus(text):
    cleaned = clean_text(text)
    keywords = extract_concepts(cleaned)
    
    return {
        "cleaned_text": cleaned,
        "keywords": keywords
    }