# STRATUM RELAY — vscode-lm-proxy (L5)

**VAGUE**: 2 | **Synchro**: 2026-05-29 | **Hub**: gerivdb/LLM-REPO

- **Strate** : `L5` — IA distribuee & LLM
- **Role canonique** : Proxy LM pour VSCode — bridge modeles locaux/cloud
- **Parent** : L4 (infrastructure)

## Regles locales
- R1 — vscode-lm-proxy est le bridge entre VSCode et les modeles LLM.
- R2 — Tout acces LLM depuis VSCode passe par vscode-lm-proxy.
- Anti-pattern: acceder directement a un modele LLM depuis VSCode sans le proxy.

## Karpathy-Recall local (Vague 2 — 5Q)
1. Quel est le role de vscode-lm-proxy dans l'ecosysteme ?
2. Pourquoi VSCode ne doit-il pas acceder directement aux modeles LLM ?
3. Quelle est la difference entre vscode-lm-proxy et vsix-ai-orchestrator ?
4. Que se passe-t-il si le proxy est desactive ?
5. Dans quelle phase UrbanVerse ce STRATUM_RELAY a-t-il ete deploye ?
