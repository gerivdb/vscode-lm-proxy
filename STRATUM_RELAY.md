# STRATUM RELAY — vscode-lm-proxy (L5)

**VAGUE**: 4 | **Synchro**: 2026-05-30 | **Hub**: gerivdb/LLM-REPO

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

## Agents locaux (Vague 4)

```yaml
# .roomodes — profil agent vscode-lm-proxy
agent: lm-proxy-bridge
strate: L5
role: LLM access proxy for VSCode
rules: vscode-lm-proxy/rules/proxy_rules.yaml
hub_ref: KIVA
```

L'agent `lm-proxy-bridge` fait le pont entre VSCode et les modeles LLM locaux/cloud et applique le routage securise.

## Auto-conformite (Vague 4)

- **Guard 1 — Proxy-only LLM access** : Aucun acces LLM depuis VSCode ne peut contourner le proxy.
- **Guard 2 — Failover local/cloud** : En cas d'indisponibilite, le proxy bascule automatiquement entre local et cloud.
- **Guard 3 — Request security** : Le proxy filtre et securise toutes les requetes LLM.

## Vague de mise a jour

| Vague | Statut | Date | Changements |
|-------|--------|------|-------------|
| V1 | Deploye | 2026-05-28 | Creation initiale — identite, regles, 5Q Karpathy |
| V2 | Deploye | 2026-05-29 | Synchronisation Hub LLM-REPO — 5Q Karpathy-Recall |
| V3 | Deploye | 2026-05-30 | 10Q Karpathy-Recall + section Dependances |
| **V4** | **Deploye** | **2026-05-30** | **Agents locaux (.roomodes) + Auto-conformite (3 guards) deployes** |

---

*Genere par `VERSUS/urban_ontology_verse/TOOLS/relay_propagator.py` v4.0*
*UrbanVerse v4.0.0 — gerivdb/VERSUS (L8)*
*IntentHash: 0xPHASE8_VSCODE_LM_PROXY_V4_20260530*