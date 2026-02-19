# PDF Support Implementation Guide

## English Version

### What Has Been Implemented

The `DocumentExtractor` class has been enhanced to support **PDF files** in addition to image formats. This implementation allows seamless processing of PDF documents using the same API methods that were previously available only for images.

### Key Changes

#### 1. New Helper Methods

Three new private methods were added to handle PDF files:

**`_is_pdf(file_path: str) -> bool`**
- Checks if a file is a PDF by examining its extension
- Returns `True` for `.pdf` files, `False` otherwise

**`_load_file(file_path: str) -> bytes`**
- Replaces the old `_load_image()` method
- Loads any file (image or PDF) from disk as bytes
- Works universally for all supported formats

**`_get_mime_type(file_path: str) -> str`**
- Automatically detects the MIME type based on file extension
- Supports:
  - Images: `image/jpeg`, `image/png`, `image/webp`, `image/gif`, `image/bmp`
  - PDFs: `application/pdf`
- Returns appropriate MIME type for Gemini API

#### 2. Updated Core Methods

**`extract_from_images()`**
- Now processes both images and PDFs
- Automatically detects file type and sets correct MIME type
- No API changes - existing code continues to work

**`extract_and_validate()`**
- Supports PDF files with Pydantic validation
- Documentation updated to reflect PDF support

**`extract_from_bytes()`**
- Already supported PDFs through MIME type parameter
- No changes needed

**`extract_from_base64()`**
- Already supported PDFs through MIME type parameter
- No changes needed

#### 3. Specialized Methods Enhanced

**`extract_document_id()`**
- Now accepts PDF files for front and back images
- Can mix PDFs and images (e.g., PDF front, JPEG back)

**`extract_invoice()`**
- Now accepts PDF invoices
- Handles multi-page PDF invoices automatically

### Technical Implementation

#### Before (Images Only)
```python
def extract_from_images(self, image_paths: list[str], ...):
    for img_path in image_paths:
        img_bytes = self._load_image(img_path)
        ext = Path(img_path).suffix.lower()
        mime_type = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }.get(ext, "image/jpeg")
        # ...
```

#### After (Images + PDFs)
```python
def extract_from_images(self, image_paths: list[str], ...):
    for file_path in image_paths:
        file_bytes = self._load_file(file_path)
        mime_type = self._get_mime_type(file_path)
        # ...
```

### How It Works

1. **File Detection**: When you pass a file path, the extractor checks the extension
2. **MIME Type Assignment**: Automatically assigns `application/pdf` for PDFs
3. **API Processing**: Sends to Gemini API with correct MIME type
4. **Data Extraction**: Gemini processes the PDF (all pages) and extracts data
5. **Validation**: Returns structured data validated with Pydantic models

### Usage Examples

#### Basic PDF Extraction
```python
from document_extractor import DocumentExtractor
from src.schemas.invoice import Invoice

extractor = DocumentExtractor()

# Extract from PDF invoice
invoice = extractor.extract_invoice(
    invoice_image_path="invoice.pdf",
    schema_model=Invoice
)
```

#### Mixed Formats
```python
# Process PDFs and images together
document = extractor.extract_and_validate(
    image_paths=[
        "page1.pdf",
        "page2.jpg",
        "page3.png"
    ],
    schema_model=Document
)
```

#### ID Documents
```python
# Both as PDFs
document_id = extractor.extract_document_id(
    front_image_path="dni_front.pdf",
    back_image_path="dni_back.pdf",
    schema_model=DocumentID
)
```

### Backward Compatibility

✅ **100% Backward Compatible**

All existing code continues to work without modifications:
- Existing image processing unchanged
- Same method signatures
- Same return types
- Same error handling

### Supported Formats

| Format | Extension | MIME Type | Status |
|--------|-----------|-----------|--------|
| JPEG | `.jpg`, `.jpeg` | `image/jpeg` | ✅ Supported |
| PNG | `.png` | `image/png` | ✅ Supported |
| WebP | `.webp` | `image/webp` | ✅ Supported |
| GIF | `.gif` | `image/gif` | ✅ Supported |
| BMP | `.bmp` | `image/bmp` | ✅ Supported |
| **PDF** | **`.pdf`** | **`application/pdf`** | **✅ NEW** |

