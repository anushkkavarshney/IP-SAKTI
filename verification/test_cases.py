"""
Synthetic Day 1 test cases for claim-to-evidence semantic matching.

IMPORTANT:
Every evidence passage here is SYNTHETIC / DEMO TEXT.
These are NOT official Indian statutes, rules, notifications, or citations.
Member 4 will later supply the real authoritative legal corpus.

Expected labels are for semantic-matching evaluation only.
They do NOT mean a claim is legally true, proven, or verified.
"""

SYNTHETIC_SOURCE = "SYNTHETIC DEMO — not an official legal source"

TEST_CASES = [
    {
        "id": "tc01_supported_biological_resource",
        "claim": "The innovation may involve a biological resource.",
        "evidence": [
            {
                "text": "The innovation may involve a biological resource if it uses plants, animals, microorganisms, or parts of them.",
                "document": "SYNTHETIC DEMO — Biodiversity overview notes",
                "section": "demo-overview",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "Cosmetic labelling should list ingredients in a manner that consumers can understand.",
                "document": "SYNTHETIC DEMO — Cosmetic labelling notes",
                "section": "demo-labelling",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "supported",
    },
    {
        "id": "tc02_supported_patent_process",
        "claim": "A new extraction process may warrant further patentability assessment.",
        "evidence": [
            {
                "text": "A novel extraction or manufacturing process that is not already known may be considered for further patentability assessment by a qualified professional.",
                "document": "SYNTHETIC DEMO — Patent process notes",
                "section": "demo-process",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "supported",
    },
    {
        "id": "tc03_supported_food_supplement_path",
        "claim": "A product intended as a food supplement may follow a food-safety regulatory path rather than a medicine path.",
        "evidence": [
            {
                "text": "If a product is intended as a food or health supplement rather than a medicine, a food-safety regulatory pathway may be more relevant than a drug pathway.",
                "document": "SYNTHETIC DEMO — Food supplement pathway notes",
                "section": "demo-food-path",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "Patent drawings should be clear enough for a person skilled in the art to understand the invention.",
                "document": "SYNTHETIC DEMO — Patent drawing notes",
                "section": "demo-drawings",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "supported",
    },
    {
        "id": "tc04_supported_expert_review",
        "claim": "Human expert review may be required when the available evidence is insufficient.",
        "evidence": [
            {
                "text": "Human expert review may be required when the available evidence is insufficient to support a confident conclusion.",
                "document": "SYNTHETIC DEMO — Escalation notes",
                "section": "demo-escalation",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "supported",
    },
    {
        "id": "tc05_partial_abs_flag",
        "claim": "Access and benefit sharing may need to be reviewed because the formulation uses a plant material.",
        "evidence": [
            {
                "text": "Biological resources obtained from plants may raise biodiversity-related questions that should be reviewed separately from product labelling rules.",
                "document": "SYNTHETIC DEMO — Plant material notes",
                "section": "demo-plant",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "A product label may include usage instructions and storage conditions.",
                "document": "SYNTHETIC DEMO — General labelling notes",
                "section": "demo-label",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "partially_supported",
    },
    {
        "id": "tc06_partial_ayurvedic_classification",
        "claim": "The product may be a proprietary Ayurvedic medicine rather than a classical formulation.",
        "evidence": [
            {
                "text": "Ayurvedic products can differ depending on whether they follow a traditional recipe or a newly designed combination of ingredients.",
                "document": "SYNTHETIC DEMO — Formulation type notes",
                "section": "demo-formulation-type",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "Warehouse temperature logs help manufacturing teams track storage conditions.",
                "document": "SYNTHETIC DEMO — Warehouse notes",
                "section": "demo-warehouse",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "partially_supported",
    },
    {
        "id": "tc07_partial_tk_prior_art",
        "claim": "Traditional knowledge may be relevant as a prior-art consideration for this formulation.",
        "evidence": [
            {
                "text": "Long-standing traditional uses of herbs may be considered when assessing whether an idea is already known, but this demo note does not complete a prior-art search.",
                "document": "SYNTHETIC DEMO — Traditional use notes",
                "section": "demo-tk",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "partially_supported",
    },
    {
        "id": "tc08_partial_cosmetic_path",
        "claim": "If the product is intended only to improve skin appearance, a cosmetic pathway may be more relevant than a medicine pathway.",
        "evidence": [
            {
                "text": "Skin-care products are grouped by intended use. Appearance-related use is one of several possible uses discussed in this demo note.",
                "document": "SYNTHETIC DEMO — Cosmetic vs medicine notes",
                "section": "demo-cosmetic",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "Export invoices should record the quantity and destination of shipped goods.",
                "document": "SYNTHETIC DEMO — Export invoice notes",
                "section": "demo-export",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "partially_supported",
    },
    {
        "id": "tc09_unsupported_irrelevant_labelling",
        "claim": "The described extraction process may warrant further patentability assessment.",
        "evidence": [
            {
                "text": "A product package should remain sealed until first use so that the contents stay clean.",
                "document": "SYNTHETIC DEMO — Packaging hygiene notes",
                "section": "demo-packaging",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "Office meeting rooms should be booked in advance during busy weeks.",
                "document": "SYNTHETIC DEMO — Office booking notes",
                "section": "demo-office",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "unsupported",
    },
    {
        "id": "tc10_unsupported_wrong_topic",
        "claim": "ABS considerations may arise because the innovation uses a biological resource.",
        "evidence": [
            {
                "text": "Printer toner should be replaced when print quality becomes faint.",
                "document": "SYNTHETIC DEMO — Office supplies notes",
                "section": "demo-printer",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "unsupported",
    },
    {
        "id": "tc11_unsupported_multiple_weak",
        "claim": "The innovation may require review of biodiversity-related obligations.",
        "evidence": [
            {
                "text": "Team lunch menus should include at least one vegetarian option.",
                "document": "SYNTHETIC DEMO — Cafeteria notes",
                "section": "demo-cafeteria",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "A bicycle helmet should fit snugly and remain fastened while riding.",
                "document": "SYNTHETIC DEMO — Safety gear notes",
                "section": "demo-helmet",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "Library books should be returned before the due date.",
                "document": "SYNTHETIC DEMO — Library notes",
                "section": "demo-library",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "unsupported",
    },
    {
        "id": "tc12_supported_best_of_several",
        "claim": "India is the jurisdiction being considered for this MVP analysis.",
        "evidence": [
            {
                "text": "India is the jurisdiction being considered for this MVP analysis, so rules from other countries should not be mixed into the same answer.",
                "document": "SYNTHETIC DEMO — Jurisdiction notes",
                "section": "demo-jurisdiction",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "A shipping container should be inspected for damage before loading.",
                "document": "SYNTHETIC DEMO — Shipping notes",
                "section": "demo-shipping",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "Rainfall measurements are useful for agricultural planning.",
                "document": "SYNTHETIC DEMO — Weather notes",
                "section": "demo-weather",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "supported",
    },
    {
        "id": "tc13_partial_weakly_related_ip",
        "claim": "Some part of the innovation may involve intellectual property considerations.",
        "evidence": [
            {
                "text": "Innovators sometimes document how a process was developed so that later professional review of novelty is easier.",
                "document": "SYNTHETIC DEMO — Innovation documentation notes",
                "section": "demo-docs",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
            {
                "text": "A kitchen timer can help avoid overcooking vegetables.",
                "document": "SYNTHETIC DEMO — Kitchen notes",
                "section": "demo-kitchen",
                "jurisdiction": "India",
                "source": SYNTHETIC_SOURCE,
            },
        ],
        "expected": "partially_supported",
    },
]
