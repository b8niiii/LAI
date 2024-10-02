# Warning control
import dill as pickle
import warnings
from openai import OpenAI
import os
import faiss
from dotenv import load_dotenv
from pydantic import BaseModel
from packages.vector import get_vector_store, get_chunks, find_articles, split_articles, question_article_dic
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from typing import List, Dict
import json

with open('C:/Users/aless/lai/venv/testiLeggi/gdpr.txt', 'r', encoding='utf-8') as file:
    gdpr = file.read() 
with open('C:/Users/aless/lai/venv/testiLeggi/AIACT.txt', 'r', encoding='utf-8') as file:
    aiact = file.read() 

warnings.filterwarnings('ignore')
load_dotenv()  
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# CODICE PER CREARE E SALVARE I VECTOR STORES

"""gdpr_vectorstore = get_vector_store(OPENAI_API_KEY = OPENAI_API_KEY,
                 txt_file = "C:/Users/aless/lai/venv/testiLeggi/gdpr.txt", )
aiact_vectorstore = get_vector_store(OPENAI_API_KEY = OPENAI_API_KEY,
                 txt_file = "C:/Users/aless/lai/venv/testiLeggi/AIACT.txt", )

# Save the FAISS index and metadata to the specified directory

gdpr_vectorstore.save_local("C:/Users/aless/lai/venv/gdpr_vec_store")
aiact_vectorstore.save_local("C:/Users/aless/lai/venv/aiact_vec_store")
"""


# Initialize your embeddings
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

gdpr_faiss_store = FAISS.load_local("C:/Users/aless/lai/venv/gdpr_vec_store",
                                     embeddings,
                                     allow_dangerous_deserialization=True)
aiact_faiss_store = FAISS.load_local("C:/Users/aless/lai/venv/aiact_vec_store", 
                                     embeddings,
                                     allow_dangerous_deserialization=True)

domanda0 = input("""What types of personal data does your software collect, and how is this data processed and 
stored? Please include details about the data subjects, the purpose of data collection, 
and any third-party data processors involved. """)

domanda1 = input("""How does your software manage user consent, and are there any mechanisms
to ensure that data subjects can exercise their rights (such as access, rectification, erasure, restriction,
data portability, and objection)?If so, please describe how these processes are documented and any tools you use to manage them. 
                 """)

domanda2 = input("""Have you implemented any measures to protect personal data, do you have a 
 procedure for handling data breaches, including notification to authorities and affected 
 data subjects?  """)

domanda3 = input("""Does your software utilize any AI or machine learning algorithms, particularly in automated
decision-making processes or in profiling? If so, please describe these AI systems, their decision-making 
 processes, and how their outputs are used. """)

domanda4 = input("""Is there any other information regarding your SaaS's operations, data processing
activities, or AI systems that you believe is relevant for assessing compliance with GDPR 
and AIACT? """)

domanda5 = input(""" Provide a very concise and brief description of how does your software work: """)

