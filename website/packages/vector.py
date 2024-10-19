from dotenv import load_dotenv
import os
from langchain_community.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import re


def get_vector_store(OPENAI_API_KEY: str, txt_file: str, chunk_size: int = 1000, chunk_overlap: int = 200): 
    # Load the text file
    loader = TextLoader(file_path=txt_file, encoding="utf-8")
    data = loader.load()

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  
        chunk_overlap=chunk_overlap
    )
    data = text_splitter.split_documents(data)

    # Create embeddings and vectorstore
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(data, embedding=embeddings)
    return vectorstore 



def get_chunks(vectorstore, query: str):
    retriever = vectorstore.as_retriever()
    relevant_chunks = retriever.invoke(query)
    # Convert each Document chunk to its text content
    string_chunks = [chunk.page_content for chunk in relevant_chunks if isinstance(chunk, Document)]   
    string_chunks = list(set(string_chunks)) 
    return string_chunks

def find_articles(text, chunk):
    # Find all article positions
    article_positions = [m.start() for m in re.finditer(r'\nArticle \d+', text)]

    # Find the position of the chunk in the text
    chunk_start = text.find(chunk)
    if chunk_start == -1:
        return "Chunk not found in the text"

    # Find the nearest article start before the chunk
    prev_article_start = max([pos for pos in article_positions if pos < chunk_start], default=None)
    if prev_article_start is None:
        return "No previous article found"

    # Find the nearest article start after the chunk
    next_article_start = min([pos for pos in article_positions if pos > chunk_start], default=len(text))

    # Extract the text between the previous article and the next article
    surrounding_text = text[prev_article_start:next_article_start]

    return surrounding_text

def split_articles(text):
    lista = []
    # Find all occurrences of article markers within the text
    article_positions = [m.start() for m in re.finditer(r'\nArticle \d+', text)]

    # If there are less than 2 articles, return the text as is
    if len(article_positions) < 2:
        lista.append(text)
        return [lista]

    # Split the text into two parts at the position of the second article marker
    first_article = text[0:article_positions[1]].strip()
    second_article = text[article_positions[1]:].strip()
    lista.append(first_article)
    lista.append(second_article)
    return lista

# funzione per salvare dizionario con domanda : [articoli]
def question_article_dic(answers, faiss_store, code, dict):
    for answer in answers:
        articles_list = []
        chunks = get_chunks(faiss_store, answer)  # restituisce uno o più chunks relativi a una singola domanda
        for chunk in chunks:
            articles = find_articles(code, chunk)  # unico testo che può avere uno o più articoli
            articles_splitted = split_articles(articles)
            articles_list.extend(articles_splitted)
        dict[answer] = articles_list
    return dict


  
