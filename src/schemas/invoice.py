"""
Factura de luz / Electricity bill

datos / data:
titular suministro / supply holder:
    nombre / name:
    nif / nif:
    direccion / address:

punto de suministro / supply point:
    direccion / address:
    cups / cups:
    empresa_distribuidora / distributor company:
    potencia_contratada / contracted power:
    tension / voltage:
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from src.schemas.base import PersonNameMixin, AddressWithPostalCode
from src.utils.invoice import get_distributor_company


class SupplyHolder(PersonNameMixin):
    nif: str = Field(description="NIF of the supply holder")
    address: AddressWithPostalCode = Field(
        description="Address of the supply holder")


class SupplyPointData(BaseModel):
    address: AddressWithPostalCode = Field(
        description="Address of the supply point")
    cups: str = Field(description="CUPS code of the supply point")
    distributor_company: Optional[str] = Field(
        default=None,
        description="Distributor company of the supply point, in spanish 'Empresa Distribuidora eléctrica'")
    contracted_power: float = Field(
        description="Contracted power of the supply point in kW, if find multiple values, take the highest")
    voltage_find: int = Field(description="Voltage of the supply point in V")
    voltage: int = None
    voltage_text: str = None

    @model_validator(mode='after')
    def calculate_voltage(self):
        """
        Calculate the voltage based on the voltage_find value.
        If voltage_find is greater than or equal to 300, set voltage to 230, otherwise to 400.
        Also set the voltage_text based on the voltage value.
        """
        if 300 <= self.voltage_find:
            self.voltage = 230
            self.voltage_text = "MONOFÁSICO"
        else:
            self.voltage = 400
            self.voltage_text = "BIFÁSICO/TRIFÁSICO"

        return self

    @field_validator('distributor_company', mode='after')
    def validate_distributor_company(cls, v):
        if v is None:
            distributor_company = get_distributor_company(cls.cups)
            if distributor_company:
                return distributor_company
        return v.strip()


class InvoiceLight(BaseModel):
    holder: SupplyHolder = Field(description="Supply holder")
    supply_point: SupplyPointData = Field(description="Supply point")
