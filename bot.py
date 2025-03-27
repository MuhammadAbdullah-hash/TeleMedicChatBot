import json
import requests, os
from openai import OpenAI
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRAVILY_API_KEY = os.getenv("TRAVILY_API_KEY")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_medical_info",
            "description": "Retrieve possible conditions based on symptoms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symptoms": {
                        "type": "string",
                        "description": "User symptoms"
                    }
                },
                "required": ["symptoms"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_nearby_clinic",
            "description": "Retrieve nearby clinics or doctors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "disease": {
                        "type": "string",
                        "description": "User disease"
                    }
                },
                "required": ["disease"]
            }
        }
    }

]


# English System Prompt
SYSTEM_PROMPT_EN = """
    You are an AI-based Tele Medic assistant named (JD Diaz Tele Medic) that provides possible conditions based on user symptoms. 
    Use human-like, empathetic responses while keeping medical information factual. 

    When a user starts discussing symptoms or a health issue, engage them in a natural conversation to gather more details. 
    Ask follow-up questions like:
    - "How long have you been experiencing this?"
    - "Have you noticed any other symptoms along with it?"
    - "On a scale of 1-10, how severe is it?"
    - "Does anything make it better or worse?"

    Only after gathering enough information, process the symptoms and provide possible conditions. 
    If external data is needed, call the 'fetch_medical_info' function.

    If user asks about clinics or doctors nearby use 'fetch_nearby_clinic' function to return response and also the url of clinic/doctor returned from function.
    User Location is {user_location}

    Whenever recommending a user about some disease or giving a suggestion, ALWAYS remind users to consult a doctor for a proper diagnosis.
"""

# Spanish System Prompt
SYSTEM_PROMPT_ES = """
    Eres un asistente de Telemedicina basado en IA llamado (JD Diaz Tele Medic) que proporciona posibles condiciones médicas basadas en los síntomas del usuario. 
    Responde de manera empática y humanizada, manteniendo la información médica basada en hechos.

    Cuando un usuario menciona síntomas o un problema de salud, involúcralo en una conversación natural para obtener más detalles. 
    Pregunta cosas como:
    - "¿Cuánto tiempo llevas experimentando esto?"
    - "¿Has notado otros síntomas junto con este?"
    - "En una escala del 1 al 10, ¿qué tan severo es?"
    - "¿Hay algo que lo mejore o lo empeore?"

    Solo después de recopilar suficiente información, analiza los síntomas y proporciona posibles condiciones. 
    Si necesitas datos externos, llama a la función 'fetch_medical_info'.

        Si el usuario pregunta sobre clínicas o médicos cercanos, utiliza la función 'fetch_nearby_clinic' para devolver la respuesta y también la URL de la clínica o del médico que devuelve la función.
        La ubicación del usuario es {user_location}

    Siempre que recomiendes algo o hables de enfermedades, RECUERDA a los usuarios que consulten a un médico para un diagnóstico adecuado.
"""




