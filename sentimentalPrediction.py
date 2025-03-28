import pandas as pd
import joblib 
import keras
import numpy as np
import spacy
import string
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="tensorflow")



nlp = spacy.load('en_core_web_sm')


def preprocess_text(text):

    if isinstance(text, str):

        text = text.lower()


        doc = nlp(text)
        tokens = [token.text for token in doc if token.text not in string.punctuation]


        tokens = [token for token in tokens if not nlp.vocab[token].is_stop]


        processed_text = ' '.join(tokens)

        return processed_text
    else:

        return ''

loaded_model = joblib.load('/Users/91829/Downloads/sentiment_model.pkl')
loaded_vectorizer = joblib.load('/Users/91829/Downloads/tfidf_vectorizer.pkl')


new_text = "Hey! Have a nice day."
new_text_processed = preprocess_text(new_text)
new_text_vectorized = loaded_vectorizer.transform([new_text_processed])
raw_prediction = loaded_model.predict(new_text_vectorized)
adjusted_prediction = 'negative' if raw_prediction == 'neutral' else raw_prediction
print(f"Predicted Sentiment: {adjusted_prediction}")
