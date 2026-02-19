import os
from typing import Any, Optional, Annotated

from dotenv import load_dotenv

from PIL import Image as PILImage
import instructor
from instructor import process_response

from google import genai

# import instructor.utils
from instructor.core import Instructor
from instructor.processing.multimodal import Image
from pydantic import BaseModel, Field, TypeAdapter

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", GEMINI_API_KEY)


class Address(BaseModel):
    street: Optional[str] = Field(default=None, description="La calle del documento")
    street_type: Optional[str] = Field(default=None, description="El tipo de calle")
    street_number: Optional[str] = Field(default=None, description="El número")
    city: Optional[str] = Field(default=None, description="La ciudad")
    province: Optional[str] = Field(default=None, description="La provincia")


class DocumentIDFront(BaseModel):
    dni: Optional[str] = Field(default=None, description="El DNI")
    surname1: Optional[str] = Field(default=None, description="El primer apellido")
    surname2: Optional[str] = Field(default=None, description="El segundo apellido")
    name1: Optional[str] = Field(default=None, description="El nombre")
    name2: Optional[str] = Field(default=None, description="El segundo nombre")
    sex: Optional[str] = Field(default=None, description="El sexo (Hombre o Mujer)")
    nacionality: Optional[str] = Field(default=None, description="La nacionalidad")
    birth_date: Optional[str] = Field(
        default=None, description="La fecha de nacimiento"
    )
    validate_date: Optional[str] = Field(
        default=None, description="La fecha de validez"
    )


class DocumentIDBack(BaseModel):
    address: Annotated[
        Optional[Address], Field(default=None, description="La dirección")
    ]


class DocumentID(BaseModel):
    front: Annotated[
        Optional[DocumentIDFront], Field(default=None, description="La parte frontal")
    ]
    back: Annotated[
        Optional[DocumentIDBack], Field(default=None, description="La parte posterior")
    ]


def update_genai_kwargs(
    kwargs: dict[str, Any], base_config: dict[str, Any]
) -> dict[str, Any]:
    """
    Update keyword arguments for google.genai package from OpenAI format.
    """
    new_kwargs = kwargs.copy()

    OPENAI_TO_GEMINI_MAP = {
        "max_tokens": "max_output_tokens",
        "temperature": "temperature",
        "n": "candidate_count",
        "top_p": "top_p",
        "stop": "stop_sequences",
        "seed": "seed",
        "presence_penalty": "presence_penalty",
        "frequency_penalty": "frequency_penalty",
    }

    generation_config = new_kwargs.pop("generation_config", {})

    for openai_key, gemini_key in OPENAI_TO_GEMINI_MAP.items():
        if openai_key in generation_config:
            val = generation_config.pop(openai_key)
            if val is not None:  # Only set if value is not None
                base_config[gemini_key] = val

    safety_settings = new_kwargs.pop("safety_settings", {})
    base_config["safety_settings"] = []

    for category, threshold in safety_settings.items():
        base_config["safety_settings"].append(
            {
                "category": category,
                "threshold": threshold,
            }
        )

    return base_config


# instructor.process_response.update_genai_kwargs = update_genai_kwargs  # type: ignore
# process_response.update_genai_kwargs = update_genai_kwargs  # type: ig

# Inicializa el cliente usando from_provider (la forma más moderna)
client = instructor.from_provider(
    "google/gemini-2.0-flash-lite-preview-02-05",
)

# img_dni_front = Image.from_path("data/dni_front.jpeg")
# img_dni_back = Image.from_path("data/dni.jpeg")
img_dni_front = PILImage.open("data/dni_front.jpeg")
img_dni_back = PILImage.open("data/dni.jpeg")

client = genai.Client(api_key=GEMINI_API_KEY)
# client = instructor.from_gemini(client, mode=instructor.Mode.GENAI_TOOLS)
response = client.models.generate_content(
    model="gemini-2.0-flash-lite-preview-02-05",
    contents=[img_dni_front, img_dni_back, "Extrae la información en formato JSON..."],
)

data = TypeAdapter(DocumentID).validate_json(response.text)
print(data)
