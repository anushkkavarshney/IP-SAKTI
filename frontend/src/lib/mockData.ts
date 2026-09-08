import {
  AnalyzePayload,
  ClarificationAnswers,
  ClarificationQuestion,
  FinalRoadmapResponse,
  LegalEvidenceChunk,
} from "../types/roadmap";

export const CLARIFICATION_QUESTIONS: ClarificationQuestion[] = [
  {
    id: "intended_use",
    field_key: "intended_use",
    question: "1. What is the primary intended use and form of your product?",
    description:
      "Helps differentiate between medicinal (therapeutic), health supplement (food), or external cosmetic classification under Indian regulations.",
    options: [
      {
        value: "therapeutic_internal",
        label: "Therapeutic / Medicinal Treatment (Internal Consumption)",
        hint: "Intended to diagnose, treat, or alleviate disease/stress symptoms (e.g. tablet, syrup, extract capsule)",
      },
      {
        value: "supplement_food",
        label: "General Health & Dietary Supplement / Wellness",
        hint: "Daily nutrition/wellness enhancement without claiming to cure specific medical diseases (FSSAI domain)",
      },
      {
        value: "cosmetic_external",
        label: "External Application / Cosmetic & Personal Care",
        hint: "Skincare, hair oil, cleansing, or beautification without medical cure claims (Cosmetics Rules 2020)",
      },
    ],
  },
  {
    id: "classical_heritage",
    field_key: "classical_heritage",
    question: "2. Is this product based on an authoritative classical Ayurvedic text?",
    description:
      "Classical Ayurvedic drugs strictly follow formulas from texts listed in the First Schedule of the Drugs & Cosmetics Act, 1940.",
    options: [
      {
        value: "classical_exact",
        label:
          "Exact formulation from a recognized classical text (Charaka, Sushruta, Sharangadhara, etc.)",
        hint: "Ingredients, dosage, and preparation match authoritative text exactly",
      },
      {
        value: "classical_modified",
        label: "Classical herb(s) utilized, but with a modified formulation or novel process",
        hint: "Derived from traditional knowledge, but incorporates modern extraction, delivery, or ratios",
      },
      {
        value: "completely_new",
        label: "New proprietary herbal blend without direct classical textual reference",
        hint: "Original research, modern herbal combination",
      },
    ],
  },
  {
    id: "novel_extraction",
    field_key: "novel_extraction",
    question:
      "3. Does the innovation involve a new extraction method, delivery mechanism, or process?",
    description:
      "Crucial for identifying potential process patentability vs mere traditional knowledge aggregation.",
    options: [
      {
        value: "novel_process_claimed",
        label: "Yes, novel extraction technique, nanocarrier, or specialized processing method",
        hint: "May have patentable process attributes if inventive step is demonstrated",
      },
      {
        value: "standard_ayurvedic_extraction",
        label: "Standard classical extraction (Kwatha, Asava, Arishta, Taila, Churna)",
        hint: "Follows conventional traditional extraction methods",
      },
      {
        value: "unsure_process",
        label: "Uncertain / Standard laboratory preparation",
        hint: "No proprietary or non-obvious engineering step claimed",
      },
    ],
  },
  {
    id: "biological_resources",
    field_key: "biological_resources",
    question: "4. Does your innovation use biological resources harvested or sourced within India?",
    description:
      "Governs applicability of the Biological Diversity Act, 2002 and National Biodiversity Authority (NBA) approvals.",
    options: [
      {
        value: "indian_wild_cultivated",
        label: "Yes, Indian medicinal plants/herbs (wild or cultivated)",
        hint: "E.g. Ashwagandha, Haritaki, Tulsi, Brahmi sourced from Indian states/localities",
      },
      {
        value: "synthetic_or_imported",
        label: "No, purely synthetic compounds or imported foreign biological material",
        hint: "No Indian indigenous biological resources involved",
      },
      {
        value: "value_added_commercial_commodity",
        label: "Normally traded commodity (NTAC) / purchased from open retail market",
        hint: "May be subject to specific exemption notifications under Section 40 of Biological Diversity Act",
      },
    ],
  },
  {
    id: "jurisdiction",
    field_key: "jurisdiction",
    question: "5. What is the target jurisdiction for regulatory filing and commercialization?",
    description:
      "IP-SAKTI Navigator MVP strictly applies Indian statutory laws (Patents Act, BDA, D&C Act, FSSAI).",
    options: [
      {
        value: "india_primary",
        label: "India (Primary Jurisdiction)",
        hint: "Evaluation against Indian Patent Office, NBA, AYUSH, CDSCO & FSSAI standards",
      },
      {
        value: "global_export",
        label: "India First, with future intention for US / EU export",
        hint: "Analysis remains strictly anchored to Indian legal prerequisites for MVP",
      },
    ],
  },
];

/**
 * -----------------------------------------------------------------------------------
 * SCENARIO 1: Canonical Section 49 Ashwagandha Extraction Formulation
 * Category: Proprietary Ayurvedic Medicine
 * Key traits: Novel extraction process, Withania somnifera, ABS applicable, Rule 158B.
 * -----------------------------------------------------------------------------------
 */
