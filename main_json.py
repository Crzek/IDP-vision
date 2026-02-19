import os
import json
from typing import Annotated, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", GEMINI_API_KEY)


# 1. Definimos el esquema de la factura
class InvoiceItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float


class Invoice(BaseModel):
    vendor_name: Optional[str] = Field(description="El nombre del emisor")
    vat_number: Optional[str] = Field(description="El CIF/NIF del emisor")
    date: Optional[str] = Field(description="La fecha de la factura")
    items: Optional[list[InvoiceItem]] = Field(
        description="Los items de la factura")
    total_amount: Optional[float] = Field(description="El total de la factura")
    currency: Optional[str] = Field(description="La moneda de la factura")


class DocumentIDFront(BaseModel):
    dni: Optional[str] = Field(description="El DNI del documento")
    surname1: Optional[str] = Field(
        description="El primer apellido del documento")
    surname2: Optional[str] = Field(
        description="El segundo apellido del documento")
    name1: Optional[str] = Field(description="El nombre del documento")
    name2: Optional[str] = Field(description="El segundo nombre del documento")
    sex: Optional[str] = Field(
        description="El sexo del documento (Hombre o Mujer)")
    nacionality: Optional[str] = Field(
        description="La nacionalidad del documento")
    birth_date: Optional[str] = Field(
        description="La fecha de nacimiento del documento"
    )
    validate_date: Optional[str] = Field(
        description="La fecha de validez del documento"
    )


class Address(BaseModel):
    street: Optional[str] = Field(description="La calle del documento")
    street_type: Optional[str] = Field(
        description="El tipo de calle del documento")
    street_number: Optional[str] = Field(
        description="El número de la calle del documento"
    )
    # postal_code: str = Field(description="El código postal del documento")
    city: Optional[str] = Field(description="La ciudad del documento")
    province: Optional[str] = Field(description="La provincia del documento")


class DocumentIDBack(BaseModel):
    address: Optional[
        Annotated[Address, Field(description="La dirección del documento")]
    ] = Field(description="La dirección del documento")


class DocumentID(BaseModel):
    front: Optional[
        Annotated[
            DocumentIDFront,
            Field(description="La parte frontal del documento de identidad"),
        ]
    ]
    back: Optional[
        Annotated[
            DocumentIDBack,
            Field(description="La parte posterior del documento de identidad"),
        ]
    ]


# 2. Configuramos el cliente de Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# 3. Cargamos las imágenes
print("Cargando imágenes...")
with open("data/dni_front.jpeg", "rb") as f:
    img_front_bytes = f.read()

with open("data/dni.jpeg", "rb") as f:
    img_back_bytes = f.read()

# 4. Creamos el esquema JSON para la salida estructurada
schema = DocumentID.model_json_schema()

# 5. Creamos el prompt con instrucciones claras
prompt = f"""Analiza estas dos imágenes de un documento de identidad español (DNI):
- La primera imagen es la parte frontal del documento
- La segunda imagen es la parte posterior del documento

Extrae TODA la información visible y devuélvela en formato JSON siguiendo exactamente este esquema:

{json.dumps(schema, indent=2)}

Instrucciones importantes:
- Extrae TODOS los campos visibles en las imágenes
- Si un campo no es visible o no existe, usa null
- Para las fechas, usa el formato que aparece en el documento
- Para el sexo, usa "Hombre" o "Mujer" según corresponda
- Asegúrate de extraer ambos apellidos si están presentes
- La dirección debe incluir todos los componentes visibles

Devuelve ÚNICAMENTE el objeto JSON, sin texto adicional."""

print("Extrayendo datos del documento de identidad...")

# 6. Hacemos la solicitud a Gemini
response = client.models.generate_content(
    # model="gemini-2.0-flash-lite",
    model="gemini-2.0-flash",
    contents=[
        types.Part.from_bytes(data=img_front_bytes, mime_type="image/jpeg"),
        types.Part.from_bytes(data=img_back_bytes, mime_type="image/jpeg"),
        prompt,
    ],
    config=types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json",
    ),
)


# 7. Parseamos la respuesta JSON
try:
    json_text = response.text
    print("\n=== Respuesta JSON de Gemini ===")
    print(json_text)

    # Parseamos el JSON con Pydantic
    data = json.loads(json_text)
    document_id = DocumentID(**data)

    print("\n=== Datos extraídos y validados ===")
    print("\n--- Parte Frontal ---")
    if document_id.front:
        print(f"DNI: {document_id.front.dni}")
        print(
            f"Apellidos: {document_id.front.surname1} {document_id.front.surname2}")
        print(
            f"Nombre(s): {document_id.front.name1} {document_id.front.name2 or ''}")
        print(f"Sexo: {document_id.front.sex}")
        print(f"Nacionalidad: {document_id.front.nacionality}")
        print(f"Fecha de nacimiento: {document_id.front.birth_date}")
        print(f"Fecha de validez: {document_id.front.validate_date}")

    print("\n--- Parte Posterior ---")
    if document_id.back and document_id.back.address:
        addr = document_id.back.address
        print(
            f"Dirección: {addr.street_type} {addr.street} {addr.street_number}")
        print(f"Ciudad: {addr.city}")
        print(f"Provincia: {addr.province}")

except json.JSONDecodeError as e:
    print(f"\n❌ Error al parsear JSON: {e}")
    print(f"Respuesta recibida: {response.text}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"Respuesta completa: {response}")
