"""
Visualization Data Formatter - Chart.js data preparation
Formats offer comparison data for interactive visualizations
"""

import json
import re
from typing import Dict, List, Any
import colorsys

def generate_colors(n_colors, alpha=0.8):
    """
    Generate n distinct colors for charts.
    
    Args:
        n_colors (int): Number of colors needed
        alpha (float): Color opacity
    
    Returns:
        list: List of hex color strings (e.g., #RRGGBB)
    """
    colors = []
    for i in range(n_colors):
        hue = i / max(1, n_colors)
        r, g, b = colorsys.hsv_to_rgb(hue, 0.65, 0.95)
        colors.append(f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}")
    return colors

def format_radar_chart(offers_data, factors=None):
    """
    Format data for radar chart comparing offers across factors.
    
    Args:
        offers_data (list): List of scored offers
        factors (list): Factors to include in radar chart
    
    Returns:
        dict: Chart.js radar chart configuration
    """
    if factors is None:
        factors = [
            "base_salary",
            "total_compensation", 
            "equity_upside",
            "work_life_balance",
            "career_growth",
            "company_culture",
            "benefits_quality",
            "location_preference"
        ]
    
    # Factor labels for display
    factor_labels = {
        "base_salary": "Base Salary",
        "total_compensation": "Total Comp",
        "equity_upside": "Equity Upside",
        "work_life_balance": "Work-Life Balance",
        "career_growth": "Career Growth", 
        "company_culture": "Company Culture",
        "benefits_quality": "Benefits",
        "location_preference": "Location"
    }
    
    labels = [factor_labels.get(f, f.replace("_", " ").title()) for f in factors]
    datasets = []
    
    colors = generate_colors(len(offers_data))
    
    for i, offer in enumerate(offers_data):
        factor_scores = offer.get("score_breakdown", {}).get("factor_scores", offer.get("factor_scores", {}))
        data = [factor_scores.get(factor, 0) for factor in factors]
        
        dataset = {
            "label": f"{offer.get('company', 'Company')} - {offer.get('position', '')}",
            "data": data,
            "borderColor": colors[i],
            "backgroundColor": colors[i],
            "pointBackgroundColor": colors[i],
            "pointBorderColor": "#fff",
            "pointHoverBackgroundColor": "#fff",
            "pointHoverBorderColor": colors[i]
        }
        datasets.append(dataset)
    
    return {
        "type": "radar",
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Offer Comparison - Multi-Factor Analysis"
                },
                "legend": {
                    "position": "top"
                }
            },
            "scales": {
                "r": {
                    "min": 0,
                    "max": 100,
                    "ticks": {
                        "stepSize": 20
                    }
                }
            }
        }
    }

def format_bar_chart(offers_data, metric="total_score"):
    """
    Format data for bar chart comparing specific metric.
    
    Args:
        offers_data (list): List of scored offers
        metric (str): Metric to compare
    
    Returns:
        dict: Chart.js bar chart configuration
    """
    labels = [f"{offer.get('company', 'Company')}\n{offer.get('position', '')}" for offer in offers_data]
    
    if metric == "total_score":
        data = [offer["total_score"] for offer in offers_data]
        title = "Overall Offer Scores"
        y_max = 100
    elif metric == "total_compensation":
        data = [offer.get("offer_data", offer).get("total_compensation", 0) for offer in offers_data]
        title = "Total Compensation Comparison"
        y_max = None
    elif metric == "base_salary":
        data = [offer.get("offer_data", offer).get("base_salary", 0) for offer in offers_data]
        title = "Base Salary Comparison"
        y_max = None
    else:
        # Factor score
        data = [offer["score_breakdown"]["factor_scores"].get(metric, 0) for offer in offers_data]
        title = f"{metric.replace('_', ' ').title()} Comparison"
        y_max = 100
    
    colors = generate_colors(len(offers_data))
    
    return {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": title,
                "data": data,
                "backgroundColor": colors,
                "borderColor": colors,
                "borderWidth": 1
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": title
                },
                "legend": {
                    "display": False
                }
            },
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "max": y_max
                }
            }
        }
    }

