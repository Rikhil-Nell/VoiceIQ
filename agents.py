from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModelSettings, GroqModel, GroqModelName
from pydantic_ai.providers.groq import GroqProvider
from pydantic import BaseModel, Field
from supabase import Client, create_client
import groq
import logfire
from settings import Settings

settings = Settings()
logfire.configure(token=settings.logfire_write_token)
logfire.instrument_pydantic_ai()

# Groq Model Definition
groq_settings = GroqModelSettings(
    temperature=0.7,
    top_p=0.95,
    frequency_penalty=0,
)

groq_model_name: GroqModelName = "llama-3.3-70b-versatile"

report_model_name : GroqModelName = "deepseek-r1-distill-llama-70b"

async_groq_client = groq.AsyncGroq(api_key=settings.groq_api_key)

groq_model = GroqModel(
    model_name=groq_model_name,
    provider=GroqProvider(groq_client=async_groq_client),
)

report_model = GroqModel(
    model_name=report_model_name,
    provider=GroqProvider(groq_client=async_groq_client),
)

class Form(BaseModel):
    responder_name: str = Field(description="The full name of the responder attending to the request, if given, else return 'null'")
    caller_name: str = Field(description="The full name of the caller making the request if given, else return 'null'")
    request_type: str = Field(description="The type of request being made out of the list: [technical support, billing, new connection]")
    issue_summary: str = Field(description="Detailed description of 50 lines of the issue being reported by the caller")
    caller_sentiment: str = Field(description="The emotion of the customer to be given in one word out of the list: [happy, sad, angry, frustrated]")

class Questionary(BaseModel):
    product_sold: str = Field(description="What did the agent sell out of the list: [TV, Wireless Connection, Internet]")

@dataclass
class Deps:
    supabase_url: str = settings.supabase_url
    supabase_key: str = settings.supabase_key
    supabase_client: Client = create_client(supabase_key=supabase_key, supabase_url=supabase_url)
    
deps = Deps()

with open("prompts/call_log_agent_prompt.txt", "r", encoding="utf-8") as file:
    call_log_agent_prompt = file.read()

with open("prompts/report_agent_prompt.txt", "r", encoding="utf-8") as file:
    report_agent_prompt = file.read()

with open("prompts/database_agent_prompt.txt", "r", encoding="utf-8") as file:
    database_agent_prompt = file.read()

with open("prompts/chat_agent_prompt.txt", "r", encoding="utf-8") as file:
    chat_agent_prompt = file.read()

with open("prompts/questionary_agent_prompt.txt", "r", encoding="utf-8")as file:
    questionary_agent_prompt = file.read()

call_log_agent = Agent(
    model=groq_model,
    model_settings=groq_settings,
    system_prompt=call_log_agent_prompt,
    retries=3,
)

report_agent = Agent(
    model=report_model,
    model_settings=groq_settings,
    system_prompt=report_agent_prompt,
    retries=3,
)

database_agent = Agent(
    model=groq_model,
    model_settings=groq_settings,
    system_prompt=database_agent_prompt,
    retries=3,
    output_type=Form
)

chat_agent = Agent(
    model=groq_model,
    model_settings=groq_settings,
    system_prompt=chat_agent_prompt,
    retries=3
)

questionary_agent = Agent(
    model=groq_model,
    model_settings=groq_settings,
    system_prompt=questionary_agent_prompt,
    retries=3
)
