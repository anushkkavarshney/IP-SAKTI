# IP-SAKTI Navigator — Frontend (Member 1)

**SIH 2026 · Problem Statement SIH26045**

AI-powered decision-support platform for Ayurvedic innovators that converts a plain-language innovation description into an evidence-backed IP, biodiversity/ABS, and regulatory commercialization roadmap.

---

## Member 1 Responsibilities Delivered
1. **Landing Page (`LandingHero.tsx`)**: Value proposition, 4 architectural pillars, and authoritative Indian statutory corpus badges (IPO, NBA, CDSCO, AYUSH, FSSAI).
2. **Innovation Input Page (`InnovationInput.tsx`)**: Plain-language input with preset scenario buttons (Canonical Section 49 Ashwagandha demo, Classical Triphala, Safe Abstention test).
3. **4–5 Question Clarification Wizard (`ClarificationWizard.tsx`)**: Targeted multi-step clarification flow analyzing intended therapeutic use, classical heritage, novelty of extraction, biological resources, and India jurisdiction.
4. **Analyze Button & Multi-Stage Loading State (`PipelineLoader.tsx`)**: 6-stage animated pipeline illustrating classification, routing, hybrid retrieval, grounded reasoning, claim verification, and confidence scoring.
5. **Final Roadmap Dashboard (`RoadmapDashboard.tsx`)**:
   - Formulation Classification (Category, reason, confidence)
   - IP & Patentability Module (Section 3(p) Traditional Knowledge scrutiny, Section 3(e) mere admixture bar)
   - Biodiversity & ABS Module (Biological Diversity Act 2002, Section 6 NBA approval, Section 7 SBB notice)
   - Regulatory Roadmap (AYUSH proprietary drug steps, Rule 158B safety proof, Schedule T GMP)
   - Export dossier (JSON download) and printable summary
6. **Independent Claim Verification (`ClaimVerificationTable.tsx`)**: Evaluates individual assertions into `SUPPORTED`, `PARTIALLY_SUPPORTED`, and `UNSUPPORTED`, quarantining unsupported statements.
7. **Evidence & Citations Drawer (`EvidenceDrawer.tsx`)**: Full Section 15 metadata displays with official gazette source links and verbatim quotes.
8. **Evidence-Based Confidence Engine (`ConfidenceCard.tsx`)**: Visual display of the 4 formulaic signals (30% Retrieval + 25% Authority + 25% Claim Support + 20% Jurisdiction).
9. **Safe Abstention Banner**: Visible when evidence is weak or ungrounded claims are detected (Rule 6).
10. **Human Expert Escalation Brief**: Structured case dossier with targeted counsel questions (Section 23).

---

## Tech Stack
- **Framework**: Next.js (App Router)
- **UI & State**: React, TypeScript
- **Styling**: Tailwind CSS, shadcn-inspired modular design
- **Icons**: Lucide React
- **API Client**: Fetch / Axios compatible (`src/lib/api.ts`)

---

## How to Run the Frontend

### 1. Install Dependencies (Already Completed)
```bash
cd frontend
npm install
```

### 2. Configure Environment (Optional)
If connecting to Member 2's FastAPI backend:
```bash
# Create .env.local
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
```
*Note: If the backend is not running, the frontend automatically functions in **Standalone / Demo Mode**, providing full access to all verified scenarios without errors.*

### 3. Run Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production
```bash
npm run build
npm run start
```