def format_compensation_breakdown(offers_data):
    """
    Format data for compensation breakdown pie/doughnut charts.
    
    Args:
        offers_data (list): List of scored offers
    
    Returns:
        dict: Multiple chart configurations
    """
    charts = {}
    
    for offer in offers_data:
        offer_id = offer.get("offer_id", offer.get("company", "offer"))
        offer_data = offer.get("offer_data", offer)
        
        base_salary = offer_data.get("base_salary", 0)
        equity = offer_data.get("equity", 0)
        bonus = offer_data.get("bonus", 0)
        
        total = base_salary + equity + bonus
        
        if total > 0:
            data = [base_salary, equity, bonus]
            labels = ["Base Salary", "Equity", "Bonus"]
            
            # Filter out zero values
            filtered_data = []
            filtered_labels = []
            for i, value in enumerate(data):
                if value > 0:
                    filtered_data.append(value)
                    filtered_labels.append(labels[i])
            
            colors = ["#36A2EB", "#FF6384", "#FFCE56"][:len(filtered_data)]
            
            charts[offer_id] = {
                "type": "doughnut",
                "data": {
                    "labels": filtered_labels,
                    "datasets": [{
                        "data": filtered_data,
                        "backgroundColor": colors,
                        "borderWidth": 2
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": f"{offer['company']} - Compensation Breakdown"
                        },
                        "legend": {
                            "position": "bottom"
                        }
                    }
                }
            }
    
    return charts

def format_market_comparison_chart(offers_data):
    """
    Format data for market percentile comparison.
    
    Args:
        offers_data (list): List of scored offers
    
    Returns:
        dict: Chart.js scatter plot configuration
    """
    datasets = []
    colors = generate_colors(len(offers_data))
    
    for i, offer in enumerate(offers_data):
        factor_scores = offer.get("score_breakdown", {}).get("factor_scores", offer.get("factor_scores", {}))
        base_percentile = factor_scores.get("base_salary", 50)
        total_percentile = factor_scores.get("total_compensation", 50)
        
        dataset = {
            "label": f"{offer['company']}",
            "data": [{
                "x": base_percentile,
                "y": total_percentile
            }],
            "backgroundColor": colors[i],
            "borderColor": colors[i],
            "pointRadius": 8
        }
        datasets.append(dataset)
    
    return {
        "type": "scatter",
        "data": {
            "datasets": datasets
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Market Position - Base vs Total Compensation"
                },
                "legend": {
                    "position": "top"
                }
            },
            "scales": {
                "x": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": "Base Salary Percentile"
                    },
                    "min": 0,
                    "max": 100
                },
                "y": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": "Total Compensation Percentile"
                    },
                    "min": 0,
                    "max": 100
                }
            }
        }
    }

def format_factor_importance_chart(weights):
    """
    Format data for factor importance/weights visualization.
    
    Args:
        weights (dict): Scoring weights
    
    Returns:
        dict: Chart.js horizontal bar chart configuration
    """
    factor_labels = {
        "base_salary": "Base Salary",
        "total_compensation": "Total Compensation",
        "equity_upside": "Equity Upside", 
        "work_life_balance": "Work-Life Balance",
        "career_growth": "Career Growth",
        "company_culture": "Company Culture",
        "benefits_quality": "Benefits Quality",
        "location_preference": "Location Preference"
    }
    
    labels = []
    data = []
    
    # Sort by weight (descending)
    sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    
    for factor, weight in sorted_weights:
        labels.append(factor_labels.get(factor, factor.replace("_", " ").title()))
        data.append(weight * 100)  # Convert to percentage
    
    return {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Importance (%)",
                "data": data,
                "backgroundColor": "#36A2EB",
                "borderColor": "#2E86AB",
                "borderWidth": 1
            }]
        },
        "options": {
            "indexAxis": "y",
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Your Scoring Priorities"
                },
                "legend": {
                    "display": False
                }
            },
            "scales": {
                "x": {
                    "beginAtZero": True,
                    "max": max(data) + 5 if data else 50,
                    "title": {
                        "display": True,
                        "text": "Weight (%)"
                    }
                }
            }
        }
    }

def format_comparison_table(offers_data):
    """
    Format data for detailed comparison table.
    
    Args:
        offers_data (list): List of scored offers
    
    Returns:
        dict: Table data and configuration
    """
    if not offers_data:
        return {"headers": [], "rows": []}
    
    headers = [
        "Rank",
        "Company",
        "Level",
        "Position", 
        "Location",
        "Total Score",
        "Base Salary",
        "Total Comp",
        "Equity",
        "WLB Score",
        "Growth Score",
        "Culture Score"
    ]
    
    rows = []
    
    for offer in offers_data:
        offer_data = offer.get("offer_data", offer)
        scores = offer.get("score_breakdown", {}).get("factor_scores", offer.get("factor_scores", {}))
        
        row = [
            offer.get("rank", "-"),
            offer.get("company", "-"),
            offer_data.get("level", "-"),
            offer.get("position", "-"),
            offer.get("location", "-"),
            f"{offer.get('total_score', 0):.1f}",
            f"${int(offer_data.get('base_salary', 0)):,}",
            f"${int(offer_data.get('total_compensation', offer_data.get('base_salary', 0) + offer_data.get('equity', 0) + offer_data.get('bonus', 0))):,}",
            f"${int(offer_data.get('equity', 0)):,}",
            f"{scores.get('work_life_balance', 0):.0f}",
            f"{scores.get('career_growth', 0):.0f}",
            f"{scores.get('company_culture', 0):.0f}"
        ]
        rows.append(row)
    
    return {
        "headers": headers,
        "rows": rows,
        "best_values": _find_best_values(rows, offers_data),
        "best_in_column": _find_best_values(rows, offers_data)
    }

