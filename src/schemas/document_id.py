from datetime import datetime, date
from pydantic import BaseModel, Field, computed_field, model_validator
from typing import Optional, Annotated
from src.schemas.base import PersonNameMixin, Address


class DocumentIDFront(PersonNameMixin):
    id_number: str = Field(
        ..., description="ID or DNI of the person",
        min_length=9, max_length=9)
    sex: str = Field(..., description="The sex of the person.")
    nacionality: Optional[str] = Field(
        default=None, description="The nationality of the person")
    birth_date_str: str = Field(
        ...,
        description="The birth date of the person, you can find with the name 'nacimiento'. Extract it as text with format 'DD MM YYYY' (space separated). Example: '15 03 1990'",
    )
    validate_date_str: str = Field(
        ...,
        description="The validate date of documentID, you can find with the name 'validez'. Extract it as text with format 'DD MM YYYY' (space separated). Example: '15 03 2030'",
    )
    emision_date_str: Optional[str] = Field(
        default=None,
        description="The emision date of documentID, you can find with the name 'emision'. Extract it as text with format 'DD MM YYYY' (space separated). Example: '15 03 2022'",
    )
    # estos los generamos nosotros
    birth_date: date = None
    validate_date: date = None
    emision_date: date = None

    @computed_field
    @property
    def type_id(self) -> str:
        """
        Tengo que ver si es un NIF o NIE
        """
        if self.id_number.startswith(("X", "Y", "Z")):
            return "NIE"
        else:
            return "NIF"

    @computed_field
    @property
    def sex_text(self) -> str:
        if self.sex == "M":
            return "Male"
        elif self.sex == "F":
            return "Female"
        elif len(self.sex) > 1:
            return self.sex
        else:
            return "Unknown"

    @model_validator(mode='after')
    def parse_dates(self):
        """
        Parsea las fechas de nacimiento, validez y emisión desde strings a objetos date.

        NOTE: tambien se podria haber hecho con computed
        """
        formatos = ["%d %m %Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]

        def parse_date_string(date_str: Optional[str]) -> Optional[date]:
            if date_str is None:
                return None

            for formato in formatos:
                try:
                    fecha = datetime.strptime(date_str.strip(), formato).date()
                    if 1900 <= fecha.year <= 2100:
                        return fecha
                except ValueError:
                    continue

            raise ValueError(f"Formato de fecha inválido: {date_str}")

        self.birth_date = parse_date_string(self.birth_date_str)
        self.validate_date = parse_date_string(self.validate_date_str)
        self.emision_date = parse_date_string(self.emision_date_str)

        return self


class DocumentIDBack(BaseModel):
    address: Optional[Annotated[Address, Field(description="The detailed address")]] = (
        Field(description="The detailed address")
    )


class DocumentID(BaseModel):
    front: Optional[
        Annotated[
            DocumentIDFront,
            Field(description="The front side of the identity document"),
        ]
    ]
    back: Optional[
        Annotated[
            DocumentIDBack,
            Field(description="The back side of the identity document"),
        ]
    ]
