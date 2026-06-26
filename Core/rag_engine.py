from dotenv import load_dotenv
load_dotenv()

import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from pydantic import SecretStr


def get_llm():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY not set in .env")
    return ChatMistralAI(model_name="mistral-small-latest", api_key=SecretStr(api_key), temperature=0.3)


def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])


def build_rag_chain(retriever):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}"""),
        ("human", "{question}"),
    ])
    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain


def ask_question(rag_chain, question: str) -> str:
    answer = rag_chain.invoke(question)
    return answer


if __name__ == "__main__":
    print("RAG engine module loaded.")