### Benefits

1. **Unified API**: Same methods for images and PDFs
2. **Automatic Detection**: No manual MIME type specification needed
3. **Multi-Page Support**: PDFs with multiple pages processed automatically
4. **Format Flexibility**: Mix PDFs and images in single request
5. **No Breaking Changes**: Existing code works as-is

### Performance Considerations

- **PDF Processing**: Slightly slower than images due to page rendering
- **Multi-Page PDFs**: Processing time increases with page count
- **File Size**: Keep PDFs under 20 MB for optimal performance
- **Quality**: Text-based PDFs process faster than scanned PDFs

### Documentation Created

1. **PDF_SUPPORT.md**: Complete user guide for PDF features
2. **PDF_IMPLEMENTATION.md**: This technical implementation guide
3. Updated docstrings in `document_extractor.py`

---

## Versión en Español

### Qué Se Ha Implementado

La clase `DocumentExtractor` ha sido mejorada para soportar **archivos PDF** además de formatos de imagen. Esta implementación permite el procesamiento sin problemas de documentos PDF usando los mismos métodos de API que antes estaban disponibles solo para imágenes.

### Cambios Principales

#### 1. Nuevos Métodos Auxiliares

Se agregaron tres nuevos métodos privados para manejar archivos PDF:

**`_is_pdf(file_path: str) -> bool`**
- Verifica si un archivo es PDF examinando su extensión
- Retorna `True` para archivos `.pdf`, `False` en caso contrario

**`_load_file(file_path: str) -> bytes`**
- Reemplaza el antiguo método `_load_image()`
- Carga cualquier archivo (imagen o PDF) desde disco como bytes
- Funciona universalmente para todos los formatos soportados

**`_get_mime_type(file_path: str) -> str`**
- Detecta automáticamente el tipo MIME basado en la extensión del archivo
- Soporta:
  - Imágenes: `image/jpeg`, `image/png`, `image/webp`, `image/gif`, `image/bmp`
  - PDFs: `application/pdf`
- Retorna el tipo MIME apropiado para la API de Gemini

#### 2. Métodos Principales Actualizados

**`extract_from_images()`**
- Ahora procesa tanto imágenes como PDFs
- Detecta automáticamente el tipo de archivo y establece el MIME type correcto
- Sin cambios en la API - el código existente continúa funcionando

**`extract_and_validate()`**
- Soporta archivos PDF con validación Pydantic
- Documentación actualizada para reflejar soporte de PDF

**`extract_from_bytes()`**
- Ya soportaba PDFs a través del parámetro MIME type
- No se necesitaron cambios

**`extract_from_base64()`**
- Ya soportaba PDFs a través del parámetro MIME type
- No se necesitaron cambios

#### 3. Métodos Especializados Mejorados

**`extract_document_id()`**
- Ahora acepta archivos PDF para imágenes frontales y posteriores
- Puede mezclar PDFs e imágenes (ej: PDF frontal, JPEG posterior)

**`extract_invoice()`**
- Ahora acepta facturas en PDF
- Maneja facturas PDF de múltiples páginas automáticamente

### Implementación Técnica

#### Antes (Solo Imágenes)
```python
def extract_from_images(self, image_paths: list[str], ...):
    for img_path in image_paths:
        img_bytes = self._load_image(img_path)
        ext = Path(img_path).suffix.lower()
        mime_type = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }.get(ext, "image/jpeg")
        # ...
```

#### Después (Imágenes + PDFs)
```python
def extract_from_images(self, image_paths: list[str], ...):
    for file_path in image_paths:
        file_bytes = self._load_file(file_path)
        mime_type = self._get_mime_type(file_path)
        # ...
```

### Cómo Funciona