export const MOCK_ASHWAGANDHA_ROADMAP: FinalRoadmapResponse = {
  classification: {
    category: "Proprietary Ayurvedic Medicine",
    reason:
      "The product utilizes Withania somnifera (Ashwagandha), an herb recognized in the Ayurvedic Pharmacopoeia of India (API), but incorporates a novel extraction process and modified dosage form not identical to classical textual recipes. Thus, it falls under the proprietary ASU (Ayurveda, Siddha, Unani) drug framework under Section 3(h) of the Drugs & Cosmetics Act rather than a pure classical medicine.",
    confidence: 0.88,
  },
  ip: {
    analysis:
      "The novel extraction methodology and modified bioactive yield may potentially be considered for a process patent under Section 2(1)(j) of The Patents Act, 1970. However, substantial scrutiny applies under Section 3(p), which excludes inventions based on traditional knowledge, and Section 3(e), which bars mere admixtures. A non-obvious technical effect and industrial applicability must be rigorously demonstrated.",
    flags: [
      "Section 3(p) Traditional Knowledge Scrutiny",
      "Section 3(e) Mere Admixture vs Synergistic Effect",
      "Process Patentability Potential (Extraction Step)",
      "Mandatory NBA Form III approval prior to patent grant",
    ],
    patentability_considerations: [
      "Product claims on Ashwagandha root alone are strictly unpatentable under Section 3(p).",
      "Method/process claims regarding novel solvent fractionation or temperature-controlled extraction may qualify if inventive step and industrial applicability are proven.",
      "Experimental data comparing therapeutic efficacy/bioavailability against conventional Kwatha or Churna is recommended to overcome obviousness objections.",
    ],
    traditional_knowledge_flags: [
      "Withania somnifera (Ashwagandha) is heavily documented in the Traditional Knowledge Digital Library (TKDL) and Ayurvedic treatises for balya (strengthening) and manasa roga (stress/mental disorders).",
      "Examiners at the Indian Patent Office routinely cite TKDL prior-art for Ashwagandha-based filings.",
    ],
    evidence: [
      {
        id: "ev_pat_1",
        jurisdiction: "India",
        legal_domain: "Patent",
        document_name: "The Patents Act, 1970",
        section: "Section 3(p)",
        authority: "Indian Patent Office (IPO) / India Code",
        effective_date: "Consolidated 2005",
        source_url:
          "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_31_1_patent-act-1970-11march2015.pdf",
        text: "The following are not inventions within the meaning of this Act: (p) an invention which in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components.",
      },
      {
        id: "ev_pat_2",
        jurisdiction: "India",
        legal_domain: "Patent",
        document_name: "The Patents Act, 1970",
        section: "Section 3(e)",
        authority: "Indian Patent Office (IPO) / India Code",
        effective_date: "Consolidated 2005",
        source_url:
          "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_31_1_patent-act-1970-11march2015.pdf",
        text: "The following are not inventions within the meaning of this Act: (e) a substance obtained by a mere admixture resulting only in the aggregation of the properties of the components thereof or a process for producing such substance.",
      },
    ],
  },
  abs: {
    applicable: true,
    analysis:
      "Because Withania somnifera is an indigenous biological resource sourced within India, the provisions of the Biological Diversity Act, 2002 apply. Under Section 6(1), no person shall apply for any intellectual property right, in or outside India, for any invention based on any biological resource obtained from India without obtaining prior approval of the National Biodiversity Authority (NBA).",
    biological_resource_identified: "Withania somnifera (Dunal) / Ashwagandha root",
    nba_action_items: [
      "Submit Form III to National Biodiversity Authority (NBA) before filing or proceeding to patent grant.",
      "If an Indian commercial entity is accessing biological resources from rural farmers or forests, intimation to State Biodiversity Board (SBB) under Section 7 is mandatory.",
      "Establish Benefit Sharing Agreements in accordance with NBA ABS Guidelines 2014 / 2023 Amendments.",
    ],
    evidence: [
      {
        id: "ev_abs_1",
        jurisdiction: "India",
        legal_domain: "Biodiversity / ABS",
        document_name: "The Biological Diversity Act, 2002",
        section: "Section 6(1)",
        authority: "National Biodiversity Authority (NBA)",
        effective_date: "2002 (Amended 2023)",
        source_url: "http://nbaindia.org/uploaded/act/BiologicalDiversityAct2002.pdf",
        text: "No person shall apply for any intellectual property right, by whatever name called, in or outside India for any invention based on any research or information on a biological resource obtained from India, without obtaining the previous approval of the National Biodiversity Authority before making such application.",
      },
      {
        id: "ev_abs_2",
        jurisdiction: "India",
        legal_domain: "Biodiversity / ABS",
        document_name: "The Biological Diversity Act, 2002",
        section: "Section 7",
        authority: "National Biodiversity Authority (NBA)",
        effective_date: "2002",
        source_url: "http://nbaindia.org/uploaded/act/BiologicalDiversityAct2002.pdf",
        text: "No person, who is a citizen of India or a body corporate, association or organisation which is registered in India, shall obtain any biological resource for commercial utilisation, or bio-survey and bio-utilisation for commercial utilisation except after giving prior intimation to the State Biodiversity Board concerned.",
      },
    ],
  },
  regulatory: {
    jurisdiction: "India",
    pathway: "AYUSH / Proprietary Ayurvedic Medicine (ASU Drug)",
    steps: [
      {
        step_number: 1,
        title: "Standardization & Identity Verification",
        authority: "Pharmacopoeia Commission for Indian Medicine & Homoeopathy (PCIM&H)",
        description:
          "Verify botanical identity of Withania somnifera according to the Ayurvedic Pharmacopoeia of India (API) monographs (TLC/HPLC fingerprinting, heavy metal limits, pesticide residue compliance).",
        requirements: ["Herbarium authentication", "API monograph compliance"],
      },
      {
        step_number: 2,
        title: "Proof of Safety & Efficacy under Rule 158B",
        authority: "State AYUSH Licensing Authority / Ministry of AYUSH",
        description:
          "Because novel extraction techniques alter the chemical profile compared to classical extracts, Rule 158B of the Drugs and Cosmetics Rules, 1945 mandates safety profile submission (acute toxicity) and pilot clinical trial evidence or published medical literature.",
        requirements: [
          "Acute oral toxicity studies",
          "Published pharmacological data or clinical trial report",
        ],
      },
      {
        step_number: 3,
        title: "Manufacturing License in GMP Compliant Unit (Schedule T)",
        authority: "State Licensing Authority (ASU Drugs)",
        description:
          "Application on Form 24D for grant of a license to manufacture Proprietary Ayurvedic medicines in a facility adhering strictly to Good Manufacturing Practices (Schedule T).",
        requirements: ["Form 24D filing", "Schedule T compliance audit", "Approved technical staff approval"],
      },
      {
        step_number: 4,
        title: "Labelling and Packaging Compliance",
        authority: "Central Drugs Standard Control Organisation (CDSCO) / AYUSH",
        description:
          "Adhere to Rule 161 of Drugs & Cosmetics Rules: displaying true list of active ingredients, Ayurvedic text references or botanical names, batch number, and manufacturing date.",
        requirements: ["Rule 161 labelling compliance", "Caution warnings for ASU scheduled drugs"],
      },
    ],
    evidence: [
      {
        id: "ev_reg_1",
        jurisdiction: "India",
        legal_domain: "AYUSH / Drug",
        document_name: "The Drugs and Cosmetics Rules, 1945",
        section: "Rule 158B",
        authority: "Central Drugs Standard Control Organisation (CDSCO) & Ministry of AYUSH",
        effective_date: "Inserted by G.S.R. 512(E)",
        source_url:
          "https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/acts_rules/Drugs_and_Cosmetics_Rules_1945.pdf",
        text: "Guidelines for issue of license with respect to patent or proprietary Ayurvedic, Siddha or Unani medicine. The safety and efficacy data shall be submitted based on classical text references, published literature, or safety studies including acute toxicity and clinical study evidence.",
      },
      {
        id: "ev_reg_2",
        jurisdiction: "India",
        legal_domain: "AYUSH / Drug",
        document_name: "The Drugs and Cosmetics Rules, 1945",
        section: "Schedule T",
        authority: "Central Drugs Standard Control Organisation (CDSCO)",
        effective_date: "1945 (as amended)",
        source_url:
          "https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/acts_rules/Drugs_and_Cosmetics_Rules_1945.pdf",
        text: "Good Manufacturing Practices (GMP) for manufacture of Ayurvedic, Siddha and Unani Medicines: covers infrastructure, hygienic conditions, batch records, quality control laboratory, and qualified technical staff.",
      },
    ],
  },
  verification: {
    total_claims: 4,
    supported_claims: 3,
    partially_supported_claims: 1,
    unsupported_claims: [],
    items: [
      {
        claim_id: "claim_ash_1",
        claim:
          "Novel extraction techniques on Withania somnifera may potentially be evaluated for process patent claims.",
        status: "partially_supported",
        score: 0.79,
        best_evidence_id: "ev_pat_1",
        explanation:
          "Process patents are permissible under Patents Act Section 2(1)(j), but Section 3(p) restricts claims directly deriving from traditional medicinal knowledge without demonstrable technological novelty.",
        evidence_snippet:
          "The Patents Act, 1970 - Section 3(p): ...an invention which in effect, is traditional knowledge...",
        source_document: "The Patents Act, 1970",
        source_section: "Section 3(p)",
      },
      {
        claim_id: "claim_ash_2",
        claim:
          "Prior approval from the National Biodiversity Authority (NBA) is statutory before obtaining a patent on an Indian biological resource.",
        status: "supported",
        score: 0.96,
        best_evidence_id: "ev_abs_1",
        explanation: "Directly verified against Section 6(1) of the Biological Diversity Act, 2002.",
        evidence_snippet:
          "No person shall apply for any intellectual property right... without obtaining the previous approval of the National Biodiversity Authority...",
        source_document: "The Biological Diversity Act, 2002",
        source_section: "Section 6(1)",
      },
      {
        claim_id: "claim_ash_3",
        claim:
          "Proprietary Ayurvedic formulations require safety and efficacy data under Rule 158B before license grant.",
        status: "supported",
        score: 0.94,
        best_evidence_id: "ev_reg_1",
        explanation:
          "Rule 158B of Drugs and Cosmetics Rules, 1945 explicitly governs proprietary ASU drugs requiring pilot studies or published literature.",
        evidence_snippet:
          "Guidelines for issue of license with respect to patent or proprietary Ayurvedic medicine... safety and efficacy data shall be submitted...",
        source_document: "The Drugs and Cosmetics Rules, 1945",
        source_section: "Rule 158B",
      },
      {
        claim_id: "claim_ash_4",
        claim: "Manufacture must take place in an authorized Schedule T GMP-certified facility.",
        status: "supported",
        score: 0.95,
        best_evidence_id: "ev_reg_2",
        explanation:
          "Schedule T establishes the mandatory Good Manufacturing Practices for ASU drugs in India.",
        evidence_snippet:
          "Good Manufacturing Practices (GMP) for manufacture of Ayurvedic, Siddha and Unani Medicines...",
        source_document: "The Drugs and Cosmetics Rules, 1945",
        source_section: "Schedule T",
      },
    ],
  },
  confidence: {
    score: 87,
    level: "HIGH",
    signals: {
      retrieval_quality: 90,
      source_authority: 95,
      claim_support: 82,
      jurisdiction_match: 100,
    },
  },
  abstain: false,
  expert_escalation: {
    recommended: true,
    reason:
      "Drafting patent claims on modified botanical extracts requires overcoming Section 3(p) TKDL citations and navigating NBA Form III filing timelines with a registered patent agent.",
    key_questions_for_counsel: [
      "Can we formulate method-of-manufacture claims that clearly differentiate the solvent yield from traditional Kwatha preparations to satisfy Section 3(p)?",
      "What is the recommended timing for NBA Form III submission relative to the Indian provisional patent application?",
      "Does the State AYUSH Licensing Authority in our manufacturing state require Phase II clinical trial data or will published animal toxicity suffice under Rule 158B?",
    ],
  },
};

