# DocumentExtractor - Advanced Usage Guide

## Table of Contents

1. [Complex Schema Definitions](#complex-schema-definitions)
2. [Working with Different Input Formats](#working-with-different-input-formats)
3. [Batch Processing](#batch-processing)
4. [Custom Prompt Engineering](#custom-prompt-engineering)
5. [Performance Optimization](#performance-optimization)
6. [Real-World Examples](#real-world-examples)

---

## Complex Schema Definitions

### Nested Models

Define complex hierarchical data structures:

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class Address(BaseModel):
    street: Optional[str] = Field(description="Street name")
    street_number: Optional[str] = Field(description="Street number")
    city: Optional[str] = Field(description="City name")
    postal_code: Optional[str] = Field(description="Postal code")
    country: Optional[str] = Field(description="Country")

class InvoiceItem(BaseModel):
    description: str = Field(description="Item description")
    quantity: int = Field(description="Quantity")
    unit_price: float = Field(description="Price per unit")
    total: float = Field(description="Total price")

class Invoice(BaseModel):
    invoice_number: Optional[str] = Field(description="Invoice number")
    date: Optional[str] = Field(description="Invoice date")
    vendor_name: Optional[str] = Field(description="Vendor name")
    vendor_address: Optional[Address] = Field(description="Vendor address")
    items: Optional[List[InvoiceItem]] = Field(description="Invoice items")
    subtotal: Optional[float] = Field(description="Subtotal amount")
    tax: Optional[float] = Field(description="Tax amount")
    total_amount: Optional[float] = Field(description="Total amount")
    currency: Optional[str] = Field(description="Currency code")

# Extract with nested structure
extractor = DocumentExtractor()
invoice = extractor.extract_and_validate(
    image_paths=["complex_invoice.pdf"],
    schema_model=Invoice
)

# Access nested data
print(f"Vendor: {invoice.vendor_name}")
print(f"City: {invoice.vendor_address.city}")
print(f"Items: {len(invoice.items)}")
for item in invoice.items:
    print(f"  - {item.description}: ${item.total}")
```

### Enums and Constraints

Use enums and validation constraints:

```python
from enum import Enum
from pydantic import BaseModel, Field, validator

class DocumentType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    ID_CARD = "id_card"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class ValidatedInvoice(BaseModel):
    document_type: DocumentType
    currency: Currency
    total_amount: float = Field(gt=0, description="Must be positive")
    
    @validator('total_amount')
    def validate_amount(cls, v):
        if v > 1000000:
            raise ValueError('Amount seems unreasonably high')
        return v

# Extract with validation
invoice = extractor.extract_and_validate(
    image_paths=["invoice.jpg"],
    schema_model=ValidatedInvoice
)
```

---

## Working with Different Input Formats

### Mixed Format Processing

Process images from different sources:

```python
import base64
import requests

class MultiSourceExtractor:
    def __init__(self):
        self.extractor = DocumentExtractor()
    
    def process_from_url(self, url: str, schema_model):
        """Download and process image from URL"""
        response = requests.get(url)
        img_bytes = response.content
        
        return self.extractor.extract_and_validate_from_bytes(
            image_bytes_list=[(img_bytes, "image/jpeg")],
            schema_model=schema_model
        )
    
    def process_from_base64(self, base64_str: str, schema_model):
        """Process base64 encoded image"""
        return self.extractor.extract_and_validate_from_base64(
            base64_images=[(base64_str, "image/jpeg")],
            schema_model=schema_model
        )
    
    def process_from_file(self, filepath: str, schema_model):
        """Process local file"""
        return self.extractor.extract_and_validate(
            image_paths=[filepath],
            schema_model=schema_model
        )

# Usage
processor = MultiSourceExtractor()

# From URL
invoice1 = processor.process_from_url(
    "https://example.com/invoice.jpg",
    Invoice
)

# From base64
invoice2 = processor.process_from_base64(
    base64_encoded_string,
    Invoice
)

# From file
invoice3 = processor.process_from_file(
    "local_invoice.jpg",
    Invoice
)
```

### Handling Multiple Pages

Process multi-page documents:

```python
class MultiPageDocument(BaseModel):
    pages: List[dict] = Field(description="Content from each page")
    total_pages: int = Field(description="Total number of pages")

# Process all pages
pages = [f"document_page_{i}.jpg" for i in range(1, 6)]

document = extractor.extract_and_validate(
    image_paths=pages,
    schema_model=MultiPageDocument,
    custom_instructions="""
    Analyze all pages sequentially.
    Extract information from each page separately.
    Combine related information across pages.
    """
)
```

---

## Batch Processing

### Process Multiple Documents

Efficiently process multiple documents:

```python
from pathlib import Path
from typing import List
import concurrent.futures

class BatchProcessor:
    def __init__(self, api_key: str = None):
        self.extractor = DocumentExtractor(api_key=api_key)
    
    def process_directory(
        self,
        directory: str,
        schema_model,
        pattern: str = "*.jpg"
    ) -> List[tuple[str, any]]:
        """Process all images in a directory"""
        results = []
        image_files = Path(directory).glob(pattern)
        
        for img_path in image_files:
            try:
                result = self.extractor.extract_and_validate(
                    image_paths=[str(img_path)],
                    schema_model=schema_model
                )
                results.append((str(img_path), result))
                print(f"✓ Processed: {img_path.name}")
            except Exception as e:
                print(f"✗ Failed: {img_path.name} - {e}")
                results.append((str(img_path), None))
        
        return results
    
    def process_parallel(
        self,
        image_paths: List[str],
        schema_model,
        max_workers: int = 3
    ) -> List[any]:
        """Process multiple images in parallel"""
        def process_single(path):
            return self.extractor.extract_and_validate(
                image_paths=[path],
                schema_model=schema_model
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_single, image_paths))
        
        return results

# Usage
processor = BatchProcessor()

# Process entire directory
results = processor.process_directory(
    directory="./invoices",
    schema_model=Invoice,
    pattern="*.png"
)

# Parallel processing
invoices = processor.process_parallel(
    image_paths=["inv1.jpg", "inv2.jpg", "inv3.jpg"],
    schema_model=Invoice,
    max_workers=3
)
```

---

## Custom Prompt Engineering

### Domain-Specific Prompts

Optimize prompts for specific document types:

```python
class MedicalRecordExtractor:
    def __init__(self):
        self.extractor = DocumentExtractor()
    
    def extract_prescription(self, image_path: str, schema_model):
        custom_instructions = """
        This is a medical prescription. Extract:
        - Patient name and ID
        - Doctor name and license number
        - Medication names (generic and brand)
        - Dosage and frequency
        - Date prescribed and refill information
        
        Important:
        - Use exact medication names as written
        - Preserve dosage units (mg, ml, etc.)
        - Extract all warnings and special instructions
        """
        
        return self.extractor.extract_and_validate(
            image_paths=[image_path],
            schema_model=schema_model,
            custom_instructions=custom_instructions
        )
    
    def extract_lab_results(self, image_path: str, schema_model):
        custom_instructions = """
        This is a laboratory test result. Extract:
        - Patient information
        - Test date and lab name
        - All test names and results
        - Reference ranges for each test
        - Abnormal flags (high/low indicators)
        
        Important:
        - Preserve exact numeric values with units
        - Mark abnormal results clearly
        - Include test methodology if visible
        """
        
        return self.extractor.extract_and_validate(
            image_paths=[image_path],
            schema_model=schema_model,
            custom_instructions=custom_instructions
        )

# Usage
medical_extractor = MedicalRecordExtractor()
prescription = medical_extractor.extract_prescription(
    "prescription.jpg",
    PrescriptionModel
)
```

### Multi-Language Support

Handle documents in different languages:

```python
def extract_multilingual(
    extractor: DocumentExtractor,
    image_path: str,
    schema_model,
    language: str = "auto"
):
    """Extract data with language-specific instructions"""
    
    language_instructions = {
        "es": "El documento está en español. Extrae toda la información visible.",
        "fr": "Le document est en français. Extrayez toutes les informations visibles.",
        "de": "Das Dokument ist auf Deutsch. Extrahieren Sie alle sichtbaren Informationen.",
        "auto": "Detect the document language automatically and extract all information."
    }
    
    instructions = language_instructions.get(language, language_instructions["auto"])
    
    return extractor.extract_and_validate(
        image_paths=[image_path],
        schema_model=schema_model,
        custom_instructions=instructions
    )

# Usage
spanish_invoice = extract_multilingual(
    extractor,
    "factura.jpg",
    Invoice,
    language="es"
)
```

---

## Performance Optimization

### Caching Results

Implement caching to avoid redundant API calls:

```python
import hashlib
import json
from pathlib import Path

class CachedExtractor:
    def __init__(self, cache_dir: str = ".cache"):
        self.extractor = DocumentExtractor()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, image_path: str) -> str:
        """Generate cache key from image hash"""
        with open(image_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    
    def extract_with_cache(
        self,
        image_path: str,
        schema_model,
        force_refresh: bool = False
    ):
        """Extract with caching support"""
        cache_key = self._get_cache_key(image_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Check cache
        if not force_refresh and cache_file.exists():
            print(f"Cache hit: {image_path}")
            with open(cache_file, "r") as f:
                data = json.load(f)
                return schema_model(**data)
        
        # Extract and cache
        print(f"Cache miss: {image_path}")
        result = self.extractor.extract_and_validate(
            image_paths=[image_path],
            schema_model=schema_model
        )
        
        # Save to cache
        with open(cache_file, "w") as f:
            json.dump(result.model_dump(), f, indent=2)
        
        return result

# Usage
cached_extractor = CachedExtractor(cache_dir=".extraction_cache")
invoice = cached_extractor.extract_with_cache("invoice.jpg", Invoice)
```

### Temperature Tuning

Optimize temperature for different use cases:

```python
# High precision (financial documents)
invoice = extractor.extract_and_validate(
    image_paths=["invoice.jpg"],
    schema_model=Invoice,
    temperature=0.0  # Most deterministic
)

# Balanced (general documents)
document = extractor.extract_and_validate(
    image_paths=["document.jpg"],
    schema_model=Document,
    temperature=0.1  # Default
)

# Creative extraction (handwritten notes)
notes = extractor.extract_and_validate(
    image_paths=["notes.jpg"],
    schema_model=Notes,
    temperature=0.3  # More flexible
)
```

---

## Real-World Examples

### Complete Invoice Processing Pipeline

```python
class InvoiceProcessor:
    def __init__(self):
        self.extractor = DocumentExtractor()
    
    def process_invoice(self, image_path: str) -> dict:
        """Complete invoice processing with validation"""
        
        # Extract data
        invoice = self.extractor.extract_invoice(
            invoice_image_path=image_path,
            schema_model=Invoice
        )
        
        # Validate business rules
        if invoice.total_amount:
            calculated_total = sum(item.total for item in invoice.items or [])
            if abs(calculated_total - invoice.total_amount) > 0.01:
                print("⚠️  Warning: Total amount mismatch")
        
        # Format output
        return {
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor_name,
            "date": invoice.date,
            "total": invoice.total_amount,
            "currency": invoice.currency,
            "items_count": len(invoice.items or []),
            "status": "processed"
        }

# Usage
processor = InvoiceProcessor()
result = processor.process_invoice("invoice.jpg")
print(json.dumps(result, indent=2))
```

### ID Document Verification System

```python
class IDVerificationSystem:
    def __init__(self):
        self.extractor = DocumentExtractor()
    
    def verify_id(
        self,
        front_image: str,
        back_image: str,
        expected_name: str = None
    ) -> dict:
        """Verify ID document and check against expected data"""
        
        # Extract ID data
        id_doc = self.extractor.extract_document_id(
            front_image_path=front_image,
            back_image_path=back_image,
            schema_model=DocumentID
        )
        
        # Verification checks
        checks = {
            "has_front_data": id_doc.front is not None,
            "has_back_data": id_doc.back is not None,
            "has_dni": id_doc.front.dni is not None if id_doc.front else False,
            "name_match": False
        }
        
        # Check name if provided
        if expected_name and id_doc.front:
            extracted_name = f"{id_doc.front.name1} {id_doc.front.surname1}"
            checks["name_match"] = expected_name.lower() in extracted_name.lower()
        
        return {
            "verified": all(checks.values()),
            "checks": checks,
            "extracted_data": id_doc
        }

# Usage
verifier = IDVerificationSystem()
result = verifier.verify_id(
    front_image="dni_front.jpg",
    back_image="dni_back.jpg",
    expected_name="Juan Pérez"
)
```

## Best Practices

1. **Always use descriptive Field descriptions** - They guide the AI extraction
2. **Make fields Optional** - Documents may have missing information
3. **Use appropriate temperature** - Lower for precision, higher for flexibility
4. **Implement error handling** - Network and parsing errors can occur
5. **Cache results** - Avoid redundant API calls for the same images
6. **Validate extracted data** - Check business rules after extraction
7. **Use custom instructions** - Tailor prompts to your specific document type

## Troubleshooting

- **Low accuracy**: Lower temperature, add more specific instructions
- **Missing fields**: Check Field descriptions, ensure they're clear
- **Slow processing**: Implement caching, use batch processing
- **API errors**: Check API key, rate limits, network connectivity
