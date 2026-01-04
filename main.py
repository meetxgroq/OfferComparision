"""
OfferCompare Pro - Main Application Entry Point
Intelligent job offer analysis and comparison system
"""

import os
import sys
import argparse
from flow import create_offer_comparison_flow, get_sample_offers
from utils.call_llm import get_provider_info
import json

def main():
    """
    Main function to run OfferCompare Pro analysis.
    
    Provides options for:
    1. Full interactive analysis
    2. Demo with sample data
    3. Help and documentation
    """
    
    # Lightweight CLI flags (non-interactive paths)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--demo", action="store_true", help="Run non-interactive demo with sample data")
    parser.add_argument("--help-cli", action="store_true", help="Show CLI help and exit")
    args, _ = parser.parse_known_args()

    if args.help_cli:
        print("Usage: python main.py [--demo]")
        print("  --demo      Run non-interactive demo using sample data")
        sys.exit(0)

    # Non-interactive demo path
    if args.demo:
        return run_demo_analysis(ask_confirm=False)

    print("\n" + "="*80)
    print("WELCOME TO OFFERCOMPARE PRO")
    print("   Intelligent Job Offer Analysis & Decision Support")
    print("="*80)
    
    # Check AI provider availability
    provider_info = get_provider_info()
    available_providers = provider_info.get("available_providers", [])
    default_provider = provider_info.get("default_provider")
    
    if not available_providers:
        print("\nWARNING: No AI providers configured!")
        print("Please set up your API keys in the .env file:")
        print("• Google Gemini: https://aistudio.google.com/app/apikey")
        print("• OpenAI: https://platform.openai.com/api-keys")
        print("• Anthropic Claude: https://console.anthropic.com/")
        print("\nRun 'python setup_local.py' for guided setup.")
        print("\nYou can still explore the system features, but AI analysis will be limited.")
    else:
        print(f"\nAI Providers Available: {', '.join(available_providers)}")
        if default_provider:
            provider_name = provider_info["provider_details"][default_provider]["name"]
            print(f"Using: {provider_name}")
    
    # Display options
    print("\nSelect an option:")
    print("1. Full Interactive Analysis (Recommended)")
    print("2. Quick Demo with Sample Data")
    print("3. Help & Documentation")
    print("4. Test Utilities")
    print("5. Configuration & Setup")
    print("6. Exit")
    print("\n(Or run 'python main.py --demo' for a non-interactive demo)")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        run_full_analysis()
    elif choice == "2":
        run_demo_analysis()
    elif choice == "3":
        show_help()
    elif choice == "4":
        test_utilities()
    elif choice == "5":
        show_configuration()
    elif choice == "6":
        print("👋 Thanks for using OfferCompare Pro!")
        sys.exit(0)
    else:
        print("Invalid choice. Please try again.")
        main()

def run_full_analysis():
    """Run the complete interactive offer comparison analysis."""
    
    print("\nStarting Full Interactive Analysis...")
    print("This will guide you through collecting offer details and preferences.")
    
    # Check AI availability
    provider_info = get_provider_info()
    if not provider_info.get("available_providers"):
        print("\nWarning: No AI providers available for analysis.")
        proceed = input("Continue with limited functionality? (y/n): ").lower()
        if proceed != 'y':
            return main()
    
    # Initialize shared store
    shared = {}
    
    # Create and run the flow
    flow = create_offer_comparison_flow()
    
    try:
        print("\n" + "="*60)
        print("🔄 STARTING OFFERCOMPARE PRO ANALYSIS")
        print("="*60)
        
        # Run the complete flow
        flow.run(shared)
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE!")
        print("="*60)
        
        # Optionally save results
        save_results(shared)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Analysis interrupted by user.")
        print("Your progress has been saved where possible.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your inputs and try again.")
        if "API" in str(e):
            print("Tip: Make sure your API keys are properly configured in .env file")

