import os
from typing import Annotated, Optional
from pprint import pprint
# import PIL.Image
from dotenv import load_dotenv
import instructor
from instructor.processing.multimodal import Image
from pydantic import BaseModel, Field


# from google import genai
from src.schemas.document_id import DocumentID

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", GEMINI_API_KEY)


# class DocumentIDFront(BaseModel):
#     dni: Optional[str] = Field(description="El DNI del documento")
#     surname1: Optional[str] = Field(description="El primer apellido del documento")
#     surname2: Optional[str] = Field(description="El segundo apellido del documento")
#     name1: Optional[str] = Field(description="El nombre del documento")
#     name2: Optional[str] = Field(description="El segundo nombre del documento")
#     sex: Optional[str] = Field(description="El sexo del documento (Hombre o Mujer)")
#     nacionality: Optional[str] = Field(description="La nacionalidad del documento")
#     birth_date: Optional[str] = Field(
#         description="La fecha de nacimiento del documento"
#     )
#     validate_date: Optional[str] = Field(
#         description="La fecha de validez del documento"
#     )


# class Address(BaseModel):
#     street: Optional[str] = Field(description="La calle del documento")
#     street_type: Optional[str] = Field(description="El tipo de calle del documento")
#     street_number: Optional[str] = Field(
#         description="El número de la calle del documento"
#     )
#     # postal_code: str = Field(description="El código postal del documento")
#     city: Optional[str] = Field(description="La ciudad del documento")
#     province: Optional[str] = Field(description="La provincia del documento")


# class DocumentIDBack(BaseModel):
#     address: Optional[
#         Annotated[Address, Field(description="La dirección del documento")]
#     ] = Field(description="La dirección del documento")


# class DocumentID(BaseModel):
#     front: Optional[
#         Annotated[
#             DocumentIDFront,
#             Field(description="La parte frontal del documento de identidad"),
#         ]
#     ]
#     back: Optional[
#         Annotated[
#             DocumentIDBack,
#             Field(description="La parte posterior del documento de identidad"),
#         ]
#     ]


# 2. Configuramos el cliente (usando el modelo multimodal)
client = instructor.from_provider(
    "google/gemini-2.0-flash", api_key=GEMINI_API_KEY)

# 3. Extraemos los datos enviando la imagen directamente
# img_dni_back = PIL.Image.open("data/dni.jpeg")
# img_dni_front = PIL.Image.open("data/dni_front.jpeg")
# Option 1: Direct URL with autodetection
# (Image.from_url(url),)
# Option 2: Local file
# Image.from_path("path/to/local/image.jpg")
# Option 3: Base64 string
# Image.from_base64("base64_encoded_string_here")
# Option 4: Autodetect
# Image.autodetect(<url|path|base64>)
img_dni_front = Image.from_path("data/dni_front.jpeg")
img_dni_back = Image.from_path("data/dni.jpeg")
print("Extrayendo datos de la parte frontal del documento de identidad...")


response: DocumentID = client.create(
    response_model=DocumentID,
    safety_settings=[],  # TODO: Add safety settings only for gemini
    messages=[
        {
            "role": "system",
            "content": """You are a helpful assistant that extracts information from identity documents in spanish.
            Instructions:
            - The format of the dates is DD MM YYYY.
            - type_street you can find in the street field.
            """,
        },
        {
            "role": "user",
            "content": [
                img_dni_front,
                img_dni_back,
                "Analyze these two images of an identity document (front and back) and extract the requested structured information.",
            ],
        },
    ],
    # config={
    #     # "safety_settings": [
    #     #     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    #     #     {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    #     #     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    #     #     {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    #     # ]
    # },
)


pprint(response.model_dump())
# print(response.items)


# if __name__ == "__main__":
# main()
