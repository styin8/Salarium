from pydantic import BaseModel
from typing import Dict, List


class MonthlyStats(BaseModel):
    person_id: int
    year: int
    month: int
    base_salary: float
    performance: float
    allowances_total: float
    bonuses_total: float
    insurance_total: float
    tax: float
    gross_income: float
    net_income: float


class YearlyStats(BaseModel):
    person_id: int
    year: int
    months: int
    total_gross: float
    total_net: float
    avg_net: float
    insurance_total: float
    tax_total: float
    allowances_total: float
    bonuses_total: float


class FamilySummary(BaseModel):
    year: int
    persons: List[int]
    total_gross: float
    total_net: float
    insurance_total: float
    tax_total: float
    by_person: Dict[int, float]