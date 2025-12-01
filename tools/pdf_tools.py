"""
Custom tools for PDF document processing and retrieval.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global store for PDF content (indexed for quick access)
# { pdf_session_id: { "text": full_text, "entities": [...], "sections": [...] } }
pdf_content_index = {}


def index_pdf_content(pdf_session_id: str, pdf_text: str) -> dict:
    """
    Index PDF content for faster retrieval and entity extraction.
    
    Args:
        pdf_session_id: Unique identifier for the PDF
        pdf_text: Full text content of the PDF
    
    Returns:
        Dictionary with indexed content metadata
    """
    logger.info(f"[pdf_tools] Indexing PDF: {pdf_session_id}, length: {len(pdf_text)}")
    
    # Extract sections (simple heuristic: lines with ALL CAPS or numbered sections)
    sections = []
    lines = pdf_text.split('\n')
    current_section = None
    
    for i, line in enumerate(lines):
        if len(line.strip()) > 5:
            # Detect section headers (all caps or numbered)
            if line.isupper() or line[0].isdigit():
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "title": line.strip()[:100],
                    "start_line": i,
                    "content": line
                }
            elif current_section:
                current_section["content"] += "\n" + line
    
    if current_section:
        sections.append(current_section)
    
    # Extract entities (simple: capitalized words, numbers, dates)
    entities = extract_entities(pdf_text)
    
    # Store indexed content
    pdf_content_index[pdf_session_id] = {
        "text": pdf_text,
        "entities": entities,
        "sections": sections,
        "indexed_at": __import__("datetime").datetime.utcnow().isoformat()
    }
    
    logger.info(f"[pdf_tools] Indexed {len(sections)} sections, {len(entities)} entities")
    
    return {
        "pdf_session_id": pdf_session_id,
        "total_chars": len(pdf_text),
        "sections_found": len(sections),
        "entities_found": len(entities)
    }


def search_pdf(pdf_session_id: str, query: str, max_results: int = 5) -> list:
    """
    Search PDF content for relevant passages matching the query.
    Uses simple keyword matching with context windows.
    
    Args:
        pdf_session_id: Unique identifier for the PDF
        query: Search query string
        max_results: Maximum number of results to return
    
    Returns:
        List of relevant passages with context
    """
    if pdf_session_id not in pdf_content_index:
        logger.warning(f"[pdf_tools] PDF not indexed: {pdf_session_id}")
        return []
    
    pdf_data = pdf_content_index[pdf_session_id]
    text = pdf_data["text"]
    
    logger.info(f"[pdf_tools] Searching PDF {pdf_session_id} for: '{query}'")
    
    # Simple keyword search
    keywords = query.lower().split()
    results = []
    
    sentences = text.split('. ')
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        match_count = sum(1 for kw in keywords if kw in sentence_lower)
        
        if match_count >= max(1, len(keywords) // 2):  # At least 50% keyword match
            # Add context: previous and next sentences
            context = []
            if i > 0:
                context.append(sentences[i-1].strip())
            context.append(sentence.strip())
            if i < len(sentences) - 1:
                context.append(sentences[i+1].strip())
            
            results.append({
                "text": ". ".join(context),
                "match_strength": match_count,
                "relevance_score": match_count / len(keywords) if keywords else 0
            })
    
    # Sort by relevance and limit results
    results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)[:max_results]
    
    logger.info(f"[pdf_tools] Found {len(results)} relevant passages")
    return results


def extract_entities(text: str, entity_types: Optional[list] = None) -> list:
    """
    Extract named entities from text (persons, locations, dates, numbers).
    Uses simple heuristic patterns.
    
    Args:
        text: Text to extract entities from
        entity_types: Types to extract ('PERSON', 'LOCATION', 'DATE', 'NUMBER')
    
    Returns:
        List of extracted entities with type and context
    """
    if entity_types is None:
        entity_types = ["PERSON", "LOCATION", "DATE", "NUMBER"]
    
    entities = []
    
    # Extract potential person names (capitalized words)
    if "PERSON" in entity_types:
        import re
        # Pattern: 2+ capitalized words in sequence
        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        for name in set(names):
            if len(name) > 3:  # Filter out short matches
                entities.append({
                    "text": name,
                    "type": "PERSON",
                    "count": text.count(name)
                })
    
    # Extract dates (simple pattern)
    if "DATE" in entity_types:
        import re
        dates = re.findall(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4})\b', text)
        for date in set(dates):
            entities.append({
                "text": date,
                "type": "DATE",
                "count": text.count(date)
            })
    
    # Extract numbers
    if "NUMBER" in entity_types:
        import re
        numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\b', text)
        # Only keep significant numbers (> 100 or in patterns)
        for num in set(numbers):
            if int(num.replace(',', '')) > 100:
                entities.append({
                    "text": num,
                    "type": "NUMBER",
                    "count": text.count(num)
                })
    
    # Sort by frequency
    entities = sorted(entities, key=lambda x: x["count"], reverse=True)[:20]
    
    return entities


def get_pdf_summary(pdf_session_id: str, max_lines: int = 10) -> str:
    """
    Get a brief summary/overview of the PDF by extracting key sections.
    
    Args:
        pdf_session_id: Unique identifier for the PDF
        max_lines: Maximum lines to return
    
    Returns:
        Summary text with key sections and entities
    """
    if pdf_session_id not in pdf_content_index:
        logger.warning(f"[pdf_tools] PDF not indexed: {pdf_session_id}")
        return "PDF not found or not indexed."
    
    pdf_data = pdf_content_index[pdf_session_id]
    sections = pdf_data.get("sections", [])[:3]  # First 3 sections
    entities = pdf_data.get("entities", [])[:5]  # Top 5 entities
    
    summary = "**PDF Overview**\n\n"
    
    if sections:
        summary += "**Key Sections:**\n"
        for section in sections:
            summary += f"- {section['title']}\n"
    
    if entities:
        summary += "\n**Key Entities:**\n"
        for entity in entities:
            summary += f"- {entity['text']} ({entity['type']}, mentioned {entity['count']} times)\n"
    
    return summary


def retrieve_relevant_context(pdf_session_id: str, question: str, max_chars: int = 2000) -> str:
    """
    Retrieve the most relevant sections of the PDF based on the question.
    Uses keyword matching and section relevance.
    Falls back to document beginning if no matches found.
    
    Args:
        pdf_session_id: Unique identifier for the PDF
        question: User's question
        max_chars: Maximum characters to return
    
    Returns:
        Relevant context from the PDF
    """
    if pdf_session_id not in pdf_content_index:
        logger.warning(f"[pdf_tools] PDF not indexed: {pdf_session_id}")
        return ""
    
    pdf_data = pdf_content_index[pdf_session_id]
    full_text = pdf_data.get("text", "")
    
    # Search for relevant passages
    search_results = search_pdf(pdf_session_id, question, max_results=3)
    
    context = ""
    for result in search_results:
        if len(context) + len(result["text"]) < max_chars:
            context += result["text"] + "\n\n"
    
    # Fallback: if no search results, use beginning of document
    if not context and full_text:
        logger.info(f"[pdf_tools] No search results found, using document beginning as fallback")
        context = full_text[:max_chars]
    
    logger.info(f"[pdf_tools] Retrieved {len(context)} chars of context for question")
    
    return context if context else ""
