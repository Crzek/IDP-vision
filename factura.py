import os
from pprint import pprint
# import PIL.Image
from dotenv import load_dotenv
import instructor
from instructor.processing.multimodal import Image, PDF

from src.schemas.invoice import InvoiceLight

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", GEMINI_API_KEY)

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
invoice_image = Image.from_path("data/factura_horror.jpeg")
# invoice_image2 = Image.from_path("data/factura_horror.jpeg")
invoice_image2 = Image.from_path("data/fac3_2.jpeg")

invoice_pdf = PDF.from_path("data/factura.pdf")

print("Extrayendo datos de la parte frontal del documento de identidad...")


response: InvoiceLight = client.create(
    response_model=InvoiceLight,
    safety_settings=[],  # TODO: Add safety settings only for gemini
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that extracts information from light invoices in spanish.",
        },
        {
            "role": "user",
            "content": [
                invoice_pdf,
                "Analyze these PDFs of an invoice and extract the requested structured information.",
            ],
        },
    ],
)
pprint(response.model_dump())
