"""
Clase propia para extracción de información de documentos usando Gemini.
"""
import os
import json
import base64
import pprint
from typing import Optional, Any
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


class DocumentExtractor:
    """
    Clase para simplificar la extracción de información de documentos usando Gemini.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        """
        Inicializa el extractor de documentos.

        Args:
            api_key: API key de Gemini. Si no se proporciona, se carga desde .env
            model: Modelo de Gemini a utilizar
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY no encontrada en variables de entorno")

        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def _is_pdf(self, file_path: str) -> bool:
        """
        Verifica si un archivo es PDF.

        Args:
            file_path: Ruta al archivo

        Returns:
            True si es PDF, False en caso contrario
        """
        return Path(file_path).suffix.lower() == ".pdf"

    def _load_file(self, file_path: str) -> bytes:
        """
        Carga un archivo (imagen o PDF) desde disco.

        Args:
            file_path: Ruta al archivo de imagen o PDF

        Returns:
            Bytes del archivo
        """
        with open(file_path, "rb") as f:
            return f.read()

    def _get_mime_type(self, file_path: str) -> str:
        """
        Detecta el MIME type basado en la extensión del archivo.

        Args:
            file_path: Ruta al archivo

        Returns:
            MIME type del archivo
        """
        ext = Path(file_path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".pdf": "application/pdf",
        }
        return mime_types.get(ext, "image/jpeg")

    def _create_prompt(self, schema: dict, instructions: str = "") -> str:
        """
        Crea el prompt para Gemini.

        Args:
            schema: Esquema JSON del modelo Pydantic
            instructions: Instrucciones adicionales personalizadas

        Returns:
            Prompt formateado
        """
        default_instructions = """
            Important instructions:
            - Extract ALL visible fields from the images
            - If a field is not visible or does not exist, use null
            - The instructions are the same as the schema in description 
            - For dates, use the format as shown on the document
            - Make sure to extract all data accurately

            Return ONLY the JSON object, with no additional text."""

        prompt = f"""Analyze the provided images and extract the information strictly following this schema following the description:

                    {json.dumps(schema, indent=2)}

                    {instructions if instructions else default_instructions}"""

        return prompt

    def _decode_base64_image(self, base64_string: str) -> bytes:
        """
        Decodifica una imagen en base64 a bytes.

        Args:
            base64_string: String en base64 de la imagen

        Returns:
            Bytes de la imagen
        """
        return base64.b64decode(base64_string)

    def extract_from_images(
        self,
        image_paths: list[str],
        schema_model: Any,
        custom_prompt: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        temperature: float = 0.1,
    ) -> dict:
        """
        Extrae información de imágenes o PDFs usando un esquema Pydantic.

        Args:
            image_paths: Lista de rutas a las imágenes o archivos PDF
            schema_model: Modelo Pydantic que define el esquema de salida
            custom_prompt: Prompt personalizado completo (opcional)
            custom_instructions: Instrucciones adicionales (opcional)
            temperature: Temperatura para la generación (default: 0.1)

        Returns:
            Diccionario con los datos extraídos
        """
        # Cargar archivos (imágenes o PDFs)
        image_parts = []
        for file_path in image_paths:
            file_bytes = self._load_file(file_path)
            mime_type = self._get_mime_type(file_path)

            image_parts.append(
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            )

        # Crear prompt
        schema = schema_model.model_json_schema()
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._create_prompt(schema, custom_instructions or "")

        # Hacer la solicitud a Gemini
        response = self.client.models.generate_content(
            model=self.model,
            contents=[*image_parts, prompt],
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
            ),
        )

        # Parsear respuesta
        json_text = response.text
        data = json.loads(json_text)

        return data

    def extract_from_bytes(
        self,
        image_bytes_list: list[tuple[bytes, str]],
        schema_model: Any,
        custom_prompt: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        temperature: float = 0.1,
    ) -> dict:
        """
        Extrae información de imágenes en bytes usando un esquema Pydantic.

        Args:
            image_bytes_list: Lista de tuplas (bytes, mime_type) de las imágenes
                             Ejemplo: [(img_bytes, "image/jpeg"), (img2_bytes, "image/png")]
            schema_model: Modelo Pydantic que define el esquema de salida
            custom_prompt: Prompt personalizado completo (opcional)
            custom_instructions: Instrucciones adicionales (opcional)
            temperature: Temperatura para la generación (default: 0.1)

        Returns:
            Diccionario con los datos extraídos
        """
        # Crear partes de imagen desde bytes
        image_parts = []
        for img_bytes, mime_type in image_bytes_list:
            image_parts.append(
                types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
            )

        # Crear prompt
        schema = schema_model.model_json_schema()
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._create_prompt(schema, custom_instructions or "")

        # Hacer la solicitud a Gemini
        response = self.client.models.generate_content(
            model=self.model,
            contents=[*image_parts, prompt],
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
            ),
        )

        # Parsear respuesta
        json_text = response.text
        data = json.loads(json_text)

        return data

    def extract_from_base64(
        self,
        base64_images: list[tuple[str, str]],
        schema_model: Any,
        custom_prompt: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        temperature: float = 0.1,
    ) -> dict:
        """
        Extrae información de imágenes en base64 usando un esquema Pydantic.

        Args:
            base64_images: Lista de tuplas (base64_string, mime_type) de las imágenes
                          Ejemplo: [(base64_str, "image/jpeg"), (base64_str2, "image/png")]
            schema_model: Modelo Pydantic que define el esquema de salida
            custom_prompt: Prompt personalizado completo (opcional)
            custom_instructions: Instrucciones adicionales (opcional)
            temperature: Temperatura para la generación (default: 0.1)

        Returns:
            Diccionario con los datos extraídos
        """
        # Decodificar base64 a bytes
        image_bytes_list = [
            (self._decode_base64_image(b64_str), mime_type)
            for b64_str, mime_type in base64_images
        ]

        # Usar el método extract_from_bytes
        return self.extract_from_bytes(
            image_bytes_list=image_bytes_list,
            schema_model=schema_model,
            custom_prompt=custom_prompt,
            custom_instructions=custom_instructions,
            temperature=temperature,
        )

    def extract_and_validate(
        self,
        image_paths: list[str],
        schema_model: Any,
        custom_prompt: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        temperature: float = 0.1,
    ) -> Any:
        """
        Extrae información de imágenes o PDFs y valida con el modelo Pydantic.

        Args:
            image_paths: Lista de rutas a las imágenes o archivos PDF
            schema_model: Modelo Pydantic que define el esquema de salida
            custom_prompt: Prompt personalizado completo (opcional)
            custom_instructions: Instrucciones adicionales (opcional)
            temperature: Temperatura para la generación (default: 0.1)

        Returns:
            Instancia del modelo Pydantic validada
        """
        data = self.extract_from_images(
            image_paths=image_paths,
            schema_model=schema_model,
            custom_prompt=custom_prompt,
            custom_instructions=custom_instructions,
            temperature=temperature,
        )
        pprint.pprint(data)
        print("\n")

        # Validar con Pydantic
        validated_data = schema_model(**data)
        return validated_data

    def extract_and_validate_from_bytes(
        self,
        image_bytes_list: list[tuple[bytes, str]],
        schema_model: Any,
        custom_prompt: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        temperature: float = 0.1,
    ) -> Any:
        """
        Extrae información de bytes y valida con el modelo Pydantic.

        Args:
            image_bytes_list: Lista de tuplas (bytes, mime_type) de las imágenes
            schema_model: Modelo Pydantic que define el esquema de salida
            custom_prompt: Prompt personalizado completo (opcional)
            custom_instructions: Instrucciones adicionales (opcional)
            temperature: Temperatura para la generación (default: 0.1)

        Returns:
            Instancia del modelo Pydantic validada
        """
        data = self.extract_from_bytes(
            image_bytes_list=image_bytes_list,
            schema_model=schema_model,
            custom_prompt=custom_prompt,
            custom_instructions=custom_instructions,
            temperature=temperature,
        )

        # Validar con Pydantic
        validated_data = schema_model(**data)
        return validated_data

    def extract_and_validate_from_base64(
        self,
        base64_images: list[tuple[str, str]],
        schema_model: Any,
        custom_prompt: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        temperature: float = 0.1,
    ) -> Any:
        """
        Extrae información de base64 y valida con el modelo Pydantic.

        Args:
            base64_images: Lista de tuplas (base64_string, mime_type) de las imágenes
            schema_model: Modelo Pydantic que define el esquema de salida
            custom_prompt: Prompt personalizado completo (opcional)
            custom_instructions: Instrucciones adicionales (opcional)
            temperature: Temperatura para la generación (default: 0.1)

        Returns:
            Instancia del modelo Pydantic validada
        """
        data = self.extract_from_base64(
            base64_images=base64_images,
            schema_model=schema_model,
            custom_prompt=custom_prompt,
            custom_instructions=custom_instructions,
            temperature=temperature,
        )

        # Validar con Pydantic
        validated_data = schema_model(**data)
        return validated_data

    def extract_document_id(
        self, front_image_path: str, back_image_path: str, schema_model: Any
    ) -> Any:
        """
        Método específico para extraer información de documentos de identidad.

        Args:
            front_image_path: Ruta a la imagen/PDF frontal del documento
            back_image_path: Ruta a la imagen/PDF posterior del documento
            schema_model: Modelo Pydantic para DocumentID

        Returns:
            Instancia del modelo validada
        """
        custom_instructions = """Analyze these two images of a Spanish identity document (DNI):
            - The first image is the front side of the document
            - The second image is the back side of the document

            Important instructions:
            - Extract ALL visible fields from the images
            - If a field is not visible or does not exist, use null
            - For dates: CRITICAL - Extract dates as STRING in the exact format "DD MM YYYY" with spaces
            - Example: if you see "05 07 1999", extract it as the string "05 07 1999"
            - Do NOT convert dates to ISO format or any other format
            - For sex, use "M" for male or "F" for female
            - Be sure to extract both surnames and names if present
            - The address should include all visible components

            Return ONLY the JSON object, with no additional text."""

        return self.extract_and_validate(
            image_paths=[front_image_path, back_image_path],
            schema_model=schema_model,
            custom_instructions=custom_instructions,
        )

    def extract_invoice(self, invoice_image_path: str, schema_model: Any) -> Any:
        """
        Método específico para extraer información de facturas.

        Args:
            invoice_image_path: Ruta a la imagen o PDF de la factura
            schema_model: Modelo Pydantic para Invoice

        Returns:
            Instancia del modelo validada
        """
        custom_instructions = """Analyze this invoice image and extract all visible information.
            Important instructions:
            - Extract the vendor/emitter name
            - Extract the VAT/CIF/NIF number of the emitter
            - Extract the invoice date
            - Extract all items with description, quantity, unit price, and total
            - Extract the total amount
            - Extract the currency used
            - If a field is not visible, use null

            Return ONLY the JSON object, with no additional text."""

        return self.extract_and_validate(
            image_paths=[invoice_image_path],
            schema_model=schema_model,
            custom_instructions=custom_instructions,
        )
