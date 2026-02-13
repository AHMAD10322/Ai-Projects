from mem0 import Memory
from openai import OpenAI
from dotenv import load_dotenv
from neo4j import GraphDatabase
import os
import json
from datetime import datetime, timezone

load_dotenv()

# ----------------- Load API Key -----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in .env")

client = OpenAI(api_key=OPENAI_API_KEY)


NEO4J_URL = "neo4j+s://c74559eb.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASS = "xocS6MGSTqjUNsGE8Vh6vFk2QrzHB2Zz0ikWbmpX-2I"

neo4j_driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASS))

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small",
        },
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-4.1",
        },
    },
    "graph-store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URL,
            "username": NEO4J_USER,
            "password": NEO4J_PASS,
            "database": "neo4j",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333},
    },
}

mem_client = Memory.from_config(config)
print("Memory client initialized successfully\n")

USER_ID = "Muhammad Ahmad"


# ----------------- Helper Functions -----------------
def format_memories(memories):
    """Format memories for system prompt"""
    if not memories:
        return "No relevant memory found."
    return "\n".join(
        [f"ID:{mem.get('id')}\nMemory: {mem.get('memory')}" for mem in memories]
    )


def save_to_neo4j(user, user_query_text, response_text):
    """Save interaction as nodes and relationships in Neo4j"""
    timestamp = datetime.now(timezone.utc).isoformat()
    with neo4j_driver.session() as session:
        session.run(
            """
            MERGE (u:User {name: $user})
            CREATE (q:Query {text: $user_query_text, timestamp: $timestamp})
            CREATE (r:Response {text: $response_text, timestamp: $timestamp})
            MERGE (u)-[:ASKED]->(q)
            MERGE (q)-[:REPLIED]->(r)
            """,
            user=user,
            user_query_text=user_query_text,
            response_text=response_text,
            timestamp=timestamp,
        )


# ----------------- Main Loop -----------------
while True:
    try:
        user_query = input("You: ").strip()
        if not user_query:
            print("Please enter a query.")
            continue

        # Search for relevant memories
        search_result = mem_client.search(query=user_query, user_id=USER_ID)
        memories = search_result.get("results", [])
        formatted_memories = format_memories(memories)

        # Display memories
        print("\nFound Memories:")
        if memories:
            for mem in memories:
                print(f"- ID:{mem.get('id')} | {mem.get('memory')}")
        else:
            print("None")

        # Build system prompt
        SYSTEM_PROMPT = (
            "You are a helpful assistant.\n"
            f"Here is relevant past memory about the user:\n{formatted_memories}"
        )

        # Generate AI response
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ],
        )

        ai_response = response.choices[0].message.content
        print("\nAI:", ai_response)

        # Save interaction to memory (Qdrant)
        mem_client.add(
            user_id=USER_ID,
            messages=[
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": ai_response},
            ],
        )
        print("Memory has been saved to Qdrant.")

        # Save structured interaction to Neo4j
        save_to_neo4j(USER_ID, user_query, ai_response)
        print("Interaction saved in Neo4j!\n")

    except KeyboardInterrupt:
        print("\nExiting... Goodbye!")
        break
    except Exception as e:
        print(f"Error: {e}\nPlease try again.")
