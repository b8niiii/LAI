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
import logging
import time

    
print(10)


class Voti(BaseModel):
        voto: int
        risposta: List[str]
        
def tutto(answer0, answer1, answer2, answer3, answer4, answer5):
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        gdpr_faiss_store = FAISS.load_local("C:/Users/aless/OneDrive/Documenti/GitHub/LAI/gdpr_vec_store",
                                            embeddings,
                                            allow_dangerous_deserialization=True)
        aiact_faiss_store = FAISS.load_local("C:/Users/aless/OneDrive/Documenti/GitHub/LAI/aiact_vec_store", 
                                            embeddings,
                                            allow_dangerous_deserialization=True)
        print(1)
        start_time = time.time()
        logging.debug(f"Starting tutto() at {start_time}")
        with open('C:/Users/aless/lai/venv/testiLeggi/gdpr.txt', 'r', encoding='utf-8') as file:
            gdpr = file.read() 
        with open('C:/Users/aless/lai/venv/testiLeggi/AIACT.txt', 'r', encoding='utf-8') as file:
            aiact = file.read() 

        
        risposte = [answer0, answer1, answer2, answer3, answer4, answer5]
        logging.debug(f"User answers received: {risposte}")
        
        risposte_migliorate = []
        
        client = OpenAI()
        print(2)
        # Start processing the user responses
        for risposta in risposte:
            logging.debug(f"Processing answer: {risposta}")
            try:
                completion = client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": """You are an expert in legal linguistics, skilled at decoding 
                        complex legal language and reformulating it to meet legal standards. Your expertise ensures 
                        that content is clear, precise, and ready for advanced analysis, making legal texts easily 
                        comparable and searchable, particularly in documents like the GDPR or the AI Act."""},
                        {
                        "role": "user", 
                        "content": f"Please summarize and reformulate to meet legal standard the following text: {risposta}. Make it max 200 words"}
                    ]
                )
                summary = completion.choices[0].message.content
                risposte_migliorate.append(summary)
                logging.debug(f"Reformulated answer: {summary}")
            except Exception as e:
                logging.error(f"Error processing answer '{risposta}': {e}")
                raise e

        logging.debug(f"Finished processing user responses at {time.time() - start_time} seconds")
        print(3)
        # Split responses into GDPR and AIACT related
        gdpr_related = risposte_migliorate[0:3]
        aiact_related = risposte_migliorate[3:]
        logging.debug(f"GDPR-related responses: {gdpr_related}")
        logging.debug(f"AIACT-related responses: {aiact_related}")

        # Process articles and compare with FAISS vectors
        article_dic_cleaned_gdpr = question_article_dic(gdpr_related, gdpr_faiss_store, gdpr, {})
        article_dic_cleaned_aiact = question_article_dic(aiact_related, aiact_faiss_store, aiact, {})
        logging.debug(f"Cleaned article dictionary for GDPR: {article_dic_cleaned_gdpr}")
        logging.debug(f"Cleaned article dictionary for AIACT: {article_dic_cleaned_aiact}")

        votazioni_gdpr: Dict[str, Voti] = {}

        # Process GDPR votes
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


                
            voti_obj = completion.choices[0].message.parsed
            votazioni_gdpr[risposta] = voti_obj
            

        votazioni_aiact: Dict[str, Voti] = {}

        # Process AIACT votes
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
            voti_obj = completion.choices[0].message.parsed
            votazioni_aiact[risposta] = voti_obj
          
        # Collect and return results
        # Collect and return results
        risposte_gdpr = [
            {"domanda": risposta, "risposta": '\n\n'.join(voti.risposta), "voto": voti.voto}
            for risposta, voti in sorted(votazioni_gdpr.items(), key=lambda item: item[1].voto, reverse=True)
            if voti.voto in [2, 3]
        ]

        risposte_aiact = [
            {"domanda": risposta, "risposta": '\n\n'.join(voti.risposta), "voto": voti.voto}
            for risposta, voti in sorted(votazioni_aiact.items(), key=lambda item: item[1].voto, reverse=True)
            if voti.voto in [2, 3]
]

        
        logging.debug(f"Final GDPR responses: {risposte_gdpr}")
        logging.debug(f"Final AIACT responses: {risposte_aiact}")
        
        logging.debug(f"Completed tutto() at {time.time() - start_time} seconds")
        
        return risposte_gdpr, risposte_aiact


if __name__ == '__main__':
    
    warnings.filterwarnings('ignore')
    load_dotenv()  
    

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
    

    
    print(20)
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


    