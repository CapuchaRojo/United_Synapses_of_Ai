from typing import Any, Dict
from supabase import create_client, Client
import os

try:
    import openai
except ImportError:
    raise SystemExit("openai library is required. Install with 'pip install openai'")

from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class SupabaseAgent:
    def __init__(self, supabase_url: str, supabase_key: str, openai_api_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        openai.api_key = openai_api_key

    # Schema operations
    def create_table(self, table_name: str, columns: Dict[str, str]) -> Any:
        payload = {
            "table": table_name,
            "columns": [{"name": k, "type": v} for k, v in columns.items()],
        }
        response = self.supabase.postgrest.rpc("create_table", payload).execute()
        return response

    def delete_table(self, table_name: str) -> Any:
        payload = {"table": table_name}
        response = self.supabase.postgrest.rpc("delete_table", payload).execute()
        return response

    # Data operations
    def insert(self, table: str, row: Dict[str, Any]) -> Any:
        return self.supabase.table(table).insert(row).execute()

    def select(self, table: str, query: Dict[str, Any] = None) -> Any:
        qb = self.supabase.table(table).select("*")
        if query:
            for k, v in query.items():
                qb = qb.eq(k, v)
        return qb.execute()

    def update(self, table: str, updates: Dict[str, Any], query: Dict[str, Any]) -> Any:
        qb = self.supabase.table(table).update(updates)
        for k, v in query.items():
            qb = qb.eq(k, v)
        return qb.execute()

    def delete(self, table: str, query: Dict[str, Any]) -> Any:
        qb = self.supabase.table(table).delete()
        for k, v in query.items():
            qb = qb.eq(k, v)
        return qb.execute()

    # Use OpenAI GPT-4o to interpret natural language commands
    def ask_openai(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": "You are a Supabase assistant."},
            {"role": "user", "content": prompt},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
        )
        return response.choices[0].message.get("content")


def example_usage():
    agent = SupabaseAgent(SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY)

    # Example: create a table
    agent.create_table("test_table", {"id": "int4", "name": "text"})

    # Example: insert a row
    agent.insert("test_table", {"id": 1, "name": "foo"})

    # Example: read rows
    data = agent.select("test_table")
    print(data)

    # Example: use GPT-4o for a natural language task
    answer = agent.ask_openai("How do I delete a table in Supabase?")
    print(answer)


if __name__ == "__main__":
    example_usage()
