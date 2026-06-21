# Pitch Commercial — Architecture Hybride IA pour Méta-Coaching

**Fabien Riou · Consultant IA & Automatisation**
**Version** : 1.0 · Juin 2026

---

## Le probleme (en 30 secondes)

Méta-Coaching, c'est **10 programmes cliniques**, **7+ assureurs partenaires**, **10-19 collaborateurs**, et une masse croissante de données : études cliniques, KPIs, reportings, protocoles TCC, propositions commerciales.

Aujourd'hui, cette connaissance est **dispersée** :

| Symptome | Impact |
|---|---|
| Un collaborateur cherche les résultats cliniques ThéraSomnia pour un pitch MGEN | → 45 min à fouiller des PDF, ou copie-colle 200 pages dans ChatGPT (coût : 3-5€ par requête, réponse dégradée) |
| Le reporting mensuel AXA est préparé manuellement | → 1-2 jours/mois de travail répétitif |
| Un nouveau collaborateur a une question sur le process ADELI | → Personne ne sait exactement, l'info est dans la tête de 2 personnes |
| Anne-Dominique veut comparer les taux de rétention entre programmes | → Les données existent mais personne ne sait les croiser vite |

**Le coût caché** : on estime cette "taxe d'amnésie organisationnelle" à **5-10h/semaine** d'inefficacité cumulée dans l'équipe. A 50€/h chargé, c'est **1 000 à 2 000€/mois** qui s'évaporent.

---

## La solution (en 60 secondes)

Un **cerveau collectif privé** qui sait tout ce que Méta-Coaching sait — mais sans jamais envoyer de données patients dans le cloud.

### Comment ca marche (pour un non-technique) :

1. **Vous posez une question** — par Slack, par email, ou via une interface web simple
2. **Le système cherche instantanément** dans toute la base MC — en 5 millisecondes, pas en 45 minutes
3. **Un agent IA spécialisé** lit les 2-3 documents pertinents (pas les 500) et formule la réponse
4. **Vous recevez une réponse sourcée** — avec les références exactes, vérifiables

### Ce que ca change concrètement :

| Avant | Après |
|---|---|
| "Quels résultats cliniques pour ThéraSomnia ?" → 45 min de recherche | → 10 secondes, réponse sourcée avec les 3 stats clés |
| Reporting AXA → 1-2 jours manuels | → Généré automatiquement, vérifié en 30 min |
| "Comment fonctionne le remboursement ADELI ?" → "Demande à Marie" | → Réponse immédiate avec le process documenté |
| Pitch nouvel assureur → 3h de préparation | → 20 min : l'IA prépare le draft avec preuves cliniques + métriques |

---

## Pourquoi cette approche et pas ChatGPT / un chatbot standard ?

### 3 raisons non négociables pour Méta-Coaching :

**1. HDS/RGPD — Vos données restent chez vous**

Méta-Coaching manipule des données de santé (BMI, habitudes alimentaires, insomnie, anxiété) hébergées chez Cegedim (HDS). Un chatbot cloud comme ChatGPT Teams ou Notion AI enverrait potentiellement ces données sur des serveurs américains → **non-conformité légale immédiate**.

Notre solution : **le moteur de recherche tourne en local**, sur un serveur français ou sur l'infra MC. Seule la reformulation finale passe par l'API Claude (Anthropic), et elle ne contient que des données agrégées/anonymisées.

**2. Performance — 95% de bruit en moins**

Un RAG classique (ChatGPT + fichiers uploadés) envoie TOUT le contenu à l'IA — y compris les mentions légales, les pages de garde, les doublons. Résultat : réponses vagues, hallucinations fréquentes, coût explosif.

Notre solution : un **filtre hybride** (mots-clés + compréhension sémantique) isole les 2-3 documents pertinents parmi 500. L'IA ne voit que ce qui compte.

**3. Coût — 5x moins cher**

| Approche | Coût/requête | Coût mensuel (20 requêtes/jour) |
|---|---|---|
| ChatGPT Teams + upload PDF | 0.05-0.15€ | 200-600€ |
| RAG cloud (Pinecone + OpenAI) | 0.03-0.08€ | 120-320€ + infra |
| **Notre solution hybride locale** | **~0.01€** | **25-80€** |

---

## Architecture en images

```
┌────────────────────────────────────────────────────────────────┐
│                    L'EQUIPE META-COACHING                      │
│                                                                │
│   Anne-Dominique    Paul    Equipe ops    Psychologues         │
│        │              │          │              │               │
│        └──────────────┴──────────┴──────────────┘               │
│                         │                                      │
│                    Slack / Interface web                        │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│               L'ORACLE (Agent Principal)                       │
│                                                                │
│   "De quoi parle cette question ?"                             │
│   → Clinique ? Ops ? Assureurs ? Transversal ?                │
│                                                                │
│   Coût : ~200 tokens (~0.001€)                                │
└──────────┬─────────────┬─────────────┬────────────────────────┘
           │             │             │
    ┌──────▼──────┐ ┌────▼─────┐ ┌────▼───────────┐
    │  CLINIQUE   │ │   OPS    │ │   ASSUREURS    │
    │             │ │          │ │                │
    │ Etudes CHU  │ │ KPIs     │ │ Partenaires    │
    │ Protocoles  │ │ Taux     │ │ ADELI          │
    │ TCC         │ │ Reporting│ │ Pricing        │
    │ Comité sci. │ │ Make.com │ │ Propositions   │
    └──────┬──────┘ └────┬─────┘ └────┬───────────┘
           │             │            │
           ▼             ▼            ▼
    ┌─────────────────────────────────────────────┐
    │     MOTEUR HYBRIDE LOCAL (votre serveur)     │
    │                                              │
    │  BM25 (mots-clés) + Embeddings (sens)       │
    │  → 5 ms pour filtrer 500 documents           │
    │  → Coût : 0€ (local, open-source)            │
    │                                              │
    │  ⚠️ AUCUNE donnée patient ne transite ici    │
    │  Uniquement : études publiées, KPIs          │
    │  agrégés, docs commerciaux, protocoles       │
    └─────────────────────────────────────────────┘
```

