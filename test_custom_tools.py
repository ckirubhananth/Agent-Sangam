#!/usr/bin/env python3
"""
Test script to demonstrate custom PDF tools functionality.
"""
import sys
sys.path.insert(0, '.')

from tools.pdf_tools import (
    index_pdf_content,
    search_pdf,
    extract_entities,
    get_pdf_summary,
    retrieve_relevant_context
)

# Sample PDF text (simulated)
SAMPLE_PDF_TEXT = """
THE HISTORY OF ANCIENT EGYPT

Chapter 1: The Pharaohs and Their Legacy

The ancient Egyptian civilization lasted over 3000 years. The most famous pharaohs include 
Khufu, Menkaure, Amenhotep III, and Tutankhamun. These rulers built the great pyramids of Giza, 
monuments that still stand today in Cairo.

Chapter 2: The Nile River and Agriculture

The Nile River was the lifeblood of Egyptian civilization. Each year, floods brought fertile 
soil to the floodplains. Farmers grew wheat, barley, and flax. The ancient Egyptians developed 
sophisticated irrigation systems as early as 3100 BC.

Chapter 3: Writing and Hieroglyphics

The Egyptians invented hieroglyphics around 3200 BC. This writing system was used on tomb walls, 
papyrus scrolls, and temple inscriptions. The Rosetta Stone, discovered in 1799 in Cairo by 
French soldiers, helped modern scholars decipher this ancient script.

Chapter 4: Religion and Mythology

The Egyptians worshipped many gods and goddesses. Ra was the sun god, Osiris ruled the afterlife, 
and Isis was the goddess of magic. They believed in eternal life after death. Pharaohs like 
Amenhotep III were buried in the Valley of the Kings near Thebes.

Chapter 5: Trade and Connections

Egypt traded with Nubia, the Levant, and even Punt. Nubian gold, Lebanese cedar, and Pontic 
incense were valued. Around 1500 BC, King Amenhotep III sent expeditions to Punt for myrrh, 
frankincense, and ebony wood.
"""

def test_pdf_tools():
    """Test all PDF tools."""
    print("=" * 70)
    print("TESTING CUSTOM PDF TOOLS")
    print("=" * 70)
    
    # Test 1: Index PDF
    print("\n[Test 1] Indexing PDF content...")
    result = index_pdf_content("test_pdf_123", SAMPLE_PDF_TEXT)
    print(f"✓ Indexed: {result['sections_found']} sections, {result['entities_found']} entities")
    
    # Test 2: Search PDF
    print("\n[Test 2] Searching for 'pharaohs and pyramids'...")
    results = search_pdf("test_pdf_123", "pharaohs pyramids", max_results=3)
    print(f"✓ Found {len(results)} relevant passages:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['text'][:100]}...")
        print(f"     Relevance: {result['relevance_score']:.2f}")
    
    # Test 3: Extract entities
    print("\n[Test 3] Extracting named entities...")
    from tools.agent_tools import pdf_entity_tool
    entities_output = pdf_entity_tool.execute("test_pdf_123")
    print("✓ Extracted entities:")
    print(entities_output)
    
    # Test 4: Get summary
    print("\n[Test 4] Getting PDF summary...")
    from tools.agent_tools import pdf_summary_tool
    summary = pdf_summary_tool.execute("test_pdf_123")
    print("✓ PDF Summary:")
    print(summary)
    
    # Test 5: Retrieve context for a question
    print("\n[Test 5] Retrieving context for question: 'What was the role of the Nile River?'...")
    from tools.agent_tools import pdf_context_tool
    context = pdf_context_tool.execute("test_pdf_123", "What was the role of the Nile River?")
    print("✓ Retrieved context:")
    print(context[:200] + "..." if len(context) > 200 else context)
    
    # Test 6: Search tool
    print("\n[Test 6] Using PDF search tool...")
    from tools.agent_tools import pdf_search_tool
    search_results = pdf_search_tool.execute("test_pdf_123", "Nile agriculture irrigation")
    print("✓ Search results:")
    print(search_results)
    
    print("\n" + "=" * 70)
    print("✓ ALL TOOLS TESTED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_pdf_tools()
