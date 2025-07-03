import os
from smolagents import CodeAgent, WebSearchTool, InferenceClientModel

HUGGINGFACE_API_KEY = "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"  # Set this securely
import os
import pandas as pd
from smolagents import CodeAgent, InferenceClientModel
from smolagents.tools.pandas import PandasDataFrameTool

# Load the Excel data
df = pd.read_excel("hospital_data.xlsx")

# Create the Pandas tool
df_tool = PandasDataFrameTool(df=df)

# Load the model (ensure your Hugging Face API key is set)
os.environ["HUGGINGFACE_API_KEY"] = "your-huggingface-api-key"
model = InferenceClientModel()

# Create the agent
hospital_agent = CodeAgent(
    tools=[df_tool],
    model=model,
    stream_outputs=True,
)

# Run a query
query = "What is the total bill amount for policy number IND-2025-0004?"
response = hospital_agent.run(query)
print(response)
