# Brief — 3 Chantiers UX · LineCoaching

**Mission** : Méta-Coaching — Fabien Riou · Consultant IA & UX  
**Version** : 1.0 · Juin 2026  
**Destinataire** : Anne-Dominique Bonte / Paul Biragnet

---

## Contexte & Objectif

Suite à l'audit UX du dashboard actuel et à l'atelier du 18 juin 2026, trois chantiers ont été identifiés pour améliorer la rétention et l'engagement utilisateur sur LineCoaching.

**Signal d'alerte principal** : 58% d'abandon entre le Start (fin d'onboarding) et le QPP (Questionnaire de Premier Passage). Le dashboard actuel présente un catalogue d'informations sans direction claire — l'utilisateur ne sait pas quoi faire maintenant.

**Direction validée** : Hypothèse C — "Plan du jour". Priorité comportements > résultats, conformément aux recommandations médicales (éviter l'obsession des métriques résultats).

---

## Chantier 1 · Dashboard & Accueil

**Objectif** : Transformer le dashboard en surface d'action, pas en catalogue.

**Problèmes adressés**
- 58% d'abandon Start → QPP (aucune direction claire pour l'utilisateur J1)
- 13 éléments de navigation → paralysie de décision
- Deux blocs identiques en compétition → confusion sur l'action prioritaire

**Direction de redesign**
- **État J1 (avant QPP)** : CTA unique, prescriptif — "Faire votre bilan avec [coach]"
- **État Programme en cours** : Plan du jour avec 1-2 actions max, progression comportementale (carnets remplis, séances faites) — pas de métriques résultats (poids, kg)
- Sidebar réduite à 4-5 items essentiels : Accueil · Mon carnet · Mon programme · Mes statistiques

**Méthode**
1. Benchmark approfondi des apps concurrentes (Kwit, apps nutrition, Sleepio) — écran par écran avec contexte. *Paul Biragnet à fournir les accès apps.*
2. 3 variantes de l'hypothèse "Plan du jour" (C1 checklist pure / C2 + jauge comportementale / C3 + message contextuel)
3. Validation interne → maquette haute fidélité → spec Angular

**Livrables**
- Benchmark screens annoté (HTML ou PDF)
- 3 variantes mockup mobile + desktop
- Spec fonctionnelle Angular (composants, états, règles d'affichage)

**Estimation** : ~1 semaine en rythme IA-first (benchmark J1 · variantes mockup J2 · validation J3 · spec J4-5)

**Dépendances** : Accès apps concurrentes (Paul) · Confirmation direction par AD Bonte

---

## Chantier 2 · Carnets — Réduction de friction

**Objectif** : Augmenter le taux de remplissage des carnets, qui alimentent toutes les données du dashboard.

**Problèmes adressés**
- Saisie actuelle trop longue (date à saisir, navigation complexe)
- Pas d'entrée contextuelle (exemple : rappel avant le repas → l'utilisateur doit retrouver le bon carnet)
- Sans carnet rempli, le dashboard n'a rien à afficher → cercle vicieux

**Direction**
- Entrée rapide depuis le dashboard (tap-to-open, date pré-remplie)
- Questions courtes, format contextuel (ex : "Comment vous sentez-vous avant ce repas ?" → 3 boutons)
- Référence : saisie Kwit (grandes touches, zéro friction, contextuelle)

**Méthode**
1. Audit du flux actuel de saisie carnet (temps, étapes, taux de complétion)
2. Proposition de flux simplifié
3. Spec + intégration dashboard (le carnet devient une action du Plan du jour)

**Livrables**
- Flux simplifié annoté
- Spec fonctionnelle (composant saisie rapide)

**Estimation** : ~3 jours (peut démarrer en parallèle du Chantier 1 dès J4)

**Dépendances** : Direction Chantier 1 validée (le carnet est un élément du dashboard)

---

## Chantier 3 · Parcours Programme — Présentation & Engagement

**Objectif** : Présenter les parcours (alimentaire, forme) de façon à inciter l'action, avec une hiérarchie claire selon l'état de complétion.

**Problèmes adressés**
- "Parcours terminé" + CTA "Revoir" = dead-end, aucune prochaine étape
- Deux parcours au même poids visuel → l'utilisateur ne sait pas lequel prioriser
- "5%" affiché = démotivant vs "Séance 2 sur 9" = concret et actionnable

**Direction**
- 1 parcours actif = card héro pleine largeur, durée de séance en avant, CTA "Commencer"
- 1 parcours terminé = mini-card compacte, CTA "Bilan de fin de programme"
- Règle de priorité : le parcours avec action aujourd'hui passe en héro
- Progression exprimée en séances (comportemental), pas en % ni en kg

**Méthode**
1. Spec des états de card parcours (actif / terminé / en pause)
2. Règles de priorité d'affichage
3. Intégration dashboard (composant parcours dans le Plan du jour)

**Livrables**
- Spec états parcours (4 états : J1 non-commencé / En cours / Terminé / Inactif >14j)
- Maquette composant

**Estimation** : ~2 jours (parallélisable avec Chantier 2)

**Dépendances** : Direction Chantier 1 validée

---

## Quick Win · Onglets Webinars

**Objectif** : Corriger la non-découvrabilité des webinars passés (onglets non identifiés comme cliquables).

**Estimation** : 2-4 heures dès réception du brief Paul Biragnet  
**Indépendant** des 3 chantiers — peut être livré à tout moment.

---

## Séquence Recommandée

```
Sem. 1 (J1–J5)                   Sem. 2 (J6–J10)
──────────────────────────────────────────────────
J1 · Benchmark apps concurrentes
J2 · 3 variantes mockup dashboard
J3 · Validation direction client
J4 · Spec Angular C1 + Audit carnets
J5 · Spec C1 finalisée            J6-J7 · Flux carnet simplifié + spec
                                  J8-J9 · Spec + maquette parcours
                                  J10   · Review finale

[QW] Onglets webinars (dès brief reçu, ~0.5j)
```

**Jalons de validation** :
- J2 : 3 variantes dashboard présentées → choix d'une direction
- J3 : Direction confirmée par AD Bonte
- J10 : Specs des 3 chantiers prêtes pour équipe dev

---

## Ce dont nous avons besoin

| Besoin | Responsable | Urgence |
|---|---|---|
| Accès comptes apps concurrentes (Kwit, nutrition, autres) | Paul Biragnet | Dès que possible |
| Confirmation direction "Plan du jour" par AD Bonte | Anne-Dominique Bonte | Avant sem. 2 |
| Brief onglets webinars | Paul Biragnet | Quand disponible |
| Taux de complétion carnets actuels (stats) | Équipe Méta-Coaching | Avant Chantier 2 |

---

*Document de travail — Fabien Riou · fabien.riou92@gmail.com*
