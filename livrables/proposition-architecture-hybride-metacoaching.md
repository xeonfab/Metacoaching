# Proposition — Architecture Hybride IA pour Méta-Coaching

**Mission** : Méta-Coaching — Fabien Riou · Consultant IA & Automatisation
**Version** : 1.0 · Juin 2026
**Destinataire** : Anne-Dominique Bonte / Equipe Méta-Coaching

---

## Pourquoi cette architecture plutot qu'un RAG classique ?

Un RAG (Retrieval-Augmented Generation) standard envoie tout le contenu brut dans un seul pipeline : embedding > retrieval > generation. Ca fonctionne pour un chatbot FAQ, mais ca explose en complexite, en cout et en risque des que :

- Le volume depasse quelques centaines de documents heterogenes (PDF cliniques, transcripts, specs techniques, KPIs assureurs)
- La confidentialite impose un perimetre strict (contrainte HDS/RGPD sur toute donnee patient)
- Les sources ont des natures differentes qui necessitent des traitements distincts (un blueprint Make.com ne se cherche pas comme une etude clinique)

L'architecture hybride **Sub-agents + Wiki structuree + Base vectorielle locale** resout ces trois problemes en separant les responsabilites.

---

## Architecture proposee pour Meta-Coaching

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────┐
│                   AGENT ORCHESTRATEUR                    │
│            (Claude API via Make.com / n8n)               │
│                                                         │
│  Recoit la requete → identifie le domaine → delegue     │
│  au sub-agent specialise → synthetise la reponse        │
└──────────┬──────────┬──────────┬────────────────────────┘
           │          │          │
    ┌──────▼──┐ ┌─────▼────┐ ┌──▼──────────────┐
    │ Sub-Ag. │ │ Sub-Ag.  │ │ Sub-Ag.         │
    │ CLINIQUE│ │ OPS/KPI  │ │ ASSUREURS/B2B2C │
    └────┬────┘ └────┬─────┘ └────┬────────────┘
         │           │            │
    ┌────▼────┐ ┌────▼─────┐ ┌───▼────────────┐
    │ Wiki +  │ │ Airtable │ │ Wiki +         │
    │ Vecteur │ │ / Sheets │ │ Vecteur        │
    │ LOCAL   │ │ + Make   │ │ LOCAL          │
    └─────────┘ └──────────┘ └────────────────┘

    ⚠️ PERIMETRE HDS : aucune donnee patient ne sort de Cegedim
