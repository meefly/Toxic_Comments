import pickle
import numpy as np
import joblib
import re

# Load the models 
# model_dict is the collection of extra tree models 
# model_dict = joblib.load('./static/models/models_compressed.p')
# word_vectorizer = joblib.load('static/models/word_vectorizer.p')

model_dict = joblib.load('./static/models/Logistic_Regression_models.p')
# model_dict = joblib.load('static/models/etc_models.p')
word_vectorizer = joblib.load('static/models/log_word_vectorizer.p')

cl_path = 'static/cleaning/clean_letters.txt'

clean_word_dict = {}
with open(cl_path, 'r', encoding='utf-8') as cl:
    for line in cl:
        line = line.strip('\n')
        typo, correct = line.split(',')
        clean_word_dict[typo] = correct

def clean_word(text):
    # Removes different characters, symbols, numbers, some stop words
    replace_numbers = re.compile(r'\d+', re.IGNORECASE)
    special_character_removal = re.compile(r'[^a-z\d ]', re.IGNORECASE)

    text = text.lower()
    text = re.sub(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)", "", text)
    text = re.sub(r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}", "", text)

    for typo, correct in clean_word_dict.items():
        text = re.sub(typo, " " + correct + " ", text)

    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"i’m", "i am", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r",", " ", text)
    text = re.sub(r"\.", " ", text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\/", " ", text)
    text = re.sub(r"\^", " ^ ", text)
    text = re.sub(r"\+", " + ", text)
    text = re.sub(r"\-", " - ", text)
    text = re.sub(r"\=", " = ", text)
    text = re.sub(r"'", " ", text)
    text = re.sub(r"(\d+)(k)", r"\g<1>000", text)
    text = re.sub(r":", " : ", text)
    text = re.sub(r" e g ", " eg ", text)
    text = re.sub(r" b g ", " bg ", text)
    text = re.sub(r" u s ", " american ", text)
    text = re.sub(r"\0s", "0", text)
    text = re.sub(r" 9 11 ", "911", text)
    text = re.sub(r"e - mail", "email", text)
    text = re.sub(r"j k", "jk", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = replace_numbers.sub('', text)
    return text



def raw_chat_to_model_input(raw_input_string):
    # Converts string into cleaned text, converts it to model input
    #return word_vectorizer.transform(cleaned_text)
    cleaned_text = []
    for text in [raw_input_string]:
        cleaned_text.append(clean_word(text))
    return word_vectorizer.transform(cleaned_text)

def predict_toxicity(raw_input_string):
    ''' Given any input string, predict the toxicity levels'''
    model_input = raw_chat_to_model_input(raw_input_string)
    results = []
    # I use a dictionary of multiple models in this project
    for key,model in model_dict.items():
        results.append(round(model.predict_proba(model_input)[0,1],3))
    return results

def make_prediction(input_chat):
    '''
    Given string to classify, returns the input argument and the    
    dictionary of model classifications in a dict so that it may be
    passed back to the HTML page.
    '''
    if not input_chat:
        input_chat = ' '
    if len(input_chat) > 500:
        input_chat = input_chat[:500]
    # Calls on previous functions to get probabilities of toxicity
    pred_probs = predict_toxicity(input_chat)

    probs = [{'name': list(model_dict.keys())[index], 'prob': pred_probs[index]}
             for index in np.argsort(pred_probs)[::-1]]

    return (input_chat, probs)
 