def run_demo_analysis(ask_confirm: bool = True):
    """Run demo analysis with sample data. If ask_confirm is False, runs non-interactively."""
    
    print("\n📊 Running Demo Analysis with Sample Data...")
    print("This showcases the full capabilities with pre-loaded offers.")
    
    # Use sample data
    shared = get_sample_offers()
    
    print(f"\nDemo includes {len(shared['offers'])} sample offers:")
    for offer in shared['offers']:
        print(f"  • {offer['company']} - {offer['position']} (${offer['base_salary']:,})")
    
    if ask_confirm:
        proceed = input("\nProceed with demo analysis? (y/n): ").lower()
        if proceed != 'y':
            return main()
    
    # Create flow (skip offer collection for demo)
    from nodes import (
        MarketResearchNode, COLAdjustmentNode, MarketBenchmarkingNode,
        PreferenceScoringNode, AIAnalysisNode, VisualizationPreparationNode,
        ReportGenerationNode
    )
    from pocketflow import AsyncFlow
    import asyncio
    
    # Create demo flow (starting from market research)
    market_research = MarketResearchNode()
    col_adjustment = COLAdjustmentNode()
    market_benchmarking = MarketBenchmarkingNode()
    preference_scoring = PreferenceScoringNode()
    ai_analysis = AIAnalysisNode()
    visualization_prep = VisualizationPreparationNode()
    report_generation = ReportGenerationNode()
    
    # Connect nodes
    market_research >> col_adjustment
    col_adjustment >> market_benchmarking
    market_benchmarking >> preference_scoring
    preference_scoring >> ai_analysis
    ai_analysis >> visualization_prep
    visualization_prep >> report_generation
    
    demo_flow = AsyncFlow(start=market_research)
    
    try:
        print("\n" + "="*60)
        print("🔄 RUNNING DEMO ANALYSIS (ASYNC)")
        print("="*60)
        
        # Run async flow
        asyncio.run(demo_flow.run_async(shared))
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETE!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        if "API" in str(e):
            print("Tip: Demo requires at least one AI provider configured")

def show_help():
    """Display help and documentation."""
    
    print("\n" + "="*60)
    print("❓ OFFERCOMPARE PRO - HELP & DOCUMENTATION")
    print("="*60)
    
    help_text = """
🎯 WHAT IS OFFERCOMPARE PRO?
OfferCompare Pro is an intelligent job offer analysis platform that helps you make 
data-driven career decisions by comparing compensation packages, work-life balance 
metrics, and growth opportunities across multiple offers.

🔧 KEY FEATURES:
• 📊 Comprehensive offer comparison beyond just salary
• 🌍 Real-time cost of living adjustments for fair location comparison  
• 📈 Market benchmarking against industry standards
• 🎯 Personalized scoring based on your priorities
• 🤖 AI-powered recommendations and risk analysis
• 📋 Professional reports with actionable insights

🚀 HOW TO USE:
1. Choose "Full Interactive Analysis" from the main menu
2. Enter your career priorities (salary vs growth vs work-life balance)
3. Input details for 2-10 job offers you want to compare
4. Let the AI analyze market data and company intelligence
5. Review your personalized recommendations and rankings

TIPS FOR BEST RESULTS:
• Have your offer letters ready with compensation details
• Be honest about your priorities and preferences
• Include equity values and vesting schedules when available
• Consider benefits and work-life balance, not just salary

🔑 SETUP REQUIREMENTS:
• Python 3.10+ environment
• At least one AI provider API key:
  - Google Gemini (Recommended): https://aistudio.google.com/app/apikey
  - OpenAI GPT: https://platform.openai.com/api-keys
  - Anthropic Claude: https://console.anthropic.com/
• 5-15 minutes depending on number of offers

📚 DOCUMENTATION:
• README.md - Complete project overview and installation
• docs/design.md - Technical architecture and design patterns
• TODO.md - Development progress and roadmap
• .env.example - Environment configuration template

🛠️ GETTING STARTED:
If you haven't set up your environment yet:
1. Run: python setup_local.py
2. Follow the guided setup process
3. Configure your API keys
4. Return here and start your analysis!

📞 SUPPORT:
• Check the README.md file for detailed documentation
• Review the design.md file for technical architecture
• Run 'Test Utilities' to verify your setup
    """
    
    print(help_text)
    
    input("\nPress Enter to return to main menu...")
    main()

