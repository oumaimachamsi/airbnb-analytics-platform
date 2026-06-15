# 🏠 Airbnb Analytics Platform

Plateforme analytique des données Airbnb (Berlin) construite selon une **architecture Médaillon** (Bronze / Silver / Gold), avec **dbt** pour les transformations, **DuckDB** comme moteur analytique et **Streamlit** pour la restitution.

Projet réalisé dans le cadre de l'évaluation *MBAESG_EVALUATION_MANAGEMENT_OPERATIONNEL_2026*.

---

## 📋 Présentation du projet

L'objectif est de mettre en place une plateforme analytique permettant d'analyser les logements, les hôtes et les avis clients d'Airbnb, et d'étudier l'impact des nuits de pleine lune sur les avis.

Le pipeline suit une architecture en trois couches :

| Couche | Rôle | Modèles dbt |
|--------|------|-------------|
| **Bronze** | Ingestion des données brutes (vues sur les fichiers sources) | `br_hosts`, `br_listings`, `br_reviews` |
| **Silver** | Nettoyage, typage, dédoublonnage des données | `sl_hosts`, `sl_listings`, `sl_reviews` |
| **Gold** | Indicateurs métier prêts pour la visualisation | `gd_listings_by_room_type`, `gd_top_hosts`, `gd_reviews_over_time`, `gd_full_moon_impact` |

Les transformations sont écrites en SQL et orchestrées par dbt. Les résultats sont stockés dans une base **DuckDB** (`airbnb.duckdb`) puis exposés dans un **dashboard Streamlit** interactif.

---

## 🗂️ Sources de données

Les fichiers de données brutes ne sont **pas versionnés** dans ce dépôt (le fichier `reviews.csv` dépasse la limite de 100 Mo de GitHub, et les données brutes ne se versionnent pas par bonne pratique). Ils se téléchargent depuis le stockage S3 fourni :

| Fichier | Description |
|---------|-------------|
| `hosts.csv` | Les hôtes (id, nom, statut superhôte, dates) |
| `listings.csv` | Les logements (id, type, prix, hôte associé...) |
| `reviews.csv` | Les avis clients (logement, date, commentaire, sentiment) |
| `seed_full_moon_dates.csv` | Table de référence des dates de pleine lune (chargée comme **seed** dbt) |

---

## ⚙️ Instructions d'installation et d'exécution

### Prérequis
- Python 3.12
- Git

### 1. Cloner le dépôt
```bash
git clone https://github.com/oumaimachamsi/airbnb-analytics-platform.git
cd airbnb-analytics-platform
```

### 2. Créer et activer l'environnement virtuel
```bash
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate          # Mac / Linux
```

### 3. Installer les dépendances
```bash
pip install dbt-duckdb streamlit plotly pandas
```

### 4. Télécharger les données
```bash
mkdir data
cd data
curl.exe -O https://logbrain-datasets.s3.eu-west-1.amazonaws.com/airbnb/hosts.csv
curl.exe -O https://logbrain-datasets.s3.eu-west-1.amazonaws.com/airbnb/reviews.csv
curl.exe -O https://logbrain-datasets.s3.eu-west-1.amazonaws.com/airbnb/listings.csv
curl.exe -O https://logbrain-datasets.s3.eu-west-1.amazonaws.com/airbnb/seed_full_moon_dates.csv
cd ..
```

### 5. Exécuter le pipeline dbt
```bash
cd airbnb_dbt
dbt seed          # charge le seed des dates de pleine lune
dbt run           # construit les couches Bronze, Silver, Gold
dbt test          # exécute les tests qualité
dbt docs generate # génère la documentation
cd ..
```

> Astuce : `dbt build` exécute seeds + modèles + tests en une seule commande.

### 6. Lancer le dashboard
```bash
streamlit run streamlit_app/app.py
```
L'application s'ouvre sur `http://localhost:8501`.

---

## 📊 Description des fonctionnalités

### Pipeline dbt
- **Sources** : les fichiers CSV sont déclarés comme sources et lus directement par DuckDB.
- **Transformations** : nettoyage des types (ex. conversion du prix `$90.00` en nombre), du statut superhôte (`t`/`f` → booléen), des dates.
- **Tests qualité** : tests `unique` et `not_null` sur les clés primaires et étrangères (6 tests).
- **Documentation** : générée via `dbt docs generate` (lineage et description des modèles).

### Dashboard Streamlit
Quatre visualisations interactives, toutes filtrables dynamiquement par **type de logement** :
1. **Logements et prix moyen par type** — nombre de logements et prix moyen.
2. **Top 15 des hôtes** — les plus gros hôtes, colorés selon leur statut superhôte.
3. **Évolution des avis dans le temps** — nombre d'avis par mois.
4. **Impact de la pleine lune** — comparaison du nombre d'avis par nuit et du taux de sentiment positif entre nuits de pleine lune et nuits normales.

### Principal résultat d'analyse
Les nuits de pleine lune génèrent légèrement plus d'avis par nuit que les nuits normales (~+3 %), mais le taux de sentiment positif reste quasiment identique (≈ 56 %). **La pleine lune n'a donc pas d'effet notable sur la positivité des avis.**

---

## 🛠️ Stack technique

- **DuckDB** — moteur analytique / base de données
- **dbt (dbt-duckdb)** — transformations SQL, tests, documentation
- **Streamlit + Plotly** — dashboard interactif
- **Git / GitHub** — versioning et collaboration

---

## 🌿 Organisation Git

Le développement suit un workflow collaboratif :
- Historique de commits clair et descriptif (conventions `feat:`, `chore:`...).
- Utilisation de branches de fonctionnalité (ex. `feature/streamlit-dashboard`).
- Intégration via Pull Requests sur la branche `main`.

---

## 👥 Répartition des tâches

Projet réalisé en binôme, avec une contribution équitable (50/50). Les deux membres ont travaillé ensemble sur l'ensemble des étapes : mise en place de l'environnement et du dépôt Git, conception du pipeline dbt (Bronze, Silver, Gold), écriture des tests qualité, développement du dashboard Streamlit et rédaction de la documentation.

| Membre | Contribution |
|--------|--------------|
| Oumaima | 50 % — pipeline dbt, dashboard, documentation (en binôme) |
| *[Nom du binôme]* | 50 % — pipeline dbt, dashboard, documentation (en binôme) |
