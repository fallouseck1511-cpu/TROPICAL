# SGRDMS LE TROPICAL v12
**Système de Gestion des Rendez-vous et Dossiers Médicaux**  
Université Iba Der Thiam de Thiès — Licence 2 Génie Logiciel

---

## 🚀 Déploiement sur Render (recommandé)

### Étape 1 — Pousser sur GitHub
```bash
git init
git add .
git commit -m "SGRDMS v12 initial"
git branch -M main
git remote add origin https://github.com/fallouseck1511-cpu/TROPICAL.git
git push -u origin main
```

### Étape 2 — Créer le projet sur Render
1. Aller sur [render.com](https://render.com) → **New** → **Blueprint**
2. Connecter ton dépôt GitHub `TROPICAL`
3. Render détecte automatiquement `render.yaml` → crée le **Web Service** + la **base PostgreSQL**
4. Cliquer **Apply**

### Étape 3 — Variables d'environnement sur Render
Dans **Dashboard → ton service → Environment**, ajouter :

| Variable | Valeur |
|---|---|
| `SECRET_KEY` | (généré automatiquement par render.yaml) |
| `DATABASE_URL` | (injecté automatiquement par render.yaml) |
| `SMS_PROVIDER` | (vide pour l'instant, à remplir plus tard) |
| `SMS_API_KEY` | (vide pour l'instant) |

### Étape 4 — Initialiser la base de données
Dans **Dashboard → Shell** du service, exécuter :
```bash
python seed.py
```
Cela crée toutes les tables et insère les données initiales (médecins, patients, médicaments...).

---

## 🖥️ Lancement en local

### Prérequis
- Python 3.11+
- PostgreSQL installé localement (ou utiliser SQLite en dev)

```bash
# 1. Cloner le dépôt
git clone https://github.com/fallouseck1511-cpu/TROPICAL.git
cd TROPICAL

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer l'environnement
cp .env.example .env
# Éditer .env : renseigner DATABASE_URL et SECRET_KEY

# 4. Initialiser la base
python seed.py

# 5. Lancer l'application
python app.py
# ou en production :
gunicorn app:app
```

---

## 👤 Comptes de connexion (données initiales)

| Rôle | Identifiant | Mot de passe |
|---|---|---|
| Admin | `admin` | `admin123` |
| Réceptionniste | `receptionniste` | `recep123` |
| Pharmacien | `pharmacien` | `pharma123` |
| Médecin (Dr. Diallo) | `dr.diallo` | `med123` |
| Médecin (Dr. Ndiaye) | `dr.ndiaye` | `med123` |
| Patient (Ibrahima Sow) | `ibra.sow` | `patient123` |
| Patient (Aminata Diallo) | `aminata.d` | `patient123` |

---

## 🏗️ Architecture

```
sgrdms/
├── app.py              # Application Flask principale (routes + logique)
├── models.py           # Modèles SQLAlchemy (27 tables)
├── seed.py             # Script d'initialisation de la base
├── requirements.txt    # Dépendances Python
├── Procfile            # Commande de démarrage (Render/Railway)
├── render.yaml         # Configuration automatique Render
├── .env.example        # Modèle de variables d'environnement
└── .gitignore
```

## 🗄️ Base de données (27 tables)
`centres` · `services` · `users` · `medecins` · `patients` · `dossiers`  
`rdvs` · `demandes_rdv` · `consultations` · `ordonnances` · `lignes_ordonnance`  
`medicaments` · `stocks` · `ventes_pharmacie` · `factures` · `paiements`  
`contrats_assurance` · `teleconsultations` · `resultats_examens` · `documents_patient`  
`liste_attente` · `triage` · `interactions_medicamenteuses` · `allergies_patient`  
`notifications` · `historiques` · `sms_envoyes`

## 📋 Règles de gestion couvertes
RG1 à RG14 toutes implémentées, dont :
- RG11 : Vérification activation téléconsultation médecin avant création RDV
- RG12 : Proposition automatique liste d'attente à l'annulation RDV
- RG13 : Blocage ordonnance si interaction médicamenteuse à risque élevé/critique
- RG14 : Prise en charge partielle par assurance avec calcul reste à payer

---

*SGRDMS v12 — Centre de Santé LE TROPICAL, Thiès, Sénégal*
