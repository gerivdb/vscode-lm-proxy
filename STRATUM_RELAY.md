# STRATUM RELAY — vscode-lm-proxy (L5)

**VAGUE**: 3 | **Synchro**: 2026-05-30 | **Hub**: gerivdb/LLM-REPO

- **Strate** : `L5` — IA distribuee & LLM
- **Role canonique** : Proxy LM pour VSCode — bridge modeles locaux/cloud
- **Parent** : L4 (infrastructure)

## Regles locales
- R1 — vscode-lm-proxy est le bridge entre VSCode et les modeles LLM.
- R2 — Tout acces LLM depuis VSCode passe par vscode-lm-proxy.
- Anti-pattern: acceder directement a un modele LLM depuis VSCode sans le proxy.

## Karpathy-Recall local (Vague 3 — 10Q)
1. Quel est le role de vscode-lm-proxy dans l'ecosysteme ?
2. Pourquoi VSCode ne doit-il pas acceder directement aux modeles LLM ?
3. Quelle est la difference entre vscode-lm-proxy et vsix-ai-orchestrator ?
4. Que se passe-t-il si le proxy est desactive ?
5. Dans quelle phase UrbanVerse ce STRATUM_RELAY a-t-il ete deploye ?
6. Quels types de modeles LLM (locaux et cloud) vscode-lm-proxy peut-il bridge ?
7. Comment vscode-lm-proxy gere-t-il le basculement entre un modele local et un modele cloud ?
8. Quels sont les avantages de passer par un proxy pour le routage des requetes LLM dans VSCode ?
9. Comment vscode-lm-proxy s'interface-t-il avec vsix-ai-orchestrator pour l'orchestration multi-agent ?
10. Quelles mesures de securite le proxy applique-t-il sur les requetes LLM ?

## Dependances directes

### Parents (Amont)
| Depot | Niveau | Role |
|-------|--------|------|
| KIVA | L4 | Infrastructure — hub d'orchestration principal |

### Enfants (Aval)
Aucun — vscode-lm-proxy est un composant feuille de L5.

## Vague de mise a jour

| Vague | Statut | Date | Changements |
|-------|--------|------|-------------|
| V1 | Deploye | 2026-05-28 | Creation initiale — identite, regles, 5Q Karpathy |
| V2 | Deploye | 2026-05-29 | Synchronisation Hub LLM-REPO — 5Q Karpathy-Recall |
| V3 | **Deploye** | **2026-05-30** | **10Q Karpathy-Recall + section Dependances** |
| V4 | Planifie | — | Enrichissement regles + cas d'usage avances |
