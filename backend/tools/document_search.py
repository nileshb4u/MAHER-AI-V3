"""
Technical Document Search Tool
Searches technical documentation and manuals
"""
from typing import Dict, Any, List


def search_documents(query: str, doc_types: List[str] = None) -> Dict[str, Any]:
    """
    Search technical documentation

    Args:
        query: Search query string
        doc_types: List of document types to search (optional)

    Returns:
        Search results with document references
    """
    if doc_types is None:
        doc_types = ["manual", "procedure", "specification", "drawing"]

    # Sample document database
    documents = [
        {
            "id": "DOC-001",
            "title": "Centrifugal Pump Maintenance Procedure",
            "type": "procedure",
            "equipment": "PUMP-001",
            "keywords": ["pump", "maintenance", "centrifugal", "seal", "bearing"],
            "revision": "Rev 3",
            "date": "2024-06-15"
        },
        {
            "id": "DOC-002",
            "title": "Compressor Safety Manual",
            "type": "manual",
            "equipment": "COMP-002",
            "keywords": ["compressor", "safety", "pressure", "lockout", "emergency"],
            "revision": "Rev 2",
            "date": "2024-03-20"
        },
        {
            "id": "DOC-003",
            "title": "Motor Installation Specifications",
            "type": "specification",
            "equipment": "MOTOR-003",
            "keywords": ["motor", "electrical", "installation", "wiring", "specifications"],
            "revision": "Rev 1",
            "date": "2024-01-10"
        },
        {
            "id": "DOC-004",
            "title": "Piping and Instrumentation Diagram - Process Area 1",
            "type": "drawing",
            "equipment": "PUMP-001",
            "keywords": ["piping", "instrumentation", "pid", "process", "flow"],
            "revision": "Rev 4",
            "date": "2024-08-05"
        },
        {
            "id": "DOC-005",
            "title": "Lubrication Procedure - Rotating Equipment",
            "type": "procedure",
            "equipment": "General",
            "keywords": ["lubrication", "oil", "grease", "bearing", "maintenance"],
            "revision": "Rev 2",
            "date": "2024-05-12"
        },
        {
            "id": "DOC-006",
            "title": "Electrical Safety Standards",
            "type": "manual",
            "equipment": "General",
            "keywords": ["electrical", "safety", "arc flash", "lockout", "ppe"],
            "revision": "Rev 3",
            "date": "2024-07-01"
        },
        {
            "id": "DOC-007",
            "title": "Vibration Analysis Guide",
            "type": "manual",
            "equipment": "General",
            "keywords": ["vibration", "analysis", "diagnostics", "monitoring", "rotating"],
            "revision": "Rev 1",
            "date": "2024-04-18"
        }
    ]

    # Perform search
    query_lower = query.lower()
    query_terms = query_lower.split()

    results = []

    for doc in documents:
        # Check if doc type matches filter
        if doc_types and doc["type"] not in doc_types:
            continue

        # Calculate relevance score
        score = 0

        # Check title
        if any(term in doc["title"].lower() for term in query_terms):
            score += 10

        # Check keywords
        for keyword in doc["keywords"]:
            if any(term in keyword for term in query_terms):
                score += 5

        # Add to results if relevant
        if score > 0:
            results.append({
                **doc,
                "relevance_score": score
            })

    # Sort by relevance
    results.sort(key=lambda x: x["relevance_score"], reverse=True)

    return {
        "success": True,
        "query": query,
        "doc_types_searched": doc_types,
        "total_results": len(results),
        "results": results[:10],  # Limit to top 10
        "search_tips": [
            "Use specific equipment IDs for targeted results",
            "Include maintenance type (routine, preventive, corrective)",
            "Try related terms if no results found"
        ] if len(results) == 0 else []
    }
