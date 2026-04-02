import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_postgres import PGVector
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()


embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY") 
)
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name="sunmark_docs",
    connection=os.getenv("DATABASE_URL"),
    use_jsonb=True,
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


# INITIALIZE MODELS 
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

openrouter_llm = ChatOpenAI(
    model="openai/gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.5
)


# PROMPT DEFINITIONS
context_prompt = ChatPromptTemplate.from_messages([
    ("system", "Given a chat history and the latest user question, formulate a standalone question."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

qa_system_prompt = (
    "You are an assistant for Sunmark School. Use the context to answer. "
    "Respond in the user's language (English/Urdu). "
    "Always include the source URL from metadata at the end.\n\n"
    "Context: {context}"
)
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", qa_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# --- CHAIN FACTORY ---
def create_safe_chain(llm, name):
    try:
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, context_prompt
        )
        qa_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

        def run(inputs):
            try:
                # Format history for LangChain classic if it's a list of lists
                result = rag_chain.invoke(inputs)
                return {"answer": result["answer"], "status": "success"}
            except Exception as e:
                return {"answer": f"[{name} ERROR]: {str(e)}", "status": "error"}

        return run
    except Exception as e:
        return lambda inputs: {"answer": f"[{name} INIT ERROR]: {str(e)}", "status": "error"}



# Exportable Chain Functions
groq_chain = create_safe_chain(groq_llm, "Groq")
openrouter_chain = create_safe_chain(openrouter_llm, "OpenRouter")











