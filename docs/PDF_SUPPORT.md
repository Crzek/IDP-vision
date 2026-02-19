# PDF Support in DocumentExtractor

## Overview

`DocumentExtractor` now supports **PDF files** in addition to images (JPEG, PNG, WebP, GIF, BMP). You can use PDFs anywhere you would use image files.

## Supported Formats

### Images
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- WebP (`.webp`)
- GIF (`.gif`)
- BMP (`.bmp`)

### Documents
- **PDF (`.pdf`)** ✨ NEW

## Usage Examples

### Extract from PDF Invoice

```python
from document_extractor import DocumentExtractor
from src.schemas.invoice import Invoice

extractor = DocumentExtractor()

# Extract from PDF file
invoice = extractor.extract_invoice(
    invoice_image_path="invoice.pdf",
    schema_model=Invoice
)

print(f"Vendor: {invoice.vendor_name}")
print(f"Total: {invoice.total_amount}")
```

### Extract from PDF ID Document

```python
from src.schemas.document_id import DocumentID

# Both files can be PDFs
document = extractor.extract_document_id(
    front_image_path="dni_front.pdf",
    back_image_path="dni_back.pdf",
    schema_model=DocumentID
)

# Or mix PDF and images
document = extractor.extract_document_id(
    front_image_path="dni_front.jpg",
    back_image_path="dni_back.pdf",  # PDF for back
    schema_model=DocumentID
)
```

### Extract from Multi-Page PDF

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class MultiPageDocument(BaseModel):
    title: Optional[str] = Field(description="Document title")
    content: Optional[str] = Field(description="Main content")
    pages_count: Optional[int] = Field(description="Number of pages")

# Single PDF with multiple pages
document = extractor.extract_and_validate(
    image_paths=["multi_page_document.pdf"],
    schema_model=MultiPageDocument,
    custom_instructions="""
    This is a multi-page PDF document.
    Extract information from all pages.
    Combine related information across pages.
    """
)
```

### Generic PDF Extraction

```python
# Any PDF document
result = extractor.extract_and_validate(
    image_paths=["document.pdf"],
    schema_model=YourModel
)
```

### Mix PDFs and Images

```python
# Process both PDFs and images together
results = extractor.extract_and_validate(
    image_paths=[
        "page1.pdf",
        "page2.jpg",
        "page3.png",
        "page4.pdf"
    ],
    schema_model=Document
)
```

## How It Works

The `DocumentExtractor` automatically:

1. **Detects file type** by extension (`.pdf`, `.jpg`, etc.)
2. **Sets correct MIME type** (`application/pdf` for PDFs)
3. **Sends to Gemini API** which handles PDF processing natively
4. **Extracts text and data** from all pages
5. **Returns structured JSON** validated with Pydantic

## PDF-Specific Features

### Automatic Page Handling

Gemini automatically processes all pages in a PDF:

```python
# No need to split PDF pages manually
invoice = extractor.extract_invoice(
    invoice_image_path="multi_page_invoice.pdf",
    schema_model=Invoice
)
```

### Text Extraction

PDFs with text layers are processed more accurately:

```python
# Works with both scanned PDFs and text-based PDFs
document = extractor.extract_and_validate(
    image_paths=["contract.pdf"],
    schema_model=Contract
)
```

## Best Practices

### 1. File Size

Keep PDF files reasonable in size:
- ✅ Good: < 10 MB per file
- ⚠️ Caution: 10-20 MB
- ❌ Avoid: > 20 MB (may timeout)

### 2. Quality

For scanned PDFs:
- Use at least 300 DPI resolution
- Ensure text is readable
- Avoid heavily compressed PDFs

### 3. Multi-Page Documents

For better accuracy with multi-page PDFs:

```python
custom_instructions = """
This is a multi-page document.
- Page 1 contains the header and summary
- Page 2 contains detailed items
- Page 3 contains terms and conditions
Extract all relevant information from all pages.
"""

