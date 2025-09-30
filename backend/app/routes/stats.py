from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from ..models import SalaryRecord, Person
from ..schemas.stats import MonthlyStats, YearlyStats, FamilySummary
from ..utils.auth import get_current_user
from ..services.payroll import compute_payroll


router = APIRouter()


@router.get("/monthly", response_model=List[MonthlyStats])
async def monthly_stats(
    user= get_current_user,
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
):
    q = SalaryRecord.filter(person__user_id=user.id)
    if person_id:
        q = q.filter(person_id=person_id)
    if year:
        q = q.filter(year=year)
    if month:
        q = q.filter(month=month)
    recs = await q.all()
    result: List[MonthlyStats] = []
    for r in recs:
        calc = compute_payroll(
            base_salary=r.base_salary,
            performance_percent=r.performance_percent,
            performance_fixed=r.performance_fixed,
            allowances=r.allowances,
            bonuses=r.bonuses,
            ins_pension=r.ins_pension,
            ins_medical=r.ins_medical,
            ins_unemployment=r.ins_unemployment,
            ins_injury=r.ins_injury,
            ins_maternity=r.ins_maternity,
            housing_fund=r.housing_fund,
            tax=r.tax,
            auto_tax=False,
        )
        result.append(
            MonthlyStats(
                person_id=r.person_id,
                year=r.year,
                month=r.month,
                base_salary=r.base_salary,
                performance=calc["performance"],
                allowances_total=calc["allowances_total"],
                bonuses_total=calc["bonuses_total"],
                insurance_total=calc["insurance_total"],
                tax=calc["tax"],
                gross_income=calc["gross_income"],
                net_income=calc["net_income"],
            )
        )
    return result


@router.get("/yearly", response_model=List[YearlyStats])
async def yearly_stats(user= get_current_user, person_id: Optional[int] = Query(default=None), year: int = Query(...)):
    persons = await Person.filter(user_id=user.id).all()
    person_ids = {p.id for p in persons}
    if person_id and person_id not in person_ids:
        raise HTTPException(status_code=404, detail="人员不存在")
    if person_id:
        person_ids = {person_id}
    recs = await SalaryRecord.filter(person_id__in=list(person_ids), year=year).all()
    stats_map = {}
    for r in recs:
        calc = compute_payroll(
            base_salary=r.base_salary,
            performance_percent=r.performance_percent,
            performance_fixed=r.performance_fixed,
            allowances=r.allowances,
            bonuses=r.bonuses,
            ins_pension=r.ins_pension,
            ins_medical=r.ins_medical,
            ins_unemployment=r.ins_unemployment,
            ins_injury=r.ins_injury,
            ins_maternity=r.ins_maternity,
            housing_fund=r.housing_fund,
            tax=r.tax,
            auto_tax=False,
        )
        s = stats_map.get(r.person_id, {
            "months": 0, "gross": 0.0, "net": 0.0, "insurance": 0.0, "tax": 0.0, "allowances": 0.0, "bonuses": 0.0
        })
        s["months"] += 1
        s["gross"] += calc["gross_income"]
        s["net"] += calc["net_income"]
        s["insurance"] += calc["insurance_total"]
        s["tax"] += calc["tax"]
        s["allowances"] += calc["allowances_total"]
        s["bonuses"] += calc["bonuses_total"]
        stats_map[r.person_id] = s
    result: List[YearlyStats] = []
    for pid, s in stats_map.items():
        avg_net = s["net"] / s["months"] if s["months"] else 0.0
        result.append(YearlyStats(
            person_id=pid,
            year=year,
            months=s["months"],
            total_gross=s["gross"],
            total_net=s["net"],
            avg_net=avg_net,
            insurance_total=s["insurance"],
            tax_total=s["tax"],
            allowances_total=s["allowances"],
            bonuses_total=s["bonuses"],
        ))
    return result


@router.get("/family", response_model=FamilySummary)
async def family_summary(user= get_current_user, year: int = Query(...)):
    persons = await Person.filter(user_id=user.id).all()
    person_ids = [p.id for p in persons]
    recs = await SalaryRecord.filter(person_id__in=person_ids, year=year).all()
    totals = {pid: 0.0 for pid in person_ids}
    insurance_total = 0.0
    tax_total = 0.0
    total_gross = 0.0
    total_net = 0.0
    for r in recs:
        calc = compute_payroll(
            base_salary=r.base_salary,
            performance_percent=r.performance_percent,
            performance_fixed=r.performance_fixed,
            allowances=r.allowances,
            bonuses=r.bonuses,
            ins_pension=r.ins_pension,
            ins_medical=r.ins_medical,
            ins_unemployment=r.ins_unemployment,
            ins_injury=r.ins_injury,
            ins_maternity=r.ins_maternity,
            housing_fund=r.housing_fund,
            tax=r.tax,
            auto_tax=False,
        )
        totals[r.person_id] += calc["net_income"]
        insurance_total += calc["insurance_total"]
        tax_total += calc["tax"]
        total_gross += calc["gross_income"]
        total_net += calc["net_income"]
    return FamilySummary(
        year=year,
        persons=person_ids,
        total_gross=total_gross,
        total_net=total_net,
        insurance_total=insurance_total,
        tax_total=tax_total,
        by_person=totals,
    )