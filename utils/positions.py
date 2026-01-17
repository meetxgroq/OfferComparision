"""
Centralized list of position auto-suggestions for the Offer Form.
Organized by role category/pillar.
"""

COMMON_POSITIONS = {
    "Engineering": [
        "Software Engineer",
        "Senior Software Engineer",
        "Staff Software Engineer",
        "Principal Software Engineer",
        "Frontend Engineer",
        "Backend Engineer",
        "Full Stack Engineer",
        "DevOps Engineer",
        "Site Reliability Engineer (SRE)",
        "Mobile Engineer (iOS)",
        "Mobile Engineer (Android)",
        "System Software Engineer",
        "Senior System Software Engineer"
    ],
    "Management": [
        "Engineering Manager",
        "Senior Engineering Manager",
        "Director of Engineering",
        "VP of Engineering",
        "Product Manager",
        "Senior Product Manager",
        "Director of Product",
        "VP of Product",
        "Technical Program Manager",
        "Senior Technical Program Manager"
    ],
    "Data": [
        "Data Scientist",
        "Senior Data Scientist",
        "Data Engineer",
        "Machine Learning Engineer",
        "Research Scientist",
        "Data Analyst"
    ],
    "Design": [
        "Product Designer",
        "UI/UX Designer",
        "Visual Designer",
        "UX Researcher"
    ]
}

def get_all_positions():
    """Return a flat list of all positions sorted alphabetically."""
    all_pos = set()
    for cat in COMMON_POSITIONS.values():
        all_pos.update(cat)
    return sorted(list(all_pos))
