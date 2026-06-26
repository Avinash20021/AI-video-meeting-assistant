from dotenv import load_dotenv
load_dotenv()

import os
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def build_vector_store(transcript: str):
    if not transcript or not transcript.strip():
        transcript = "The video transcript metadata is empty or could not be generated."

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.create_documents([transcript])

    embeddings = get_embeddings()
    print("Building vector store...")
    vector_store = FAISS.from_documents(docs, embeddings)
    print("Vector store ready.")
    return vector_store

def get_retriever(vector_store, k=4):
    return vector_store.as_retriever(search_kwargs={"k": k})