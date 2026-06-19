---
last_reviewed: 2026-06-12
---

# HDS — Hébergeur de Données de Santé

**Regulatory framework**: French health code (Code de la santé publique) + RGPD
**MOC**: [MOC Méta-Coaching](../mocs/MOC_Metacoaching.md)

---

## Definition

French state certification (accreditation) for organizations that host health-related personal data on behalf of healthcare producers or health IT companies. Mandatory under French law when storing, processing, or transmitting personal health data (données de santé à caractère personnel).

An organization must be certified HDS by an accredited body (ANS — Agence du Numérique en Santé) before it can legally host patient health data in France.

---

## Relevance to Méta-Coaching

[Méta-Coaching](../entities/Metacoaching.md) collects highly sensitive user data: BMI, eating habits, sleep architecture, anxiety levels, addictive behaviors. To comply with RGPD and the health code, all this data is hosted by [Cegedim](../entities/Cegedim.md), a certified HDS provider.

---

## Hard Constraint for Automation

**Any Make.com scenario or Claude API integration must not route identifiable patient data outside the Cegedim HDS perimeter.**

Automation is scoped to:
- ✅ Aggregated/anonymized KPIs
- ✅ Insurer reporting (non-patient-level)
- ✅ Email management (operational, not clinical)
- ✅ Back-office workflows
- ❌ Individual patient data, clinical records, session content

---

## Related Concepts

- [ADELI & Remboursement](ADELI_Remboursement.md) — psychologist registration and reimbursement framework
- [Modèle Phygital](Modele_Phygital.md) — delivery model that touches patient data

---

## Sources

- [Analyse Stratégique Méta-Coaching (2026-06-12)](../syntheses/research/2026-06-12_analyse-strategique-metacoaching.md)
