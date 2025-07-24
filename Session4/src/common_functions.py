import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_score, recall_score, f1_score
import nltk
from nltk.tokenize import word_tokenize, TreebankWordTokenizer, TweetTokenizer
import re

def clean_text(text, stop_words=[]):
    text = text.lower()
    # Remover RT/USER do início do texto (ex: "RT: USER USER")
    text = re.sub(r'^(rt[:\s]*(user\s*)+)', '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r"http\S+|www.\S+|\burl\b", "", text) # remover links e URL!
    # text = re.sub(r"[^a-z\s]", "", text) # remover pontuação e números
    text = " ".join([word for word in text.split() if word not in stop_words]) # Apagar Stopwords
    # text = " ".join([word for word in text.split()])
    # text = re.sub(r'\buser\b', '', text) #REMOVER USER???
    return text

def preprocess(text):
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
    tokens = tokenizer.tokenize(text)
    tokens = [t for t in tokens]
    return tokens

def plot_confusion_matrix(true_labels, pred_labels, model_name="Modelo", labels=["pos", "neg"]):
    cm = confusion_matrix(true_labels, pred_labels, labels=labels)
    sns.set(font_scale=1.2)
    plt.figure(figsize=(12, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=["Positivo", "Negativo"],
                yticklabels=["Positivo", "Negativo"])
    plt.xlabel("Predito")
    plt.ylabel("Verdadeiro")
    plt.title(f"Matriz de Confusão - {model_name}")
    plt.show()

# Função para plotar a matriz de confusão com GloVe
def plot_confusion_matrix_glove(true_labels, pred_labels, label_encoder, model_name="GloVe"):
    # Inverter a ordem dos rótulos
    classes_ordenadas = label_encoder.transform(label_encoder.classes_)[::-1]
    labels_texto = label_encoder.classes_[::-1]

    cm = confusion_matrix(true_labels, pred_labels, labels=classes_ordenadas)

    sns.set(font_scale=1.2)
    plt.figure(figsize=(12, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels_texto,
                yticklabels=labels_texto)
    plt.xlabel("Predito")
    plt.ylabel("Verdadeiro")
    plt.title(f"Matriz de Confusão - {model_name}")
    plt.show()

def print_classification_report(true_labels, pred_labels, model_name="Modelo", pos_label="pos"):
    acc = accuracy_score(true_labels, pred_labels)
    prec = precision_score(true_labels, pred_labels, pos_label=pos_label)
    rec = recall_score(true_labels, pred_labels, pos_label=pos_label)
    f1 = f1_score(true_labels, pred_labels, pos_label=pos_label)

    print(f"\n=== Relatório de Desempenho: {model_name} ===")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precisão : {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-score : {f1:.4f}")
    print("\n--- Relatório Detalhado ---")
    print(classification_report(true_labels, pred_labels, target_names=["neg", "pos"]))

# Função para imprimir o relatório de classificação com GloVe
def print_classification_report_glove(true_labels, pred_labels, label_encoder, model_name="GloVe"):
    acc = accuracy_score(true_labels, pred_labels)
    f1 = f1_score(true_labels, pred_labels, average='weighted')
    prec = precision_score(true_labels, pred_labels, average='weighted')
    rec = recall_score(true_labels, pred_labels, average='weighted')

    print(f"\n=== Relatório de Desempenho: {model_name} ===")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precisão : {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-score : {f1:.4f}")
    print("\n--- Relatório Detalhado ---")
    print(classification_report(true_labels, pred_labels, target_names=label_encoder.classes_))

    from nltk.corpus import stopwords