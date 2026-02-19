from datetime import date
from pydantic import BaseModel, Field, computed_field
from typing import Optional, Annotated
from src.schemas.base import PersonNameMixin, Address, DateValidatorMixin, FlexibleDate


class DocumentIDFront(PersonNameMixin, DateValidatorMixin):
    dni: Optional[str] = Field(description="ID or DNI of the person")
    sex: Optional[str] = Field(description="The sex of the person.")
    nacionality: Optional[str] = Field(description="The nationality of the person")
    birth_date: Optional[FlexibleDate] = Field(
        default=None,
        description="The birth date of the person, you can find with the name 'nacimiento'. Extract it as text with format 'DD MM YYYY' (space separated). Example: '15 03 1990'",
    )
    validate_date: Optional[FlexibleDate] = Field(
        default=None,
        description="The validate date of documentID, you can find with the name 'validez'. Extract it as text with format 'DD MM YYYY' (space separated). Example: '15 03 2030'",
    )
    emision_date: Optional[FlexibleDate] = Field(
        default=None,
        description="The emision date of documentID, you can find with the name 'emision'. Extract it as text with format 'DD MM YYYY' (space separated). Example: '15 03 2022'",
    )

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