def show_configuration():
    """Show configuration and setup information."""
    
    print("\n" + "="*60)
    print("⚙️ CONFIGURATION & SETUP")
    print("="*60)
    
    # Show AI provider status
    provider_info = get_provider_info()
    print("\n🤖 AI Providers Status:")
    
    if provider_info.get("available_providers"):
        for provider_id, details in provider_info.get("provider_details", {}).items():
            status = "✅ CONFIGURED" + (" (DEFAULT)" if details.get("is_default") else "")
            print(f"  • {details['name']}: {status}")
            print(f"    Models: {', '.join(details['models'][:2])}...")
    else:
        print("  ❌ No AI providers configured")
    
    # Show environment file status
    print(f"\n📄 Environment Configuration:")
    env_exists = os.path.exists(".env")
    print(f"  • .env file: {'✅ EXISTS' if env_exists else '❌ MISSING'}")
    
    if env_exists:
        # Check for API keys
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = {
            "GEMINI_API_KEY": "Google Gemini",
            "OPENAI_API_KEY": "OpenAI",
            "ANTHROPIC_API_KEY": "Anthropic Claude"
        }
        
        for env_key, name in api_keys.items():
            has_key = bool(os.environ.get(env_key))
            print(f"  • {name}: {'✅ SET' if has_key else '❌ NOT SET'}")
    
    # Show setup options
    print(f"\n🔧 Setup Options:")
    print("1. Run guided setup: python setup_local.py")
    print("2. Manual setup: Copy .env.example to .env and edit")
    print("3. Test configuration: Select 'Test Utilities' from main menu")
    
    # Show quick setup for Gemini (easiest)
    print(f"\n⚡ Quick Setup (Recommended - Google Gemini):")
    print("1. Visit: https://aistudio.google.com/app/apikey")
    print("2. Create a free API key")
    print("3. Add to .env file: GEMINI_API_KEY=your_key_here")
    print("4. Set default provider: DEFAULT_AI_PROVIDER=gemini")
    
    input("\nPress Enter to return to main menu...")
    main()

def test_utilities():
    """Test individual utility functions."""
    
    print("\n🧪 Testing Utility Functions...")
    
    test_options = {
        "1": ("AI Provider Configuration", test_ai_providers),
        "2": ("Web Research Agent", test_web_research),
        "3": ("Cost of Living Calculator", test_col_calculator), 
        "4": ("Market Data Fetcher", test_market_data),
        "5": ("Scoring Engine", test_scoring),
        "6": ("Company Database", test_company_db),
        "7": ("Return to Main Menu", lambda: main())
    }
    
    print("\nSelect utility to test:")
    for key, (name, _) in test_options.items():
        print(f"{key}. {name}")
    
    choice = input("\nEnter choice (1-7): ").strip()
    
    if choice in test_options:
        _, test_func = test_options[choice]
        test_func()
    else:
        print("Invalid choice.")
        test_utilities()

def test_ai_providers():
    """Test AI provider configuration and availability."""
    print("\n🤖 Testing AI Provider Configuration...")
    
    try:
        from utils.call_llm import get_provider_info, call_llm
        
        provider_info = get_provider_info()
        available = provider_info.get("available_providers", [])
        default = provider_info.get("default_provider")
        
        print(f"\nProvider Status:")
        print(f"  Available: {available}")
        print(f"  Default: {default}")
        
        if available:
            # Test basic LLM call
            test_prompt = "Say 'Hello from OfferCompare Pro!' in one sentence."
            print(f"\nTesting LLM call with prompt: {test_prompt}")
            
            response = call_llm(test_prompt)
            print(f"✅ Response: {response}")
            
            # Show provider details
            for provider_id, details in provider_info.get("provider_details", {}).items():
                print(f"\n{details['name']}:")
                print(f"  Models: {', '.join(details['models'])}")
                print(f"  Default: {'Yes' if details.get('is_default') else 'No'}")
        else:
            print("\n❌ No providers available. Please configure API keys.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")
    test_utilities()

def test_web_research():
    """Test the web research utility."""
    print("\n🔍 Testing Web Research Agent...")
    
    # Check if AI provider is available
    provider_info = get_provider_info()
    if not provider_info.get("available_providers"):
        print("❌ No AI providers available. Web research requires AI.")
        input("\nPress Enter to continue...")
        test_utilities()
        return
    
    from utils.web_research import research_company
    
    company = input("Enter company name to research: ").strip() or "Google"
    position = input("Enter position title: ").strip() or "Software Engineer"
    
    print(f"\nResearching {company} for {position} role...")
    try:
        result = research_company(company, position)
        print("\n✅ Research completed!")
        print(f"Culture Score: {result['metrics']['culture_score']['score']}/10")
        print(f"WLB Score: {result['metrics']['wlb_score']['score']}/10")
        print(f"Growth Score: {result['metrics']['growth_score']['score']}/10")
        print(f"Key Strengths: {', '.join(result['metrics']['key_strengths'][:2])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")
    test_utilities()