class TeleMedicBot:
    def __init__(
            self, lang = "en",  model="gpt-4o-mini", tools=None, temprature=0.2,
            max_tokens=4096, system_prompt=None , user_location : dict = {}
            ):
        self.lang = lang
        self.model = model
        self.temprature = temprature
        self.max_tokens = max_tokens
        self.user_location = user_location
        self.tools = tools if tools else TOOLS
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.tavily_client = TavilyClient(api_key=TRAVILY_API_KEY)
        self.system_prompt = SYSTEM_PROMPT_ES if self.lang == "es" else SYSTEM_PROMPT_EN
        self.system_prompt = self.system_prompt.format(user_location=self.user_location)


        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.__str__()

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content.strip()})

    def web_search_tool(self, query , reuturn_urls = False):
        """ 
            Calls the external API (Tavily) to fetch medical data.
        """
        result = None
        response = self.tavily_client.search(query)
        if len(response.get('results', [])) > 0:
            if reuturn_urls : 
                result = [ { "content" : res['content'] , "url" : res['url'] } for res in response['results']]
            else : 
                result = [res['content'] for res in response['results']]

        print(f"[WEB_SEARCH] Query => {query} Result => {result}" , flush=True)
        return result or {"error": "No relevant information found."}
    
    def fetch_medical_info(self , symptoms) : 
        """
            Fetch Medical Info
        """
        query = f"possible conditions for symptoms: {symptoms}"
        response = self.web_search_tool(query=query)
        return response
    
    def fetch_nearby_clinic(self , disease): 
        """
            Fetch Nearby clinic
        """
        city = self.user_location.get("city")
        country = self.user_location.get("country")
        query = f'doctors or clinics in {city}, {country} for {disease}'
        response = self.web_search_tool(query=query , reuturn_urls=True)
        return response

        


    def get_inference(self, is_tool=True, stream=False):
        """ Get response from OpenAI API with optional streaming. """
        print(f"[INFO] Conversation Lenght : {len(self.messages)}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools if is_tool else None,
            tool_choice="auto" if is_tool else None,
            temperature=self.temprature,
            max_tokens=self.max_tokens,
            stream=stream 
        )
        return response

    def chat(self, user_message, stream=False):
        """ Process user input and generate an AI response with optional streaming. """
        self.add_message(role="user", content=user_message)

        # Step 1: Check if a function needs to be called (No Streaming)
        response = self.get_inference(stream=False)
        output = response.choices[0].message

        if hasattr(output, "tool_calls") and output.tool_calls:
            # Step 2: Execute Function if required
            tool_call = output.tool_calls[0]
            print(f'[TOOL_CALL] Tool Call => {tool_call.function}' , flush=True)
            if tool_call.function.name == "fetch_medical_info":
                symptoms = json.loads(tool_call.function.arguments)["symptoms"]
                medical_data = self.fetch_medical_info(symptoms)
                tool_response = f"Using the following relevant info to answer user query. Info: {str(medical_data)}. User Question: {user_message}"

            if tool_call.function.name == "fetch_nearby_clinic" : 
                disease = json.loads(tool_call.function.arguments)["disease"]
                clinics_data = self.fetch_nearby_clinic(disease)                
                tool_response = f"Here are few neearby clnics / doctors info: {str(clinics_data)}. Use this clinics / doctors info to answer user query. User Question: {user_message}"

            # Add retrieved data and regenerate response (With Streaming)
            self.add_message(
                role="assistant",
                content=tool_response
            )

            print(f"[INFO] ToolResp => {tool_response}" , flush=True)

            # Step 3: Now generate the final response using streaming
            response_stream = self.get_inference(is_tool=False, stream=True)
            def stream_response():
                collected_text = ""
                for chunk in response_stream:
                    if hasattr(chunk, "choices") and chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            collected_text += delta.content
                            yield delta.content  # Yield progressively
                self.add_message(role="assistant", content=collected_text)

            return stream_response()

        # Step 4: If no function is required, just return streaming response
        if stream:
            response_stream = self.get_inference(stream=True)
            def stream_response():
                collected_text = ""
                for chunk in response_stream:
                    if hasattr(chunk, "choices") and chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            collected_text += delta.content
                            yield delta.content  # Yield progressively
                self.add_message(role="assistant", content=collected_text)

            return stream_response()

        return {"response": output.content}  # Fallback for non-streaming

    def __str__(self):
        doc_string = f"""[BOT] Initialized TeleMedic Bot with 
                    [-] Model::{self.model}
                    [-] Language:: {self.lang}
                    [-] MaxTokens::{self.max_tokens}
                    [-] Temprature::{self.temprature}
                    [-] UserLocation::{self.user_location}
                    [-] SystemPrompt::{self.system_prompt[:80].strip()}
                """.strip()
        print(doc_string , flush=True)
        return doc_string

if __name__ == "__main__":
    bot = TeleMedicBot()
    while True:
        user_input = input("[USER] : ")
        response_stream = bot.chat(user_input, stream=True)
        print("[BOT] : ", end="", flush=True)

        for chunk in response_stream:
            print(chunk, end="", flush=True)

        print("\n")