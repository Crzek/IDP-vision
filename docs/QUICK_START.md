# DocumentExtractor - Quick Start Guide

## Overview

`DocumentExtractor` is a Python class that simplifies document information extraction using Google's Gemini AI. It supports multiple input formats (file paths, bytes, base64) and provides structured JSON output validated with Pydantic models.

## Installation

```bash
pip install google-genai pydantic python-dotenv
```

## Setup

1. Create a `.env` file in your project root:

```env
GEMINI_API_KEY=your_api_key_here
```

2. Import the class:

```python
from document_extractor import DocumentExtractor
```

## Basic Usage

### Initialize the Extractor

```python
# Load API key from .env
extractor = DocumentExtractor()

# Or provide API key directly
extractor = DocumentExtractor(api_key="your_api_key")

# Use a different model
extractor = DocumentExtractor(model="gemini-2.0-flash")
```

## Extraction Methods

### 1. From File Paths

Extract data from image files:

```python
from pydantic import BaseModel, Field
from typing import Optional

# Define your schema
class Invoice(BaseModel):
    vendor_name: Optional[str] = Field(description="Vendor name")
    total_amount: Optional[float] = Field(description="Total amount")
    date: Optional[str] = Field(description="Invoice date")

# Extract and validate
invoice = extractor.extract_and_validate(
    image_paths=["invoice.jpg"],
    schema_model=Invoice
)

print(f"Vendor: {invoice.vendor_name}")
print(f"Total: {invoice.total_amount}")
```

### 2. From Bytes

Extract data from image bytes:

```python
# Read image as bytes
with open("invoice.jpg", "rb") as f:
    img_bytes = f.read()

# Extract and validate
invoice = extractor.extract_and_validate_from_bytes(
    image_bytes_list=[(img_bytes, "image/jpeg")],
    schema_model=Invoice
)
```

### 3. From Base64

Extract data from base64-encoded images:

```python
import base64

# Encode image to base64
with open("invoice.jpg", "rb") as f:
    base64_string = base64.b64encode(f.read()).decode()

# Extract and validate
invoice = extractor.extract_and_validate_from_base64(
    base64_images=[(base64_string, "image/jpeg")],
    schema_model=Invoice
)
```

## Specialized Methods

### Extract ID Documents

For documents with front and back images:

```python
class DocumentIDFront(BaseModel):
    dni: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    birth_date: Optional[str]

class DocumentIDBack(BaseModel):
    address: Optional[str]

class DocumentID(BaseModel):
    front: Optional[DocumentIDFront]
    back: Optional[DocumentIDBack]

# Extract ID document
document = extractor.extract_document_id(
    front_image_path="dni_front.jpg",
    back_image_path="dni_back.jpg",
    schema_model=DocumentID
)

print(f"Name: {document.front.name}")
print(f"Address: {document.back.address}")
```

### Extract Invoices

Simplified invoice extraction:

```python
invoice = extractor.extract_invoice(
    invoice_image_path="invoice.png",
    schema_model=Invoice
)
```

## Customization

### Custom Instructions

```python
custom_instructions = """
Extract all visible fields.
Use ISO date format (YYYY-MM-DD).
Convert amounts to USD.
"""

result = extractor.extract_and_validate(
    image_paths=["document.jpg"],
    schema_model=MyModel,
    custom_instructions=custom_instructions
)
```

### Custom Prompt

```python
custom_prompt = """
Analyze this receipt and extract:
- Store name
- Items purchased
- Total amount
Return as JSON.
"""

result = extractor.extract_and_validate(
    image_paths=["receipt.jpg"],
    schema_model=Receipt,
    custom_prompt=custom_prompt
)
```

### Temperature Control

```python
# Lower temperature = more deterministic
result = extractor.extract_and_validate(
    image_paths=["document.jpg"],
    schema_model=MyModel,
    temperature=0.0  # Default is 0.1
)
```

## Multiple Images

Process multiple images in a single request:

```python
result = extractor.extract_and_validate(
    image_paths=[
        "page1.jpg",
        "page2.jpg",
        "page3.jpg"
    ],
    schema_model=MultiPageDocument
)
```

## Error Handling

```python
try:
    result = extractor.extract_and_validate(
        image_paths=["document.jpg"],
        schema_model=MyModel
    )
except json.JSONDecodeError as e:
    print(f"JSON parsing error: {e}")
except Exception as e:
    print(f"Extraction error: {e}")
```

## Return Types

- **`extract_from_*`** methods: Return `dict` (raw JSON)
- **`extract_and_validate_*`** methods: Return validated Pydantic model instance

```python
# Get raw dict
data_dict = extractor.extract_from_images(
    image_paths=["doc.jpg"],
    schema_model=MyModel
)

# Get validated model
data_model = extractor.extract_and_validate(
    image_paths=["doc.jpg"],
    schema_model=MyModel
)
```

## Supported Image Formats

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- WebP (`.webp`)

MIME types are auto-detected from file extensions.

## Next Steps

- See [ADVANCED_USAGE.md](./ADVANCED_USAGE.md) for advanced features
- Check the [examples](../examples/) directory for complete examples
