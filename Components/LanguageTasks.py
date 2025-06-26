import openai
from coloredlogs import Empty
from dotenv import load_dotenv
import os
import json

from openai import OpenAI
import google.generativeai as genai

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API"))
openai.api_key = os.getenv("OPENAI_API")

genai.configure(api_key=os.getenv("GEMINI_API"))

if not openai.api_key:
    raise ValueError("API key not found. Make sure it is defined in the .env file.")


# Function to extract start and end times
def extract_times(json_string):
    try:
        # Parse the JSON string
        data = json.loads(json_string)

        times = []
        for item in data:
            # Extract start and end times as floats
            start_time = float(item["start"])
            end_time = float(item["end"])
            content = str(item["content"])
            times.append((int(start_time), int(end_time), content))

        return times
    except Exception as e:
        print(f"Error in extract_times: {e}")
        return 0, 0


system = """

Based on the Transcription user provides with start and end, Highlight the main parts in less than 1 min which can be directly converted into a short. highlight it such that its interesting and also keep the time stamps for the clip to start and end. only select a continues Part of the video

Follow this Format and return in valid json 
[{
start: "Start time of the clip",
content: "Highlight Text",
end: "End Time for the highlighted clip"
}]
It should be one continue clip as it will then be cut from the video and uploaded as a tiktok video. so only have one start, end and content

Dont say anything else, just return Proper Json. no explanation etc


IF YOU DONT HAVE ONE start AND end WHICH IS FOR THE LENGTH OF THE ENTIRE HIGHLIGHT, THEN 10 KITTENS WILL DIE, I WILL DO JSON['start'] AND IF IT DOESNT WORK THEN...
"""

User = """
Any Example
"""

question = """
Eres un youtuber famoso que se dedica a hacer videos con mucho engagement. Basado en la transcripción siguiente que se proporciona con inicio y fin, resalta las partes principales con duracion entre 30 segundos y de menos de 1 minuto que se puede convertir directamente en un video corto. Deben tener una duracion minima de 30 segundos. Resaltalo de tal manera que su contenido sea interesante y también manten las marcas de tiempo para el clip de inicio y fin.
Sigue este formato y devuelve en json válido:

[{
start: «Hora de inicio del clip»,
content: «Resumen del contenido»,
end: «Hora de finalización del clip resaltado»
},
{
start «Hora de inicio del clip»,
content: «Resumen del contenido»,
end: «Hora de finalización del clip resaltado»
}
]

TIENE QUE DURAR ENTRE 30 Y 60 SEGUNDOS. Debe ser un clip continuo, ya que luego será cortado del vídeo completo y subido como un vídeo para tiktok. No añadas nada más, sólo devuelve una lista de Json correcto, sin explicaciones ni nada similar, etc.
SOLO QUIERO EL JSON, NADA MAS. SIN NINGUN OTRO TIPO DE TEXTO QUE NO SEA UN JSON CON LA  INFORMACION QUE TE HE PEDIDO. QUIERO UN TOTAL DE 5 ELEMENTOS EN EL JSON.

Transcript:
"""


def getHighlight(transcription):
    print("Getting Highlight from Transcription ")
    try:
        # google
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(question + transcription)
        print(response.text)

        # OPENAI
        # response = client.chat.completions.create(model="gpt-3.5-turbo",
        #                                          temperature=0.7,
        #                                          messages=[
        #                                              {"role": "system", "content": system},
        #                                              {"role": "user", "content": Transcription + system},
        #                                          ])

        # json_string = response.choices[0].message.content
        json_string = response.text
        json_string = json_string.replace("json", "")
        json_string = json_string.replace("```", "")
        print(json_string)
        time_segments = extract_times(json_string)

        if len(time_segments) == 0:
            ask = input("Error - Get Highlights again (y/n) -> ").lower()
            if ask == "y":
                time_segments = getHighlight(transcription)
        return time_segments
    except Exception as e:
        print(f"Error in GetHighlight: {e}")
        return 0, 0


if __name__ == "__main__":
    print(getHighlight(User))