/**
 * -----------------------------------------------------------------------------------
 * SCENARIO 2: Classical Formulation — Triphala Churna
 * Category: Classical Ayurvedic Medicine
 * Key traits: Strict adherence to Sharangadhara Samhita, Section 3(p) absolute patent bar,
 * Section 40 NTAC commodity list, Exemption from Rule 158B clinical trials.
 * -----------------------------------------------------------------------------------
 */
export const MOCK_TRIPHALA_ROADMAP: FinalRoadmapResponse = {
  classification: {
    category: "Classical Ayurvedic Medicine",
    reason:
      "The formulation comprises Haritaki (Terminalia chebula), Bibhitaki (Terminalia bellirica), and Amalaki (Phyllanthus emblica) in equal proportions, prepared in exact accordance with Sharangadhara Samhita (Madhyama Khanda), an authoritative treatise listed in the First Schedule of the Drugs and Cosmetics Act, 1940. Because no modification or novel extraction is introduced, it is classified as a Classical Ayurvedic Medicine under Section 3(a).",
    confidence: 0.96,
  },
  ip: {
    analysis:
      "The product is an exact classical Ayurvedic formulation and is strictly non-patentable under Section 3(p) of The Patents Act, 1970 as traditional knowledge. The Indian Patent Office (IPO), backed by exhaustive citations from the Traditional Knowledge Digital Library (TKDL), uniformly rejects attempts to monopolize classical ASU recipes or obvious herbal combinations with known therapeutic uses. Intellectual Property strategy should focus on brand protection through Trademark Law rather than patenting.",
    flags: [
      "Section 3(p) Traditional Knowledge Bar (Absolute Exclusion)",
      "TKDL Documented Prior-Art",
      "No Patentable Subject Matter (Public Domain Knowledge)",
      "Trademark Protection Recommended",
    ],
    patentability_considerations: [
      "Classical Ayurvedic formulations are in the public domain and cannot be patented under Indian law.",
      "Any patent application would face immediate Section 3(p) objections referencing Charaka Samhita, Sushruta Samhita, and Sharangadhara Samhita.",
      "Innovators should focus on trademark registration for the proprietary brand name under the Trade Marks Act, 1999.",
    ],
    traditional_knowledge_flags: [
      "Triphala is comprehensively documented in TKDL with thousands of classical citations for deepana, pachana, and rasayana properties.",
      "CSIR and IPO treat classical Triphala as canonical prior art worldwide.",
    ],
    evidence: [
      {
        id: "ev_pat_triphala_1",
        jurisdiction: "India",
        legal_domain: "Patent",
        document_name: "The Patents Act, 1970",
        section: "Section 3(p)",
        authority: "Indian Patent Office (IPO) / India Code",
        effective_date: "Consolidated 2005",
        source_url:
          "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_31_1_patent-act-1970-11march2015.pdf",
        text: "The following are not inventions within the meaning of this Act: (p) an invention which in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components.",
      },
      {
        id: "ev_pat_triphala_2",
        jurisdiction: "India",
        legal_domain: "Patent",
        document_name: "The Drugs and Cosmetics Act, 1940",
        section: "First Schedule",
        authority: "Ministry of AYUSH / India Code",
        effective_date: "1940 (Consolidated)",
        source_url: "https://indiacode.nic.in",
        text: "The First Schedule lists authoritative books of Ayurvedic, Siddha and Unani Tibb systems, including Sharangadhara Samhita, Charaka Samhita, Sushruta Samhita, and Sahasrayogam.",
      },
    ],
  },
  abs: {
    applicable: true,
    analysis:
      "The product utilizes Indian biological resources (Terminalia chebula, Terminalia bellirica, and Phyllanthus emblica). However, if purchased as dried fruits from open agricultural mandis under the MoEFCC Normally Traded Commodities (NTAC) notification issued under Section 40 of the Biological Diversity Act, 2002, specific commercial utilization exemptions may apply. Commercial manufacturing companies registered in India must still file an intimation with the State Biodiversity Board (SBB) under Section 7.",
    biological_resource_identified:
      "Terminalia chebula (Haritaki), Terminalia bellirica (Bibhitaki), Phyllanthus emblica (Amalaki)",
    nba_action_items: [
      "Verify whether fruit supplies qualify under MoEFCC Normally Traded as Commodities (NTAC) list under Section 40 of BDA 2002.",
      "Submit prior intimation to the concerned State Biodiversity Board (SBB) under Section 7 for commercial utilization.",
      "No NBA Form III application required because no patent or intellectual property right can be sought for classical recipes.",
    ],
    evidence: [
      {
        id: "ev_abs_triphala_1",
        jurisdiction: "India",
        legal_domain: "Biodiversity / ABS",
        document_name: "The Biological Diversity Act, 2002",
        section: "Section 7",
        authority: "National Biodiversity Authority (NBA)",
        effective_date: "2002",
        source_url: "http://nbaindia.org/uploaded/act/BiologicalDiversityAct2002.pdf",
        text: "Prior intimation to State Biodiversity Board for obtaining biological resource for certain purposes: No person who is a citizen of India or a body corporate registered in India shall obtain biological resources for commercial utilization except after giving prior intimation to the State Biodiversity Board.",
      },
      {
        id: "ev_abs_triphala_2",
        jurisdiction: "India",
        legal_domain: "Biodiversity / ABS",
        document_name: "The Biological Diversity Act, 2002",
        section: "Section 40",
        authority: "Ministry of Environment, Forest and Climate Change (MoEFCC)",
        effective_date: "2002 (as notified)",
        source_url: "http://nbaindia.org/uploaded/act/BiologicalDiversityAct2002.pdf",
        text: "Power of Central Government to exempt certain biological resources normally traded as commodities (NTAC) from the provisions of this Act when traded as commodities.",
      },
    ],
  },
  regulatory: {
    jurisdiction: "India",
    pathway: "AYUSH / Classical Ayurvedic Medicine (Form 25D)",
    steps: [
      {
        step_number: 1,
        title: "Classical Monograph & Pharmacopoeial Compliance",
        authority: "Pharmacopoeia Commission for Indian Medicine & Homoeopathy (PCIM&H)",
        description:
          "Verify that the Triphala Churna ingredients and ratio conform strictly to the Ayurvedic Pharmacopoeia of India (API) Part II monograph and Sharangadhara Samhita.",
        requirements: ["API Part II monograph compliance", "Authentication of dried fruit raw materials"],
      },
      {
        step_number: 2,
        title: "Exemption from Rule 158B Clinical Trial Submissions",
        authority: "State AYUSH Licensing Authority",
        description:
          "Because the product matches an authoritative First Schedule classical treatise exactly, it is statutory exempt from submitting clinical trials, animal toxicity, or safety studies under Rule 158B of Drugs & Cosmetics Rules.",
        requirements: [
          "Citation of Sharangadhara Samhita (Madhyama Khanda)",
          "Declaration of zero modern non-classical excipients",
        ],
      },
      {
        step_number: 3,
        title: "Manufacturing License under Schedule T (Form 25D)",
        authority: "State Licensing Authority (ASU)",
        description:
          "Obtain an Ayurvedic Manufacturing License on Form 25D for Classical Medicines in a factory premises certified for Good Manufacturing Practices (Schedule T).",
        requirements: [
          "Schedule T GMP certified facility",
          "Qualified Ayurvedic technical manufacturing personnel",
        ],
      },
      {
        step_number: 4,
        title: "Rule 161 Classical Labelling Standard",
        authority: "Ministry of AYUSH & CDSCO",
        description:
          "Labels must prominently declare the words 'Ayurvedic Medicine', cite the classical text name ('Sharangadhara Samhita'), list Sanskrit/Hindi and botanical ingredient names, batch number, and retail price.",
        requirements: ["Rule 161 labelling compliance", "Explicit classical text reference on container"],
      },
    ],
    evidence: [
      {
        id: "ev_reg_triphala_1",
        jurisdiction: "India",
        legal_domain: "AYUSH / Drug",
        document_name: "The Drugs and Cosmetics Act, 1940",
        section: "Section 3(a)",
        authority: "Ministry of AYUSH & CDSCO",
        effective_date: "1940 (Consolidated)",
        source_url:
          "https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/acts_rules/Drugs_and_Cosmetics_Act_1940.pdf",
        text: "Ayurvedic, Siddha or Unani drug includes all medicines intended for internal or external use for or in the diagnosis, treatment, mitigation or prevention of disease or disorder in human beings or animals, and manufactured exclusively in accordance with the formulae described in the authoritative books of Ayurvedic, Siddha and Unani Tibb systems specified in the First Schedule.",
      },
      {
        id: "ev_reg_triphala_2",
        jurisdiction: "India",
        legal_domain: "AYUSH / Drug",
        document_name: "The Drugs and Cosmetics Rules, 1945",
        section: "Rule 158B (Clause 1)",
        authority: "Central Drugs Standard Control Organisation (CDSCO)",
        effective_date: "1945 (as amended)",
        source_url:
          "https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/acts_rules/Drugs_and_Cosmetics_Rules_1945.pdf",
        text: "Medicines manufactured strictly in accordance with classical treatises specified in the First Schedule are exempt from pilot clinical trials and animal safety studies required for proprietary patent medicines.",
      },
    ],
  },
  verification: {
    total_claims: 4,
    supported_claims: 4,
    partially_supported_claims: 0,
    unsupported_claims: [],
    items: [
      {
        claim_id: "claim_triphala_1",
        claim: "Classical Triphala Churna cannot be patented in India due to traditional knowledge exclusion.",
        status: "supported",
        score: 0.98,
        best_evidence_id: "ev_pat_triphala_1",
        explanation:
          "Directly supported by Section 3(p) of The Patents Act, 1970, which bans patents on traditional knowledge and classical herbal formulations.",
        evidence_snippet:
          "The Patents Act, 1970 - Section 3(p): ...an invention which in effect, is traditional knowledge...",
        source_document: "The Patents Act, 1970",
        source_section: "Section 3(p)",
      },
      {
        claim_id: "claim_triphala_2",
        claim:
          "Sharangadhara Samhita is a legally recognized authoritative classical text under the Drugs and Cosmetics Act, 1940.",
        status: "supported",
        score: 0.99,
        best_evidence_id: "ev_pat_triphala_2",
        explanation:
          "Verified under the First Schedule of the Drugs & Cosmetics Act, 1940, which lists Sharangadhara Samhita as a canonical Ayurvedic text.",
        evidence_snippet:
          "The First Schedule lists authoritative books of Ayurvedic... including Sharangadhara Samhita.",
        source_document: "The Drugs and Cosmetics Act, 1940",
        source_section: "First Schedule",
      },
      {
        claim_id: "claim_triphala_3",
        claim:
          "Classical formulations are exempt from new clinical trials under Rule 158B of Drugs and Cosmetics Rules.",
        status: "supported",
        score: 0.96,
        best_evidence_id: "ev_reg_triphala_2",
        explanation:
          "Rule 158B explicitly exempts genuine First Schedule classical formulations from pilot clinical trial requirements.",
        evidence_snippet:
          "Medicines manufactured strictly in accordance with classical treatises specified in the First Schedule are exempt...",
        source_document: "The Drugs and Cosmetics Rules, 1945",
        source_section: "Rule 158B (Clause 1)",
      },
      {
        claim_id: "claim_triphala_4",
        claim:
          "Commercial manufacturing requires a Form 25D license in a Schedule T GMP certified facility.",
        status: "supported",
        score: 0.95,
        best_evidence_id: "ev_reg_triphala_1",
        explanation:
          "Under Section 3(a) and Schedule T of the Drugs and Cosmetics Act/Rules, classical ASU manufacture requires GMP compliance.",
        evidence_snippet:
          "Manufacture of Ayurvedic medicines must comply with Schedule T Good Manufacturing Practices...",
        source_document: "The Drugs and Cosmetics Rules, 1945",
        source_section: "Schedule T & Form 25D",
      },
    ],
  },
  confidence: {
    score: 95,
    level: "HIGH",
    signals: {
      retrieval_quality: 96,
      source_authority: 98,
      claim_support: 94,
      jurisdiction_match: 100,
    },
  },
  abstain: false,
  expert_escalation: {
    recommended: false,
    reason:
      "The legal pathway for Classical Triphala Churna is completely standardized and well-settled under Indian drug law. No patent disputes or clinical trial uncertainties exist.",
    key_questions_for_counsel: [
      "Which State AYUSH Licensing Authority provides the most streamlined online Form 25D issuance?",
      "Does bulk procurement of dried fruits from local agricultural mandis require State Biodiversity Board intimation in our specific manufacturing state?",
    ],
  },
};

