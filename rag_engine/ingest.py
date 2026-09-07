import fitz
import json
import os
import re

def parse_and_chunk_sections(pdf_path, act_name, category):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return []
        
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"

    raw_sections = re.split(r'\n(?=\d+\.\s+[A-Z])', full_text)
    
    chunks = []
    for idx, sec_text in enumerate(raw_sections):
        cleaned_text = sec_text.strip()
        if len(cleaned_text) < 40:
            continue
            
        sec_title_match = re.search(r'^(\d+)\.\s+([^\n]+)', cleaned_text)
        if sec_title_match:
            sec_num = sec_title_match.group(1)
            sec_heading = sec_title_match.group(2)
            section_label = f"Section {sec_num}: {sec_heading}"
        else:
            section_label = f"Section Chunk {idx + 1}"

        chunk = {
            "doc_id": f"{act_name.upper().replace(' ', '_')}_SEC_{idx + 1}",
            "act_name": act_name,
            "section": section_label,
            "jurisdiction": "India",
            "as_of_date": "2024-08-01",
            "category": category,
            "content": cleaned_text
        }
        chunks.append(chunk)
        
    return chunks

if __name__ == "__main__":
    raw_docs_dir = "rag_engine/raw_docs"
    all_chunks = []
    
    patents_pdf = os.path.join(raw_docs_dir, "patents_act_1970.pdf")
    all_chunks.extend(parse_and_chunk_sections(patents_pdf, "The Patents Act, 1970", "IP_PATENT"))
    
    bio_pdf = os.path.join(raw_docs_dir, "biological_diversity_act_2002.pdf")
    all_chunks.extend(parse_and_chunk_sections(bio_pdf, "The Biological Diversity Act, 2002", "ABS_BIODIVERSITY"))
    
    drugs_pdf = os.path.join(raw_docs_dir, "drugs_and_cosmetics_act_1940.pdf")
    all_chunks.extend(parse_and_chunk_sections(drugs_pdf, "The Drugs and Cosmetics Act, 1940", "REGULATORY_AYUSH"))
    
    output_file = "rag_engine/processed_data/corpus.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
        
    print(f"Success! Generated {len(all_chunks)} section-level chunks in {output_file}")