```

### Les 3 sub-agents specialises

#### 1. Sub-Agent CLINIQUE — "Le cerveau medical"

**Perimetre** : Etudes cliniques, protocoles TCC, contenus programmes (LC, TS, TSE, TT, NK, OC), comite scientifique, evidence clinique.

**Base de connaissances** :
- Etudes CHU Montpellier (TheraSomnia : 91% reduction hypnotiques)
- Etudes CHRU Lille + Pasteur (LineCoaching : 79% maintien perte poids)
- Protocoles TCC par programme (9 etapes LC, 7 phases TheraSérena, TCC-I TheraSomnia)
- Profils comite scientifique (Apfeldorfer, Zermati, Cungi, Billiard/Dauvilliers)
- Concept de restriction cognitive et approche anti-regime

**Cas d'usage concrets pour MC** :
- Generer un argumentaire clinique pour un nouveau partenaire assureur (ex: "Donnez-moi les preuves cliniques TheraSomnia pour un pitch MGEN")
- Comparer les protocoles entre programmes pour identifier des synergies (ex: "Quels modules TCC sont communs entre TheraSérena et ThéraTabac ?")
- Alimenter la roadmap IA (detection predictive de decrochage) avec les metriques cliniques existantes

**Stockage** : Wiki Obsidian structuree (wiki/concepts/ + wiki/entities/) + embeddings locaux (Ollama/Qwen) sur les etudes PDF completes

**Contrainte HDS** : Ce sub-agent ne traite AUCUNE donnee patient individuelle. Uniquement des donnees cliniques aggregees et publiees.

---

#### 2. Sub-Agent OPS/KPI — "Le tableau de bord"

**Perimetre** : Metriques operationnelles, suivi engagement utilisateurs, reporting assureurs, KPIs programmes, automatisations Make.com.

**Base de connaissances** :
- Taux d'abandon Start → QPP (58% actuellement — chantier UX en cours)
- Taux de completion carnets par programme
- Metriques satisfaction (4.8/5 LC, 646 avis)
- Reporting B2B2C par assureur (AXA, Macif, GMF, MAAF, MMA, BPCE, Matmut)
- Blueprints Make.com documentes (scenarios/)

**Cas d'usage concrets pour MC** :
- "Quel est le taux de retention a 3 mois sur LineCoaching vs TheraSomnia ?" → requete directe sur les KPIs structures
- "Genere le rapport mensuel pour AXA avec les metriques d'engagement" → le sub-agent sait quel template utiliser et quelles donnees extraire
- "Alerte : le taux d'abandon a depasse 60% cette semaine" → monitoring proactif via Make.com

**Stockage** : Airtable / Google Sheets (donnees tabulaires) + scenarios Make.com pour l'extraction automatique

**Contrainte HDS** : Donnees TOUJOURS anonymisees/aggregees. Jamais de donnee patient-level hors perimetre Cegedim.

---

#### 3. Sub-Agent ASSUREURS/B2B2C — "Le commercial"

**Perimetre** : Partenariats assureurs, modele economique B2B2C, pricing, propositions commerciales, benchmark concurrence.

**Base de connaissances** :
- Fiches partenaires (AXA, Macif, GMF, MAAF, MMA, BPCE, Matmut — wiki/entities/Partenaires_Assureurs.md)
- Trois axes de valeur assureurs : (1) gestion des risques / reduction sinistralite, (2) differenciation / retention, (3) conformite reglementaire
- Modele ADELI : psychologues → numeros ADELI → remboursement complementaires → levier conversion B2C
- Pricing B2C : Autonomie ~25€/mois, Coaching Premium ~45€/mois
- Argumentaire QVT B2B : stress = 12 600€/an/employe, 40% effectifs touches

**Cas d'usage concrets pour MC** :
- "Prepare une proposition pour un nouvel assureur regional" → le sub-agent a deja le template, les preuves cliniques (appel au sub-agent clinique), et les metriques (appel au sub-agent OPS)
- "Compare notre offre avec les concurrents e-sante TCC" → recherche vectorielle dans les benchmarks stockes
- "Quel est le ROI projete pour Matmut si on integre ThéraTabac ?" → calcul base sur les donnees existantes

**Stockage** : Wiki Obsidian (wiki/entities/ + wiki/syntheses/) + embeddings locaux sur les rapports de marche PDF

---

## Implementation technique : 3 phases

### Phase 1 — Fondations (Semaines 1-3)

**Objectif** : Structurer le wiki existant et deployer les embeddings locaux.

| Action | Outil | Livrable |
|---|---|---|
| Consolider le wiki existant (ce repo) en base de reference | Claude Code + wiki-ingest | Wiki complete avec toutes les sources raw/ indexees |
| Deployer Ollama + modele d'embeddings (Qwen2.5 ou nomic-embed) | Docker / serveur local MC | Serveur embeddings operationnel |
| Indexer les documents wiki dans la base vectorielle | ChromaDB ou LanceDB (local) | Base vectorielle searchable |
| Creer les 3 index specialises (clinique, ops, assureurs) | Scripts Python | 3 collections separees |

**Cout estime** : 0€ en infra (tout local). ~3 jours de travail consultant.

**Pourquoi local et pas cloud ?** :
- HDS/RGPD : aucune donnee ne sort du perimetre
- Cout : embeddings Ollama = gratuit vs OpenAI embeddings = ~0.10$/1M tokens (s'accumule vite sur 10 programmes)
- Latence : recherche locale < 50ms vs API cloud 200-500ms

---

### Phase 2 — Sub-agents + Orchestration (Semaines 4-6)

**Objectif** : Deployer les 3 sub-agents et l'orchestrateur via Make.com.

| Action | Outil | Livrable |
|---|---|---|
| Creer le scenario Make.com "Orchestrateur" | Make.com + Claude API | Blueprint documente |
| Developper le sub-agent Clinique (prompt systeme + RAG local) | Claude API + ChromaDB | Agent fonctionnel |
| Developper le sub-agent OPS (connexion Airtable/Sheets) | Make.com + Claude API | Agent fonctionnel |
| Developper le sub-agent Assureurs (prompt + RAG local) | Claude API + ChromaDB | Agent fonctionnel |
| Tests integres : requetes cross-agents | Tous | Rapport de tests |

**Architecture Make.com** :
```
Webhook entrant (Slack / front MC)
  → Router (Claude API : classification de la requete)
    → Branche 1 : Sub-agent Clinique
    → Branche 2 : Sub-agent OPS
    → Branche 3 : Sub-agent Assureurs
    → Branche 4 : Multi-agent (requete transversale)
  → Aggregateur de reponses
  → Webhook sortant (reponse)