def tutto(answer0, answer1, answer2, answer3, answer4, answer5):
    risposte = [answer0, answer1, answer2, answer3, answer4, answer5]

    risposte_migliorate =[]

    client = OpenAI()


    for risposta in risposte:
        completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are an expert in legal linguistics, skilled at decoding 
                    complex legal language and reformulating it to meet legal standards. Your expertise ensures 
                    that content is clear, precise, and ready for advanced analysis, making legal texts easily 
                    comparable and searchable, particularly in documents like the GDPR or the AI Act. Your work 
                    is essential for maintaining clarity and legal accuracy. You are helpinng me learning how to 
                    write in legal terms, the purpose of this is to make me more comfortable in by written exmas
                    at the law university. I checked that no legal terms are violated. Don't introduce your summary
                    but summarize it directly so that I can copy the whole text without modifying it. """},
                    {
                    "role": "user", 
                    "content": f"Please summarize and reformulate to meet legal standard the following text: {risposta}. Make it max 200 words"}]
                
        )
        summary = completion.choices[0].message.content
        risposte_migliorate.append(summary)

    gdpr_related = risposte_migliorate[0:3]
    aiact_related = risposte_migliorate[3:]


    article_dic_cleaned_gdpr = {}
    article_dic_cleaned_aiact = {}

    article_dic_cleaned_gdpr = question_article_dic(gdpr_related, gdpr_faiss_store, gdpr, article_dic_cleaned_gdpr)
    article_dic_cleaned_aiact = question_article_dic(aiact_related, aiact_faiss_store, aiact, article_dic_cleaned_aiact)

    # forse bisogna inserire uno step qua in mezzo che riduca la quantità di token per ogni articolo riportato

    class Voti(BaseModel):
        voto: int
        risposta: List[str]

    votazioni_gdpr: Dict[str, Voti] = {}

    for risposta, articoli in article_dic_cleaned_gdpr.items():
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a professor in law, skilled at decoding 
                    complex legal language and reformulating it to meet legal standards. Your expertise ensures 
                    that the best feedback is always provided to students on their homework. Your work 
                    is essential for maintaining clarity and accuracy. You are helping students learn how to 
                    write business plans with a particular exercise: they will give you a brief description on 
                    the way a particular branch of their businesses works or a brief description of the entire business, 
                    along with some articles. You will have to give them a score on how precise they have been.
                    The score is the following: 1 if they are compliant to the GDPR articles you'll be given, 
                    2 if it is debatable, 3 if they are not compliant."""
                },
                {
                    "role": "user", 
                    "content": f"""Please go ahead and see if the following description is coherent with the articles provided: 
                    '{risposta}' - {articoli}. You will use a defined response format. Under "voto" you'll have to insert a grade from
                    1 to 3 as I already told you, and under "risposta" you need to append your answer on where they
                    are not compliant or, in case of 2, where they might not be compliant. Ignore the case of 1, 
                    if you give an empty answer it'll mean that students will get 100/100 as a grade."""
                }
            ],
            response_format= Voti
        )
        

        voti_obj = completion.choices[0].message.parsed  # Usa model_validate_json
        votazioni_gdpr[risposta] = voti_obj
    # print("------------------------------------------------------------------------------------")
    # print(list(votazioni_gdpr.values())[2])


    votazioni_aiact: Dict[str, Voti] = {}

    for risposta, articoli in article_dic_cleaned_aiact.items():
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a professor in law, skilled at decoding 
                    complex legal language and reformulating it to meet legal standards. Your expertise ensures 
                    that the best feedback is always provided to students on their homework. Your work 
                    is essential for maintaining clarity and accuracy. You are helping students learn how to 
                    write business plans with a particular exercise: they will give you a brief description on 
                    the way a particular branch of their businesses works or a brief description of the entire business, 
                    along with some articles. You will have to give them a score on how precise they have been.
                    The score is the following: 1 if they are compliant to the AIACT articles you'll be given, 
                    2 if it is debatable, 3 if they are not compliant."""
                },
                {
                    "role": "user", 
                    "content": f"""Please go ahead and see if the following description is coherent with the articles provided: 
                    '{risposta}' - {articoli}. You will use a defined response format. Under "voto" you'll have to insert a grade from
                    1 to 3 as I already told you, and under "risposta" you need to append your answer on where they
                    are not compliant or, in case of 2, where they might not be compliant. Ignore the case of 1, 
                    if you give an empty answer it'll mean that students will get 100/100 as a grade. Answer in first oerson
                    directly to the person who has done the research as if you were speaking face to face"""
                }
            ],
            response_format= Voti
        )
        
        voti_obj = completion.choices[0].message.parsed  # Usa model_validate_json
        votazioni_aiact[risposta] = voti_obj

    risposte_gdpr = []
    risposte_aiact = []

    # Iterazione per raccogliere prima le chiavi con voto 3, poi quelle con voto 2 per GDPR
    risposte_gdpr = []
    risposte_aiact = []

    # Iterazione per raccogliere prima le chiavi con voto 3, poi quelle con voto 2 per GDPR
    for risposta, voti in sorted(votazioni_gdpr.items(), key=lambda item: item[1].voto, reverse=True):
        if voti.voto in [2, 3]:
            risposta_str = '\n\n'.join(voti.risposta)
            risposte_gdpr.append((risposta, risposta_str, voti.voto))

    # Iterazione per raccogliere prima le chiavi con voto 3, poi quelle con voto 2 per AIACT
    for risposta, voti in sorted(votazioni_aiact.items(), key=lambda item: item[1].voto, reverse=True):
        if voti.voto in [2, 3]:
            risposta_str = '\n\n'.join(voti.risposta)
            risposte_aiact.append((risposta, risposta_str, voti.voto))

    # Visualizzazione delle risposte come lista di tuple
    for risposta, voti in sorted(votazioni_gdpr.items(), key=lambda item: item[1].voto, reverse=True):
        if voti.voto in [2, 3]:
            risposta_str = '\n\n'.join(voti.risposta)
            risposte_gdpr.append((risposta, risposta_str, voti.voto))

    for risposta, voti in sorted(votazioni_aiact.items(), key=lambda item: item[1].voto, reverse=True):
        if voti.voto in [2, 3]:
            risposta_str = '\n\n'.join(voti.risposta)
            risposte_aiact.append((risposta, risposta_str, voti.voto))

    # Invece di stampare, restituisci le risposte
    return risposte_gdpr, risposte_aiact