result = extractor.extract_and_validate(
    image_paths=["document.pdf"],
    schema_model=YourModel,
    custom_instructions=custom_instructions
)
```

### 4. Mixed Formats

When processing both PDFs and images:

```python
# Organize by document type
files = [
    "invoice_page1.pdf",
    "invoice_page2.jpg",  # Scanned image
    "invoice_page3.pdf"
]

invoice = extractor.extract_and_validate(
    image_paths=files,
    schema_model=Invoice
)
```

## Complete Example

```python
from document_extractor import DocumentExtractor
from src.schemas.document_id import DocumentID
from src.schemas.invoice import Invoice

# Initialize extractor
extractor = DocumentExtractor()

# Example 1: PDF Invoice
print("Processing PDF invoice...")
invoice = extractor.extract_invoice(
    invoice_image_path="data/invoice.pdf",
    schema_model=Invoice
)
print(f"✓ Invoice from {invoice.vendor_name}: ${invoice.total_amount}")

# Example 2: PDF ID Documents
print("\nProcessing PDF ID documents...")
document_id = extractor.extract_document_id(
    front_image_path="data/dni_front.pdf",
    back_image_path="data/dni_back.pdf",
    schema_model=DocumentID
)
print(f"✓ ID: {document_id.front.dni}")

# Example 3: Mixed formats
print("\nProcessing mixed formats...")
result = extractor.extract_and_validate(
    image_paths=[
        "data/page1.pdf",
        "data/page2.jpg",
        "data/page3.png"
    ],
    schema_model=YourModel
)
print("✓ Mixed format processing complete")
```

## Troubleshooting

### PDF Not Processing

**Issue**: PDF file not being recognized

**Solution**:
```python
# Verify file extension
from pathlib import Path
file_path = "document.pdf"
print(f"Extension: {Path(file_path).suffix}")  # Should be .pdf

# Check MIME type detection
mime_type = extractor._get_mime_type(file_path)
print(f"MIME type: {mime_type}")  # Should be application/pdf
```

### Poor Extraction Quality

**Issue**: Low accuracy with scanned PDFs

**Solutions**:
1. Increase PDF resolution (300+ DPI)
2. Use OCR preprocessing if needed
3. Convert to high-quality images first
4. Provide more specific instructions

```python
custom_instructions = """
This is a scanned PDF document.
The text may be unclear in some areas.
Focus on extracting the most visible and clear information.
If text is unclear, use null for that field.
"""
```

### Large File Errors

**Issue**: Timeout or memory errors with large PDFs

**Solutions**:
1. Split large PDFs into smaller chunks
2. Reduce PDF file size
3. Use image conversion for specific pages

## API Compatibility

The PDF support uses Gemini's native PDF processing:
- ✅ **gemini-2.0-flash**: Full PDF support
- ✅ **gemini-2.0-flash-lite**: Full PDF support
- ✅ **gemini-1.5-pro**: Full PDF support
- ✅ **gemini-1.5-flash**: Full PDF support

## Migration Guide

If you're currently using images, switching to PDFs is seamless:

### Before (Images only)
```python
invoice = extractor.extract_invoice(
    invoice_image_path="invoice.jpg",
    schema_model=Invoice
)
```

### After (PDF support)
```python
# Just change the file extension - everything else stays the same!
invoice = extractor.extract_invoice(
    invoice_image_path="invoice.pdf",
    schema_model=Invoice
)
```

No code changes required! 🎉

## Performance Comparison

| Format | Processing Time | Accuracy | Best For |
|--------|----------------|----------|----------|
| PDF (text) | Fast | Excellent | Digital documents |
| PDF (scanned) | Medium | Good | Scanned documents |
| JPEG | Fast | Good | Photos, scans |
| PNG | Fast | Excellent | Screenshots, diagrams |

## Limitations

1. **File size**: Keep PDFs under 20 MB
2. **Page count**: Best results with < 50 pages
3. **Password protection**: Encrypted PDFs not supported
4. **Forms**: Interactive PDF forms may not extract properly

## Next Steps

- See [QUICK_START.md](./QUICK_START.md) for basic usage
- See [ADVANCED_USAGE.md](./ADVANCED_USAGE.md) for advanced features
- Check examples in the `/examples` directory
