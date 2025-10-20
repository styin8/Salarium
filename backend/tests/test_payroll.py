from decimal import Decimal

from app.services.payroll import compute_payroll


def test_compute_payroll_basic_decimal_accuracy():
    data = compute_payroll(
        base_salary=Decimal("10000.00"),
        performance_salary=Decimal("1500.25"),
        high_temp_allowance=Decimal("200.50"),
        low_temp_allowance=Decimal("0.00"),
        computer_allowance=Decimal("100.00"),
        meal_allowance=Decimal("300.00"),
        mid_autumn_benefit=Decimal("0.00"),
        dragon_boat_benefit=Decimal("0.00"),
        spring_festival_benefit=Decimal("0.00"),
        other_income=Decimal("50.00"),
        pension_insurance=Decimal("800.00"),
        medical_insurance=Decimal("300.00"),
        unemployment_insurance=Decimal("50.00"),
        critical_illness_insurance=Decimal("20.00"),
        enterprise_annuity=Decimal("0.00"),
        housing_fund=Decimal("600.00"),
        other_deductions=Decimal("0.00"),
        tax=Decimal("500.00"),
    )

    assert data["total_income"] == Decimal("12250.75")
    assert data["total_deductions"] == Decimal("1770.00")
    assert data["gross_income"] == Decimal("12250.75")
    assert data["tax"] == Decimal("500.00")
    assert data["net_income"] == Decimal("9980.75")  # 12250.75 - 1770.00 - 500.00
    # Actual take-home excludes meal & festival benefits
    assert data["actual_take_home"] == Decimal("10000.00") + Decimal("1500.25") + Decimal("200.50") + Decimal("100.00") + Decimal("50.00") - Decimal("1770.00")
    assert data["non_cash_benefits"] == Decimal("300.00")
