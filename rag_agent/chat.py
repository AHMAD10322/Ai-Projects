from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore


load_dotenv()

openai_client = OpenAI()

embedding_models = OpenAIEmbeddings(model="text-embedding-3-large")

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_models,
)

user_query = input("ask something bro 😃: ")

search_result = vector_db.similarity_search(query=user_query)

content_str = ""


content = "\n\n\n".join(
    [
        f"Page Content : {result.page_content} \n Page Number : {result.metadata['page_label']}\n File location : {result.metadata['source']}"
        for result in search_result
    ]
)


SYSTEM_PROMPT = f"""
You are a helpful and knowledgeable AI assistant using Retrieval-Augmented Generation (RAG).

You will be given extracted content from a vector database. Each piece of content may include:
- Page Content
- Page Number
- File Location

You should only ans the user based on the following context. 

Content: 
{content}
"""

# what is the leave policy please give me one line answer

response = openai_client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ],
)

print(f"Agent Response {response.choices[0].message.content}")
