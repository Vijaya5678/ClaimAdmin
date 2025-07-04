from smolagents import CodeAgent, InferenceClientModel
from tools.hospital_db_tool import sql_engine
from config.settings import HF_TOKEN

agent = CodeAgent(
    tools=[sql_engine],
    model=InferenceClientModel(
        model_id="meta-llama/Meta-Llama-3-8B-Instruct",
        token=HF_TOKEN
    ),
)