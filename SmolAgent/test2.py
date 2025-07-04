import os
import google.generativeai as genai

# Set your Gemini API key
os.environ["GEMINI_API_KEY"] ="AIzaSyDqRhGpUFS2tl3FovaCS0cvSSKFwMQ2qO8"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create a model instance
model = genai.GenerativeModel("gemini-1.5-flash")

# Generate content
response = model.generate_content("hi")

# Print the result
print("Gemini says:", response.text)