---

## Grille tarifaire

### Phase 1 — Audit & Taxonomie

| Prestation | Contenu | Durée | Tarif |
|---|---|---|---|
| Audit données existantes | Cartographie du wiki, des sources brutes, des flux Make.com existants | 1 jour | 800€ |
| Interviews utilisateurs | 3-4 entretiens de 30 min (AD Bonte, Paul, ops, psy) pour identifier les cas d'usage prioritaires | 0.5 jour | 400€ |
| Taxonomie & architecture | Définition des 3 domaines, des règles de routage, du schéma de données | 0.5 jour | 400€ |
| **Sous-total Phase 1** | | **2 jours** | **1 600€** |

**Livrable** : Document d'architecture validé + cartographie des données + priorisation des cas d'usage

---

### Phase 2 — Pipeline & Moteur de recherche

| Prestation | Contenu | Durée | Tarif |
|---|---|---|---|
| Pipeline d'ingestion | Script de nettoyage et conversion des sources (PDF → Markdown structuré) | 1.5 jours | 1 200€ |
| Moteur hybride local | Déploiement BM25 + embeddings Ollama + indexation complète du wiki | 2 jours | 1 600€ |
| Tests & calibrage | Ajustement des poids BM25/sémantique, validation sur 20 requêtes réelles | 0.5 jour | 400€ |
| **Sous-total Phase 2** | | **4 jours** | **3 200€** |

**Livrable** : Moteur de recherche opérationnel, testé, documenté

---

### Phase 3 — Agents IA & Intégration

| Prestation | Contenu | Durée | Tarif |
|---|---|---|---|
| Sub-agents spécialisés | 3 agents (Clinique, Ops, Assureurs) avec prompts systèmes, tests, documentation | 2 jours | 1 600€ |
| Orchestrateur Make.com | Scénario Make.com complet (webhook → routage → agents → réponse) | 1 jour | 800€ |
| Interface utilisateur | Intégration Slack (ou interface web minimale) pour l'accès équipe | 1 jour | 800€ |
| **Sous-total Phase 3** | | **4 jours** | **3 200€** |

**Livrable** : Système complet opérationnel, accessible à l'équipe

---

### Formation & Transfert

| Prestation | Contenu | Durée | Tarif |
|---|---|---|---|
| Formation équipe | 2 sessions de 1h30 : utilisation du système + bonnes pratiques de requêtage | 0.5 jour | 400€ |
| Documentation | Guide utilisateur + guide technique (maintenance, ajout de sources) | 0.5 jour | 400€ |
| **Sous-total Formation** | | **1 jour** | **800€** |

---

### Synthese investissement

| Phase | Durée | Tarif HT |
|---|---|---|
| Phase 1 — Audit & Taxonomie | 2 jours | 1 600€ |
| Phase 2 — Pipeline & Moteur | 4 jours | 3 200€ |
| Phase 3 — Agents & Intégration | 4 jours | 3 200€ |
| Formation & Transfert | 1 jour | 800€ |
| **TOTAL MISE EN PLACE** | **11 jours** | **8 800€ HT** |

**TJM appliqué** : 800€ HT/jour

---

### Retainer de maintenance (optionnel, recommandé)

| Formule | Contenu | Tarif mensuel HT |
|---|---|---|
| **Essentiel** | Monitoring système + correction bugs + 2h support/mois | 400€ |
| **Standard** | Essentiel + ajout de nouvelles sources/agents + optimisation mensuelle | 800€ |
| **Premium** | Standard + évolutions fonctionnelles + formation continue | 1 200€ |

**Engagement recommandé** : 3 mois minimum pour mesurer le ROI.

---

## ROI estimé

| Poste | Economie mensuelle estimée |
|---|---|
| Temps de recherche d'information (5-10h/semaine → 1-2h) | 800-1 600€ |
| Reporting automatisé (1-2j/mois → 2h) | 400-800€ |
| Réduction coûts API (vs RAG cloud) | 150-400€ |
| Onboarding accéléré (nouveaux collaborateurs) | Qualitatif |
| **Total économie mensuelle** | **1 350-2 800€** |

**Retour sur investissement** : 3-6 mois après mise en place.

---

## Garanties

- **Conformité HDS/RGPD** : aucune donnée patient ne quitte le périmètre Cegedim. Architecture validable par le DPO
- **Propriété intellectuelle** : tout le code, les configurations et les prompts sont la propriété de Méta-Coaching
- **Réversibilité** : stack 100% open-source (Ollama, ChromaDB, Python). Pas de vendor lock-in
- **Transparence** : chaque réponse cite ses sources. Vérifiable. Auditable

---

## Prochaine étape

**Un call de 30 minutes** pour :
1. Valider les 3 cas d'usage prioritaires
2. Vérifier l'infra technique disponible (serveur ? VPS ?)
3. Caler le planning Phase 1

**Contact** : Fabien Riou — fabien.riou92@gmail.com

---

*Ce document est confidentiel et destiné exclusivement à la direction de Méta-Coaching.*
