"""
MASTER ORCHESTRATOR
Chains all Gunnercooke agents into automated pipelines.

Pipelines:
1. RECRUITING: A → B → C → D (Scout → Profile → Outreach → Schedule)
2. CONTENT: E → F (Signal → Ghostwrite)
3. ENGAGEMENT: G (Authority Amplifier)
4. DEALS: L (Insolvency Finder)
5. ONBOARDING: H (New Partner Setup)
6. RISK: K (Revenue Monitor)
"""

import os
import sys
import json
from datetime import datetime

# Add agents directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.agent_a_glass_ceiling_scout import analyze_profiles
from agents.agent_b_rainmaker_profiler import analyze_book_of_business, generate_business_case_memo
from agents.agent_c_outreach_architect import generate_outreach, format_linkedin_message
from agents.agent_d_scheduling_concierge import SchedulingConcierge
from agents.agent_e_signal_hunter import run_signal_hunter, format_signal_report
from agents.agent_f_thought_leader_ghostwriter import generate_linkedin_post, format_post_preview
from agents.agent_k_revenue_predictor import assess_risk, format_risk_report, PartnerFinancials


class GunnercookeOrchestrator:
    """Master orchestrator for all Gunnercooke automation agents."""
    
    def __init__(self):
        self.results = {}
        self.log = []
    
    def _log(self, pipeline: str, step: str, status: str):
        entry = {"time": datetime.now().isoformat(), "pipeline": pipeline, "step": step, "status": status}
        self.log.append(entry)
        print(f"  [{status}] {step}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # PIPELINE 1: RECRUITING (A → B → C → D)
    # ═══════════════════════════════════════════════════════════════════════
    
    def run_recruiting_pipeline(self, profiles_text: str, sender_name: str = "Managing Partner"):
        """
        Full recruiting pipeline:
        1. Agent A: Score candidates (Frustration Score)
        2. Agent B: Estimate portable revenue (Go/No-Go)
        3. Agent C: Generate outreach message
        4. Agent D: Prepare scheduling + briefing
        """
        print("\n" + "═" * 70)
        print("🎯 RECRUITING PIPELINE")
        print("═" * 70)
        
        # Step 1: Agent A - Glass Ceiling Scout
        print("\n📊 STEP 1: Agent A - Glass Ceiling Scout")
        self._log("recruiting", "Agent A", "RUNNING")
        candidates = analyze_profiles(profiles_text)
        
        if isinstance(candidates, dict) and "error" in candidates:
            self._log("recruiting", "Agent A", "FAILED")
            return {"error": candidates["error"]}
        
        # Filter high-potential only
        high_potential = [c for c in candidates if c.get('Frustration_Score', 0) > 70]
        self._log("recruiting", "Agent A", f"DONE - {len(high_potential)} candidates scored >70")
        
        if not high_potential:
            print("  ⚠️ No high-potential candidates found.")
            return {"candidates": [], "message": "No candidates above threshold"}
        
        pipeline_results = []
        
        for candidate in high_potential:
            print(f"\n{'─' * 50}")
            print(f"👤 Processing: {candidate['Name']}")
            
            # Step 2: Agent B - Rainmaker Profiler
            print("\n💰 STEP 2: Agent B - Rainmaker Profiler")
            self._log("recruiting", "Agent B", "RUNNING")
            
            # Create a mock deal sheet from the candidate data
            deal_sheet = f"""
            {candidate['Name']} - {candidate['Current_Firm']}
            Years in Role: {candidate['Years_in_Role']}
            Estimated Book: {candidate['Estimated_Book_of_Business']}
            Reason for Score: {candidate['Reason_for_Score']}
            """
            
            revenue_analysis = analyze_book_of_business(deal_sheet, candidate['Name'])
            portable_revenue = revenue_analysis.get('total_portable_revenue', 0)
            recommendation = revenue_analysis.get('recommendation', 'UNKNOWN')
            
            self._log("recruiting", "Agent B", f"DONE - €{portable_revenue:,.0f} → {recommendation}")
            
            if recommendation != "GO":
                print(f"  ⚠️ Skipping (below €200k threshold)")
                continue
            
            # Step 3: Agent C - Outreach Architect
            print("\n✉️ STEP 3: Agent C - Outreach Architect")
            self._log("recruiting", "Agent C", "RUNNING")
            
            outreach = generate_outreach(
                candidate_name=candidate['Name'],
                current_firm=candidate['Current_Firm'],
                recent_achievement=candidate['Reason_for_Score'],
                practice_area="Legal",  # Could be extracted from profile
                sender_name=sender_name
            )
            self._log("recruiting", "Agent C", "DONE")
            
            # Step 4: Agent D - Scheduling Concierge
            print("\n📅 STEP 4: Agent D - Scheduling Concierge")
            self._log("recruiting", "Agent D", "RUNNING")
            
            concierge = SchedulingConcierge()
            scheduling = concierge.process_acceptance(
                candidate_name=candidate['Name'],
                candidate_email=f"{candidate['Name'].lower().replace(' ', '.')}@example.com",
                current_firm=candidate['Current_Firm'],
                practice_area="Restructuring",
                frustration_score=candidate['Frustration_Score'],
                frustration_reasons=candidate['Reason_for_Score'],
                portable_revenue=portable_revenue
            )
            self._log("recruiting", "Agent D", "DONE")
            
            pipeline_results.append({
                "candidate": candidate,
                "revenue_analysis": revenue_analysis,
                "outreach": outreach,
                "scheduling": scheduling
            })
        
        self.results["recruiting"] = pipeline_results
        return pipeline_results
    
    # ═══════════════════════════════════════════════════════════════════════
    # PIPELINE 2: CONTENT (E → F)
    # ═══════════════════════════════════════════════════════════════════════
    
    def run_content_pipeline(self, partner_name: str = "Senior Partner"):
        """
        Content pipeline:
        1. Agent E: Find signals (regulatory, insolvency, competitor)
        2. Agent F: Generate LinkedIn posts
        """
        print("\n" + "═" * 70)
        print("📝 CONTENT PIPELINE")
        print("═" * 70)
        
        # Step 1: Agent E - Signal Hunter
        print("\n📡 STEP 1: Agent E - Signal Hunter")
        self._log("content", "Agent E", "RUNNING")
        signals = run_signal_hunter()
        self._log("content", "Agent E", f"DONE - {len(signals)} signals found")
        
        if not signals:
            return {"signals": [], "posts": [], "message": "No signals found"}
        
        # Step 2: Agent F - Thought Leader Ghostwriter
        print("\n✍️ STEP 2: Agent F - Thought Leader Ghostwriter")
        posts = []
        
        for signal in signals[:3]:  # Top 3 signals
            self._log("content", "Agent F", f"Generating post for: {signal.get('headline', 'Unknown')[:30]}...")
            post = generate_linkedin_post(signal, partner_name)
            posts.append({"signal": signal, "post": post})
        
        self._log("content", "Agent F", f"DONE - {len(posts)} posts generated")
        
        self.results["content"] = {"signals": signals, "posts": posts}
        return self.results["content"]
    
    # ═══════════════════════════════════════════════════════════════════════
    # PIPELINE 3: DAILY DASHBOARD
    # ═══════════════════════════════════════════════════════════════════════
    
    def run_daily_dashboard(self, partners: list):
        """
        Daily dashboard combining:
        - Agent K: Revenue predictions for all partners
        - Agent L: New insolvency opportunities
        - Agent E: Fresh signals
        """
        print("\n" + "═" * 70)
        print("📊 DAILY DASHBOARD")
        print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("═" * 70)
        
        dashboard = {"date": datetime.now().isoformat(), "risk_alerts": [], "signals": []}
        
        # Revenue Risk Check
        print("\n💰 REVENUE RISK CHECK (Agent K)")
        for p in partners:
            assessment = assess_risk(p)
            if assessment['at_risk']:
                dashboard["risk_alerts"].append(assessment)
                print(f"  🔴 {p.name}: AT RISK")
            else:
                print(f"  🟢 {p.name}: Healthy")
        
        # Signal Scan
        print("\n📡 SIGNAL SCAN (Agent E)")
        signals = run_signal_hunter()
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
║                    GUNNERCOOKE ORCHESTRATOR SUMMARY                          ║
║                    {datetime.now().strftime('%Y-%m-%d %H:%M')}                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣

📋 EXECUTION LOG:
"""
        for entry in self.log[-20:]:  # Last 20 entries
            summary += f"  [{entry['time'][11:19]}] {entry['pipeline']}: {entry['step']} → {entry['status']}\n"
        
        summary += f"""
═══════════════════════════════════════════════════════════════════════════════

📊 RESULTS SUMMARY:
"""
        if "recruiting" in self.results:
            summary += f"  • Recruiting: {len(self.results['recruiting'])} candidates processed\n"
        if "content" in self.results:
            summary += f"  • Content: {len(self.results['content'].get('posts', []))} posts generated\n"
        if "dashboard" in self.results:
            summary += f"  • Dashboard: {len(self.results['dashboard'].get('risk_alerts', []))} risk alerts\n"
        
        return summary


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    orchestrator = GunnercookeOrchestrator()
    
    # Demo: Run Content Pipeline
    print("\n" + "█" * 70)
    print("█  GUNNERCOOKE MASTER ORCHESTRATOR")
    print("█" * 70)
    
    # Example 1: Content Pipeline
    content_results = orchestrator.run_content_pipeline("Sebastian Förster")
    
    if content_results.get("posts"):
        print("\n" + "═" * 70)
        print("📝 GENERATED POSTS PREVIEW")
        print("═" * 70)
        for item in content_results["posts"]:
            print(format_post_preview(item["post"]))
    
    # Example 2: Recruiting Pipeline (with sample data)
    sample_profiles = """
    Dr. Anna Müller - Senior Associate at Freshfields (6 years)
    Practice: FinTech/Crypto, lead on €50m deals
    
    Marcus Weber - Counsel at Hengeler Mueller (5 years)
    Practice: Restructuring, key contact on major insolvencies
    """
    
    # Uncomment to run:
    # recruiting_results = orchestrator.run_recruiting_pipeline(sample_profiles, "Sebastian Förster")
    
    # Print summary
    print(orchestrator.generate_summary())
    
    # Save results
    with open("orchestrator_results.json", "w", encoding="utf-8") as f:
        json.dump(orchestrator.results, f, indent=2, ensure_ascii=False, default=str)
    print("\n💾 Results saved to orchestrator_results.json")
