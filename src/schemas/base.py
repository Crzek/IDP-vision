from datetime import date, datetime
from pydantic import BaseModel, BeforeValidator, Field, field_validator
from typing import Annotated, Optional


class PersonNameMixin(BaseModel):
    """Mixin para nombres de personas siguiendo el formato español"""

    first_name: Optional[str] = Field(
        default=None, description="First name of the person"
    )
    second_name: Optional[str] = Field(
        default=None, description="Second name of the person"
    )
    first_surname: Optional[str] = Field(
        default=None, description="First surname of the person"
    )
    second_surname: Optional[str] = Field(
        default=None, description="Second surname of the person"
    )


class Address(BaseModel):
    """Dirección base reutilizable"""

    street: Optional[str] = Field(default=None, description="The name of the street")
    street_type: Optional[str] = Field(
        default=None, description="The type of street in spanish, get from street"
    )
    street_number: Optional[str] = Field(
        default=None, description="The number of the street"
    )
    city: Optional[str] = Field(default=None, description="The city")
    province: Optional[str] = Field(default=None, description="The province")


class AddressWithPostalCode(Address):
    """Dirección con código postal para casos que lo requieran"""

    postal_code: Optional[str] = Field(default=None, description="The postal code")


def parse_flexible_date(valor):
    """
    Parser flexible de fechas que acepta múltiples formatos.
    Este validador se ejecuta ANTES de la validación de tipo de Pydantic.
    """
    if valor is None:
        return None

    # Si ya es un objeto date, validamos que sea razonable
    if isinstance(valor, date):
        # Validar rango de años razonable
        if valor.year < 1900 or valor.year > 2100:
            raise ValueError(
                f"Año fuera de rango razonable: {valor.year}. Debe estar entre 1900 y 2100."
            )
        return valor

    # Si es una cadena, intentamos parsearla
    if isinstance(valor, str):
        formatos_aceptados = [
            "%d %m %Y",  # Formato DD MM YYYY (tu caso principal)
            "%d/%m/%Y",  # Formato DD/MM/YYYY
            "%d-%m-%Y",  # Formato DD-MM-YYYY
            "%Y-%m-%d",  # Formato ISO
        ]

        for formato in formatos_aceptados:
            try:
                fecha_parseada = datetime.strptime(valor.strip(), formato).date()

                # Validar que el año esté en un rango razonable
                if fecha_parseada.year < 1900 or fecha_parseada.year > 2100:
                    raise ValueError(
                        f"Año fuera de rango razonable: {fecha_parseada.year}"
                    )

                return fecha_parseada
            except (ValueError, TypeError):
                continue

        raise ValueError(
            f"Formato de fecha inválido: '{valor}'. Formatos aceptados: {', '.join(formatos_aceptados)}"
        )

    raise ValueError(f"Tipo de dato no válido para fecha: {type(valor)}")


# Tipo anotado para fechas flexibles
FlexibleDate = Annotated[date, BeforeValidator(parse_flexible_date)]
