"""
LEGAL AGENT SWARM - MASTER ORCHESTRATOR
Supervised multi-agent system for legal operations.

Pipelines:
1. INTAKE:      Structured matter intake, classification and urgency triage
2. REVIEW:      Contract risk review, product counsel and regulatory assessment
3. MONITORING:  Regulatory change detection and alert drafting
4. APPROVAL:    Human-in-the-loop routing, approval gates and audit trail
5. REPORTING:   Board risk brief and escalation summaries
6. SCHEDULING:  Matter routing and reviewer calendar coordination
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add agents directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.agent_a_glass_ceiling_scout import analyze_profiles
from agents.agent_b_rainmaker_profiler import analyze_book_of_business
from agents.agent_c_outreach_architect import generate_outreach
from agents.agent_d_scheduling_concierge import SchedulingConcierge
from agents.agent_e_signal_hunter import run_signal_hunter
from agents.agent_f_thought_leader_ghostwriter import format_post_preview, generate_linkedin_post
from agents.agent_k_revenue_predictor import assess_risk, load_partners_from_json


class LegalAgentOrchestrator:
    """Supervised master orchestrator for legal operations agent pipelines."""

    def __init__(self):
        self.results = {}
        self.log = []

    def _log(self, pipeline: str, step: str, status: str):
        entry = {
            "time": datetime.now().isoformat(),
            "pipeline": pipeline,
            "step": step,
            "status": status,
        }
        self.log.append(entry)
        print(f"  [{status}] {step}")

    # ═══════════════════════════════════════════════════════════════════════
    # PIPELINE 1: RECRUITING (A → B → C → D)
    # ═══════════════════════════════════════════════════════════════════════

    async def process_candidate(self, candidate, sender_name):
        """Async wrapper to process a single candidate through B->C->D."""
        print(f"\n{'─' * 50}")
        print(f"👤 Processing: {candidate['Name']}")

        # Step 2: Agent B - Rainmaker Profiler
        self._log("recruiting", f"Agent B ({candidate['Name']})", "RUNNING")

        deal_sheet = f"""
        {candidate["Name"]} - {candidate["Current_Firm"]}
        Years in Role: {candidate["Years_in_Role"]}
        Estimated Book: {candidate["Estimated_Book_of_Business"]}
        Reason for Score: {candidate["Reason_for_Score"]}
        """

        # Run blocking call in thread
        revenue_analysis = await asyncio.to_thread(
            analyze_book_of_business, deal_sheet, candidate["Name"]
        )
        portable_revenue = revenue_analysis.get("total_portable_revenue", 0)
        recommendation = revenue_analysis.get("recommendation", "UNKNOWN")

        self._log(
            "recruiting",
            f"Agent B ({candidate['Name']})",
            f"DONE - €{portable_revenue:,.0f} → {recommendation}",
        )

        if recommendation != "GO":
            print(f"  ⚠️ {candidate['Name']}: Skipping (below threshold)")
            return None

        # Step 3: Agent C - Outreach Architect
        self._log("recruiting", f"Agent C ({candidate['Name']})", "RUNNING")

        outreach = await asyncio.to_thread(
            generate_outreach,
            candidate_name=candidate["Name"],
            current_firm=candidate["Current_Firm"],
            recent_achievement=candidate["Reason_for_Score"],
            practice_area="Legal",
            sender_name=sender_name,
        )
        self._log("recruiting", f"Agent C ({candidate['Name']})", "DONE")

        # Step 4: Agent D - Scheduling Concierge
        self._log("recruiting", f"Agent D ({candidate['Name']})", "RUNNING")

        concierge = SchedulingConcierge()
        scheduling = await asyncio.to_thread(
            concierge.process_acceptance,
            candidate_name=candidate["Name"],
            candidate_email=f"{candidate['Name'].lower().replace(' ', '.')}@example.com",
            current_firm=candidate["Current_Firm"],
            practice_area="Restructuring",
            frustration_score=candidate["Frustration_Score"],
            frustration_reasons=candidate["Reason_for_Score"],
            portable_revenue=portable_revenue,
        )
        self._log("recruiting", f"Agent D ({candidate['Name']})", "DONE")

        return {
            "candidate": candidate,
            "revenue_analysis": revenue_analysis,
            "outreach": outreach,
            "scheduling": scheduling,
        }

    async def run_recruiting_pipeline(
        self, profiles_text: str, sender_name: str = "Managing Partner"
    ):
        """
        Full recruiting pipeline (Async):
        1. Agent A: Score candidates (Frustration Score) - Single batch
        2. Agent B/C/D: Parallel execution per candidate
        """
        print("\n" + "═" * 70)
        print("🎯 RECRUITING PIPELINE (ASYNC)")
        print("═" * 70)

        # Step 1: Agent A - Glass Ceiling Scout
        print("\n📊 STEP 1: Agent A - Glass Ceiling Scout")
        self._log("recruiting", "Agent A", "RUNNING")

        # Agent A is fast enough to run in one go usually, but let's thread it too
        candidates = await asyncio.to_thread(analyze_profiles, profiles_text)

        if isinstance(candidates, dict) and "error" in candidates:
            self._log("recruiting", "Agent A", "FAILED")
            return {"error": candidates["error"]}

        # Filter high-potential only
        high_potential = [c for c in candidates if c.get("Frustration_Score", 0) > 70]
        self._log("recruiting", "Agent A", f"DONE - {len(high_potential)} candidates scored >70")

        if not high_potential:
            print("  ⚠️ No high-potential candidates found.")
            return {"candidates": [], "message": "No candidates above threshold"}

        # Parallel Execution for B -> C -> D
        print(f"\n🚀 Launching parallel processing for {len(high_potential)} candidates...")
        tasks = [self.process_candidate(c, sender_name) for c in high_potential]
        results = await asyncio.gather(*tasks)

        # Filter out None results (skipped candidates)
        valid_results = [r for r in results if r is not None]

        self.results["recruiting"] = valid_results
        return valid_results

    # ═══════════════════════════════════════════════════════════════════════
    # PIPELINE 2: CONTENT (E → F)
    # ═══════════════════════════════════════════════════════════════════════

    async def run_content_pipeline(self, partner_name: str = "Senior Partner"):
        """Content pipeline (Async)"""
        print("\n" + "═" * 70)
        print("📝 CONTENT PIPELINE")
        print("═" * 70)

        # Step 1: Agent E - Signal Hunter
        print("\n📡 STEP 1: Agent E - Signal Hunter")
        self._log("content", "Agent E", "RUNNING")
        signals = await asyncio.to_thread(run_signal_hunter)
        self._log("content", "Agent E", f"DONE - {len(signals)} signals found")

        if not signals:
            return {"signals": [], "posts": [], "message": "No signals found"}

        # Step 2: Agent F - Thought Leader Ghostwriter
        print("\n✍️ STEP 2: Agent F - Thought Leader Ghostwriter")

        async def process_signal(signal):
            self._log("content", f"Agent F ({signal.get('headline', '')[:10]})", "RUNNING")
            post = await asyncio.to_thread(generate_linkedin_post, signal, partner_name)
            return {"signal": signal, "post": post}

        # Process top 3 signals concurrently
        tasks = [process_signal(s) for s in signals[:3]]
        posts = await asyncio.gather(*tasks)

        self._log("content", "Agent F", f"DONE - {len(posts)} posts generated")

        self.results["content"] = {"signals": signals, "posts": posts}
        return self.results["content"]

    # ═══════════════════════════════════════════════════════════════════════
    # PIPELINE 3: DAILY DASHBOARD
    # ═══════════════════════════════════════════════════════════════════════

    async def run_daily_dashboard(self, partners: list):
        """Daily dashboard (Async)"""
        print("\n" + "═" * 70)
        print("📊 DAILY DASHBOARD")
        print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("═" * 70)

        dashboard = {"date": datetime.now().isoformat(), "risk_alerts": [], "signals": []}

        # Parallel Revenue Check
        print("\n💰 REVENUE RISK CHECK (Agent K)")

        async def check_partner(p):
            assessment = await asyncio.to_thread(assess_risk, p)
            if assessment["at_risk"]:
                print(f"  🔴 {p.name}: AT RISK")
                return assessment
            else:
                print(f"  🟢 {p.name}: Healthy")
                return None

        risk_results = await asyncio.gather(*[check_partner(p) for p in partners])
        dashboard["risk_alerts"] = [r for r in risk_results if r]

        # Signal Scan
        print("\n📡 SIGNAL SCAN (Agent E)")
        signals = await asyncio.to_thread(run_signal_hunter)
        dashboard["signals"] = signals[:5]

        self.results["dashboard"] = dashboard
        return dashboard

    # ═══════════════════════════════════════════════════════════════════════
    # SUMMARY REPORT
    # ═══════════════════════════════════════════════════════════════════════

    def generate_summary(self) -> str:
        """Generate a summary of all pipeline runs."""
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    APEXLAW ORCHESTRATOR SUMMARY                          ║
║                    {datetime.now().strftime("%Y-%m-%d %H:%M")}                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣

📋 EXECUTION LOG:
"""
        for entry in self.log[-20:]:  # Last 20 entries
            summary += f"  [{entry['time'][11:19]}] {entry['pipeline']}: {entry['step']} → {entry['status']}\n"

        summary += """
═══════════════════════════════════════════════════════════════════════════════

📊 RESULTS SUMMARY:
"""
        if "recruiting" in self.results:
            summary += f"  • Recruiting: {len(self.results['recruiting'])} candidates processed\n"
        if "content" in self.results:
            summary += (
                f"  • Content: {len(self.results['content'].get('posts', []))} posts generated\n"
            )
        if "dashboard" in self.results:
            summary += f"  • Dashboard: {len(self.results['dashboard'].get('risk_alerts', []))} risk alerts\n"

        return summary


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════


