"""
OfferCompare Pro - Node Implementations
Complete set of nodes for intelligent job offer analysis and comparison
"""

from pocketflow import Node, BatchNode, AsyncNode, AsyncBatchNode, AsyncParallelBatchNode
from utils.call_llm import call_llm, call_llm_structured, call_llm_async, call_llm_structured_async
from utils.web_research import research_company, get_market_sentiment, research_company_async, get_market_sentiment_async
from utils.col_calculator import estimate_annual_expenses, get_location_insights
from utils.tax_calculator import calculate_net_pay
from utils.market_data import (get_compensation_insights, calculate_market_percentile, ai_market_analysis,
                              get_compensation_insights_async, calculate_market_percentile_async, ai_market_analysis_async)
from utils.levels import get_universal_level_async, get_level_description
from utils.scoring import calculate_offer_score, compare_offers, customize_weights
from utils.viz_formatter import create_visualization_package
from utils.company_db import get_company_data, enrich_company_data
import json
import asyncio
import time
from datetime import datetime

class OfferCollectionNode(Node):
    """
    Collect and validate comprehensive offer data from user input.
    Handles multiple job offers with detailed information.
    """
    
    def prep(self, shared):
        """Initialize empty offers list and user preferences."""
        if "offers" not in shared:
            shared["offers"] = []
        if "user_preferences" not in shared:
            shared["user_preferences"] = {}
        return {"existing_offers": len(shared["offers"])}
    
    def exec(self, prep_data):
        """Collect offer information from user with comprehensive validation."""
        offers = []
        
        print("\nWelcome to BenchMarked - Intelligent Job Offer Analysis!")
        print("=" * 60)
        
        # Collect user preferences first
        print("\nFirst, let's understand your priorities...")
        priorities = self._collect_user_priorities()
        
        # Collect offers
        num_offers = self._get_number_of_offers()
        
        for i in range(num_offers):
            print(f"\nCollecting details for Offer #{i+1}")
            print("-" * 40)
            offer = self._collect_single_offer(i+1)
            if offer:
                offers.append(offer)
        
        return {
            "offers": offers,
            "user_preferences": priorities,
            "collection_summary": f"Collected {len(offers)} offers successfully"
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store collected offers and preferences in shared store."""
        shared["offers"] = exec_res["offers"]
        shared["user_preferences"] = exec_res["user_preferences"]
        shared["collection_summary"] = exec_res["collection_summary"]
        
        print(f"\n{exec_res['collection_summary']}")
        return "default"
    
    def _collect_user_priorities(self):
        """Collect user priorities and preferences."""
        print("What's most important to you in a job offer?")
        print("1. Salary and compensation")
        print("2. Career growth and learning")
        print("3. Work-life balance")
        print("4. Mixed priorities")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        priorities = {}
        if choice == "1":
            priorities["salary_focused"] = True
        elif choice == "2":
            priorities["growth_focused"] = True
        elif choice == "3":
            priorities["balance_focused"] = True
        else:
            priorities["mixed"] = True
        
        return priorities
    
    def _get_number_of_offers(self):
        """Get number of offers to compare."""
        while True:
            try:
                num = int(input("\nHow many job offers would you like to compare? (2-10): "))
                if 2 <= num <= 10:
                    return num
                else:
                    print("Please enter a number between 2 and 10.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _collect_single_offer(self, offer_num):
        """Collect comprehensive details for a single offer."""
        offer = {"id": f"offer_{offer_num}"}
        
        # Basic information
        offer["company"] = input("Company name: ").strip()
        offer["position"] = input("Position title: ").strip()
        offer["location"] = input("Location (e.g., 'Seattle, WA' or 'Remote'): ").strip()
        
        # Compensation details
        try:
            offer["base_salary"] = float(input("Base salary ($): ").replace("$", "").replace(",", ""))
            
            equity_input = input("Annual equity value ($ or press Enter for 0): ").strip()
            offer["equity"] = float(equity_input.replace("$", "").replace(",", "")) if equity_input else 0
            
            bonus_input = input("Annual bonus ($ or press Enter for 0): ").strip()
            offer["bonus"] = float(bonus_input.replace("$", "").replace(",", "")) if bonus_input else 0
            
            offer["total_compensation"] = offer["base_salary"] + offer["equity"] + offer["bonus"]
            
        except ValueError:
            print("Invalid salary format. Please enter numbers only.")
            return None
        
        # Additional details
        offer["years_experience"] = self._get_optional_int("Years of experience for this role", default=5)
        offer["vesting_years"] = self._get_optional_int("Equity vesting period (years)", default=4)
        
        return offer
    
    def _get_optional_int(self, prompt, default=None):
        """Get optional integer input with default."""
        user_input = input(f"{prompt} (default {default}): ").strip()
        if not user_input and default is not None:
            return default
        try:
            return int(user_input)
        except ValueError:
            return default if default is not None else 0

def map_score_to_grade(score: float) -> str:
    """Map a 1-10 or 0-100 score to a letter grade consistently."""
    # Handle 0-100 normalization if needed
    val = score if score <= 10 else score / 10
    if val >= 9.0: return "A+"
    if val >= 8.0: return "A"
    if val >= 7.0: return "B+"
    if val >= 6.0: return "B"
    return "C"

class MarketResearchNode(AsyncParallelBatchNode):
    """
    Gather comprehensive market intelligence for each company using AI agents.
    Uses AsyncParallelBatchNode for concurrent parallel I/O operations across all companies.
    """
    
    async def prep_async(self, shared):
        """Extract company and position details for research."""
        offers = shared.get("offers", [])
        research_items = []
        
        for offer in offers:
            research_items.append({
                "offer_id": offer.get("id"),
                "company": offer.get("company", "Unknown"),
                "position": offer.get("position", "Unknown"),
                "location": offer.get("location", "Unknown")
            })
        
        return research_items
    
    async def exec_async(self, research_item):
        """
        Conduct AI-powered research for a single company.
        Uses async I/O for parallel processing.
        """
        start_time = time.time()
        timestamp = datetime.fromtimestamp(start_time).strftime("%H:%M:%S.%f")[:-3]
        print(f"\n[DEBUG] MarketResearch for {research_item['company']} started at {timestamp}")
        print(f"Conducting market research for {research_item['company']}...")
        
        try:
            # Parallel async calls for research data - run concurrently
            company_research, market_sentiment = await asyncio.gather(
                research_company_async(research_item["company"], research_item["position"]),
                get_market_sentiment_async(research_item["company"], research_item["position"]),
            )
            
            # These are local operations, so keep sync for now
            company_db_data = get_company_data(research_item["company"])
            enriched_data = enrich_company_data(research_item["company"], {
                "position_context": research_item["position"],
                "location": research_item["location"]
            })
            
            end_time = time.time()
            duration = end_time - start_time
            end_timestamp = datetime.fromtimestamp(end_time).strftime("%H:%M:%S.%f")[:-3]
            print(f"[DEBUG] MarketResearch for {research_item['company']} completed at {end_timestamp}, duration: {duration:.2f}s")
            
            return {
                "offer_id": research_item["offer_id"],
                "company_research": company_research,
                "market_sentiment": market_sentiment,
                "company_db_data": company_db_data,
                "enriched_data": enriched_data
            }
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Quota" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"[INFO] Quota hit in MarketResearch. Using mock data.")
                return {
                    "offer_id": research_item["offer_id"],
                    "company_research": {
                        "summary": f"Mock research for {research_item['company']}",
                        "metrics": {},
                        "insights": "Mock insights"
                    },
                    "market_sentiment": "Positive (Mock)",
                    "company_db_data": {},
                    "enriched_data": {}
                }
            raise e
    
    async def post_async(self, shared, prep_res, exec_res_list):
        """Enrich offers with research data."""
        research_lookup = {r.get("offer_id"): r for r in exec_res_list if isinstance(r, dict)}
        
        # Enrich each offer with research data
        for offer in shared["offers"]:
            if offer["id"] in research_lookup:
                research_data = research_lookup[offer["id"]]
                offer["company_research"] = research_data["company_research"]
                offer["market_sentiment"] = research_data["market_sentiment"]
                offer["company_db_data"] = research_data["company_db_data"]
                offer["enriched_data"] = research_data["enriched_data"]
                
                # Auto-populate grades consistently
                metrics = research_data["company_research"].get("metrics", {})
                culture_metrics = research_data["company_db_data"].get("culture_metrics", {}) if research_data.get("company_db_data") else {}
                
                wlb_score = culture_metrics.get("work_life_balance", metrics.get("wlb_score", {}).get("score", 7.0))
                growth_score = culture_metrics.get("career_growth", metrics.get("growth_score", {}).get("score", 7.0))
                benefits_score = culture_metrics.get("benefits_quality", metrics.get("benefits_score", {}).get("score", 7.0))
                
                offer["wlb_score"] = wlb_score
                offer["growth_score"] = growth_score
                
                offer["wlb_grade"] = map_score_to_grade(wlb_score)
                offer["growth_grade"] = map_score_to_grade(growth_score)
                offer["benefits_grade"] = map_score_to_grade(benefits_score)
        
        print(f"Market research completed for {len(exec_res_list)} companies")
        return "default"

class TaxCalculationNode(BatchNode):
    """
    Calculate estimated tax and net pay for each offer.
    Separated from COL logic for clarity.
    """
    
    def prep(self, shared):
        """Extract offers for tax calculation."""
        offers = shared.get("offers", [])
        return offers
    
    def exec(self, offer):
        """Calculate tax and net pay for a single offer."""
        print(f"\nCalculating tax for {offer['company']} ({offer['location']})...")
        
        # Handle Remote logic: Use base_location from user prefs if location is 'Remote'
        # Note: In a real flow, we might want to pass user prefs explicitly, 
        # but here we'll assume the offer might act as the container or we pass a tuple.
        # Actually, let's keep it simple and just use the offer's location for now, 
        # or implies we should have enriched usage of base_location.
        # Let's fix prep to pass the base_location.
        pass # Placeholder as we need to fix prep below
        
    # Re-implementing correctly with prep passing tuple
    
    def prep(self, shared):
        """Extract offers and user base location."""
        offers = shared.get("offers", [])
        user_base_location = shared.get("user_preferences", {}).get("base_location", "San Francisco, CA")
        
        items = []
        for offer in offers:
            items.append({
                "offer": offer,
                "base_location": user_base_location
            })
        return items

    def exec(self, item):
        """Calculate tax for a single offer."""
        offer = item["offer"]
        base_location = item["base_location"]
        
        tax_location = offer["location"]
        if "remote" in tax_location.lower():
            tax_location = base_location
            print(f"  -> Remote offer detected, using base location: {tax_location}")
            
        print(f"  -> Calculating tax for location: {tax_location}, Total Comp: ${offer['total_compensation']:,}")
        
        net_pay_analysis = calculate_net_pay(
            offer["total_compensation"],
            tax_location
        )
        
        print(f"  -> Estimated Net Pay: ${net_pay_analysis['estimated_net_pay']:,}")
        
        return {
            "offer_id": offer["id"],
            "net_pay_analysis": net_pay_analysis
        }

    def post(self, shared, prep_res, exec_res_list):
        """Update offers with tax analysis."""
        analysis_lookup = {r["offer_id"]: r["net_pay_analysis"] for r in exec_res_list}
        
        for offer in shared["offers"]:
            if offer["id"] in analysis_lookup:
                offer["net_pay_analysis"] = analysis_lookup[offer["id"]]
                offer["estimated_net_pay"] = analysis_lookup[offer["id"]]["estimated_net_pay"]
                offer["estimated_tax"] = analysis_lookup[offer["id"]]["estimated_tax_amount"]
        
        print("Tax calculations completed")
        return "default"


class COLAnalysisNode(BatchNode):
    """
    Analyze Cost of Living and Savings Potential.
    Calculates annual expenses and Net Savings.
    """
    
    def prep(self, shared):
        """Extract offers for COL analysis."""
        return shared.get("offers", [])
    
    def exec(self, offer):
        """Calculate expenses and savings for a single offer."""
        location = offer["location"]
        print(f"\nAnalyzing Cost of Living for {offer['company']} ({location})...")
        
        # Estimate Annual Expenses
        expense_analysis = estimate_annual_expenses(location)
        annual_expenses = expense_analysis["estimated_annual_expenses"]
        
        # Calculate Net Savings
        # Net Savings = Net Pay - Annual Expenses
        net_pay = offer.get("estimated_net_pay", 0)
        net_savings = net_pay - annual_expenses
        
        print(f"  -> Annual Expenses (Est): ${annual_expenses:,}")
        print(f"  -> Net Savings (Est): ${net_savings:,}")
        
        return {
            "offer_id": offer["id"],
            "expense_analysis": expense_analysis,
            "net_savings": net_savings
        }
        
    def post(self, shared, prep_res, exec_res_list):
        """Update offers with COL and Savings analysis."""
        results_lookup = {r["offer_id"]: r for r in exec_res_list}
        
        for offer in shared["offers"]:
            if offer["id"] in results_lookup:
                res = results_lookup[offer["id"]]
                offer["expense_analysis"] = res["expense_analysis"]
                offer["estimated_annual_expenses"] = res["expense_analysis"]["estimated_annual_expenses"]
                offer["net_savings"] = res["net_savings"]
                
        print("COL and Net Savings analysis completed")
        return "default"

class MarketBenchmarkingNode(AsyncParallelBatchNode):
    """
    Compare each offer against industry market standards.
    Uses AsyncParallelBatchNode for concurrent parallel market data API calls.
    """
    
    async def prep_async(self, shared):
        """Extract offer data for market comparison."""
        offers = shared.get("offers", [])
        benchmark_items = []
        
        for offer in offers:
            benchmark_items.append({
                "offer_id": offer["id"],
                "company": offer["company"],
                "position": offer["position"],
                "level": offer.get("level"),  # Captured from user input
                "location": offer["location"],
                "base_salary": offer["base_salary"],
                "total_compensation": offer["total_compensation"],
                "equity": offer.get("equity", 0),
                "bonus": offer.get("bonus", 0),
                "years_experience": offer.get("years_experience", 5)
            })
        
        return benchmark_items
    
    async def exec_async(self, benchmark_item):
        """Perform market benchmarking for a single offer using async calls."""
        start_time = time.time()
        timestamp = datetime.fromtimestamp(start_time).strftime("%H:%M:%S.%f")[:-3]
        print(f"\n[DEBUG] MarketBenchmarking for {benchmark_item['company']} started at {timestamp}")
        print(f"Performing market benchmarking analysis for {benchmark_item['company']} {benchmark_item['position']}...")
        
        try:
            # 1. Determine seniority level for benchmarking
            # This can involve an LLM call, so move it inside try/except
            universal_level = await get_universal_level_async(
                benchmark_item["company"], 
                benchmark_item["level"] or "", 
                benchmark_item["position"]
            )
            level_desc = get_level_description(universal_level)
            print(f"  -> Identified seniority level: {level_desc}")

            # 2. Parallel async calls for market data - run concurrently
            # Passing universal_level to refine the search
            compensation_insights, base_percentile, total_percentile, ai_analysis = await asyncio.gather(
                get_compensation_insights_async(
                    benchmark_item["position"],
                    benchmark_item["base_salary"],
                    benchmark_item["equity"],
                    benchmark_item["bonus"],
                    benchmark_item["location"],
                    universal_level=universal_level
                ),
                calculate_market_percentile_async(
                    benchmark_item["base_salary"],
                    benchmark_item["position"],
                    benchmark_item["location"],
                    universal_level=universal_level
                ),
                calculate_market_percentile_async(
                    benchmark_item["total_compensation"],
                    benchmark_item["position"],
                    benchmark_item["location"],
                    universal_level=universal_level
                ),
                ai_market_analysis_async(
                    benchmark_item["position"],
                    benchmark_item["company"],
                    benchmark_item["location"],
                    {
                        "base_salary": benchmark_item["base_salary"],
                        "equity_value": benchmark_item["equity"],
                        "bonus": benchmark_item["bonus"],
                        "total_compensation": benchmark_item["total_compensation"],
                        "company_level": benchmark_item["level"],
                        "universal_level": universal_level
                    }
                )
            )
            
            end_time = time.time()
            duration = end_time - start_time
            end_timestamp = datetime.fromtimestamp(end_time).strftime("%H:%M:%S.%f")[:-3]
            print(f"[DEBUG] MarketBenchmarking for {benchmark_item['company']} completed at {end_timestamp}, duration: {duration:.2f}s")
            
            # Include alias keys expected by tests
            return {
                "offer_id": benchmark_item["offer_id"],
                "universal_level": universal_level,
                "level_description": level_desc,
                "compensation_insights": compensation_insights,
                "market_insights": compensation_insights,
                "base_percentile": base_percentile,
                "market_analysis": base_percentile,
                "total_percentile": total_percentile,
                "total_comp_analysis": total_percentile,
                "ai_analysis": ai_analysis
            }
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Quota" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"[INFO] Quota hit in MarketBenchmarking. Using mock data.")
                return {
                    "offer_id": benchmark_item["offer_id"],
                    "universal_level": universal_level,
                    "level_description": level_desc,
                    "compensation_insights": "Mock compensation insights (Quota reached)",
                    "market_insights": "Mock compensation insights (Quota reached)",
                    "base_percentile": {"market_percentile": 50, "score": 50},
                    "market_analysis": {"market_percentile": 50, "score": 50},
                    "total_percentile": {"market_percentile": 50, "score": 50},
                    "total_comp_analysis": {"market_percentile": 50, "score": 50},
                    "ai_analysis": "Market analysis placeholder (Quota hit)"
                }
            raise e
    
    async def post_async(self, shared, prep_res, exec_res_list):
        """Add market benchmarking data to offers."""
        benchmark_lookup = {r.get("offer_id"): r for r in exec_res_list if isinstance(r, dict)}
        
        for offer in shared["offers"]:
            if offer["id"] in benchmark_lookup:
                benchmark_data = benchmark_lookup[offer["id"]]
                offer["market_analysis"] = benchmark_data["base_percentile"]
                offer["total_comp_analysis"] = benchmark_data["total_percentile"]
                offer["compensation_insights"] = benchmark_data["compensation_insights"]
                offer["ai_market_analysis"] = benchmark_data["ai_analysis"]
        
        print("Market benchmarking completed")
        return "default"

class PreferenceScoringNode(BatchNode):
    """
    Calculate personalized scores based on user-defined weightings.
    Uses BatchNode to process each offer individually with user preferences.
    """
    
    def prep(self, shared):
        """Prepare offer-preference pairs for individual scoring."""
        offers = shared.get("offers", [])
        user_preferences = shared.get("user_preferences", {})
        
        # Return list of (offer, preferences) tuples for batch processing
        return [(offer, user_preferences) for offer in offers]
    
    def exec(self, offer_with_prefs):
        """Calculate score for a single offer with user preferences."""
        offer, user_preferences = offer_with_prefs
        
        print(f"\nCalculating personalized score for {offer.get('company', 'Unknown')}...")
        
        # Customize weights based on user priorities  
        weights = customize_weights(user_preferences)
        
        # Calculate score for this specific offer
        score_data = calculate_offer_score(offer, user_preferences, weights)
        
        return {
            "offer_id": offer["id"],
            "score_data": score_data,
            "weights_used": weights
        }
    
    def post(self, shared, prep_res, exec_res_list):
        """Store scoring results and generate comparison."""
        # Add individual scores to offers
        score_lookup = {s["offer_id"]: s["score_data"] for s in exec_res_list}
        
        for offer in shared["offers"]:
            if offer["id"] in score_lookup:
                offer["score_data"] = score_lookup[offer["id"]]
        
        # Generate comparison results using all scored offers
        user_preferences = shared.get("user_preferences", {})
        weights = exec_res_list[0]["weights_used"] if exec_res_list else customize_weights(user_preferences)
        comparison_results = compare_offers(shared["offers"], user_preferences, weights)
        
        # Store comparison results and weights
        shared["comparison_results"] = comparison_results
        shared["scoring_weights"] = weights
        
        print("Personalized scoring completed")
        return "default"

class AIAnalysisNode(AsyncNode):
    """
    Generate comprehensive AI-powered recommendations and risk assessments.
    Provides detailed analysis and career trajectory insights.
    """
    
    async def prep_async(self, shared):
        """Prepare all processed offer data for AI analysis."""
        return {
            "offers": shared.get("offers", []),
            "comparison_results": shared.get("comparison_results", {}),
            "user_preferences": shared.get("user_preferences", {}),
            "scoring_weights": shared.get("scoring_weights", {})
        }
    
    async def exec_async(self, prep_data):
        """Generate comprehensive AI analysis using async LLM calls."""
        start_time = time.time()
        timestamp = datetime.fromtimestamp(start_time).strftime("%H:%M:%S.%f")[:-3]
        print(f"\n[DEBUG] AIAnalysis started at {timestamp}")
        
        offers = prep_data["offers"]
        comparison_results = prep_data["comparison_results"]
        user_preferences = prep_data["user_preferences"]
        
        print(f"Generating AI-powered analysis and recommendations...")
        
        # Prepare comprehensive data for AI analysis
        analysis_prompt = self._build_analysis_prompt(offers, comparison_results, user_preferences)
        
        # Get comprehensive AI analysis with async LLM call
        try:
            ai_analysis = await call_llm_async(
                analysis_prompt,
                temperature=0.3,
                system_prompt="You are an expert career advisor and compensation analyst providing comprehensive job offer analysis."
            )
        except Exception as e:
            error_str = str(e)
            print(f"[WARNING] Main AI Analysis failed: {error_str[:100]}...")
            ai_analysis = "Our AI is currently at capacity. Here is a summary of your data: " + comparison_results.get("comparison_summary", "Comparison available in details.")
        
        # Generate specific recommendations for each offer (async) - run in parallel
        rec_start_time = time.time()
        rec_timestamp = datetime.fromtimestamp(rec_start_time).strftime("%H:%M:%S.%f")[:-3]
        print(f"[DEBUG] Generating {len(offers)} recommendations in parallel, started at {rec_timestamp}")
        
        recommendation_tasks = [
            self._generate_offer_recommendation_async(offer, user_preferences)
            for offer in offers
        ]
        recommendations = await asyncio.gather(*recommendation_tasks)
        
        rec_end_time = time.time()
        rec_duration = rec_end_time - rec_start_time
        rec_end_timestamp = datetime.fromtimestamp(rec_end_time).strftime("%H:%M:%S.%f")[:-3]
        print(f"[DEBUG] Recommendations generation completed at {rec_end_timestamp}, duration: {rec_duration:.2f}s")
        
        offer_recommendations = [
            {
                "offer_id": offer["id"],
                "recommendation": recommendation
            }
            for offer, recommendation in zip(offers, recommendations)
        ]
        
        # Generate decision framework (async)
        try:
            decision_framework = await self._generate_decision_framework_async(offers, comparison_results)
        except Exception as e:
            print(f"[WARNING] Decision Framework AI failed: {str(e)[:100]}...")
            decision_framework = "1. Compare Net Pay\n2. Evaluate WLB vs Growth\n3. Consider long-term career trajectory."
        
        end_time = time.time()
        duration = end_time - start_time
        end_timestamp = datetime.fromtimestamp(end_time).strftime("%H:%M:%S.%f")[:-3]
        print(f"[DEBUG] AIAnalysis completed at {end_timestamp}, total duration: {duration:.2f}s")
        
        return {
            "comprehensive_analysis": ai_analysis,
            "offer_recommendations": offer_recommendations,
            "decision_framework": decision_framework,
            # Aliases for tests
            "ai_analysis": ai_analysis,
            "recommendation": offer_recommendations[0]["recommendation"] if offer_recommendations else ""
        }
    
    async def post_async(self, shared, prep_res, exec_res):
        """Store AI analysis results."""
        # Add recommendations to individual offers
        rec_lookup = {r["offer_id"]: r["recommendation"] for r in exec_res["offer_recommendations"]}
        
        for offer in shared["offers"]:
            if offer["id"] in rec_lookup:
                offer["ai_recommendation"] = rec_lookup[offer["id"]]
        
        # KEY FIX: Also update the ranked_offers list in comparison_results
        # because the frontend uses THIS list for the dashboard, not shared["offers"]
        if "comparison_results" in shared and "ranked_offers" in shared["comparison_results"]:
            for ranked_offer in shared["comparison_results"]["ranked_offers"]:
                if ranked_offer["offer_id"] in rec_lookup: # Note: ranked_offer uses 'offer_id', original uses 'id'
                    ranked_offer["ai_recommendation"] = rec_lookup[ranked_offer["offer_id"]]
                elif ranked_offer.get("id") in rec_lookup: # Handle case where it might use 'id'
                    ranked_offer["ai_recommendation"] = rec_lookup[ranked_offer["id"]]
        
        # Store comprehensive analysis
        shared["ai_analysis"] = exec_res["comprehensive_analysis"]
        shared["decision_framework"] = exec_res["decision_framework"]
        
        print("AI analysis completed")
        return "default"
    
    def _build_analysis_prompt(self, offers, comparison_results, user_preferences):
        """Build comprehensive prompt for AI analysis."""
        prompt = f"""
        Analyze these {len(offers)} job offers and provide comprehensive insights:

        USER PRIORITIES: {user_preferences}

        OFFERS SUMMARY:
        """
        
        for offer in offers:
            net_pay = offer.get('estimated_net_pay', 0)
            net_pay_str = f"${net_pay:,}" if net_pay > 0 else "N/A"
            prompt += f"""
        {offer.get('company', 'Unknown')} - {offer.get('position', 'Unknown')} ({offer.get('location', 'Unknown')})
        - Base Salary: ${offer.get('base_salary', 0):,}
        - Total Comp: ${offer.get('total_compensation', offer.get('base_salary', 0) + offer.get('equity', 0) + offer.get('bonus', 0)):,}
        - Estimated Net Pay (After Tax): {net_pay_str}
        - Market Percentile: {offer.get('market_analysis', {}).get('market_percentile', 'N/A')}
        - Score: {offer.get('score_data', {}).get('total_score', 'N/A')}
        """
        
        prompt += f"""
        
        TOP CHOICE: {comparison_results.get('top_offer', {}).get('company', 'N/A')}
        
        Please provide:
        1. Executive summary of the offer comparison
        2. Detailed analysis of each offer's strengths and weaknesses (MANDATORY: Mention the Estimated Net Pay/Take-home salary for each offer here)
        3. Risk factors and considerations for each offer
        4. Career trajectory implications (1-5 year outlook)
        5. Negotiation opportunities and strategies
        6. Final recommendation with reasoning
        7. Red flags or concerns to watch out for
        8. Questions to ask each company before deciding
        
        Focus on actionable insights for decision-making.
        """
        
        return prompt
    
    async def _generate_offer_recommendation_async(self, offer, user_preferences):
        """Generate specific recommendation for an individual offer using async LLM."""
        net_pay = offer.get('estimated_net_pay', 0)
        net_pay_str = f"${net_pay:,}" if net_pay > 0 else "N/A"
        
        # Use structured LLM call for dashboard-ready JSON
        prompt = f"""
        Analyze this job offer and return a JSON object for the visual dashboard.
        
        Company: {offer.get('company', 'Unknown')}
        Position: {offer.get('position', 'Unknown')}
        Location: {offer.get('location', 'Unknown')}
        Total Compensation: ${offer.get('total_compensation', 0):,}
        Estimated Net Pay (After Tax): {net_pay_str}
        Total Score: {offer.get('score_data', {}).get('total_score', offer.get('total_score', 'N/A'))}
        
        User Priorities: {user_preferences}
        
        Required JSON Structure:
        {{
            "verdict": {{
                "badge": "Short badge text (e.g. 'Top Pick 🏆', 'Growth Rocket 🚀', 'Safe Bet 🛡️')",
                "color": "green/yellow/red/blue",
                "one_line_summary": "Concise summary max 15 words"
            }},
            "scores": {{
                "compensation": 1-10,
                "work_life_balance": 1-10,
                "growth_potential": 1-10, 
                "job_stability": 1-10,
                "culture_fit": 1-10
            }},
            "key_insights": {{
                "pros": ["pro1", "pro2"],
                "cons": ["con1", "con2"]
            }}
        }}
        """
        
        json_str = ""
        try:
            # Try to get real AI analysis
            try:
                json_str = await call_llm_structured_async(prompt=prompt, response_format={"type": "json_object"}, temperature=0.3)
                
                # Cleaning step: Remove markdown code blocks if present
                clean_str = json_str.strip()
                if clean_str.startswith("```"):
                    clean_str = clean_str.split("\n", 1)[1]
                    if clean_str.endswith("```"):
                        clean_str = clean_str.rsplit("\n", 1)[0]
                
                return json.loads(clean_str)

            except Exception as e:
                # Catch ALL errors here, including Rate Limits that bubble up
                error_str = str(e)
                print(f"[WARNING] AI Analysis failed for {offer.get('id')}: {error_str[:100]}...")
                
                # If it's a Quota/Rate Limit error, use Mock Data
                if "429" in error_str or "Quota" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    print(f"[INFO] Quota hit (Caught in Node). Generating MOCK data.")
                    return {
                        "verdict": {
                            "badge": "Mock Analysis 🛠️", 
                            "color": "blue", 
                            "one_line_summary": "API Quota exceeded. Showing reliable mock data for UI testing."
                        },
                        "scores": {
                            "compensation": 8.5,
                            "work_life_balance": 7.0,
                            "growth_potential": 9.0, 
                            "job_stability": 8.0,
                            "culture_fit": 7.5
                        },
                        "key_insights": {
                            "pros": ["Excellent base salary (Mock)", "Strong brand recognition (Mock)", "Remote options available (Mock)"],
                            "cons": ["High cost of living area (Mock)", "Potential for burnout (Mock)"]
                        },
                        "financial_view": {
                                "net_pay": 150000,
                                "monthly_burn": 5000,
                                "savings_rate": "45%"
                        }
                    }
                raise e # Re-raise other errors to be caught effectively by outer loop or logged

        except Exception as e:
            print(f"Error parsing/generating AI recommendation: {e}")
            # Fallback structure for non-quota errors (e.g. parsing failed)
            return {
                "verdict": {"badge": "Analysis Failed", "color": "gray", "one_line_summary": "Could not generate analysis suitable for visuals."},
                "scores": {
                    "compensation": 0,
                    "work_life_balance": 0,
                    "growth_potential": 0, 
                    "job_stability": 0,
                    "culture_fit": 0
                },
                "key_insights": {
                    "pros": ["Analysis unavailable"],
                    "cons": ["Please check logs"]
                }
            }
    
    async def _generate_decision_framework_async(self, offers, comparison_results):
        """Generate a decision-making framework using async LLM."""
        prompt = f"""
        Create a decision framework for choosing between these {len(offers)} offers.
        
        Provide:
        1. Top 3 decision criteria to focus on
        2. Deal-breakers to watch for
        3. Questions to ask yourself before deciding
        4. Timeline recommendations for decision-making
        5. How to handle counteroffers
        
        Keep it practical and actionable.
        """
        
        return await call_llm_async(prompt, temperature=0.3)

class VisualizationPreparationNode(Node):
    """
    Prepare data for interactive charts and comparison visualizations.
    Creates Chart.js compatible data structures.
    """
    
    def prep(self, shared):
        """Prepare scored offers and weights for visualization."""
        return {
            "comparison_results": shared.get("comparison_results", {}),
            "scoring_weights": shared.get("scoring_weights", {})
        }
    
    def exec(self, prep_data):
        """Generate comprehensive visualization package."""
        comparison_results = prep_data["comparison_results"]
        scoring_weights = prep_data["scoring_weights"]
        
        print(f"\nPreparing interactive visualizations...")
        
        ranked_offers = comparison_results.get("ranked_offers", [])
        
        # Create comprehensive visualization package
        viz_package = create_visualization_package(ranked_offers, scoring_weights)
        
        return {
            "visualization_data": viz_package,
            "chart_count": len([k for k in viz_package.keys() if k.endswith("_chart") or k.endswith("_comparison")]),
            "charts_ready": True
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store visualization data."""
        shared["visualization_data"] = exec_res["visualization_data"]
        
        print(f"Prepared {exec_res['chart_count']} interactive visualizations")
        return "default"

class ReportGenerationNode(Node):
    """
    Generate final comprehensive comparison report with actionable insights.
    Creates structured report with recommendations and visualizations.
    """
    
    def prep(self, shared):
        """Gather all analysis results for final report."""
        return {
            "offers": shared.get("offers", []),
            "comparison_results": shared.get("comparison_results", {}),
            "ai_analysis": shared.get("ai_analysis", ""),
            "decision_framework": shared.get("decision_framework", ""),
            "visualization_data": shared.get("visualization_data", {}),
            "user_preferences": shared.get("user_preferences", {})
        }
    
    def exec(self, prep_data):
        """Generate comprehensive final report."""
        print(f"\nGenerating comprehensive comparison report...")
        
        # Create structured report
        report = self._generate_structured_report(prep_data)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(prep_data)
        
        # Create action items
        action_items = self._generate_action_items(prep_data)
        
        return {
            "final_report": report,
            "executive_summary": executive_summary,
            "action_items": action_items,
            "report_timestamp": "2024-01-01",  # In production, use actual timestamp
            # Added metadata for tests
            "analysis_metadata": {
                "offers": len(prep_data.get("offers", [])),
                "timestamp": "2024-01-01"
            }
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store final report and display summary."""
        shared["final_report"] = exec_res["final_report"]
        shared["executive_summary"] = exec_res["executive_summary"]
        shared["action_items"] = exec_res["action_items"]
        
        # Display executive summary
        print("\n" + "="*80)
        print("BENCHMARKED - EXECUTIVE SUMMARY")
        print("="*80)
        print(exec_res["executive_summary"])
        print("\n" + "="*80)
        
        print("Comprehensive analysis completed!")
        return "default"
    
    def _generate_structured_report(self, data):
        """Generate the main structured report."""
        offers = data["offers"]
        comparison_results = data["comparison_results"]
        
        # Enrich offer rankings with AI recommendations
        ranked_offers = comparison_results.get("ranked_offers", [])
        enriched_rankings = []
        
        for ranking in ranked_offers:
            # Find the corresponding offer to get the AI recommendation
            offer_data = ranking.get("offer_data", {})
            offer_id = ranking.get("offer_id")
            
            # Look for AI recommendation in the original offers array
            ai_recommendation = "No specific recommendation available"
            for offer in offers:
                if offer.get("id") == offer_id:
                    ai_recommendation = offer.get("ai_recommendation", "No specific recommendation available")
                    break
            
            # Create enriched ranking with AI recommendation
            enriched_ranking = {
                "offer_id": ranking.get("offer_id"),
                "company": ranking.get("company"),
                "position": ranking.get("position"),
                "total_score": ranking.get("total_score"),
                "rank": ranking.get("rank"),
                "ai_recommendation": ai_recommendation
            }
            enriched_rankings.append(enriched_ranking)
        
        report = {
            "report_type": "BenchMarked Analysis",
            "analysis_date": "2024-01-01",
            "offers_analyzed": len(offers),
            "top_recommendation": comparison_results.get("top_offer", {}).get("company", "N/A"),
            "detailed_analysis": data["ai_analysis"],
            "decision_framework": data["decision_framework"],
            "offer_rankings": enriched_rankings,
            "visualization_summary": data["visualization_data"].get("summary_stats", {})
        }
        
        return report
    
    def _generate_executive_summary(self, data):
        """Generate executive summary for immediate decision-making."""
        comparison_results = data["comparison_results"]
        top_offer = comparison_results.get("top_offer", {})
        
        if not top_offer:
            return "No offers available for comparison."
        
        summary = f"""
    TOP RECOMMENDATION: {top_offer.get('company', 'N/A')} - {top_offer.get('position', 'N/A')}
   Overall Score: {top_offer.get('total_score', 0):.1f}/100 ({top_offer.get('rating', 'N/A')})

COMPARISON SUMMARY:
   {comparison_results.get('comparison_summary', 'Analysis completed')}

KEY INSIGHTS:
   • Total offers analyzed: {len(data['offers'])}
   • Score range: {data['visualization_data'].get('summary_stats', {}).get('score_range', {}).get('min', 0):.1f} - {data['visualization_data'].get('summary_stats', {}).get('score_range', {}).get('max', 0):.1f}
   • Average score: {data['visualization_data'].get('summary_stats', {}).get('avg_score', 0):.1f}

NEXT STEPS:
   1. Review detailed analysis below
   2. Consider negotiation opportunities
   3. Ask clarifying questions to companies
   4. Make your decision with confidence!
        """
        
        return summary.strip()
    
    def _generate_action_items(self, data):
        """Generate specific action items for the user."""
        action_items = [
            "Review the detailed AI analysis for each offer",
            "Consider the decision framework provided",
            "Identify negotiation opportunities with top choices",
            "Prepare questions to ask companies before final decision",
            "Set a decision timeline and stick to it"
        ]
        
        return action_items


class QuickVisualizationNode(Node):
    """
    Quick Visualization - Generates essential charts and concise report.
    Combines visualization prep and report generation for fast results.
    """
    
    def prep(self, shared):
        """Gather all analysis results for quick visualization and report."""
        return {
            "offers": shared.get("offers", []),
            "comparison_results": shared.get("comparison_results", {}),
            # New Net Value Analysis fields
            "net_value_analysis": shared.get("net_value_analysis", {}),
            "lifestyle_comparison": shared.get("lifestyle_comparison", {}),
            "summary_table": shared.get("summary_table", {}),
            "verdict": shared.get("verdict", {}),
            "negotiation_options": shared.get("negotiation_options", []),
            "negotiation_opportunities": shared.get("negotiation_opportunities", []),  # Keep for backward compatibility
            "reality_checks": shared.get("reality_checks", {}),
            # Old fields for backward compatibility
            "ai_analysis": shared.get("ai_analysis", ""),
            "decision_framework": shared.get("decision_framework", ""),
            "scoring_weights": shared.get("scoring_weights", {}),
            "user_preferences": shared.get("user_preferences", {})
        }
    
    def exec(self, prep_data):
        """Generate essential visualizations and concise report."""
        print(f"\nPreparing quick visualizations and report...")
        
        comparison_results = prep_data["comparison_results"]
        ranked_offers = comparison_results.get("ranked_offers", [])
        scoring_weights = prep_data["scoring_weights"]
        
        # Generate essential visualization package (radar and bar charts only)
        viz_package = create_visualization_package(ranked_offers, scoring_weights)
        
        # Keep only essential charts
        essential_viz = {
            "radar_chart": viz_package.get("radar_chart"),
            "bar_chart": viz_package.get("bar_chart"),
            "summary_stats": viz_package.get("summary_stats", {})
        }
        
        # Generate concise executive summary
        top_offer = comparison_results.get("top_offer", {})
        executive_summary = self._generate_quick_summary(prep_data, top_offer)
        
        # Generate minimal structured report with new Net Value Analysis fields
        final_report = {
            "report_type": "BenchMarked Quick Analysis",
            "analysis_date": "2024-01-01",
            "offers_analyzed": len(prep_data["offers"]),
            "top_recommendation": top_offer.get("company", "N/A"),
            # Include new Net Value Analysis fields
            "net_value_analysis": prep_data.get("net_value_analysis", {}),
            "lifestyle_comparison": prep_data.get("lifestyle_comparison", {}),
            "summary_table": prep_data.get("summary_table", {}),
            "verdict": prep_data.get("verdict", {}),
            "negotiation_options": prep_data.get("negotiation_options", []),
            "negotiation_opportunities": prep_data.get("negotiation_opportunities", []),  # Keep for backward compatibility
            # Keep old fields for backward compatibility with full analysis
            "detailed_analysis": prep_data.get("ai_analysis", ""),
            "decision_framework": prep_data.get("decision_framework", ""),
            "offer_rankings": [
                {
                    "offer_id": r.get("offer_id"),
                    "company": r.get("company"),
                    "total_score": r.get("total_score"),
                    "rank": r.get("rank"),
                    "offer_data": r.get("offer_data")  # Ensure full data is passed
                }
                for r in ranked_offers
            ]
        }
        
        return {
            "visualization_data": essential_viz,
            "executive_summary": executive_summary,
            "final_report": final_report,
            "action_items": [
                "Review the AI analysis above",
                "Consider the decision framework",
                "Use full analysis for detailed insights"
            ],
            "chart_count": 2,
            "charts_ready": True
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store quick visualization and report data."""
        shared["visualization_data"] = exec_res["visualization_data"]
        shared["executive_summary"] = exec_res["executive_summary"]
        shared["final_report"] = exec_res["final_report"]
        shared["action_items"] = exec_res["action_items"]
        
        print(f"Prepared {exec_res['chart_count']} essential visualizations")
        print("\n" + "="*80)
        print("BENCHMARKED - QUICK ANALYSIS SUMMARY")
        print("="*80)
        print(exec_res["executive_summary"])
        print("\n" + "="*80)
        print("Quick analysis completed!")
        return "default"
    
    def _generate_quick_summary(self, data, top_offer):
        """Generate concise executive summary."""
        comparison_results = data["comparison_results"]
        ranked_offers = comparison_results.get("ranked_offers", [])
        
        if not top_offer:
            return "No offers available for comparison."
        
        # Calculate score stats directly from ranked_offers
        scores = [offer.get("total_score", 0) for offer in ranked_offers if offer.get("total_score") is not None]
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        avg_score = sum(scores) / len(scores) if scores else 0
        
        summary = f"""
TOP RECOMMENDATION: {top_offer.get('company', 'N/A')} - {top_offer.get('position', 'N/A')}
Overall Score: {top_offer.get('total_score', 0):.1f}/100

COMPARISON SUMMARY:
{comparison_results.get('comparison_summary', 'Analysis completed')}

KEY INSIGHTS:
• Total offers analyzed: {len(data['offers'])}
• Score range: {min_score:.1f} - {max_score:.1f}
• Average score: {avg_score:.1f}

NEXT STEPS:
1. Review AI analysis above
2. Consider decision framework
3. Run full analysis for detailed insights
"""
        return summary.strip()


# ============================================================================
# QUICK ANALYSIS NODES - Streamlined workflow for fast results
# ============================================================================

class QuickFinancialAnalysisNode(BatchNode):
    """
    Quick Financial Analysis - Combines Tax Calculation and COL Analysis.
    Processes all offers in one pass for faster results.
    """
    
    def prep(self, shared):
        """Extract offers and user base location."""
        offers = shared.get("offers", [])
        user_base_location = shared.get("user_preferences", {}).get("base_location", "San Francisco, CA")
        
        items = []
        for offer in offers:
            items.append({
                "offer": offer,
                "base_location": user_base_location
            })
        return items
    
    def exec(self, item):
        """Calculate tax, net pay, COL, and net savings for a single offer."""
        offer = item["offer"]
        base_location = item["base_location"]
        
        # Determine tax location (handle Remote)
        tax_location = offer["location"]
        if "remote" in tax_location.lower():
            tax_location = base_location
        
        # Calculate net pay (tax calculation)
        net_pay_analysis = calculate_net_pay(
            offer["total_compensation"],
            tax_location
        )
        
        # Calculate COL and expenses
        expense_analysis = estimate_annual_expenses(offer["location"])
        annual_expenses = expense_analysis["estimated_annual_expenses"]
        
        # Calculate net savings
        net_pay = net_pay_analysis["estimated_net_pay"]
        net_savings = net_pay - annual_expenses
        
        return {
            "offer_id": offer["id"],
            "net_pay_analysis": net_pay_analysis,
            "expense_analysis": expense_analysis,
            "net_savings": net_savings
        }
    
    def post(self, shared, prep_res, exec_res_list):
        """Update offers with financial analysis."""
        results_lookup = {r["offer_id"]: r for r in exec_res_list}
        
        for offer in shared["offers"]:
            if offer["id"] in results_lookup:
                res = results_lookup[offer["id"]]
                offer["net_pay_analysis"] = res["net_pay_analysis"]
                offer["estimated_net_pay"] = res["net_pay_analysis"]["estimated_net_pay"]
                offer["expense_analysis"] = res["expense_analysis"]
                offer["estimated_annual_expenses"] = res["expense_analysis"]["estimated_annual_expenses"]
                offer["net_savings"] = res["net_savings"]
                offer["estimated_tax"] = res["net_pay_analysis"]["estimated_tax_amount"]
        
        print(f"Quick financial analysis completed for {len(exec_res_list)} offers")
        return "default"


class QuickMarketAnalysisNode(AsyncParallelBatchNode):
    """
    Quick Market Analysis - Uses cached company data and quick market lookups.
    Skips deep web research for faster results.
    """
    
    async def prep_async(self, shared):
        """Extract offer data for quick market analysis."""
        offers = shared.get("offers", [])
        market_items = []
        
        for offer in offers:
            market_items.append({
                "offer_id": offer["id"],
                "company": offer["company"],
                "position": offer["position"],
                "level": offer.get("level"),
                "location": offer["location"],
                "base_salary": offer["base_salary"],
                "total_compensation": offer["total_compensation"],
                "equity": offer.get("equity", 0),
                "bonus": offer.get("bonus", 0),
                "years_experience": offer.get("years_experience", 5)
            })
        
        return market_items
    
    async def exec_async(self, market_item):
        """Quick market analysis using cached data and fast lookups."""
        start_time = time.time()
        timestamp = datetime.fromtimestamp(start_time).strftime("%H:%M:%S.%f")[:-3]
        print(f"\n[DEBUG] QuickMarketAnalysis for {market_item['company']} started at {timestamp}")
        
        # Use cached company data (fast, no API calls)
        company_db_data = get_company_data(market_item["company"])
        
        # Infer experience level from position/years (no LLM call)
        from utils.market_data import infer_experience_level
        experience_level = infer_experience_level(
            market_item["position"],
            market_item["years_experience"]
        )
        
        # Quick market percentile calculations (synchronous, no API)
        from utils.market_data import calculate_market_percentile, get_market_salary_range
        
        # Run percentile calculations in parallel using asyncio
        base_percentile_task = asyncio.to_thread(
            calculate_market_percentile,
            market_item["base_salary"],
            market_item["position"],
            market_item["location"],
            experience_level=experience_level
        )
        total_percentile_task = asyncio.to_thread(
            calculate_market_percentile,
            market_item["total_compensation"],
            market_item["position"],
            market_item["location"],
            experience_level=experience_level
        )
        market_range_task = asyncio.to_thread(
            get_market_salary_range,
            market_item["position"],
            market_item["location"],
            experience_level=experience_level
        )
        
        base_percentile, total_percentile, market_range = await asyncio.gather(
            base_percentile_task,
            total_percentile_task,
            market_range_task
        )
        
        # Create quick compensation insights from market data
        compensation_insights = {
            "market_range": market_range["adjusted_range"],
            "base_percentile": base_percentile["market_percentile"],
            "total_percentile": total_percentile["market_percentile"],
            "competitiveness": base_percentile.get("competitiveness", "Average")
        }
        
        end_time = time.time()
        duration = end_time - start_time
        end_timestamp = datetime.fromtimestamp(end_time).strftime("%H:%M:%S.%f")[:-3]
        print(f"[DEBUG] QuickMarketAnalysis for {market_item['company']} completed at {end_timestamp}, duration: {duration:.2f}s")
        
        return {
            "offer_id": market_item["offer_id"],
            "company_db_data": company_db_data or {},
            "compensation_insights": compensation_insights,
            "market_insights": compensation_insights,
            "base_percentile": base_percentile,
            "market_analysis": base_percentile,
            "total_percentile": total_percentile,
            "total_comp_analysis": total_percentile,
            "experience_level": experience_level
        }
    
    async def post_async(self, shared, prep_res, exec_res_list):
        """Add quick market analysis data to offers."""
        market_lookup = {r.get("offer_id"): r for r in exec_res_list if isinstance(r, dict)}
        
        for offer in shared["offers"]:
            if offer["id"] in market_lookup:
                market_data = market_lookup[offer["id"]]
                # Add company data
                if market_data.get("company_db_data"):
                    offer["company_db_data"] = market_data["company_db_data"]
                    # Extract metrics for compatibility
                    culture_metrics = market_data["company_db_data"].get("culture_metrics", {})
                    if culture_metrics:
                        wlb_score = culture_metrics.get("work_life_balance", 7.0)
                        growth_score = culture_metrics.get("career_growth", 7.5)
                        offer["wlb_score"] = wlb_score
                        offer["growth_score"] = growth_score
                        
                        # Use centralized grade mapping
                        offer["wlb_grade"] = map_score_to_grade(wlb_score)
                        offer["growth_grade"] = map_score_to_grade(growth_score)
                        
                        offer["benefits_grade"] = "A" if market_data["company_db_data"].get("glassdoor_rating", 0) >= 4.0 else "B"
                
                # Add market data
                offer["market_analysis"] = market_data["base_percentile"]
                offer["total_comp_analysis"] = market_data["total_percentile"]
                offer["compensation_insights"] = market_data["compensation_insights"]
                # Direct access fields for UI
                offer["market_percentile"] = market_data["total_percentile"].get("market_percentile", 50)
                offer["market_median"] = market_data["total_percentile"].get("market_range", {}).get("median", 0)
        
        print(f"Quick market analysis completed for {len(exec_res_list)} offers")
        return "default"


class QuickAIAnalysisNode(AsyncNode):
    """
    Quick AI Analysis - Combines scoring and AI recommendations in single comprehensive LLM call.
    Uses structured output for efficiency.
    """
    
    async def prep_async(self, shared):
        """Prepare all offer data for quick AI analysis."""
        offers = shared.get("offers", [])
        user_preferences = shared.get("user_preferences", {})
        
        # Calculate weights for scoring
        weights = customize_weights(user_preferences)
        
        return {
            "offers": offers,
            "user_preferences": user_preferences,
            "scoring_weights": weights
        }
    
    async def exec_async(self, prep_data):
        """Generate comprehensive analysis with single LLM call."""
        start_time = time.time()
        timestamp = datetime.fromtimestamp(start_time).strftime("%H:%M:%S.%f")[:-3]
        print(f"\n[DEBUG] QuickAIAnalysis started at {timestamp}")
        print("Generating quick AI-powered analysis and recommendations...")
        
        offers = prep_data["offers"]
        user_preferences = prep_data["user_preferences"]
        weights = prep_data["scoring_weights"]
        
        # CRITICAL: Always calculate scores first using existing scoring logic
        # This ensures comparison_results has proper structure with scores
        for offer in offers:
            if not offer.get("score_data"):
                score_data = calculate_offer_score(offer, user_preferences, weights)
                offer["score_data"] = score_data
        
        # Generate proper comparison_results with scores using compare_offers
        comparison_results = compare_offers(offers, user_preferences, weights)
        
        # Build comprehensive prompt with all offer data
        prompt = self._build_quick_analysis_prompt(offers, user_preferences, weights)
        
        # Single structured LLM call for AI insights (not for scores - scores are already calculated)
        try:
            structured_response = await call_llm_structured_async(
                prompt=prompt,
                response_format={"type": "json_object"},
                temperature=0.3,
                system_prompt="You are an expert career advisor. Provide comprehensive job offer analysis with rankings and recommendations in JSON format.",
                provider=None
            )
            
            # Parse JSON response
            if isinstance(structured_response, str):
                analysis_data = json.loads(structured_response)
            else:
                analysis_data = structured_response
            
            # Extract new Net Value Analysis structure from LLM response
            net_value_analysis = analysis_data.get("net_value_analysis", {})
            lifestyle_comparison = analysis_data.get("lifestyle_comparison", {})
            summary_table = analysis_data.get("summary_table", {})
            verdict = analysis_data.get("verdict", {})
            reality_checks = analysis_data.get("reality_checks", {})
            # Extract structured negotiation options (preferred) or fallback to simple list
            negotiation_options = analysis_data.get("negotiation_options", [])
            negotiation_opportunities = analysis_data.get("negotiation_opportunities", [])
            # If we have structured options, use them; otherwise convert simple list to structured format
            if not negotiation_options and negotiation_opportunities:
                negotiation_options = [
                    {
                        "id": f"option_{i+1}",
                        "title": opp.split("·")[0].strip() if "·" in opp else opp,
                        "description": opp,
                        "difficulty": "worth_asking",
                        "difficulty_label": "Worth asking",
                        "expected_value_impact": 0,
                        "script": f"Based on the analysis, {opp}"
                    }
                    for i, opp in enumerate(negotiation_opportunities) if isinstance(opp, str)
                ]
            comparison_summary = analysis_data.get("comparison_summary", comparison_results.get("comparison_summary", "Quick analysis completed."))
            
            # Extract per-offer recommendations from LLM (for Smart Analysis Dashboard)
            offer_recommendations = []
            llm_ranked_offers = analysis_data.get("ranked_offers", [])
            
            for offer in offers:
                offer_id = offer["id"]
                # Find recommendation for this offer from LLM response
                recommendation = None
                for ranked in llm_ranked_offers:
                    if ranked.get("offer_id") == offer_id or ranked.get("company") == offer.get("company"):
                        recommendation = ranked.get("recommendation", {})
                        break
                
                if not recommendation:
                    # Fallback: create basic recommendation based on actual score
                    score_data = offer.get("score_data", {})
                    total_score = score_data.get("total_score", 70)
                    recommendation = {
                        "verdict": {
                            "badge": "Analysis Complete",
                            "color": "blue",
                            "one_line_summary": f"Score: {total_score:.1f}/100"
                        },
                        "scores": {
                            "compensation": min(10, total_score / 10),
                            "work_life_balance": min(10, (offer.get("wlb_score", 7) or 7)),
                            "growth_potential": min(10, (offer.get("growth_score", 7) or 7)),
                            "job_stability": 7.0,
                            "culture_fit": 7.0
                        },
                        "key_insights": {
                            "pros": ["Competitive compensation", "Good growth potential"],
                            "cons": ["Review full analysis for details"]
                        }
                    }
                
                offer_recommendations.append({
                    "offer_id": offer_id,
                    "recommendation": recommendation
                })
            
            end_time = time.time()
            duration = end_time - start_time
            end_timestamp = datetime.fromtimestamp(end_time).strftime("%H:%M:%S.%f")[:-3]
            print(f"[DEBUG] QuickAIAnalysis completed at {end_timestamp}, duration: {duration:.2f}s")
            
            return {
                "net_value_analysis": net_value_analysis,
                "lifestyle_comparison": lifestyle_comparison,
                "summary_table": summary_table,
                "verdict": verdict,
                "negotiation_options": negotiation_options,
                "negotiation_opportunities": negotiation_opportunities,  # Keep for backward compatibility
                "reality_checks": reality_checks,
                "comparison_summary": comparison_summary,
                "offer_recommendations": offer_recommendations,
                "comparison_results": comparison_results  # Use properly scored comparison_results
            }
            
        except Exception as e:
            error_str = str(e)
            print(f"[WARNING] Quick AI Analysis LLM call failed: {error_str[:100]}...")
            print("[INFO] Generating fallback Net Value Analysis from calculated data")
            
            # Generate structured fallback using calculated data
            net_value_offers = []
            winner_id = None
            winner_discretionary = -float('inf')
            
            for offer in offers:
                net_pay = offer.get('estimated_net_pay', 0)
                annual_expenses = offer.get('estimated_annual_expenses', 0)
                gross_total = offer.get('total_compensation', 0)
                estimated_tax = gross_total - net_pay
                discretionary_income = net_pay - annual_expenses
                
                net_value_offers.append({
                    "offer_id": offer["id"],
                    "company": offer.get("company", "Unknown"),
                    "gross_total": gross_total,
                    "estimated_tax": estimated_tax,
                    "estimated_tax_amount": estimated_tax,  # Add explicit amount field
                    "net_annual": net_pay,
                    "annual_col": annual_expenses,
                    "discretionary_income": discretionary_income,
                    "discretionary_income_delta": 0  # Will calculate below
                })
                
                if discretionary_income > winner_discretionary:
                    winner_discretionary = discretionary_income
                    winner_id = offer["id"]
            
            # Calculate deltas
            if len(net_value_offers) > 1:
                max_discretionary = max(o["discretionary_income"] for o in net_value_offers)
                for offer_data in net_value_offers:
                    offer_data["discretionary_income_delta"] = offer_data["discretionary_income"] - max_discretionary
            
            # Build summary table
            table_headers = ["Metric"] + [o.get("company", "Unknown") for o in offers]
            table_rows = []
            if len(offers) >= 2:
                table_rows.append(["Gross Total (Inc. Equity)"] + [f"${o.get('total_compensation', 0):,}" for o in offers])
                table_rows.append(["Estimated Tax Amount"] + [f"${net_value_offers[i].get('estimated_tax', 0):,}" for i in range(len(offers))])
                table_rows.append(["Net Take-Home"] + [f"${o.get('estimated_net_pay', 0):,}" for o in offers])
                table_rows.append(["Annual CoL"] + [f"${o.get('estimated_annual_expenses', 0):,}" for o in offers])
                table_rows.append(["Final Discretionary Income"] + [f"${o.get('discretionary_income', 0):,}" for o in net_value_offers])
            
            # Create basic verdict
            winner_offer = next((o for o in offers if o["id"] == winner_id), offers[0] if offers else None)
            verdict_reasoning = [
                f"{winner_offer.get('company', 'Unknown')} offers ${winner_discretionary:,.0f} in discretionary income",
                "Based on calculated net pay and cost of living analysis",
                "Consider work-life balance and career growth opportunities",
                "Review full analysis for detailed insights"
            ]
            
            # Generate structured negotiation options for all companies
            negotiation_options = []
            for offer in offers:
                company_name = offer.get("company", "Unknown")
                max_total = max(o.get('total_compensation', 0) for o in offers)
                curr_total = offer.get('total_compensation', 0)
                gap = max_total - curr_total if max_total > curr_total else 5000 # Default gap if winner
                
                # Add 3 universal options per company
                negotiation_options.append({
                    "id": f"opt_{offer['id']}_a",
                    "company": company_name,
                    "title": "Sign-on bonus",
                    "description": f"Targeting ${int(gap):,.0f} one-time sign-on bonus.",
                    "financial_impact": f"+${int(gap/1000)}k",
                    "difficulty": "worth_asking",
                    "difficulty_label": "Worth asking",
                    "expected_value_impact": int(gap),
                    "script": f"I'm genuinely excited about joining {company_name}. To help bridge the gap with my other current opportunities, I'd appreciate consideration for a sign-on bonus. This would help demonstrate the company's commitment to my transition."
                })
                
                negotiation_options.append({
                    "id": f"opt_{offer['id']}_b",
                    "company": company_name,
                    "title": "Base salary increase",
                    "description": f"Targeting +5-10% increase in base salary.",
                    "financial_impact": "+$15k",
                    "difficulty": "likely_achievable",
                    "difficulty_label": "Likely achievable",
                    "expected_value_impact": 15000,
                    "script": f"Thank you for the offer at {company_name}. Given my specific expertise and the market data I've reviewed for similar roles, I'd like to discuss if there's flexibility to increase the base salary to better align with the value I'll be bringing to the team."
                })
                
                negotiation_options.append({
                    "id": f"opt_{offer['id']}_c",
                    "company": company_name,
                    "title": "Equity refresher eligibility",
                    "description": "Confirm timeline for subsequent grants.",
                    "financial_impact": "Variable",
                    "difficulty": "worth_asking",
                    "difficulty_label": "Worth asking",
                    "expected_value_impact": 0,
                    "script": f"I'm very interested in the equity component of the {company_name} package. Could you clarify the policy on annual equity refreshers and how those grants are Typically structured for this level? Understanding the long-term growth potential is key for me."
                })
            
            # Keep simple list for backward compatibility
            negotiation_opportunities = [opt["title"] + " · " + opt["description"] for opt in negotiation_options]
            
            # Create basic recommendations
            offer_recommendations = []
            for offer in offers:
                score_data = offer.get("score_data", {})
                total_score = score_data.get("total_score", 70)
                offer_recommendations.append({
                    "offer_id": offer["id"],
                    "recommendation": {
                        "verdict": {
                            "badge": "Analysis Complete",
                            "color": "blue",
                            "one_line_summary": f"Score: {total_score:.1f}/100"
                        },
                        "scores": {
                            "compensation": min(10, total_score / 10),
                            "work_life_balance": min(10, (offer.get("wlb_score", 7) or 7)),
                            "growth_potential": min(10, (offer.get("growth_score", 7) or 7)),
                            "job_stability": 7.0,
                            "culture_fit": 7.0
                        },
                        "key_insights": {
                            "pros": ["Analysis completed"],
                            "cons": ["Full analysis recommended for detailed insights"]
                        }
                    }
                })
            
            return {
                "net_value_analysis": {
                    "offers": net_value_offers,
                    "winner": winner_id,
                    "winner_discretionary_income": winner_discretionary
                },
                "lifestyle_comparison": {
                    "location_tradeoffs": f"- Compare locations: {', '.join([o.get('location', 'Unknown') for o in offers])}\n- Consider tax implications and local state income tax brackets\n- Analyze cost of living deltas for housing and utilities\n- Evaluate quality of life and proximity to networking hubs",
                    "hidden_costs": "- Transportation and commute expenses\n- Local and city-level taxes or surcharges\n- Differential in utility and grocery costs"
                },
                "summary_table": {
                    "headers": table_headers,
                    "rows": table_rows
                },
                "verdict": {
                    "recommended_offer_id": winner_id,
                    "recommended_company": winner_offer.get("company", "Unknown") if winner_offer else "Unknown",
                    "is_tie": False,
                    "summary_reasoning": f"{winner_offer.get('company', 'Unknown')} provided the best overall financial value with ${winner_discretionary:,.0f} in discretionary income.",
                    "financial_superiority": winner_offer.get("company", "Unknown") if winner_offer else "Unknown",
                    "reasoning": verdict_reasoning,
                    "career_growth_considerations": "Evaluate career growth opportunities, company culture, and long-term trajectory at each organization."
                },
                "negotiation_options": negotiation_options,
                "negotiation_opportunities": negotiation_opportunities,  # Keep for backward compatibility
                "reality_checks": {
                    "red_flags": [
                        "Equity may be diluted in future funding rounds",
                        "High cost of living area may reduce purchasing power"
                    ],
                    "considerations": [
                        "Consider vesting schedule and cliff period",
                        "Evaluate company growth trajectory"
                    ]
                },
                "comparison_summary": comparison_results.get("comparison_summary", "Quick analysis completed."),
                "offer_recommendations": offer_recommendations,
                "comparison_results": comparison_results
            }
    
    async def post_async(self, shared, prep_res, exec_res):
        """Store quick AI analysis results."""
        # Add recommendations to individual offers
        rec_lookup = {r["offer_id"]: r["recommendation"] for r in exec_res["offer_recommendations"]}
        
        # Create offer lookup for easy access
        offer_lookup = {offer["id"]: offer for offer in shared["offers"]}
        
        for offer in shared["offers"]:
            if offer["id"] in rec_lookup:
                offer["ai_recommendation"] = rec_lookup[offer["id"]]
        
        # Update ranked_offers with recommendations and ensure offer_data is populated
        comparison_results = exec_res["comparison_results"]
        if "ranked_offers" in comparison_results:
            for ranked_offer in comparison_results["ranked_offers"]:
                offer_id = ranked_offer.get("offer_id") or ranked_offer.get("id")
                
                # Ensure offer_data is populated with full offer details
                if "offer_data" not in ranked_offer or not ranked_offer["offer_data"]:
                    if offer_id in offer_lookup:
                        ranked_offer["offer_data"] = offer_lookup[offer_id]
                
                # Add AI recommendation and market data
                if offer_id in rec_lookup:
                    ranked_offer["ai_recommendation"] = rec_lookup[offer_id]
                
                # Add market insights for benchmarking UI
                if offer_id in offer_lookup:
                    offer_obj = offer_lookup[offer_id]
                    ranked_offer["market_percentile"] = offer_obj.get("market_percentile", 50)
                    ranked_offer["market_median"] = offer_obj.get("market_median", 0)
        
        # Store new Net Value Analysis fields directly in shared state
        shared["net_value_analysis"] = exec_res.get("net_value_analysis", {})
        shared["lifestyle_comparison"] = exec_res.get("lifestyle_comparison", {})
        shared["summary_table"] = exec_res.get("summary_table", {})
        shared["negotiation_options"] = exec_res.get("negotiation_options", [])
        shared["negotiation_opportunities"] = exec_res.get("negotiation_opportunities", [])  # Keep for backward compatibility
        shared["reality_checks"] = exec_res.get("reality_checks", {})
        shared["verdict"] = exec_res.get("verdict", {})
        shared["comparison_summary"] = exec_res.get("comparison_summary", comparison_results.get("comparison_summary", ""))
        shared["comparison_results"] = comparison_results
        shared["scoring_weights"] = prep_res["scoring_weights"]
        
        print("Quick AI analysis completed")
        return "default"
    
    def _build_quick_analysis_prompt(self, offers, user_preferences, weights):
        """Build Net Value Analysis prompt for quick analysis."""
        prompt = f"""
Act as a senior financial advisor and career coach. Conduct a "Net Value Analysis" comparing {len(offers)} job offers to determine which provides better quality of life and financial outlook.

USER PRIORITIES: {user_preferences}

OFFERS DATA:
"""
        for i, offer in enumerate(offers, 1):
            net_pay = offer.get('estimated_net_pay', 0)
            annual_expenses = offer.get('estimated_annual_expenses', 0)
            net_savings = offer.get('net_savings', 0)
            tax_rate = offer.get('net_pay_analysis', {}).get('effective_tax_rate', 0)
            tax_rate_pct = f"{tax_rate * 100:.1f}%" if tax_rate > 0 else "N/A"
            
            prompt += f"""
Offer {i}:
- Company: {offer.get('company', 'Unknown')}
- Position: {offer.get('position', 'Unknown')}
- Location: {offer.get('location', 'Unknown')}
- Base Salary: ${offer.get('base_salary', 0):,}
- Equity/Year: ${offer.get('equity', 0):,}
- Bonus: ${offer.get('bonus', 0):,}
- Gross Total (Salary + Equity + Bonus): ${offer.get('total_compensation', 0):,}
- Estimated Tax Rate: {tax_rate_pct}
- Estimated Tax Amount: ${offer.get('net_pay_analysis', {}).get('estimated_tax_amount', 0):,}
- Estimated Net Pay (After Tax): ${net_pay:,}
- Monthly Cost of Living: ${annual_expenses / 12:,.0f} (Annual: ${annual_expenses:,})
- Net Savings (Discretionary Income): ${net_savings:,}
- Market Percentile: {offer.get('market_analysis', {}).get('market_percentile', 'N/A')}
- WLB Score: {offer.get('wlb_score', 'N/A')}
- Growth Score: {offer.get('growth_score', 'N/A')}
- Benefits Grade: {offer.get('benefits_grade', 'N/A')}
"""
        
        prompt += """

YOUR TASKS - Provide a comprehensive JSON response:

1. Net Value Analysis: Calculate and compare discretionary income (Net Pay - Annual CoL) for each offer. Identify the financial winner.

2. Lifestyle Comparison: Analyze location trade-offs, hidden costs, and quality of life factors for each location. Use short, punchy bullet points (max 5 per section) instead of paragraphs.

3. Summary Table: Create a side-by-side comparison table with key financial metrics.

4. Verdict: Provide a clear recommendation with 4-5 bullet points of reasoning, considering both financial superiority and career growth.

5. Negotiation Strategy: Provide 3-5 structured negotiation options for EACH company being compared. Ensure these are tailored to the specific offer terms and location. Each option should include:
   - A clear title (e.g., "Higher salary", "Signing bonus", "Accelerated vesting")
   - Description with expected value impact (e.g., "+$48K/year · Adds ~$133K over 4 years")
   - difficulty: "likely_achievable", "worth_asking", or "ambitious_ask"
   - Expected value impact in dollars
   - A personalized negotiation script (2-3 paragraphs) that the user can copy and use
   - MANDATORY: Include the "company" name in each negotiation option.

6. Reality Checks: Identify potential red flags and important considerations for each offer. Include:
   - Red flags: Critical warnings or concerns (e.g., "Equity may be diluted in future funding rounds", "High cost of living may reduce purchasing power")
   - Considerations: Important factors to keep in mind (e.g., "Consider vesting schedule and cliff period", "Evaluate company growth trajectory")

Provide a JSON response with this EXACT structure:
{
    "net_value_analysis": {
        "offers": [
            {
                "offer_id": "offer_1",
                "company": "Company Name",
                "gross_total": 275000,
                "estimated_tax": 71500,
                "net_annual": 203500,
                "annual_col": 54000,
                "discretionary_income": 149500,
                "discretionary_income_delta": 14650
            }
        ],
        "winner": "offer_1",
        "winner_discretionary_income": 149500
    },
    "lifestyle_comparison": {
        "location_tradeoffs": "- Point 1: Benefits\n- Point 2: Drawbacks\n- Point 3: Networking",
        "hidden_costs": "- Cost 1: Local taxes\n- Cost 2: Commute costs"
    },
    "summary_table": {
        "headers": ["Metric", "Company 1 (Location)", "Company 2 (Location)"],
        "rows": [
            ["Gross Total (Inc. Equity)", "$275,000", "$309,000"],
            ["Estimated Tax Amount", "$71,500", "$108,150"],
            ["Net Take-Home", "$203,500", "$200,850"],
            ["Annual CoL", "$54,000", "$66,000"],
            ["Final Discretionary Income", "$149,500", "$134,850"]
        ]
    },
    "verdict": {
        "recommended_offer_id": "offer_1",
        "recommended_company": "Company Name",
        "is_tie": false,
        "summary_reasoning": "Company Name offers the best balance of total compensation and work-life balance for your specific priorities.",
        "financial_superiority": "Company Name",
        "reasoning": [
            "Tax Efficiency: Explaining why the location is better for taxes",
            "Relocation: Breakdown of relocation benefits",
            "Growth: Long-term career trajectory points"
        ],
        "career_growth_considerations": "Detailed analysis of career growth potential"
    },
    "negotiation_options": [
        {
            "id": "option_a",
            "company": "Company Name",
            "title": "Higher salary",
            "description": "+$48K/year · Adds ~$133K over 4 years",
            "financial_impact": "+$48k",
            "difficulty": "likely_achievable",
            "difficulty_label": "Likely achievable",
            "expected_value_impact": 133000,
            "script": "I'm genuinely excited about this role..."
        }
    ],
    "negotiation_opportunities": ["Legacy field - use negotiation_options instead"],
    "comparison_summary": "Brief 2-3 sentence summary for executive summary",
    "ranked_offers": [
        {
            "offer_id": "offer_1",
            "company": "Company Name",
            "position": "Position",
            "total_score": 85.5,
            "rank": 1
        }
    ]
}

Be objective, highlight hidden costs, and provide actionable insights. Focus on real financial impact and quality of life.
"""
        return prompt