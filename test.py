import google.generativeai as genai

genai.configure(api_key="AIzaSyDFR1QyWkrFkMKMHj-pL_vv8qUIJyJhNqE")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explain how AI works")
print(response.text)