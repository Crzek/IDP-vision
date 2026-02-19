from document_extractor import DocumentExtractor
from src.schemas.document_id import DocumentID
from src.schemas.invoice import InvoiceLight
import os
from dotenv import load_dotenv

load_dotenv()

extractor = DocumentExtractor(
    api_key=os.getenv("GEMINI_API_KEY"),
    # model="gemini-2.0-flash"
    model="gemini-2.0-flash-lite"
)

dni_front = "data/dni.jpeg"
dni_back = "data/dni_front.jpeg"
invoice_pdf = "data/factura.pdf"
invoice_img = "data/factura_horror.jpeg"
# dni_back = "/data/dni_back.jpg"

# Extract and validate
invoice_pdf_result = extractor.extract_and_validate(
    image_paths=[invoice_pdf],
    schema_model=InvoiceLight
)

invoice_img_result = extractor.extract_and_validate(
    image_paths=[invoice_img],
    schema_model=InvoiceLight
)

print(f"DocumentID General Extract: {invoice_pdf_result}")
print(f"DocumentID General Extract: {invoice_img_result}")
