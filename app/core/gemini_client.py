import sys
import os
import json
import urllib.request
import urllib.error
from google import genai
from google.genai import types
from app.config import settings

def parse_text_response(text: str) -> dict:
    valid_categories = ["Ventas", "Caja", "Compras", "Almacen", "Administracion", "General"]
    text = text or ""
    lines = text.strip().split("\n")
    if not lines:
        return {
            "respuesta": "No pude procesar tu consulta en este momento.",
            "categoria": "General"
        }
        
    last_line = lines[-1].strip()
    category = "General"
    matched = False
    
    for cat in valid_categories:
        if cat.lower() in last_line.lower():
            category = cat
            matched = True
            break
            
    if matched:
        answer_text = "\n".join(lines[:-1]).strip()
    else:
        answer_text = text.strip()
        
    if not answer_text:
        answer_text = text.strip()
        
    return {
        "respuesta": answer_text,
        "categoria": category
    }

def obtener_respuesta_simulada(pregunta: str) -> dict:
    pregunta_lower = pregunta.lower()
    
    if "devoluc" in pregunta_lower or "devolver" in pregunta_lower:
        return {
            "respuesta": (
                "Para registrar una devolución en Bit24 Impulsa, ve al módulo de "
                "Almacén > Devoluciones, selecciona la factura de venta original, "
                "e ingresa los productos a devolver junto con el motivo de la devolución."
            ),
            "categoria": "Almacen"
        }
    elif any(x in pregunta_lower for x in ["caja", "dinero", "arqueo", "apertura", "cierre"]):
        return {
            "respuesta": (
                "Para la gestión de caja, dirígete a Caja > Apertura/Cierre. "
                "Registra el monto inicial de apertura. Al finalizar el turno, "
                "ingresa los montos contados para realizar el arqueo correspondiente."
            ),
            "categoria": "Caja"
        }
    elif any(x in pregunta_lower for x in ["venta", "vender", "factura", "boleta"]):
        return {
            "respuesta": (
                "Puedes registrar ventas en Ventas > Nueva Venta. Agrega el cliente, "
                "selecciona los artículos al carrito, define el método de pago y "
                "haz clic en Emitir para generar la boleta o factura de venta."
            ),
            "categoria": "Ventas"
        }
    elif any(x in pregunta_lower for x in ["compra", "proveedor", "comprar"]):
        return {
            "respuesta": (
                "Las compras a proveedores se gestionan en Compras > Registro de Compras. "
                "Ingresa los datos de la factura/guía de remisión del proveedor y "
                "los productos adquiridos para actualizar automáticamente el inventario."
            ),
            "categoria": "Compras"
        }
    elif any(x in pregunta_lower for x in ["stock", "inventario", "almacen"]):
        return {
            "respuesta": (
                "El control de stock está disponible en Almacén > Inventario. "
                "Aquí podrás ver las existencias físicas de todos tus productos en tiempo real "
                "y filtrar por almacén o categoría."
            ),
            "categoria": "Almacen"
        }
    elif any(x in pregunta_lower for x in ["usuario", "contraseña", "password", "rol", "roles"]):
        return {
            "respuesta": (
                "La gestión de permisos, roles y usuarios o restablecimiento de contraseñas "
                "se realiza por un administrador desde el módulo Configuración > Gestión de Usuarios."
            ),
            "categoria": "Administracion"
        }
        
    return {
        "respuesta": (
            "Hola, soy el asistente virtual de Bit24 Impulsa. Tu clave API "
            "actual está inactiva o sin cuota en este momento.\n\nPuedo responder a "
            "preguntas clave sobre Ventas, Almacén, Caja, Compras o Administración."
        ),
        "categoria": "General"
    }

def query_groq(api_key: str, pregunta: str) -> dict:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
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
    
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": pregunta}
        ],
        "temperature": 0.5
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        text = res_data["choices"][0]["message"]["content"]
        return parse_text_response(text)

def query_openrouter(api_key: str, pregunta: str) -> dict:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "Bit24 Impulsa",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
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
    
    body = {
        "model": "google/gemini-2.5-flash:free",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": pregunta}
        ],
        "temperature": 0.5
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        text = res_data["choices"][0]["message"]["content"]
        return parse_text_response(text)

async def preguntar_ia(pregunta: str) -> dict:
    """
    Sends a query to an AI API depending on the prefix of the API key,
    or falls back to a simulated response if all else fails.
    """
    api_key = settings.gemini_api_key or ""
    
    try:
        # Determine provider by prefix
        if api_key.startswith("gsk_"):
            print("Using Groq API integration...")
            return query_groq(api_key, pregunta)
            
        elif api_key.startswith("sk-or-") or api_key.startswith("sk-"):
            print("Using OpenRouter/OpenAI API integration...")
            return query_openrouter(api_key, pregunta)
            
        else:
            print("Using standard Google Gemini API client...")
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

            client = genai.Client(api_key=api_key)
            response = await client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=pregunta,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            
            text = response.text or ""
            return parse_text_response(text)
            
    except Exception as e:
        print(f"AI Provider Error occurred ({type(e).__name__}): {e}")
        print("Falling back to local simulated response...")
        return obtener_respuesta_simulada(pregunta)
