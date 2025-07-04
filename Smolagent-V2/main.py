from agents.hospital_agent import agent


if __name__ == "__main__":  # Seed DB
    query = "give the name and age of the patient with the third lowest bill amount"
    response = agent.run(query)
    print("\n🤖 Agent Response:\n", response)
HF_TOKEN="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"