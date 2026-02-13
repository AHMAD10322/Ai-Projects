from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class State(TypeDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]
 