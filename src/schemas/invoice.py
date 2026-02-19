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

from pydantic import BaseModel, Field
from src.schemas.base import PersonNameMixin, AddressWithPostalCode


class SupplyHolder(PersonNameMixin):
    nif: str = Field(description="NIF of the supply holder")
    address: AddressWithPostalCode = Field(
        description="Address of the supply holder")


class SupplyPointData(BaseModel):
    address: AddressWithPostalCode = Field(
        description="Address of the supply point")
    cups: str = Field(description="CUPS code of the supply point")
    distributor_company: str = Field(
        description="Distributor company of the supply point")
    contracted_power: str = Field(
        description="Contracted power of the supply point in kW")
    voltage: str = Field(description="Voltage of the supply point in V")


class InvoiceLight(BaseModel):
    holder: SupplyHolder = Field(description="Supply holder")
    supply_point: SupplyPointData = Field(description="Supply point")
