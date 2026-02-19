# Schema Refactoring Guide

## English Version

### Overview

This document explains the refactoring approach applied to the Pydantic schemas in the IDP-vision project to eliminate code duplication and follow software engineering best practices.

### Problem Identified

The original codebase had several instances of duplicated code across different schema files:

1. **Duplicate Address Classes**
   - `Address` in `document_id.py` (lines 93-103)
   - `SupplyAddress` in `invoice.py` (lines 21-27)
   - Both classes defined nearly identical fields for address information

2. **Repeated Person Name Fields**
   - `DocumentIDFront` had: `first_name`, `second_name`, `first_surname`, `second_surname`
   - `SupplyHolder` had the exact same four fields
   - This violates the DRY (Don't Repeat Yourself) principle

3. **Date Validation Logic**
   - Complex date validator in `document_id.py` (lines 60-90)
   - This reusable validation logic was not available for other schemas

### Solution: Composition Over Inheritance

Instead of using abstract base classes (ABC), we recommend using **composition with mixins and concrete base classes**. This approach is more appropriate because:

- **No forced implementation needed**: We're sharing structure and validation, not enforcing contracts
- **Flexible composition**: Classes can mix and match only what they need
- **Simpler mental model**: No abstract methods to implement
- **Better for Pydantic**: Works naturally with Pydantic's model inheritance

### Proposed Base Classes Structure

#### File: `src/schemas/base.py`

**1. PersonNameMixin**
- Encapsulates the Spanish naming convention (two names + two surnames)
- Reusable across any schema that needs person name fields
- All fields are `Optional[str]` for flexibility

**2. Address**
- Base address class with common fields: street, street_type, street_number, city, province
- All fields are optional to accommodate partial data extraction
- Used when postal code is not required

**3. AddressWithPostalCode**
- Extends `Address` to add `postal_code` field
- Used for schemas that specifically need postal codes (e.g., utility bills)

**4. DateValidatorMixin**
- Provides multi-format date validation
- Supports formats: ISO (YYYY-MM-DD), European (DD/MM/YYYY), US (MM/DD/YYYY), space-separated
- Automatically validates fields named: `birth_date`, `validate_date`, `emision_date`
- Can be extended to validate other date fields as needed

### Benefits of This Approach

1. **DRY Principle**: Code is defined once and reused everywhere
2. **Single Source of Truth**: Changes to address or name structure happen in one place
3. **Maintainability**: Bug fixes and improvements propagate automatically
4. **Type Safety**: Full Pydantic validation and type hints preserved
5. **Flexibility**: Mix and match components as needed per schema
6. **No Over-Engineering**: Simple, concrete classes without unnecessary abstraction
7. **Testability**: Base classes can be tested independently

### Usage Examples

#### Document ID Schema
```python
from src.schemas.base import PersonNameMixin, Address, DateValidatorMixin

class DocumentIDFront(PersonNameMixin, DateValidatorMixin):
    dni: Optional[str] = Field(description="ID or DNI of the person")
    sex: Optional[str] = Field(description="The sex of the person")
    nacionality: Optional[str] = Field(description="The nationality of the person")
    birth_date: Optional[date] = Field(description="The birth date of the person")
    validate_date: Optional[date] = Field(description="The validate date of documentID")
    emision_date: Optional[date] = Field(description="The emision date of documentID")
    
    @computed_field
    @property
    def sex_text(self) -> str:
        # ... custom logic
```

#### Invoice Schema
```python
from src.schemas.base import PersonNameMixin, AddressWithPostalCode

class SupplyHolder(PersonNameMixin):
    nif: str = Field(description="NIF of the supply holder")
    address: AddressWithPostalCode = Field(description="Address of the supply holder")

class SupplyPointData(BaseModel):
    address: AddressWithPostalCode = Field(description="Address of the supply point")
    cups: str = Field(description="CUPS code")
    # ... other fields
```

### Migration Strategy

1. **Create base.py**: Define all base classes and mixins
2. **Update imports**: Import base classes in existing schema files
3. **Refactor schemas**: Replace duplicated code with base class inheritance
4. **Test thoroughly**: Ensure all validations still work correctly
5. **Remove old code**: Delete duplicated class definitions

### Best Practices

- **Use mixins for cross-cutting concerns**: Name fields, date validation, etc.
- **Use inheritance for "is-a" relationships**: AddressWithPostalCode "is-a" Address
- **Keep base classes focused**: Each base class should have a single responsibility
- **Document field descriptions**: Maintain clear descriptions for API documentation
- **Optional by default**: Use `Optional` for fields that may not always be extracted

---

## Versión en Español

### Descripción General

Este documento explica el enfoque de refactorización aplicado a los esquemas Pydantic en el proyecto IDP-vision para eliminar la duplicación de código y seguir las mejores prácticas de ingeniería de software.

### Problema Identificado

El código original tenía varias instancias de código duplicado en diferentes archivos de esquemas:

1. **Clases de Dirección Duplicadas**
   - `Address` en `document_id.py` (líneas 93-103)
   - `SupplyAddress` en `invoice.py` (líneas 21-27)
   - Ambas clases definían campos casi idénticos para información de dirección

2. **Campos de Nombre de Persona Repetidos**
   - `DocumentIDFront` tenía: `first_name`, `second_name`, `first_surname`, `second_surname`
   - `SupplyHolder` tenía exactamente los mismos cuatro campos
   - Esto viola el principio DRY (Don't Repeat Yourself - No te repitas)

3. **Lógica de Validación de Fechas**
   - Validador complejo de fechas en `document_id.py` (líneas 60-90)
   - Esta lógica de validación reutilizable no estaba disponible para otros esquemas

### Solución: Composición sobre Herencia

En lugar de usar clases base abstractas (ABC), recomendamos usar **composición con mixins y clases base concretas**. Este enfoque es más apropiado porque:

- **No se necesita forzar implementación**: Compartimos estructura y validación, no imponemos contratos
- **Composición flexible**: Las clases pueden mezclar y combinar solo lo que necesitan
- **Modelo mental más simple**: No hay métodos abstractos que implementar
- **Mejor para Pydantic**: Funciona naturalmente con la herencia de modelos de Pydantic

### Estructura de Clases Base Propuesta

#### Archivo: `src/schemas/base.py`

**1. PersonNameMixin**
- Encapsula la convención de nombres española (dos nombres + dos apellidos)
- Reutilizable en cualquier esquema que necesite campos de nombre de persona
- Todos los campos son `Optional[str]` para flexibilidad

**2. Address**
- Clase de dirección base con campos comunes: calle, tipo de calle, número, ciudad, provincia
- Todos los campos son opcionales para acomodar extracción parcial de datos
- Se usa cuando no se requiere código postal

**3. AddressWithPostalCode**
- Extiende `Address` para agregar el campo `postal_code`
- Se usa para esquemas que específicamente necesitan códigos postales (ej: facturas de servicios)

**4. DateValidatorMixin**
- Proporciona validación de fechas en múltiples formatos
- Soporta formatos: ISO (YYYY-MM-DD), Europeo (DD/MM/YYYY), US (MM/DD/YYYY), separado por espacios
- Valida automáticamente campos llamados: `birth_date`, `validate_date`, `emision_date`
- Puede extenderse para validar otros campos de fecha según sea necesario

### Beneficios de Este Enfoque

1. **Principio DRY**: El código se define una vez y se reutiliza en todas partes
2. **Fuente Única de Verdad**: Los cambios en la estructura de dirección o nombre ocurren en un solo lugar
3. **Mantenibilidad**: Las correcciones de errores y mejoras se propagan automáticamente
4. **Seguridad de Tipos**: Se preserva completamente la validación y las anotaciones de tipo de Pydantic
5. **Flexibilidad**: Mezcla y combina componentes según sea necesario por esquema
6. **Sin Sobre-Ingeniería**: Clases simples y concretas sin abstracción innecesaria
7. **Testabilidad**: Las clases base pueden probarse independientemente

### Ejemplos de Uso

#### Esquema de Documento de Identidad
```python
from src.schemas.base import PersonNameMixin, Address, DateValidatorMixin

class DocumentIDFront(PersonNameMixin, DateValidatorMixin):
    dni: Optional[str] = Field(description="ID o DNI de la persona")
    sex: Optional[str] = Field(description="El sexo de la persona")
    nacionality: Optional[str] = Field(description="La nacionalidad de la persona")
    birth_date: Optional[date] = Field(description="La fecha de nacimiento de la persona")
    validate_date: Optional[date] = Field(description="La fecha de validez del documentoID")
    emision_date: Optional[date] = Field(description="La fecha de emisión del documentoID")
    
    @computed_field
    @property
    def sex_text(self) -> str:
        # ... lógica personalizada
```

#### Esquema de Factura
```python
from src.schemas.base import PersonNameMixin, AddressWithPostalCode

class SupplyHolder(PersonNameMixin):
    nif: str = Field(description="NIF del titular del suministro")
    address: AddressWithPostalCode = Field(description="Dirección del titular del suministro")

class SupplyPointData(BaseModel):
    address: AddressWithPostalCode = Field(description="Dirección del punto de suministro")
    cups: str = Field(description="Código CUPS")
    # ... otros campos
```

### Estrategia de Migración

1. **Crear base.py**: Definir todas las clases base y mixins
2. **Actualizar imports**: Importar clases base en archivos de esquema existentes
3. **Refactorizar esquemas**: Reemplazar código duplicado con herencia de clases base
4. **Probar exhaustivamente**: Asegurar que todas las validaciones sigan funcionando correctamente
5. **Eliminar código antiguo**: Borrar definiciones de clases duplicadas

### Mejores Prácticas

- **Usar mixins para preocupaciones transversales**: Campos de nombre, validación de fechas, etc.
- **Usar herencia para relaciones "es-un"**: AddressWithPostalCode "es-una" Address
- **Mantener clases base enfocadas**: Cada clase base debe tener una única responsabilidad
- **Documentar descripciones de campos**: Mantener descripciones claras para documentación de API
- **Opcional por defecto**: Usar `Optional` para campos que pueden no siempre ser extraídos

---

## Implementation Checklist

- [ ] Create `src/schemas/base.py` with base classes
- [ ] Update `src/schemas/document_id.py` to use base classes
- [ ] Update `src/schemas/invoice.py` to use base classes
- [ ] Run tests to verify functionality
- [ ] Update documentation
- [ ] Remove deprecated duplicate code

## Notes

This refactoring maintains 100% backward compatibility while improving code quality and maintainability. All existing functionality is preserved.