/**
 * -----------------------------------------------------------------------------------
 * SCENARIO 3: Safe Abstention Demo — Vague / Guaranteed Miracle Claims
 * Category: Unknown / Insufficient Information
 * Key traits: Rule 6 anti-hallucination guard, unsupported claims flagged, low confidence.
 * -----------------------------------------------------------------------------------
 */
export const MOCK_SAFE_ABSTENTION_ROADMAP: FinalRoadmapResponse = {
  classification: {
    category: "Unknown / Insufficient Information",
    reason:
      "The submitted description lacks verifiable botanical identities, textual citations, extraction parameters, or chemical characterization. Claims such as '100% guaranteed cure' and 'fast-track automatic patent' violate statutory legal definitions. In accordance with Rule 6 and Section 22 of the Master Brief, the system safely abstains from fabricating regulatory conclusions.",
    confidence: 0.32,
  },
  ip: {
    analysis:
      "Insufficient technical disclosure regarding chemical composition or inventive step. The system safely abstains from speculative patentability claims. The Patents Act, 1970 strictly excludes unscientific claims or assertions unsupported by written description under Section 10(4).",
    flags: [
      "Insufficient Technical Disclosure",
      "High Speculative Uncertainty",
      "Safe Abstention Active (Rule 6)",
      "Unsubstantiated Patent Claims",
    ],
    patentability_considerations: [
      "No patent application can be filed in India without a provisional or complete specification detailing the best method of performing the invention under Section 10.",
      "Vague assertions of 'miracle cures' violate Section 3(b) (inventions contrary to public order or morality) and Section 3(d).",
    ],
    traditional_knowledge_flags: [
      "Because the herbal components are unidentified, no prior-art search against the TKDL or Ayurvedic treatises can be performed.",
    ],
    evidence: [
      {
        id: "ev_abstain_pat_1",
        jurisdiction: "India",
        legal_domain: "Patent",
        document_name: "The Patents Act, 1970",
        section: "Section 10(4)",
        authority: "Indian Patent Office (IPO)",
        effective_date: "Consolidated 2005",
        source_url: "https://ipindia.gov.in",
        text: "Every complete specification shall fully and particularly describe the invention and its operation or use and the method by which it is to be performed.",
      },
    ],
  },
  abs: {
    applicable: false,
    analysis:
      "Biological taxonomy, geographical harvest origin, and supplier jurisdiction cannot be established from the vague disclosure. No authoritative Access and Benefit Sharing (ABS) determination can be made.",
    biological_resource_identified: "Unspecified / Undetermined Biological Material",
    nba_action_items: [
      "Identify precise scientific botanical genus and species.",
      "Document geographical source in India (state, forest division, or farm) before contacting the State Biodiversity Board.",
    ],
    evidence: [],
  },
  regulatory: {
    jurisdiction: "India",
    pathway: "Pathway Undetermined (Safe Abstention Active)",
    steps: [
      {
        step_number: 1,
        title: "Scientific Clarification & Phytochemical Testing Required",
        authority: "State AYUSH Licensing Authority / CDSCO",
        description:
          "Before any regulatory application can be lodged, the innovator must carry out botanical authentication, heavy metal analysis, and standard pharmacopoeial identification.",
        requirements: ["Botanical authentication certificate", "Certificate of Analysis (CoA)"],
      },
      {
        step_number: 2,
        title: "Prohibition of Misleading Medical Claims",
        authority: "Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954",
        description:
          "Claims of 'guaranteed cure' for chronic diseases violate the Drugs and Magic Remedies Act, 1954. All public therapeutic assertions must be strictly substantiated.",
        requirements: ["Compliance with Drugs & Magic Remedies Act", "Elimination of guaranteed cure claims"],
      },
    ],
    evidence: [
      {
        id: "ev_abstain_dmr_1",
        jurisdiction: "India",
        legal_domain: "AYUSH / Drug",
        document_name: "The Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954",
        section: "Section 3 & Section 4",
        authority: "Ministry of Health & Family Welfare / India Code",
        effective_date: "1954",
        source_url: "https://indiacode.nic.in",
        text: "Prohibition of advertisement of certain drugs for treatment of certain diseases and disorders: No person shall take any part in the publication of any advertisement referring to any drug which suggests or is calculated to lead to the use of that drug for diagnosis, cure, mitigation, treatment or prevention of any disease specified in the Schedule.",
      },
    ],
  },
  verification: {
    total_claims: 2,
    supported_claims: 0,
    partially_supported_claims: 0,
    unsupported_claims: [
      "Guaranteed fast-track patent grant within 3 months for herbal powder.",
      "100% cure for all stress and chronic conditions without clinical trial proof.",
    ],
    items: [
      {
        claim_id: "claim_unsupported_1",
        claim: "Guaranteed fast-track patent grant within 3 months for herbal powder.",
        status: "unsupported",
        score: 0.05,
        explanation:
          "Refuted by The Patents Act, 1970. Indian law offers no automatic guarantee of patent grant. Traditional herbal compositions are strictly barred under Section 3(p).",
        evidence_snippet:
          "No statutory provision provides automatic patent grant without substantive examination.",
        source_document: "The Patents Act, 1970",
        source_section: "Section 3(p) & Section 11B",
      },
      {
        claim_id: "claim_unsupported_2",
        claim: "100% cure for all stress and chronic conditions without clinical trial proof.",
        status: "unsupported",
        score: 0.02,
        explanation:
          "Violates the Drugs & Magic Remedies (Objectionable Advertisements) Act, 1954. Indian law strictly prohibits making guaranteed cure claims for severe conditions without CDSCO/AYUSH clinical validation.",
        evidence_snippet:
          "The Drugs and Magic Remedies Act, 1954 prohibits misleading advertisements guaranteeing disease cures.",
        source_document: "The Drugs and Magic Remedies Act, 1954",
        source_section: "Section 3",
      },
    ],
  },
  confidence: {
    score: 28,
    level: "LOW",
    signals: {
      retrieval_quality: 20,
      source_authority: 40,
      claim_support: 10,
      jurisdiction_match: 50,
    },
  },
  abstain: true,
  abstain_reason:
    "The available authoritative sources do not provide sufficient evidence to confidently determine a commercialization roadmap for this vague description. Safe abstention has been activated in accordance with Rule 6 to prevent hallucinated legal outcomes.",
  expert_escalation: {
    recommended: true,
    reason:
      "The innovation requires structured preliminary scientific disclosure and counsel with an IP/regulatory expert before any official regulatory submissions.",
    key_questions_for_counsel: [
      "What taxonomic identification and phytochemical fingerprinting should be performed first?",
      "Which specific classical or proprietary therapeutic category does the product target?",
      "How to eliminate misleading marketing claims to comply with the Drugs and Magic Remedies Act, 1954?",
    ],
  },
};