def test_col_calculator():
    """Test the cost of living calculator."""
    from utils.col_calculator import calculate_col_adjustment
    
    print("\n💰 Testing Cost of Living Calculator...")
    
    try:
        salary = float(input("Enter base salary: $").replace("$", "").replace(",", ""))
        from_loc = input("From location (e.g., 'San Francisco, CA'): ").strip()
        to_loc = input("To location (e.g., 'Austin, TX'): ").strip()
        
        result = calculate_col_adjustment(salary, from_loc, to_loc)
        
        print(f"\n✅ Calculation completed!")
        print(f"Original salary: ${result['original_salary']:,}")
        print(f"Adjusted salary: ${result['adjusted_salary']:,}")
        print(f"Cost difference: {result['cost_difference_percent']:+.1f}%")
        print(f"Purchasing power: ${result['effective_value']:,}")
        
    except ValueError:
        print("❌ Invalid salary format")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")
    test_utilities()

def test_market_data():
    """Test the market data fetcher."""
    from utils.market_data import get_market_salary_range, calculate_market_percentile
    
    print("\n📊 Testing Market Data Fetcher...")
    
    position = input("Enter position title: ").strip() or "Senior Software Engineer"
    location = input("Enter location: ").strip() or "Seattle, WA"
    
    try:
        # Get market range
        market_range = get_market_salary_range(position, location)
        print(f"\n✅ Market data retrieved!")
        print(f"Market range: ${market_range['adjusted_range']['min']:,} - ${market_range['adjusted_range']['max']:,}")
        print(f"Median: ${market_range['adjusted_range']['median']:,}")
        
        # Test percentile calculation
        salary = float(input(f"\nEnter a salary to check percentile: $").replace("$", "").replace(",", ""))
        percentile = calculate_market_percentile(salary, position, location)
        print(f"Your salary percentile: {percentile['market_percentile']:.1f} ({percentile['competitiveness']})")
        
    except ValueError:
        print("❌ Invalid salary format")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")
    test_utilities()

def test_scoring():
    """Test the scoring engine."""
    from utils.scoring import calculate_offer_score
    
    print("\n🎯 Testing Scoring Engine...")
    
    # Create sample offer
    sample_offer = {
        "id": "test_offer",
        "company": "Test Company",
        "position": "Software Engineer",
        "location": "Seattle, WA",
        "base_salary": 150000,
        "equity": 30000,
        "market_analysis": {"market_percentile": 70},
        "total_comp_analysis": {"market_percentile": 75},
        "company_research": {
            "stage": "growth",
            "metrics": {
                "wlb_score": {"score": 8},
                "growth_score": {"score": 9},
                "culture_score": {"score": 7},
                "benefits_score": {"score": 8},
                "stability_score": {"score": 8}
            }
        }
    }
    
    try:
        result = calculate_offer_score(sample_offer)
        print(f"\n✅ Scoring completed!")
        print(f"Total Score: {result['total_score']:.1f}/100 ({result['rating']})")
        print(f"Top strengths: {[f['factor'] for f in result['top_strengths']]}")
        print(f"Improvement areas: {[f['factor'] for f in result['improvement_areas']]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")
    test_utilities()

def test_company_db():
    """Test the company database."""
    from utils.company_db import get_company_data, search_companies
    
    print("\n🏢 Testing Company Database...")
    
    company = input("Enter company name to lookup: ").strip() or "Google"
    
    try:
        data = get_company_data(company)
        if data:
            print(f"\n✅ Company data found!")
            print(f"Industry: {data['industry']}")
            print(f"Size: {data['size']}")
            print(f"Glassdoor Rating: {data['glassdoor_rating']}")
            print(f"Work-Life Balance: {data['culture_metrics']['work_life_balance']}/10")
            print(f"Benefits: {list(data['benefits'].keys())[:3]}...")
        else:
            print(f"\n❌ No data found for {company}")
            
            # Show search results
            search_results = search_companies(company)
            if search_results:
                print(f"Found {len(search_results)} similar companies:")
                for result in search_results[:3]:
                    print(f"  • {result['name']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")
    test_utilities()

def save_results(shared):
    """Optionally save analysis results to file."""
    
    save = input("\nWould you like to save the results? (y/n): ").lower()
    if save == 'y':
        try:
            filename = f"offer_analysis_{shared.get('final_report', {}).get('analysis_date', '2024-01-01')}.json"
            
            # Prepare data for saving (remove non-serializable content)
            save_data = {
                "final_report": shared.get("final_report", {}),
                "executive_summary": shared.get("executive_summary", ""),
                "offers": shared.get("offers", []),
                "comparison_results": shared.get("comparison_results", {}),
                "user_preferences": shared.get("user_preferences", {})
            }
            
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            print(f"✅ Results saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")

if __name__ == "__main__":
    main()
