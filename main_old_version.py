import os
from typing import Annotated, Optional

# import PIL.Image
from dotenv import load_dotenv
import google.generativeai as genai
import instructor
from instructor.processing.multimodal import Image
from pydantic import BaseModel, Field

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
    items: Optional[list[InvoiceItem]] = Field(description="Los items de la factura")
    total_amount: Optional[float] = Field(description="El total de la factura")
    currency: Optional[str] = Field(description="La moneda de la factura")


class DocumentIDFront(BaseModel):
    dni: Optional[str] = Field(description="El DNI del documento")
    surname1: Optional[str] = Field(description="El primer apellido del documento")
    surname2: Optional[str] = Field(description="El segundo apellido del documento")
    name1: Optional[str] = Field(description="El nombre del documento")
    name2: Optional[str] = Field(description="El segundo nombre del documento")
    sex: Optional[str] = Field(description="El sexo del documento (Hombre o Mujer)")
    nacionality: Optional[str] = Field(description="La nacionalidad del documento")
    birth_date: Optional[str] = Field(
        description="La fecha de nacimiento del documento"
    )
    validate_date: Optional[str] = Field(
        description="La fecha de validez del documento"
    )


class Address(BaseModel):
    street: Optional[str] = Field(description="La calle del documento")
    street_type: Optional[str] = Field(description="El tipo de calle del documento")
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


# 2. Configuramos el cliente (usando el modelo multimodal)
# Configura la API de Google (como indica la documentación oficial)
genai.configure(api_key=GEMINI_API_KEY)

# Inicializa el modelo Gemini y "parchea" instructor
client = instructor.from_gemini(
    client=genai.GenerativeModel("gemini-2.0-flash-lite-preview-02-05"),
    mode=instructor.Mode.GEMINI_JSON,
)

img_dni_front = Image.from_path("data/dni_front.jpeg")
img_dni_back = Image.from_path("data/dni.jpeg")


response = client.create(
    response_model=DocumentID,
    messages=[
        {
            "role": "user",
            "content": [
                img_dni_front,
                img_dni_back,
                "Extrae los datos de la parte frontal del DNI. Si no hay datos, devuelve None.",
                "Extrae los datos de la parte posterior del DNI. Si no hay datos, devuelve None.",
            ],
        }
    ],
)
# print(response.items)


# if __name__ == "__main__":
# main()