1. **Detección de Archivo**: Cuando pasas una ruta de archivo, el extractor verifica la extensión
2. **Asignación de MIME Type**: Asigna automáticamente `application/pdf` para PDFs
3. **Procesamiento API**: Envía a la API de Gemini con el MIME type correcto
4. **Extracción de Datos**: Gemini procesa el PDF (todas las páginas) y extrae datos
5. **Validación**: Retorna datos estructurados validados con modelos Pydantic

### Ejemplos de Uso

#### Extracción Básica de PDF
```python
from document_extractor import DocumentExtractor
from src.schemas.invoice import Invoice

extractor = DocumentExtractor()

# Extraer de factura PDF
invoice = extractor.extract_invoice(
    invoice_image_path="factura.pdf",
    schema_model=Invoice
)
```

#### Formatos Mixtos
```python
# Procesar PDFs e imágenes juntos
document = extractor.extract_and_validate(
    image_paths=[
        "pagina1.pdf",
        "pagina2.jpg",
        "pagina3.png"
    ],
    schema_model=Document
)
```

#### Documentos de Identidad
```python
# Ambos como PDFs
document_id = extractor.extract_document_id(
    front_image_path="dni_frontal.pdf",
    back_image_path="dni_posterior.pdf",
    schema_model=DocumentID
)
```

### Compatibilidad Hacia Atrás

✅ **100% Compatible Hacia Atrás**

Todo el código existente continúa funcionando sin modificaciones:
- Procesamiento de imágenes existente sin cambios
- Mismas firmas de métodos
- Mismos tipos de retorno
- Mismo manejo de errores

### Formatos Soportados

| Formato | Extensión | Tipo MIME | Estado |
|---------|-----------|-----------|--------|
| JPEG | `.jpg`, `.jpeg` | `image/jpeg` | ✅ Soportado |
| PNG | `.png` | `image/png` | ✅ Soportado |
| WebP | `.webp` | `image/webp` | ✅ Soportado |
| GIF | `.gif` | `image/gif` | ✅ Soportado |
| BMP | `.bmp` | `image/bmp` | ✅ Soportado |
| **PDF** | **`.pdf`** | **`application/pdf`** | **✅ NUEVO** |

### Beneficios

1. **API Unificada**: Mismos métodos para imágenes y PDFs
2. **Detección Automática**: No se necesita especificar MIME type manualmente
3. **Soporte Multi-Página**: PDFs con múltiples páginas procesados automáticamente
4. **Flexibilidad de Formato**: Mezcla PDFs e imágenes en una sola solicitud
5. **Sin Cambios Disruptivos**: El código existente funciona tal cual

### Consideraciones de Rendimiento

- **Procesamiento PDF**: Ligeramente más lento que imágenes debido al renderizado de páginas
- **PDFs Multi-Página**: El tiempo de procesamiento aumenta con el número de páginas
- **Tamaño de Archivo**: Mantén los PDFs bajo 20 MB para rendimiento óptimo
- **Calidad**: PDFs basados en texto procesan más rápido que PDFs escaneados

### Documentación Creada

1. **PDF_SUPPORT.md**: Guía completa de usuario para características PDF
2. **PDF_IMPLEMENTATION.md**: Esta guía técnica de implementación
3. Docstrings actualizados en `document_extractor.py`

### Resumen de Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `document_extractor.py` | ✏️ Métodos principales actualizados, 3 métodos nuevos agregados |
| `docs/PDF_SUPPORT.md` | ✨ Nuevo - Guía de usuario completa |
| `docs/PDF_IMPLEMENTATION.md` | ✨ Nuevo - Guía técnica de implementación |

### Migración

**No se requiere migración** - Todo el código existente funciona sin cambios.

Para usar PDFs, simplemente cambia la extensión del archivo:

```python
# Antes
invoice = extractor.extract_invoice("factura.jpg", Invoice)

# Ahora - ¡solo cambia la extensión!
invoice = extractor.extract_invoice("factura.pdf", Invoice)
```

¡Eso es todo! 🎉
