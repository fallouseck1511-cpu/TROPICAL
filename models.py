"""
SGRDMS LE TROPICAL — Modèles SQLAlchemy (PostgreSQL)
Toutes les entités du système mappées en tables relationnelles.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

# ─────────────────────────────────────────────────────────────
# 1. CENTRE
# ─────────────────────────────────────────────────────────────
class Centre(db.Model):
    __tablename__ = "centres"
    id            = db.Column(db.Integer, primary_key=True)
    nom           = db.Column(db.String(100), nullable=False)
    ville         = db.Column(db.String(80))
    adresse       = db.Column(db.String(150))
    telephone     = db.Column(db.String(30))

    services  = db.relationship("Service",  back_populates="centre")
    medecins  = db.relationship("Medecin",  back_populates="centre")

# ─────────────────────────────────────────────────────────────
# 2. SERVICE
# ─────────────────────────────────────────────────────────────
class Service(db.Model):
    __tablename__ = "services"
    id          = db.Column(db.Integer, primary_key=True)
    libelle     = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    id_centre   = db.Column(db.Integer, db.ForeignKey("centres.id"), nullable=False)

    centre      = db.relationship("Centre",  back_populates="services")
    medecins    = db.relationship("Medecin", back_populates="service")
    liste_att   = db.relationship("ListeAttente", back_populates="service")

# ─────────────────────────────────────────────────────────────
# 3. USER (compte de connexion)
# ─────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__    = "users"
    id               = db.Column(db.Integer, primary_key=True)
    username         = db.Column(db.String(60), unique=True, nullable=False)
    password         = db.Column(db.String(255), nullable=False)
    role             = db.Column(db.String(30), nullable=False)  # admin|medecin|receptionniste|pharmacien|patient
    nom              = db.Column(db.String(80))
    prenom           = db.Column(db.String(80))
    email            = db.Column(db.String(120))
    telephone        = db.Column(db.String(30))
    photo            = db.Column(db.Text)                 # base64 ou URL
    status_med       = db.Column(db.String(40), default="Disponible")
    teleconsult_actif = db.Column(db.Boolean, default=False)
    id_ref           = db.Column(db.String(20))           # matricule medecin ou id patient

# ─────────────────────────────────────────────────────────────
# 4. MEDECIN
# ─────────────────────────────────────────────────────────────
class Medecin(db.Model):
    __tablename__      = "medecins"
    matricule          = db.Column(db.String(10), primary_key=True)
    nom                = db.Column(db.String(80), nullable=False)
    prenom             = db.Column(db.String(80), nullable=False)
    specialite         = db.Column(db.String(80))
    telephone          = db.Column(db.String(30))
    email              = db.Column(db.String(120))
    username           = db.Column(db.String(60), db.ForeignKey("users.username"))
    est_chef           = db.Column(db.Boolean, default=False)
    teleconsult_actif  = db.Column(db.Boolean, default=False)
    id_service         = db.Column(db.Integer, db.ForeignKey("services.id"))
    id_centre          = db.Column(db.Integer, db.ForeignKey("centres.id"))

    service            = db.relationship("Service", back_populates="medecins")
    centre             = db.relationship("Centre",  back_populates="medecins")
    rdvs               = db.relationship("Rdv",              back_populates="medecin")
    consultations      = db.relationship("Consultation",      back_populates="medecin")
    teleconsultations  = db.relationship("Teleconsultation",  back_populates="medecin")

# ─────────────────────────────────────────────────────────────
# 5. PATIENT
# ─────────────────────────────────────────────────────────────
class Patient(db.Model):
    __tablename__    = "patients"
    id               = db.Column(db.Integer, primary_key=True)
    nom              = db.Column(db.String(80), nullable=False)
    prenom           = db.Column(db.String(80), nullable=False)
    sexe             = db.Column(db.String(1))             # M / F
    date_naissance   = db.Column(db.Date)
    telephone        = db.Column(db.String(30))
    email            = db.Column(db.String(120))
    adresse          = db.Column(db.String(150))
    assurance        = db.Column(db.String(60))
    groupe_sanguin   = db.Column(db.String(10), default="Non connu")
    statut           = db.Column(db.String(20), default="Actif")
    username         = db.Column(db.String(60), db.ForeignKey("users.username"))
    photo            = db.Column(db.Text)

    dossier          = db.relationship("Dossier",            back_populates="patient", uselist=False)
    rdvs             = db.relationship("Rdv",                back_populates="patient")
    consultations    = db.relationship("Consultation",        back_populates="patient")
    ordonnances      = db.relationship("Ordonnance",          back_populates="patient")
    factures         = db.relationship("Facture",             back_populates="patient")
    teleconsultations = db.relationship("Teleconsultation",   back_populates="patient")
    notifications    = db.relationship("Notification",        back_populates="patient")
    contrats         = db.relationship("ContratAssurance",    back_populates="patient")
    allergies        = db.relationship("AllergiePatient",     back_populates="patient")
    documents        = db.relationship("DocumentPatient",     back_populates="patient")
    liste_att        = db.relationship("ListeAttente",        back_populates="patient")
    triage           = db.relationship("Triage",              back_populates="patient")
    resultats        = db.relationship("ResultatExamen",      back_populates="patient")
    demandes_rdv     = db.relationship("DemandeRdv",          back_populates="patient")
    sms              = db.relationship("SmsEnvoye",           back_populates="patient")

# ─────────────────────────────────────────────────────────────
# 6. DOSSIER MÉDICAL
# ─────────────────────────────────────────────────────────────
class Dossier(db.Model):
    __tablename__       = "dossiers"
    id                  = db.Column(db.Integer, primary_key=True)
    num_dossier         = db.Column(db.String(20), unique=True)
    date_creation       = db.Column(db.Date, default=date.today)
    diagnostic_general  = db.Column(db.Text)
    id_patient          = db.Column(db.Integer, db.ForeignKey("patients.id"), unique=True)

    patient = db.relationship("Patient", back_populates="dossier")

# ─────────────────────────────────────────────────────────────
# 7. RENDEZ-VOUS
# ─────────────────────────────────────────────────────────────
class Rdv(db.Model):
    __tablename__    = "rdvs"
    id               = db.Column(db.Integer, primary_key=True)
    date             = db.Column(db.Date, nullable=False)
    heure            = db.Column(db.String(5), nullable=False)
    type             = db.Column(db.String(20), default="Presentiel")  # Presentiel|Teleconsultation
    statut           = db.Column(db.String(20), default="Confirme")    # Confirme|Annule|En attente
    motif            = db.Column(db.Text)
    lien_teleconsult = db.Column(db.Text)
    id_patient       = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    matricule        = db.Column(db.String(10), db.ForeignKey("medecins.matricule"), nullable=False)

    patient          = db.relationship("Patient",  back_populates="rdvs")
    medecin          = db.relationship("Medecin",  back_populates="rdvs")
    consultation     = db.relationship("Consultation", back_populates="rdv", uselist=False)
    teleconsultation = db.relationship("Teleconsultation", back_populates="rdv", uselist=False)

# ─────────────────────────────────────────────────────────────
# 8. DEMANDE RDV (portail patient)
# ─────────────────────────────────────────────────────────────
class DemandeRdv(db.Model):
    __tablename__  = "demandes_rdv"
    id             = db.Column(db.Integer, primary_key=True)
    type           = db.Column(db.String(20), default="Presentiel")
    motif          = db.Column(db.Text)
    statut         = db.Column(db.String(20), default="En attente")  # En attente|Traite|Annule
    date_demande   = db.Column(db.Date, default=date.today)
    traite_par     = db.Column(db.String(60))
    id_patient     = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    id_service     = db.Column(db.Integer, db.ForeignKey("services.id"))

    patient = db.relationship("Patient", back_populates="demandes_rdv")

# ─────────────────────────────────────────────────────────────
# 9. CONSULTATION
# ─────────────────────────────────────────────────────────────
class Consultation(db.Model):
    __tablename__  = "consultations"
    id             = db.Column(db.Integer, primary_key=True)
    date           = db.Column(db.Date, nullable=False, default=date.today)
    observation    = db.Column(db.Text)
    diagnostic     = db.Column(db.Text)
    type           = db.Column(db.String(20), default="Presentiel")
    id_patient     = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    matricule      = db.Column(db.String(10), db.ForeignKey("medecins.matricule"), nullable=False)
    id_rdv         = db.Column(db.Integer, db.ForeignKey("rdvs.id"))

    patient        = db.relationship("Patient",    back_populates="consultations")
    medecin        = db.relationship("Medecin",    back_populates="consultations")
    rdv            = db.relationship("Rdv",        back_populates="consultation")
    ordonnance     = db.relationship("Ordonnance", back_populates="consultation", uselist=False)
    facture        = db.relationship("Facture",    back_populates="consultation", uselist=False)
    resultat       = db.relationship("ResultatExamen", back_populates="consultation", uselist=False)

# ─────────────────────────────────────────────────────────────
# 10. ORDONNANCE
# ─────────────────────────────────────────────────────────────
class Ordonnance(db.Model):
    __tablename__    = "ordonnances"
    id               = db.Column(db.Integer, primary_key=True)
    date             = db.Column(db.Date, nullable=False, default=date.today)
    duree            = db.Column(db.Integer, default=7)   # en jours
    id_patient       = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    matricule        = db.Column(db.String(10), db.ForeignKey("medecins.matricule"), nullable=False)
    id_consultation  = db.Column(db.Integer, db.ForeignKey("consultations.id"))

    patient          = db.relationship("Patient",      back_populates="ordonnances")
    consultation     = db.relationship("Consultation", back_populates="ordonnance")
    lignes           = db.relationship("LigneOrdonnance", back_populates="ordonnance", cascade="all, delete-orphan")

# ─────────────────────────────────────────────────────────────
# 11. LIGNE ORDONNANCE
# ─────────────────────────────────────────────────────────────
class LigneOrdonnance(db.Model):
    __tablename__   = "lignes_ordonnance"
    id              = db.Column(db.Integer, primary_key=True)
    posologie       = db.Column(db.String(200))
    duree           = db.Column(db.String(50))
    id_ordonnance   = db.Column(db.Integer, db.ForeignKey("ordonnances.id"), nullable=False)
    id_medicament   = db.Column(db.Integer, db.ForeignKey("medicaments.id"), nullable=False)

    ordonnance  = db.relationship("Ordonnance",  back_populates="lignes")
    medicament  = db.relationship("Medicament",  back_populates="lignes_ordonnance")

# ─────────────────────────────────────────────────────────────
# 12. MEDICAMENT
# ─────────────────────────────────────────────────────────────
class Medicament(db.Model):
    __tablename__      = "medicaments"
    id                 = db.Column(db.Integer, primary_key=True)
    libelle            = db.Column(db.String(120), nullable=False)
    type               = db.Column(db.String(80))
    dosage             = db.Column(db.String(30))
    prix               = db.Column(db.Integer, default=0)
    contre_indication  = db.Column(db.Text)
    notice             = db.Column(db.Text)

    stock              = db.relationship("Stock",          back_populates="medicament", uselist=False)
    lignes_ordonnance  = db.relationship("LigneOrdonnance", back_populates="medicament")
    ventes             = db.relationship("VentePharmacie", back_populates="medicament")
    interactions_med1  = db.relationship("InteractionMedicamenteuse",
                                          foreign_keys="InteractionMedicamenteuse.id_med1",
                                          back_populates="medicament1")
    interactions_med2  = db.relationship("InteractionMedicamenteuse",
                                          foreign_keys="InteractionMedicamenteuse.id_med2",
                                          back_populates="medicament2")

# ─────────────────────────────────────────────────────────────
# 13. STOCK PHARMACIE
# ─────────────────────────────────────────────────────────────
class Stock(db.Model):
    __tablename__   = "stocks"
    id              = db.Column(db.Integer, primary_key=True)
    quantite        = db.Column(db.Integer, default=0)
    date_stock      = db.Column(db.Date, default=date.today)
    statut          = db.Column(db.String(20), default="Normal")  # Normal|Faible|Epuise
    seuil_alerte    = db.Column(db.Integer, default=20)
    id_medicament   = db.Column(db.Integer, db.ForeignKey("medicaments.id"), unique=True, nullable=False)

    medicament = db.relationship("Medicament", back_populates="stock")

# ─────────────────────────────────────────────────────────────
# 14. VENTE PHARMACIE
# ─────────────────────────────────────────────────────────────
class VentePharmacie(db.Model):
    __tablename__   = "ventes_pharmacie"
    id              = db.Column(db.Integer, primary_key=True)
    quantite        = db.Column(db.Integer, nullable=False)
    prix_unitaire   = db.Column(db.Integer)
    montant_total   = db.Column(db.Integer)
    date            = db.Column(db.Date, default=date.today)
    vendeur         = db.Column(db.String(60))
    nom_acheteur    = db.Column(db.String(100))
    id_medicament   = db.Column(db.Integer, db.ForeignKey("medicaments.id"), nullable=False)
    id_patient      = db.Column(db.Integer, db.ForeignKey("patients.id"))

    medicament = db.relationship("Medicament", back_populates="ventes")

# ─────────────────────────────────────────────────────────────
# 15. FACTURE
# ─────────────────────────────────────────────────────────────
class Facture(db.Model):
    __tablename__     = "factures"
    id                = db.Column(db.Integer, primary_key=True)
    num_facture       = db.Column(db.String(20), unique=True)
    montant           = db.Column(db.Integer, nullable=False)
    part_assurance    = db.Column(db.Integer, default=0)
    part_patient      = db.Column(db.Integer, default=0)
    montant_paye      = db.Column(db.Integer, default=0)
    reste_a_payer     = db.Column(db.Integer, default=0)
    statut            = db.Column(db.String(20), default="Impayee")  # Impayee|Partielle|Payee
    mode_paiement     = db.Column(db.String(30), default="-")
    date              = db.Column(db.Date, default=date.today)
    id_patient        = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    id_consultation   = db.Column(db.Integer, db.ForeignKey("consultations.id"))

    patient           = db.relationship("Patient",      back_populates="factures")
    consultation      = db.relationship("Consultation", back_populates="facture")
    paiements         = db.relationship("Paiement",     back_populates="facture")

# ─────────────────────────────────────────────────────────────
# 16. PAIEMENT
# ─────────────────────────────────────────────────────────────
class Paiement(db.Model):
    __tablename__  = "paiements"
    id             = db.Column(db.Integer, primary_key=True)
    montant        = db.Column(db.Integer, nullable=False)
    date           = db.Column(db.Date, default=date.today)
    mode           = db.Column(db.String(30))
    statut         = db.Column(db.String(20), default="Valide")
    id_facture     = db.Column(db.Integer, db.ForeignKey("factures.id"), nullable=False)
    id_patient     = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    facture = db.relationship("Facture",  back_populates="paiements")

# ─────────────────────────────────────────────────────────────
# 17. CONTRAT ASSURANCE
# ─────────────────────────────────────────────────────────────
class ContratAssurance(db.Model):
    __tablename__          = "contrats_assurance"
    id                     = db.Column(db.Integer, primary_key=True)
    assureur               = db.Column(db.String(80))
    num_contrat            = db.Column(db.String(60), unique=True)
    date_debut             = db.Column(db.Date)
    date_fin               = db.Column(db.Date)
    plafond_annuel         = db.Column(db.Integer, default=0)
    montant_utilise        = db.Column(db.Integer, default=0)
    taux_prise_en_charge   = db.Column(db.Integer, default=0)  # pourcentage
    statut                 = db.Column(db.String(20), default="Actif")
    id_patient             = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    patient = db.relationship("Patient", back_populates="contrats")

# ─────────────────────────────────────────────────────────────
# 18. TÉLÉCONSULTATION
# ─────────────────────────────────────────────────────────────
class Teleconsultation(db.Model):
    __tablename__  = "teleconsultations"
    id             = db.Column(db.Integer, primary_key=True)
    date_debut     = db.Column(db.String(20))
    statut         = db.Column(db.String(20), default="Planifiee")
    lien           = db.Column(db.Text)
    lien_envoye    = db.Column(db.Boolean, default=False)
    id_patient     = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    matricule      = db.Column(db.String(10), db.ForeignKey("medecins.matricule"), nullable=False)
    id_rdv         = db.Column(db.Integer, db.ForeignKey("rdvs.id"))

    patient = db.relationship("Patient", back_populates="teleconsultations")
    medecin = db.relationship("Medecin", back_populates="teleconsultations")
    rdv     = db.relationship("Rdv",     back_populates="teleconsultation")

# ─────────────────────────────────────────────────────────────
# 19. RÉSULTAT EXAMEN
# ─────────────────────────────────────────────────────────────
class ResultatExamen(db.Model):
    __tablename__   = "resultats_examens"
    id              = db.Column(db.Integer, primary_key=True)
    type            = db.Column(db.String(80))
    date            = db.Column(db.Date, default=date.today)
    commentaire     = db.Column(db.Text)
    statut          = db.Column(db.String(20), default="Disponible")
    fichier         = db.Column(db.Text)
    id_patient      = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    id_consultation = db.Column(db.Integer, db.ForeignKey("consultations.id"))
    matricule       = db.Column(db.String(10), db.ForeignKey("medecins.matricule"))

    patient         = db.relationship("Patient",      back_populates="resultats")
    consultation    = db.relationship("Consultation", back_populates="resultat")

# ─────────────────────────────────────────────────────────────
# 20. DOCUMENT PATIENT
# ─────────────────────────────────────────────────────────────
class DocumentPatient(db.Model):
    __tablename__   = "documents_patient"
    id              = db.Column(db.Integer, primary_key=True)
    type_document   = db.Column(db.String(60))   # Ordonnance|Facture|Resultat examen
    nom_fichier     = db.Column(db.String(120))
    type_fichier    = db.Column(db.String(10), default="PDF")
    date_creation   = db.Column(db.Date, default=date.today)
    ref_id          = db.Column(db.Integer)
    ref_type        = db.Column(db.String(30))   # ordonnance|facture|resultat
    id_patient      = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    patient = db.relationship("Patient", back_populates="documents")

# ─────────────────────────────────────────────────────────────
# 21. LISTE D'ATTENTE
# ─────────────────────────────────────────────────────────────
class ListeAttente(db.Model):
    __tablename__  = "liste_attente"
    id             = db.Column(db.Integer, primary_key=True)
    numero_ordre   = db.Column(db.Integer)
    date_arrivee   = db.Column(db.String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    statut         = db.Column(db.String(20), default="En attente")   # En attente|Appele|Traite
    priorite       = db.Column(db.String(20), default="Normal")       # Urgent|Prioritaire|Normal
    motif          = db.Column(db.Text)
    id_patient     = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    id_service     = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)

    patient = db.relationship("Patient", back_populates="liste_att")
    service = db.relationship("Service", back_populates="liste_att")

# ─────────────────────────────────────────────────────────────
# 22. TRIAGE / URGENCE
# ─────────────────────────────────────────────────────────────
class Triage(db.Model):
    __tablename__          = "triage"
    id                     = db.Column(db.Integer, primary_key=True)
    date_arrivee           = db.Column(db.String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    motif                  = db.Column(db.Text)
    niveau_urgence         = db.Column(db.String(30))  # ex: "2 - Urgent"
    tension                = db.Column(db.String(20))
    temperature            = db.Column(db.Float)
    saturation             = db.Column(db.Integer)
    frequence_cardiaque    = db.Column(db.Integer)
    statut                 = db.Column(db.String(20), default="En cours")
    pris_en_charge_par     = db.Column(db.String(10), db.ForeignKey("medecins.matricule"))
    observations           = db.Column(db.Text)
    id_patient             = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    patient = db.relationship("Patient", back_populates="triage")

# ─────────────────────────────────────────────────────────────
# 23. INTERACTION MÉDICAMENTEUSE
# ─────────────────────────────────────────────────────────────
class InteractionMedicamenteuse(db.Model):
    __tablename__  = "interactions_medicamenteuses"
    id             = db.Column(db.Integer, primary_key=True)
    niveau         = db.Column(db.String(20))   # modere|eleve|critique
    description    = db.Column(db.Text)
    id_med1        = db.Column(db.Integer, db.ForeignKey("medicaments.id"), nullable=False)
    id_med2        = db.Column(db.Integer, db.ForeignKey("medicaments.id"), nullable=False)

    medicament1 = db.relationship("Medicament", foreign_keys=[id_med1], back_populates="interactions_med1")
    medicament2 = db.relationship("Medicament", foreign_keys=[id_med2], back_populates="interactions_med2")

# ─────────────────────────────────────────────────────────────
# 24. ALLERGIE PATIENT
# ─────────────────────────────────────────────────────────────
class AllergiePatient(db.Model):
    __tablename__   = "allergies_patient"
    id              = db.Column(db.Integer, primary_key=True)
    libelle         = db.Column(db.String(100), nullable=False)
    type            = db.Column(db.String(40))        # Medicament|Aliment|Environnement
    severite        = db.Column(db.String(20))        # Faible|Moderee|Elevee|Critique
    date_constatee  = db.Column(db.Date)
    id_patient      = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    patient = db.relationship("Patient", back_populates="allergies")

# ─────────────────────────────────────────────────────────────
# 25. NOTIFICATION
# ─────────────────────────────────────────────────────────────
class Notification(db.Model):
    __tablename__  = "notifications"
    id             = db.Column(db.Integer, primary_key=True)
    type           = db.Column(db.String(60))
    objet          = db.Column(db.String(150))
    contenu        = db.Column(db.Text)
    date           = db.Column(db.String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    lu             = db.Column(db.Boolean, default=False)
    dest_role      = db.Column(db.String(30))
    dest_user      = db.Column(db.String(60))
    expediteur     = db.Column(db.String(60))
    id_patient     = db.Column(db.Integer, db.ForeignKey("patients.id"))

    patient = db.relationship("Patient", back_populates="notifications")

# ─────────────────────────────────────────────────────────────
# 26. HISTORIQUE
# ─────────────────────────────────────────────────────────────
class Historique(db.Model):
    __tablename__   = "historiques"
    id              = db.Column(db.Integer, primary_key=True)
    date_action     = db.Column(db.String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    description     = db.Column(db.Text)
    type            = db.Column(db.String(60))
    id_user         = db.Column(db.String(60))
    matricule       = db.Column(db.String(10))
    id_patient      = db.Column(db.Integer, db.ForeignKey("patients.id"))

# ─────────────────────────────────────────────────────────────
# 27. SMS ENVOYÉ
# ─────────────────────────────────────────────────────────────
class SmsEnvoye(db.Model):
    __tablename__  = "sms_envoyes"
    id             = db.Column(db.Integer, primary_key=True)
    numero         = db.Column(db.String(30), nullable=False)
    message        = db.Column(db.Text)
    date           = db.Column(db.String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    statut         = db.Column(db.String(30))   # success|non_configure|erreur
    detail         = db.Column(db.Text)
    par            = db.Column(db.String(60))
    id_patient     = db.Column(db.Integer, db.ForeignKey("patients.id"))

    patient = db.relationship("Patient", back_populates="sms")
