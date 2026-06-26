from dotenv import load_dotenv
load_dotenv()

import os
from pydantic import SecretStr
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


def get_llm():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY not set in .env")
    return ChatMistralAI(model_name="mistral-small-latest", api_key=SecretStr(api_key), temperature=0.2)


def build_chain(system_prompt: str):
    llm = get_llm()
    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )


def extract_action_items(transcript: str) -> str:
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    )
    try:
        return chain.invoke(transcript)
    except Exception as e:
        raise RuntimeError(f"Failed to extract action items: {e}") from e


def extract_key_decisions(transcript: str) -> str:
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
    )
    try:
        return chain.invoke(transcript)
    except Exception as e:
        raise RuntimeError(f"Failed to extract key decisions: {e}") from e


def extract_questions(transcript: str) -> str:
    chain = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )
    try:
        return chain.invoke(transcript)
    except Exception as e:
        raise RuntimeError(f"Failed to extract questions: {e}") from e


if __name__ == "__main__":
    print("Extractor module loaded.")