```

**Maitrise des couts API** :
- Phase de retrieval (recherche) : 100% local via Ollama → 0€
- Phase de generation : Claude API uniquement pour la synthese finale → budget maitrise
- Estimation : ~5-15$/mois pour un usage quotidien (vs 100-300$/mois en RAG cloud full-API)

---

### Phase 3 — Usages avances + Transfert (Semaines 7-10)

**Objectif** : Deployer les cas d'usage business et former l'equipe.

| Action | Livrable |
|---|---|
| Automatisation reporting assureurs (mensuel) | Scenario Make.com + template |
| Assistant preparation pitch (nouveaux partenaires) | Prompt + workflow documente |
| Monitoring proactif engagement (alertes decrochage) | Scenario Make.com + seuils |
| Dashboard KPI interne (Airtable/Notion) | Vue consolidee |
| Formation equipe MC (2 sessions) | Support de formation |
| Documentation complete | Fiches scenarios finales |

---

## Mapping sur les 4 cas d'usage du texte original

### 1. "Deuxieme Cerveau" Professionnel → Deja en place

**Ce repo EST le deuxieme cerveau.** Le wiki/ structure selon le pattern Karpathy avec wiki-ingest et wiki-clean est exactement ce pattern. Ce qui manque : la couche vectorielle pour les recherches semantiques.

**Solution MC** : Ajouter ChromaDB/LanceDB par-dessus le wiki existant. Chaque page wiki indexee = un chunk semantiquement recherchable. Les "liens invisibles" deviennent des requetes vectorielles : "Quels concepts cliniques de LineCoaching s'appliquent a la prevention diabete type 2 ?"

### 2. Knowledge Management Entreprise → Sub-agents specialises

**Probleme MC** : 10-19 employes, 10 programmes, 7+ assureurs, comite scientifique, processus back-office. Trop de contexte pour un seul LLM.

**Solution MC** : Les 3 sub-agents ci-dessus. Un nouveau membre de l'equipe peut demander : "Comment on prepare un reporting Macif ?" → le sub-agent OPS sait exactement quel process suivre, quel template utiliser, quelles metriques extraire.

### 3. Recherche Documentaire & Analyse de Marche → Sub-agent Clinique + Assureurs

**Probleme MC** : Les etudes cliniques (CHU Montpellier, CHRU Lille) font des dizaines de pages. Les rapports de marche e-sante/assurtech aussi. Un LLM classique perd le fil.

**Solution MC** : Les PDF sont chunks et indexes localement. Le sub-agent Clinique peut repondre a "Quels sont les resultats a 1 an sur le sevrage hypnotique dans l'etude Gui de Chauliac ?" sans renvoyer 200 pages dans le contexte. Extraction chirurgicale, pas force brute.

### 4. Architecture d'Agents IA → L'orchestrateur Make.com

**Probleme MC** : Aujourd'hui, Make.com + Claude API sont utilises en mode "one-shot". Chaque scenario est independant, sans memoire partagee.

**Solution MC** : L'orchestrateur centralise l'intelligence. Chaque scenario Make.com peut appeler le bon sub-agent au bon moment. Budget tokens maitrise car le retrieval est local (Ollama) et seule la generation finale passe par l'API Claude.

---

## Contraintes specifiques Meta-Coaching

### HDS/RGPD — Ligne rouge absolue

| Autorise | Interdit |
|---|---|
| Donnees cliniques aggregees publiees | Donnees patient individuelles |
| KPIs anonymises par programme | Contenu de sessions patient |
| Informations partenaires assureurs | Coordonnees patients |
| Contenus programmes (modules, etapes) | Donnees comportementales individuelles |
| Benchmarks concurrence | Tout transit hors perimetre Cegedim |

**Implementation** : La base vectorielle locale est hebergee sur l'infra MC (pas de cloud tiers). Les sub-agents n'ont JAMAIS acces a la base Cegedim directement — uniquement aux exports anonymises et valides par le DPO.

### Stack compatible

| Composant | Choix recommande | Alternative |
|---|---|---|
| Orchestration | Make.com (deja en place) | n8n (self-hosted) |
| LLM Generation | Claude API Anthropic | — |
| Embeddings | Ollama + Qwen2.5 (local) | Ollama + nomic-embed-text |
| Base vectorielle | ChromaDB (local, Python) | LanceDB (local, plus leger) |
| Wiki structuree | Ce repo (Obsidian-compatible) | — |
| KPIs structures | Airtable ou Google Sheets | Notion databases |
| Hebergement | Serveur local MC ou VPS francais | OVH (localisation FR) |

---

## Budget previsionnel

| Poste | Cout mensuel | Notes |
|---|---|---|
| Claude API (generation) | 15-50€ | Uniquement synthese finale, pas retrieval |
| Ollama / embeddings | 0€ | Local, open-source |
| ChromaDB | 0€ | Local, open-source |
| Make.com | Inclus dans abonnement existant | Scenarios supplementaires |
| Serveur / VPS | 10-30€ | Si pas d'infra existante |
| **Total** | **25-80€/mois** | vs 200-500€/mois pour un RAG cloud |

**Mise en place (one-shot)** : 8-10 jours de consulting, repartis sur les 3 phases.

---

## Prochaines etapes

1. **Valider le perimetre** avec Anne-Dominique Bonte — quels cas d'usage prioritaires ?
2. **Audit technique** — infra existante MC (serveur ? VPS ? postes locaux ?)
3. **Phase 1** — structurer le wiki, deployer les embeddings locaux
4. **Mesurer** — taux d'utilisation, temps gagne, qualite des reponses

---

*Document de travail — Fabien Riou · fabien.riou92@gmail.com*
