"""
Web Research Agent - AI-powered company intelligence gathering
Uses LLM capabilities to research and synthesize company information
"""

from .call_llm import call_llm, call_llm_structured
from .config import get_config
from .cache import cached_call
import json

def research_company(company_name, position=None, research_topics=None):
    """
    AI-powered company research agent that gathers comprehensive intelligence.
    
    Args:
        company_name (str): Name of the company to research
        position (str): Position title for context
        research_topics (list): Specific areas to focus research on
    
    Returns:
        dict: Comprehensive company research data
    """
    if research_topics is None:
        research_topics = [
            "company_culture",
            "work_life_balance", 
            "career_growth",
            "compensation_trends",
            "recent_news",
            "employee_satisfaction",
            "benefits_quality",
            "remote_work_policy",
            "diversity_inclusion",
            "financial_stability"
        ]
    
    system_prompt = """You are an expert company research analyst. Your task is to provide comprehensive, 
    accurate, and up-to-date information about companies based on your knowledge. Focus on factual, 
    objective analysis that would be valuable for job seekers evaluating offers."""
    
    research_prompt = f"""
    Please provide comprehensive research on {company_name} covering the following areas:
    {', '.join(research_topics)}
    
    {f"Context: This research is for evaluating a {position} position." if position else ""}
    
    For each area, provide:
    1. Current status/situation
    2. Recent trends or changes  
    3. Comparison to industry standards
    4. Specific insights relevant to potential employees
    
    Format your response as detailed analysis with specific examples and data points where possible.
    Focus on information that would influence job offer decisions.
    """
    
    # Get comprehensive analysis
    config = get_config()
    if config.enable_cache:
        research_analysis = cached_call(
            "web_research", config.cache_ttl_seconds, [company_name, position or "", research_topics, "analysis"]
        )(lambda: call_llm(
            research_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        ))()
    else:
        research_analysis = call_llm(
            research_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )
    
    # Extract structured metrics
    metrics_prompt = f"""
    Based on the following research about {company_name}, extract key metrics in JSON format:
    
    {research_analysis}
    
    Provide scores (1-10 scale) AND letter grades (A+, A, B+, B, C, D, F) where applicable:
    {{
        "culture_score": {{"score": X, "explanation": "brief reason"}},
        "wlb_score": {{"score": X, "grade": "Letter Grade", "explanation": "brief reason"}},
        "growth_score": {{"score": X, "grade": "Letter Grade", "explanation": "brief reason"}},
        "benefits_score": {{"score": X, "grade": "Letter Grade", "explanation": "brief reason"}},
        "stability_score": {{"score": X, "explanation": "brief reason"}},
        "reputation_score": {{"score": X, "explanation": "brief reason"}},
        "innovation_score": {{"score": X, "explanation": "brief reason"}},
        "diversity_score": {{"score": X, "explanation": "brief reason"}},
        "remote_friendliness": {{"score": X, "explanation": "brief reason"}},
        "key_strengths": ["strength1", "strength2", "strength3"],
        "potential_concerns": ["concern1", "concern2"],
        "recent_highlights": ["highlight1", "highlight2"]
    }}
    """
    
    try:
        if config.enable_cache:
            metrics_json = cached_call(
                "web_research", config.cache_ttl_seconds, [company_name, position or "", "metrics"]
            )(lambda: call_llm_structured(
                metrics_prompt,
                response_format={"type": "json_object"},
                system_prompt="You are a data analyst extracting structured metrics from company research.",
            ))()
        else:
            metrics_json = call_llm_structured(
                metrics_prompt,
                response_format={"type": "json_object"},
                system_prompt="You are a data analyst extracting structured metrics from company research."
            )
        metrics = json.loads(metrics_json)
    except:
        # Fallback to default scores if parsing fails
        metrics = {
            "culture_score": {"score": 7, "explanation": "Analysis not available"},
            "wlb_score": {"score": 7, "grade": "B", "explanation": "Analysis not available"},
            "growth_score": {"score": 7, "grade": "B", "explanation": "Analysis not available"},
            "benefits_score": {"score": 7, "grade": "B", "explanation": "Analysis not available"},
            "stability_score": {"score": 7, "explanation": "Analysis not available"},
            "reputation_score": {"score": 7, "explanation": "Analysis not available"},
            "innovation_score": {"score": 7, "explanation": "Analysis not available"},
            "diversity_score": {"score": 7, "explanation": "Analysis not available"},
            "remote_friendliness": {"score": 7, "explanation": "Analysis not available"},
            "key_strengths": ["Established company", "Competitive in market"],
            "potential_concerns": ["Limited data available"],
            "recent_highlights": ["Active in industry"]
        }
    
    return {
        "company_name": company_name,
        "position_context": position,
        "research_analysis": research_analysis,
        "metrics": metrics,
        "research_timestamp": "2024-01-01",  # In production, use actual timestamp
        "research_topics": research_topics
    }

def get_market_sentiment(company_name, position=None):
    """
    Get market sentiment and recent news analysis for a company.
    
    Args:
        company_name (str): Company to analyze
        position (str): Position context
    
    Returns:
        dict: Market sentiment analysis
    """
    sentiment_prompt = f"""
    Analyze the current market sentiment and recent developments for {company_name}.
    {f"Focus on implications for {position} roles." if position else ""}
    
    Consider:
    - Recent news and announcements
    - Stock performance and financial health
    - Industry position and competitive landscape
    - Employee sentiment and reviews
    - Leadership changes or strategic shifts
    
    Provide:
    1. Overall sentiment (Positive/Neutral/Negative)
    2. Key recent developments
    3. Implications for job seekers
    4. Risk factors to consider
    5. Growth opportunities
    """
    
    sentiment_analysis = call_llm(
        sentiment_prompt,
        temperature=0.3,
        system_prompt="You are a market analyst providing objective sentiment analysis."
    )
    
    return {
        "company_name": company_name,
        "sentiment_analysis": sentiment_analysis,
        "analysis_timestamp": "2024-01-01"
    }

# Async versions for AsyncNode usage
async def research_company_async(company_name, position=None, research_topics=None):
    """Async version of research_company for use with AsyncNode."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, research_company, company_name, position, research_topics)

async def get_market_sentiment_async(company_name, position=None):
    """Async version of get_market_sentiment for use with AsyncNode."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_market_sentiment, company_name, position)

if __name__ == "__main__":
    # Test the research agent
    research_data = research_company("Google", "Senior Software Engineer")
    print("Research Data:", json.dumps(research_data, indent=2))
    
    sentiment_data = get_market_sentiment("Google", "Senior Software Engineer")
    print("Sentiment Data:", json.dumps(sentiment_data, indent=2)) 