async def main():
    orchestrator = LegalAgentOrchestrator()

    print("\n" + "█" * 70)
    print("█  APEXLAW MASTER ORCHESTRATOR (ASYNC)")
    print("█" * 70)

    # 1. Content Pipeline
    content_results = await orchestrator.run_content_pipeline("Alex Vancer")

    if content_results.get("posts"):
        print("\n" + "═" * 70)
        print("📝 GENERATED POSTS PREVIEW")
        print("═" * 70)
        for item in content_results["posts"]:
            print(format_post_preview(item["post"]))

    # 2. Recruiting Pipeline
    sample_profiles = """
    1. Dr. Anna Miller
       - Firm: Vanguard Law Group, Frankfurt
       - Title: Senior Associate (since 2018)
       - Practice: Banking & Finance, FinTech
       - Notable Deals: Lead on €50m crypto custody framework for major German bank
       - Bio: 8 years at Vanguard Law, recognized in Legal 500 as "Rising Star"
    
    2. Dr. Marcus Vance
       - Firm: Helm & Mueller, Düsseldorf
       - Title: Counsel (since 2019)
       - Practice: M&A, Restructuring
       - Notable Deals: Key Contact on €120m restructuring of retail group
       - Bio: 10 years at Helm, passed over in 2023 partner round
    
    3. Dr. Lisa Schneider
       - Firm: CMS, Berlin
       - Title: Partner (since 2020)
       - Practice: Employment Law
       - Bio: Recently promoted, growing team
    """
    await orchestrator.run_recruiting_pipeline(sample_profiles, "Alex Vancer")

    # 3. Daily Dashboard Pipeline
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "partners_db.json")
    partners = load_partners_from_json(db_path)
    
    await orchestrator.run_daily_dashboard(partners)

    # Print summary
    print(orchestrator.generate_summary())

    # Save results
    with open("orchestrator_results.json", "w", encoding="utf-8") as f:
        json.dump(orchestrator.results, f, indent=2, ensure_ascii=False, default=str)
    print("\n💾 Results saved to orchestrator_results.json")


if __name__ == "__main__":
    asyncio.run(main())