/**
 * -----------------------------------------------------------------------------------
 * Dynamic Scenario Selector & Adapter
 * Directly fulfills Requirement 1 & Requirement 2:
 * 1. Responds to selected scenario (Ashwagandha, Triphala, Safe Abstention).
 * 2. Directly passes and adapts based on clarification answers!
 * -----------------------------------------------------------------------------------
 */
export function getMockRoadmapByScenario(payload: AnalyzePayload): FinalRoadmapResponse {
  const { preset_id, innovation_description = "", clarifications = {} } = payload;
  const descLower = innovation_description.toLowerCase();

  let baseRoadmap: FinalRoadmapResponse;

  // 1. Check explicit preset_id or text match
  if (preset_id === "triphala" || descLower.includes("triphala") || clarifications.classical_heritage === "classical_exact") {
    baseRoadmap = JSON.parse(JSON.stringify(MOCK_TRIPHALA_ROADMAP));
  } else if (
    preset_id === "abstention" ||
    descLower.includes("guaranteed") ||
    descLower.includes("100%") ||
    descLower.includes("miracle") ||
    descLower.includes("cure anything") ||
    (descLower.length < 25 && !descLower.includes("ashwagandha"))
  ) {
    baseRoadmap = JSON.parse(JSON.stringify(MOCK_SAFE_ABSTENTION_ROADMAP));
  } else {
    // Default to Canonical Ashwagandha
    baseRoadmap = JSON.parse(JSON.stringify(MOCK_ASHWAGANDHA_ROADMAP));
  }

  // 2. Adapt dynamically based on the clarification answers
  // Biological Resources Answer:
  if (clarifications.biological_resources === "synthetic_or_imported") {
    baseRoadmap.abs.applicable = false;
    baseRoadmap.abs.analysis =
      "Because the innovator indicated purely synthetic or imported foreign biological material, the provisions of the Biological Diversity Act, 2002 regarding Indian indigenous biological resources are not triggered.";
    baseRoadmap.abs.nba_action_items = [
      "Maintain customs import bills of entry to document foreign biological material provenance.",
      "Verify that foreign biological materials comply with relevant CITES and DGFT import permissions.",
    ];
  } else if (clarifications.biological_resources === "value_added_commercial_commodity") {
    baseRoadmap.abs.applicable = true;
    baseRoadmap.abs.analysis +=
      " (Note: Procured as value-added commercial commodity; verify specific Section 40 NTAC exemptions with State Biodiversity Board).";
  }

  // Intended Use Answer:
  if (clarifications.intended_use === "supplement_food") {
    baseRoadmap.regulatory.pathway = "FSSAI / Health Supplement & Nutraceutical (Regulations 2016)";
    baseRoadmap.classification.category = "Nutraceutical";
    baseRoadmap.regulatory.steps = [
      {
        step_number: 1,
        title: "Schedule Schedule I / II Ingredient Verification",
        authority: "Food Safety and Standards Authority of India (FSSAI)",
        description:
          "Confirm botanical ingredients are listed under Schedule I (Essential Nutrients) or Schedule II (Plants/Botanicals) of FSSAI Nutraceutical Regulations 2016.",
        requirements: ["Schedule II botanical compliance", "Standard daily allowance limits"],
      },
      {
        step_number: 2,
        title: "FSSAI Central Food Manufacturing License",
        authority: "FSSAI FoSCoS Portal",
        description:
          "Obtain an FSSAI Central License under Category 13 (Foodstuffs intended for particular nutritional uses) in a Food Safety and Standards certified unit.",
        requirements: ["FoSCoS Central License", "HACCP & GMP compliance"],
      },
      {
        step_number: 3,
        title: "FSSAI Labelling & Disclaimer Compliance",
        authority: "FSSAI",
        description:
          "Mandatory display: 'NOT FOR MEDICINAL USE', nutritional facts table, and health claim limits in accordance with Food Safety Regulations.",
        requirements: ["'NOT FOR MEDICINAL USE' statement", "True nutritional panel"],
      },
    ];
  } else if (clarifications.intended_use === "cosmetic_external") {
    baseRoadmap.classification.category = "Cosmetic";
    baseRoadmap.regulatory.pathway = "CDSCO / Cosmetics Rules, 2020";
  }

  return baseRoadmap;
}
