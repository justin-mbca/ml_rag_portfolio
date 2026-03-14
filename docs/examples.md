# Example Queries and Outputs

This document shows representative queries and the platform's responses, illustrating how each agent and retrieval method works.

---

## 1. Compliance Query (AML Regulations)

**Query:**
```
What are the key compliance risks related to AML regulations?
```

**API Request:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key compliance risks related to AML regulations?",
    "agent": "compliance_agent",
    "retrieval_method": "hybrid"
  }'
```

**Response:**
```json
{
  "answer": "The key compliance risks related to Anti-Money Laundering (AML) regulations include:\n\n1. **Customer Due Diligence (CDD) failures** – Inadequate identification and verification of customers, particularly high-risk individuals and Politically Exposed Persons (PEPs).\n2. **Suspicious Activity Reporting (SAR) deficiencies** – Failure to detect, investigate, and report suspicious transactions within required timeframes.\n3. **Transaction monitoring gaps** – Insufficient automated systems to detect structuring, layering, or integration of illicit funds.\n4. **Sanctions screening failures** – Not screening against OFAC, EU, and UN sanctions lists in real-time.\n5. **Correspondent banking exposure** – Risk of processing transactions for foreign banks with weaker AML controls.",
  "sources": [
    {"filename": "AML_Policy_2024.pdf", "page": 3, "relevance_score": 0.94},
    {"filename": "BSA_Compliance_Guide.pdf", "page": 12, "relevance_score": 0.89}
  ],
  "retrieval_method": "hybrid",
  "agent": "compliance_agent",
  "latency_ms": 1240
}
```

---

## 2. Capital Requirements (Basel III)

**Query:**
```
Summarise the Basel III capital requirements for Tier 1 capital.
```

**Response:**
```json
{
  "answer": "Basel III mandates the following Tier 1 capital requirements:\n\n- **Common Equity Tier 1 (CET1)**: Minimum 4.5% of Risk-Weighted Assets (RWA)\n- **Tier 1 Capital**: Minimum 6% of RWA\n- **Capital Conservation Buffer**: Additional 2.5% CET1, bringing the effective CET1 minimum to 7%\n- **Countercyclical Buffer**: 0–2.5% of RWA, set by national regulators\n- **G-SIB Surcharge**: Additional 1–3.5% for Global Systemically Important Banks",
  "sources": [
    {"filename": "Basel_III_Framework.pdf", "page": 7},
    {"filename": "Capital_Requirements_Policy_Internal.pdf", "page": 2}
  ],
  "retrieval_method": "vector",
  "agent": "retrieval_agent"
}
```

---

## 3. Risk Analysis Report

**Query:**
```
Generate a risk analysis report for our credit portfolio exposure to commercial real estate.
```

**Response:**
```json
{
  "report": {
    "title": "Credit Portfolio Risk Analysis – Commercial Real Estate Exposure",
    "date": "2024-01-15",
    "executive_summary": "The commercial real estate (CRE) portfolio represents 18.4% of total loan exposure. Current risk indicators suggest elevated concentration risk driven by rising interest rates and declining office occupancy rates.",
    "risk_categories": {
      "concentration_risk": "HIGH",
      "credit_risk": "MEDIUM-HIGH",
      "market_risk": "MEDIUM",
      "liquidity_risk": "LOW"
    },
    "key_findings": [
      "Office sector loans account for 42% of CRE exposure with average LTV of 68%",
      "12 loans totalling $340M are on the watchlist due to covenant breaches",
      "Stress scenario (20% CRE value decline) would require $45M additional provisions"
    ],
    "recommendations": [
      "Reduce new originations in office sector",
      "Increase loan loss reserves by 15 basis points",
      "Conduct enhanced monitoring for loans maturing within 12 months"
    ]
  },
  "retrieval_method": "hybrid",
  "agent": "report_agent"
}
```

---

## 4. Document Search

**Query:**
```
Find all policies related to GDPR data subject rights.
```

**Response:**
```json
{
  "documents": [
    {
      "title": "Data Privacy Policy v3.2",
      "filename": "data_privacy_policy_v3.2.pdf",
      "relevance_score": 0.97,
      "excerpt": "Section 4.2 – Data Subject Rights: Customers have the right to access, rectify, erase, restrict processing, and port their personal data..."
    },
    {
      "title": "GDPR Compliance Framework",
      "filename": "gdpr_compliance_framework.pdf",
      "relevance_score": 0.93,
      "excerpt": "Article 17 Right to Erasure ('Right to be Forgotten'): The bank must respond to erasure requests within 30 days..."
    }
  ],
  "total_results": 2,
  "retrieval_method": "vector"
}
```

---

## 5. Graph-based Regulatory Relationship Query

**Query:**
```
What regulations are connected to the Basel III framework?
```

**Response:**
```json
{
  "answer": "The following regulations are directly connected to Basel III in the knowledge graph:\n\n- **CRD IV / CRR** (EU Capital Requirements Directive / Regulation) – EU implementation of Basel III\n- **Dodd-Frank Act** – US regulatory response with complementary capital requirements\n- **FRTB** (Fundamental Review of the Trading Book) – Basel III market risk reform\n- **NSFR** (Net Stable Funding Ratio) – Liquidity standard under Basel III\n- **LCR** (Liquidity Coverage Ratio) – Short-term liquidity standard\n- **SRMR** (Single Resolution Mechanism Regulation) – EU bank resolution framework",
  "graph_nodes": 6,
  "graph_edges": 9,
  "retrieval_method": "graph",
  "agent": "retrieval_agent"
}
```

---

## 6. Multi-step Reasoning (Agentic Workflow)

**Query:**
```
What are the capital implications if our CET1 ratio falls below 7%?
```

**Agent Reasoning Steps:**
```
Step 1 [retrieval_agent]: Search capital requirements policies → Found Basel III CET1 thresholds
Step 2 [compliance_agent]: Identify regulatory triggers at 7% CET1 → Capital Conservation Buffer breach
Step 3 [report_agent]: Calculate dividend restriction ratios → 40% maximum distribution
Step 4 [report_agent]: Generate structured response with implications
```

**Response:**
```json
{
  "answer": "If your CET1 ratio falls below 7% (breaching the Capital Conservation Buffer), the following restrictions apply:\n\n1. **Dividend restrictions**: Maximum payout ratio limited to 40% of earnings\n2. **Share buyback restrictions**: Share repurchases may be prohibited\n3. **Bonus cap**: Discretionary bonuses are restricted\n4. **Regulatory notification**: Supervisor must be notified within 5 business days\n5. **Capital restoration plan**: A plan to restore capital must be submitted within 30 days",
  "agent_steps": 4,
  "retrieval_method": "hybrid",
  "agent": "multi_agent"
}
```