def _find_best_values(rows, offers_data):
    """Find best values in each column for highlighting."""
    if not rows:
        return {}
    
    import re
    def _num(s: str) -> float:
        # Extract numeric, allow decimals
        if not s or s == '-':
            return 0.0
        val = re.sub(r"[^0-9.\-]", "", str(s))
        try:
            return float(val)
        except Exception:
            return 0.0

    best_indices = {}
    
    # Total Score (highest)
    score_col = 4
    try:
        max_score = max(_num(row[score_col]) for row in rows)
        if max_score > 0:
            for i, row in enumerate(rows):
                if _num(row[score_col]) == max_score:
                    best_indices[f"{i},{score_col}"] = "highest_score"
    except (ValueError, IndexError):
        pass
    
    # Base Salary (highest)
    salary_col = 5
    try:
        max_salary = max(_num(row[salary_col]) for row in rows)
        if max_salary > 0:
            for i, row in enumerate(rows):
                if _num(row[salary_col]) == max_salary:
                    best_indices[f"{i},{salary_col}"] = "highest_comp"
    except (ValueError, IndexError):
        pass
        if _num(row[salary_col]) == max_salary:
            best_indices[f"{i},{salary_col}"] = "highest_value"
    
    return best_indices

def create_visualization_package(offers_data, weights=None):
    """
    Create complete visualization package for offer comparison.
    
    Args:
        offers_data (list): List of scored offers
        weights (dict): Scoring weights
    
    Returns:
        dict: Complete visualization package
    """
    if not offers_data:
        return {"error": "No offers data provided"}
    
    return {
        "radar_chart": format_radar_chart(offers_data),
        "overall_scores": format_bar_chart(offers_data, "total_score"),
        "salary_comparison": format_bar_chart(offers_data, "base_salary"),
        "total_comp_comparison": format_bar_chart(offers_data, "total_compensation"),
        "compensation_breakdowns": format_compensation_breakdown(offers_data),
        "market_position": format_market_comparison_chart(offers_data),
        "factor_importance": format_factor_importance_chart(weights or {}),
        "comparison_table": format_comparison_table(offers_data),
        "summary_stats": {
            "total_offers": len(offers_data),
            "avg_score": sum(offer["total_score"] for offer in offers_data) / len(offers_data),
            "score_range": {
                "min": min(offer["total_score"] for offer in offers_data),
                "max": max(offer["total_score"] for offer in offers_data)
            },
            "top_company": offers_data[0]["company"] if offers_data else None
        }
    }

if __name__ == "__main__":
    # Test visualization formatting
    sample_offers = [
        {
            "offer_id": "offer_1",
            "company": "Google",
            "position": "Senior SWE",
            "location": "Seattle, WA",
            "total_score": 85.2,
            "offer_data": {"base_salary": 180000, "equity": 50000, "bonus": 20000, "total_compensation": 250000},
            "score_breakdown": {
                "factor_scores": {
                    "base_salary": 75, "total_compensation": 80, "work_life_balance": 85,
                    "career_growth": 90, "company_culture": 85, "equity_upside": 70
                }
            }
        },
        {
            "offer_id": "offer_2", 
            "company": "Microsoft",
            "position": "Senior SWE",
            "location": "Seattle, WA",
            "total_score": 78.5,
            "offer_data": {"base_salary": 175000, "equity": 40000, "bonus": 25000, "total_compensation": 240000},
            "score_breakdown": {
                "factor_scores": {
                    "base_salary": 70, "total_compensation": 75, "work_life_balance": 90,
                    "career_growth": 85, "company_culture": 80, "equity_upside": 65
                }
            }
        }
    ]
    
    weights = {"base_salary": 0.3, "total_compensation": 0.2, "work_life_balance": 0.2, "career_growth": 0.15, "company_culture": 0.1, "equity_upside": 0.05}
    
    viz_package = create_visualization_package(sample_offers, weights)
    print("Visualization Package Keys:", list(viz_package.keys())) 