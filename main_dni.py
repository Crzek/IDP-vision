from document_extractor import DocumentExtractor
from src.schemas.document_id import DocumentID
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()

extractor = DocumentExtractor(
    api_key=os.getenv("GEMINI_API_KEY"),
    # model="gemini-2.0-flash"
    model="gemini-2.0-flash-lite",
)

dni_front = "data/dni.jpeg"
dni_back = "data/dni_front.jpeg"
# dni_back = "/data/dni_back.jpg"

# Extract and validate
dni_general: DocumentID = extractor.extract_and_validate(
    image_paths=[dni_front, dni_back], schema_model=DocumentID
)

document_id: DocumentID = extractor.extract_document_id(
    front_image_path=dni_front, back_image_path=dni_back, schema_model=DocumentID
)

# print(f"DocumentID General Extract: {invoice}")
# print(f"DocumentID Especific Extract: {document_id}")

pprint(dni_general.model_dump(), indent=2)
print("--------------------------------")
pprint(document_id.model_dump(), indent=2)
