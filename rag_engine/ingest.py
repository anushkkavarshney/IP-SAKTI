import fitz
import json
import os
import re

def parse_and_chunk_sections(pdf_path, act_name, category, authority, source_url):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return []

    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"

    # Find all real section starts: a line beginning with "<number>. <Capital Word>"
    pattern = re.compile(r'\n(?=(\d{1,3})\.\s+[A-Z])')
    matches = list(pattern.finditer(full_text))

    raw_sections = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        raw_sections.append(full_text[start:end].strip())

    # Merge by section number, keeping the LONGEST version of each
    # (drops short/duplicate fragments caused by page breaks or false splits)
    best_by_section = {}
    for sec_text in raw_sections:
        if len(sec_text) < 80:
            continue  # too short to be real clause content, likely a heading fragment

        sec_title_match = re.search(r'^(\d{1,3})\.\s+([^\n]+)', sec_text)
        if not sec_title_match:
            continue

        sec_num = sec_title_match.group(1)
        sec_heading = sec_title_match.group(2).strip()

        if sec_num not in best_by_section or len(sec_text) > len(best_by_section[sec_num]["content"]):
            best_by_section[sec_num] = {
                "sec_num": sec_num,
                "heading": sec_heading,
                "content": sec_text
            }

    chunks = []
    for sec_num in sorted(best_by_section.keys(), key=lambda x: int(x)):
        entry = best_by_section[sec_num]
        chunk = {
            "doc_id": f"{act_name.upper().replace(' ', '_').replace(',', '')}_SEC_{entry['sec_num']}",
            "act_name": act_name,
            "section": f"Section {entry['sec_num']}: {entry['heading']}",
            "jurisdiction": "India",
            "as_of_date": "2024-08-01",
            "effective_date": "2024-08-01",
            "category": category,
            "authority": authority,
            "source_url": source_url,
            "content": entry["content"]
        }
        chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    raw_docs_dir = "rag_engine/raw_docs"
    all_chunks = []

    patents_pdf = os.path.join(raw_docs_dir, "patents_act_1970.pdf")
    all_chunks.extend(parse_and_chunk_sections(
        patents_pdf, "The Patents Act, 1970", "IP_PATENT",
        authority="Indian Patent Office (IPO)",
        source_url="https://ipindia.gov.in/"
    ))

    bio_pdf = os.path.join(raw_docs_dir, "biological_diversity_act_2002.pdf")
    all_chunks.extend(parse_and_chunk_sections(
        bio_pdf, "The Biological Diversity Act, 2002", "ABS_BIODIVERSITY",
        authority="National Biodiversity Authority (NBA)",
        source_url="https://nbaindia.org/"
    ))

    drugs_pdf = os.path.join(raw_docs_dir, "drugs_and_cosmetics_act_1940.pdf")
    all_chunks.extend(parse_and_chunk_sections(
        drugs_pdf, "The Drugs and Cosmetics Act, 1940", "REGULATORY_AYUSH",
        authority="Central Drugs Standard Control Organisation (CDSCO)",
        source_url="https://cdsco.gov.in/"
    ))
    cosmetics_pdf = os.path.join(raw_docs_dir, "cosmetics_rules_2020.pdf")
    all_chunks.extend(parse_and_chunk_sections(
        cosmetics_pdf, "The Cosmetics Rules, 2020", "REGULATORY_COSMETICS",
        authority="Central Drugs Standard Control Organisation (CDSCO)",
        source_url="https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2022/cos_rules/Cosmetics%20Rules%202020.pdf"
    ))

    fssai_pdf = os.path.join(raw_docs_dir, "fssai_nutraceutical_regulations_2016.pdf")
    all_chunks.extend(parse_and_chunk_sections(
        fssai_pdf, "Food Safety and Standards (Health Supplements, Nutraceuticals, Food for Special Dietary Use, Food for Special Medical Purpose, Functional Food and Novel Food) Regulations, 2016", "REGULATORY_NUTRACEUTICAL",
        authority="Food Safety and Standards Authority of India (FSSAI)",
        source_url="https://faolex.fao.org/docs/pdf/IND168163.pdf"
    ))

    output_file = "rag_engine/processed_data/corpus.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"Success! Generated {len(all_chunks)} section-level chunks in {output_file}")