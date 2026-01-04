"""
OfferCompare Pro - Main Flow Implementation
Connects all 8 nodes for comprehensive job offer analysis and comparison
"""

from pocketflow import Flow, AsyncFlow
from nodes import (
    OfferCollectionNode,
    MarketResearchNode,
    TaxCalculationNode,
    COLAnalysisNode,
    MarketBenchmarkingNode,
    PreferenceScoringNode,
    AIAnalysisNode,
    VisualizationPreparationNode,
    ReportGenerationNode
)

def create_offer_comparison_flow():
    """
    Create and return the complete OfferCompare Pro flow using AsyncFlow.
    
    Flow Sequence:
    1. OfferCollection → Collect user offers and preferences (Regular Node)
    2. MarketResearch → AI-powered company intelligence (AsyncBatchNode)
    3. TaxCalculation → Estimated Net Pay (BatchNode)
    4. COLAnalysis → Net Savings Analysis (BatchNode)
    5. MarketBenchmarking → Industry comparison and percentiles (AsyncBatchNode)
    6. PreferenceScoring → Personalized weighted scoring (BatchNode)
    7. AIAnalysis → Comprehensive AI recommendations (AsyncNode)
    8. VisualizationPreparation → Interactive chart data (Regular Node)
    9. ReportGeneration → Final comprehensive report (Regular Node)
    
    Returns:
        AsyncFlow: Complete OfferCompare Pro workflow with async support
    """
    
    print("Initializing OfferCompare Pro AsyncFlow...")
    
    # Create all nodes
    offer_collection = OfferCollectionNode()
    market_research = MarketResearchNode()          # AsyncBatchNode
    tax_calculation = TaxCalculationNode()          # BatchNode
    col_analysis = COLAnalysisNode()                # BatchNode
    market_benchmarking = MarketBenchmarkingNode()  # AsyncBatchNode
    preference_scoring = PreferenceScoringNode()    # BatchNode
    ai_analysis = AIAnalysisNode()                  # AsyncNode
    visualization_prep = VisualizationPreparationNode()  # Regular Node
    report_generation = ReportGenerationNode()     # Regular Node
    
    # Connect nodes in sequence (AsyncFlow supports mixed sync/async nodes)
    offer_collection >> market_research
    market_research >> tax_calculation
    tax_calculation >> col_analysis
    col_analysis >> market_benchmarking
    market_benchmarking >> preference_scoring
    preference_scoring >> ai_analysis
    ai_analysis >> visualization_prep
    visualization_prep >> report_generation
    
    # Create AsyncFlow to handle async nodes
    flow = AsyncFlow(start=offer_collection)
    
    print("OfferCompare Pro AsyncFlow initialized successfully!")
    return flow

def create_demo_flow():
    """
    Create a simplified demo flow for testing with sample data.
    
    Returns:
        Flow: Demo workflow with minimal user input
    """
    
    # For demo purposes, we'll use the same flow but with sample data
    return create_offer_comparison_flow()

def get_sample_offers():
    """
    Generate sample offers for testing and demonstration.
    
    Returns:
        dict: Sample shared store data with offers
    """
    
    sample_data = {
        "offers": [
            {
                "id": "offer_1",
                "company": "Google",
                "position": "Senior Software Engineer",
                "location": "Seattle, WA",
                "base_salary": 180000,
                "equity": 50000,
                "bonus": 20000,
                "total_compensation": 250000,
                "years_experience": 6,
                "vesting_years": 4
            },
            {
                "id": "offer_2",
                "company": "Microsoft",
                "position": "Senior Software Engineer",
                "location": "Seattle, WA",
                "base_salary": 175000,
                "equity": 40000,
                "bonus": 25000,
                "total_compensation": 240000,
                "years_experience": 6,
                "vesting_years": 4
            },
            {
                "id": "offer_3",
                "company": "Stripe",
                "position": "Senior Software Engineer",
                "location": "Remote",
                "base_salary": 170000,
                "equity": 60000,
                "bonus": 15000,
                "total_compensation": 245000,
                "years_experience": 6,
                "vesting_years": 4
            }
        ],
        "user_preferences": {
            "growth_focused": True,
            "location_preferences": {
                "Seattle, WA": 85,
                "Remote": 95,
                "San Francisco, CA": 70
            }
        }
    }
    
    return sample_data

# Main flow instance
offer_comparison_flow = create_offer_comparison_flow()