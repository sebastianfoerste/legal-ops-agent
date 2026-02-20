"""
Agent K: The Revenue Predictor
Purpose: Monitor financial risk of new hires during their 'Bridge Fund' period.
"""

from dataclasses import dataclass


@dataclass
class PartnerFinancials:
    name: str
    start_date: str
    monthly_draw: float  # Guaranteed monthly payment
    months_active: int
    cash_collected: list  # List of monthly collections
    pipeline_value: float  # Open matters value
    pipeline_probability: float  # Weighted probability (0-1)


# Historical benchmark
IDEAL_PARTNER_CURVE = {
    1: 0.3,
    2: 0.5,
    3: 0.7,
    4: 0.85,
    5: 0.95,
    6: 1.0,
    7: 1.1,
    8: 1.2,
    9: 1.3,
    10: 1.4,
    11: 1.5,
    12: 1.6,
}


def calculate_burn_rate(partner: PartnerFinancials) -> dict:
    """Calculate monthly burn rate: Draw vs Cash Collected."""
    total_draw = partner.monthly_draw * partner.months_active
    total_collected = sum(partner.cash_collected)
    burn_rate = (total_draw - total_collected) / total_draw if total_draw > 0 else 0

    return {
        "total_draw": total_draw,
        "total_collected": total_collected,
        "net_position": total_collected - total_draw,
        "burn_rate_pct": burn_rate * 100,
    }


def calculate_pipeline_velocity(partner: PartnerFinancials) -> dict:
    """Calculate weighted pipeline value."""
    weighted_pipeline = partner.pipeline_value * partner.pipeline_probability
    months_remaining = 12 - partner.months_active
    monthly_velocity = weighted_pipeline / months_remaining if months_remaining > 0 else 0

    return {
        "raw_pipeline": partner.pipeline_value,
        "probability": partner.pipeline_probability,
        "weighted_pipeline": weighted_pipeline,
        "projected_monthly": monthly_velocity,
    }


def project_collection(partner: PartnerFinancials, month: int) -> float:
    """Project cash collection for a future month."""
    pipeline = calculate_pipeline_velocity(partner)
    avg_monthly = (
        sum(partner.cash_collected) / len(partner.cash_collected) if partner.cash_collected else 0
    )
    return avg_monthly * 0.7 + pipeline["projected_monthly"] * 0.3


def compare_to_ideal_curve(partner: PartnerFinancials) -> dict:
    """Compare ramp-up speed to ideal partner curve."""
    ideal_ratio = IDEAL_PARTNER_CURVE.get(partner.months_active, 1.0)
    ideal_collected = partner.monthly_draw * partner.months_active * ideal_ratio
    actual_collected = sum(partner.cash_collected)

    performance_index = actual_collected / ideal_collected if ideal_collected > 0 else 0

    return {
        "ideal_collected": ideal_collected,
        "actual_collected": actual_collected,
        "performance_index": performance_index,
        "status": "AHEAD"
        if performance_index >= 1.0
        else "ON TRACK"
        if performance_index >= 0.7
        else "BEHIND",
    }


def assess_risk(partner: PartnerFinancials) -> dict:
    """Full risk assessment for a partner."""
    burn = calculate_burn_rate(partner)
    pipeline = calculate_pipeline_velocity(partner)
    curve = compare_to_ideal_curve(partner)

    # Check if projected collection < guaranteed draw
    next_month = partner.months_active + 1
    projected = project_collection(partner, next_month)
    at_risk = projected < partner.monthly_draw

    return {
        "partner": partner.name,
        "months_active": partner.months_active,
        "burn_rate": burn,
        "pipeline": pipeline,
        "curve_comparison": curve,
        "next_month_projection": projected,
        "monthly_draw": partner.monthly_draw,
        "at_risk": at_risk,
        "alert": f"⚠️ AT RISK: Projected €{projected:,.0f} < Draw €{partner.monthly_draw:,.0f}"
        if at_risk
        else "✅ Healthy",
    }


def format_risk_report(assessment: dict) -> str:
    """Format risk assessment as a report."""
    risk_icon = "🔴" if assessment["at_risk"] else "🟢"

    return f"""
╔══════════════════════════════════════════════════════════════════╗
║                    REVENUE PREDICTOR                             ║
║                    Agent K: Financial Risk Monitor               ║
╠══════════════════════════════════════════════════════════════════╣
║ Partner: {assessment["partner"]:<54} ║
║ Month: {assessment["months_active"]}/12 (Bridge Fund Period)                      ║
╠══════════════════════════════════════════════════════════════════╣

{risk_icon} STATUS: {assessment["alert"]}

💰 BURN RATE ANALYSIS
   Total Draw: €{assessment["burn_rate"]["total_draw"]:,.0f}
   Total Collected: €{assessment["burn_rate"]["total_collected"]:,.0f}
   Net Position: €{assessment["burn_rate"]["net_position"]:,.0f}
   Burn Rate: {assessment["burn_rate"]["burn_rate_pct"]:.1f}%

📊 PIPELINE VELOCITY
   Raw Pipeline: €{assessment["pipeline"]["raw_pipeline"]:,.0f}
   Weighted (@ {assessment["pipeline"]["probability"]:.0%}): €{assessment["pipeline"]["weighted_pipeline"]:,.0f}
   Projected Monthly: €{assessment["pipeline"]["projected_monthly"]:,.0f}

📈 VS. IDEAL PARTNER CURVE
   Status: {assessment["curve_comparison"]["status"]}
   Performance Index: {assessment["curve_comparison"]["performance_index"]:.2f}x
   (Ideal: €{assessment["curve_comparison"]["ideal_collected"]:,.0f} | Actual: €{assessment["curve_comparison"]["actual_collected"]:,.0f})

═══════════════════════════════════════════════════════════════════
"""


if __name__ == "__main__":
    # Example partner in month 4
    partner = PartnerFinancials(
        name="Dr. Marcus Weber",
        start_date="2025-10-01",
        monthly_draw=15000,  # €15k/month guaranteed
        months_active=4,
        cash_collected=[8000, 12000, 18000, 22000],  # Monthly collections
        pipeline_value=150000,  # €150k in open matters
        pipeline_probability=0.6,  # 60% likely to close
    )

    print("=" * 70)
    print("AGENT K: REVENUE PREDICTOR")
    print("=" * 70)

    assessment = assess_risk(partner)
    print(format_risk_report(assessment))
