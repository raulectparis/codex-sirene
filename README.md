# codex-sirene

Projet test avec Codex pour API SIRENE

## Script d'exemple

Le fichier `fetch_sirene.py` permet d'interroger l'API SIRENE afin de
récupérer les établissements actifs dont l'activité principale est
`1083Z` en Île‑de‑France. Pour l'utiliser :

1. Installer les dépendances : `pip install requests`.
2. Définir les variables d'environnement `SIRENE_CLIENT_ID` et
   `SIRENE_CLIENT_SECRET` (identifiants fournis par l'INSEE).
3. Exécuter le script : `python fetch_sirene.py`.

Le résultat est affiché dans un tableau (SIREN, SIRET, raison sociale et
adresse complète).
