import google.generativeai as genai
API_KEY = "AIzaSyDtHRqJge0pofOfE_Iny2o1H4JET64L-ec"
genai.configure(api_key=API_KEY)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
