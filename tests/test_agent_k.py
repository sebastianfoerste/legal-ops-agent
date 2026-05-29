import os
import pytest
from agents.agent_k_revenue_predictor import (
    PartnerFinancials,
    calculate_burn_rate,
    assess_risk,
    load_partners_from_json,
)


def test_calculate_burn_rate():
    partner = PartnerFinancials(
        name="Test Partner",
        start_date="2025-01-01",
        monthly_draw=10000.0,
        months_active=3,
        cash_collected=[8000.0, 10000.0, 12000.0],
        pipeline_value=50000.0,
        pipeline_probability=0.5,
    )
    burn = calculate_burn_rate(partner)
    assert burn["total_draw"] == 30000.0
    assert burn["total_collected"] == 30000.0
    assert burn["net_position"] == 0.0
    assert burn["burn_rate_pct"] == 0.0


def test_assess_risk_low_pipeline():
    partner = PartnerFinancials(
        name="At Risk Partner",
        start_date="2025-01-01",
        monthly_draw=15000.0,
        months_active=2,
        cash_collected=[2000.0, 3000.0],
        pipeline_value=10000.0,
        pipeline_probability=0.2,
    )
    assessment = assess_risk(partner)
    assert assessment["at_risk"] is True


def test_load_partners_from_json():
    # Resolve file relative to workspace
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "partners_db.json")

    partners = load_partners_from_json(db_path)
    assert len(partners) > 0
    assert partners[0].name == "Dr. Marcus Vance"
