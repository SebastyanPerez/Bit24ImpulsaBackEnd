import sys
from google import genai
from google.genai import types
from app.config import settings

async def preguntar_ia(pregunta: str) -> dict:
    """
    Sends a query to Google Gemini 2.5 Flash using the google-genai SDK.
    Parses the response to separate the answer and its categorized area.
    Defends against external API failures by returning a default fallback.
    """
    # System prompt instructing Gemini to categorize queries on a separate final line.
    system_instruction = (
        "Eres el asistente virtual de Bit24 Impulsa, un sistema ERP para "
        "colaboradores de REGENDA. Responde de forma breve, clara y en español, "
        "ayudando con dudas sobre ventas, caja, compras, almacén y administración "
        "dentro del sistema. Si la pregunta no tiene relación con el sistema, "
        "indica amablemente que solo puedes ayudar con temas de Bit24 Impulsa. "
        "Al final de tu respuesta, en una línea aparte, indica la categoría más "
        "relevante de la pregunta usando exactamente una de estas palabras: "
        "Ventas, Caja, Compras, Almacen, Administracion, General."
    )

    valid_categories = ["Ventas", "Caja", "Compras", "Almacen", "Administracion", "General"]

    try:
        # Initialize the GenAI Client with settings api key
        client = genai.Client(api_key=settings.gemini_api_key)
        
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=pregunta,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        text = response.text or ""
        lines = text.strip().split("\n")
        
        if not lines:
            return {
                "respuesta": "No pude procesar tu consulta en este momento, intenta de nuevo.",
                "categoria": "General"
            }

        last_line = lines[-1].strip()
        category = "General"
        matched = False
        
        for cat in valid_categories:
            # Case-insensitive substring match of valid category words
            if cat.lower() in last_line.lower():
                category = cat
                matched = True
                break
        
        if matched:
            answer_text = "\n".join(lines[:-1]).strip()
        else:
            answer_text = text.strip()
            
        # Ensure answer_text is not completely empty if categorization took the only line
        if not answer_text:
            answer_text = text.strip()
            
        return {
            "respuesta": answer_text,
            "categoria": category
        }
        
    except Exception as e:
        # Log to stderr or keep silent (avoiding logging API key in exceptions)
        
        print(f"Gemini API Error occurred: {type(e).__name__}: {e}")
        return {
            "respuesta": "No pude procesar tu consulta en este momento, intenta de nuevo.",
            "categoria": "General"
        }
