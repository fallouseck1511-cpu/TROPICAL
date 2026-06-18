"""
SGRDMS — Script de seeding initial de la base de données PostgreSQL.
À lancer UNE SEULE FOIS après la création des tables :
    python seed.py
"""
from app import app
from models import db, Centre, Service, User, Medecin, Patient, Dossier, \
    Medicament, Stock, Rdv, Consultation, Ordonnance, LigneOrdonnance, \
    Facture, Paiement, ContratAssurance, Teleconsultation, \
    AllergiePatient, InteractionMedicamenteuse, Notification, Historique, \
    ListeAttente, Triage, ResultatExamen, DocumentPatient, DemandeRdv
from datetime import date

with app.app_context():
    db.create_all()

    # ── CENTRE ──────────────────────────────────────────────────
    c1 = Centre(nom="LE TROPICAL", ville="Thies", adresse="Diaxao, Thies", telephone="33 951 00 00")
    db.session.add(c1); db.session.flush()

    # ── SERVICES ────────────────────────────────────────────────
    svcs = [
        Service(libelle="Pediatrie",          description="Soins pour enfants (0-15 ans)",   id_centre=c1.id),
        Service(libelle="Medecine Generaliste",description="Consultation adulte generale",    id_centre=c1.id),
        Service(libelle="Gynecologie",         description="Sante de la femme et maternite", id_centre=c1.id),
        Service(libelle="Cardiologie",         description="Maladies du coeur et vaisseaux", id_centre=c1.id),
        Service(libelle="Urgences",            description="Prise en charge urgente 24h/24", id_centre=c1.id),
        Service(libelle="Laboratoire",         description="Analyses biologiques et medicales", id_centre=c1.id),
    ]
    db.session.add_all(svcs); db.session.flush()
    s_ped,s_gen,s_gyn,s_car,s_urg,s_lab = svcs

    # ── USERS ───────────────────────────────────────────────────
    users = [
        User(username="admin",          password="admin123",   role="admin",          nom="Systeme",    prenom="Admin",    email="admin@tropical.sn",     telephone="33 951 00 00"),
        User(username="receptionniste", password="recep123",   role="receptionniste", nom="Ndiaye",     prenom="Fatou",    email="recep@tropical.sn",      telephone="77 444 55 66"),
        User(username="pharmacien",     password="pharma123",  role="pharmacien",     nom="Fall",       prenom="Mamadou",  email="pharma@tropical.sn",     telephone="76 555 66 77"),
        User(username="dr.ndiaye",      password="med123",     role="medecin",        nom="Ndiaye",     prenom="Rokhaya",  email="dr.ndiaye@tropical.sn",  telephone="76 222 33 44", id_ref="MED001", status_med="Disponible",  teleconsult_actif=False),
        User(username="dr.diallo",      password="med123",     role="medecin",        nom="Diallo",     prenom="Cheikh",   email="dr.diallo@tropical.sn",  telephone="77 111 22 33", id_ref="MED002", status_med="Disponible",  teleconsult_actif=True),
        User(username="dr.toure",       password="med123",     role="medecin",        nom="Toure",      prenom="Fatou",    email="dr.toure@tropical.sn",   telephone="76 888 99 00", id_ref="MED003", status_med="Disponible",  teleconsult_actif=True),
        User(username="dr.sarr",        password="med123",     role="medecin",        nom="Sarr",       prenom="Abdoulaye",email="dr.sarr@tropical.sn",    telephone="70 333 44 55", id_ref="MED004", status_med="En conge",    teleconsult_actif=True),
        User(username="dr.fall",        password="med123",     role="medecin",        nom="Fall",       prenom="Mariama",  email="dr.fall@tropical.sn",    telephone="77 444 55 66", id_ref="MED005", status_med="Disponible",  teleconsult_actif=False),
        User(username="dr.ba",          password="med123",     role="medecin",        nom="Ba",         prenom="Oumar",    email="dr.ba@tropical.sn",      telephone="76 555 66 77", id_ref="MED006", status_med="Disponible",  teleconsult_actif=True),
        User(username="dr.gueye",       password="med123",     role="medecin",        nom="Gueye",      prenom="Aminata",  email="dr.gueye@tropical.sn",   telephone="70 666 77 88", id_ref="MED007", status_med="Disponible",  teleconsult_actif=False),
        User(username="dr.diop",        password="med123",     role="medecin",        nom="Diop",       prenom="Moussa",   email="dr.diop@tropical.sn",    telephone="77 777 88 99", id_ref="MED008", status_med="Disponible",  teleconsult_actif=False),
        User(username="ibra.sow",       password="patient123", role="patient",        nom="Sow",        prenom="Ibrahima", email="ibra@email.com",          telephone="77 123 45 67"),
        User(username="aminata.d",      password="patient123", role="patient",        nom="Diallo",     prenom="Aminata",  email="aminata@email.com",       telephone="76 234 56 78"),
    ]
    db.session.add_all(users); db.session.flush()

    # ── MEDECINS ─────────────────────────────────────────────────
    medecins = [
        Medecin(matricule="MED001", nom="Ndiaye",  prenom="Rokhaya",   specialite="Pediatrie",            telephone="76 222 33 44", email="dr.ndiaye@tropical.sn",  username="dr.ndiaye",  est_chef=True,  teleconsult_actif=False, id_service=s_ped.id, id_centre=c1.id),
        Medecin(matricule="MED002", nom="Diallo",  prenom="Cheikh",    specialite="Medecine Generaliste", telephone="77 111 22 33", email="dr.diallo@tropical.sn",  username="dr.diallo",  est_chef=True,  teleconsult_actif=True,  id_service=s_gen.id, id_centre=c1.id),
        Medecin(matricule="MED003", nom="Toure",   prenom="Fatou",     specialite="Medecine Generaliste", telephone="76 888 99 00", email="dr.toure@tropical.sn",   username="dr.toure",   est_chef=False, teleconsult_actif=True,  id_service=s_gen.id, id_centre=c1.id),
        Medecin(matricule="MED004", nom="Sarr",    prenom="Abdoulaye", specialite="Gynecologie",          telephone="70 333 44 55", email="dr.sarr@tropical.sn",    username="dr.sarr",    est_chef=True,  teleconsult_actif=True,  id_service=s_gyn.id, id_centre=c1.id),
        Medecin(matricule="MED005", nom="Fall",    prenom="Mariama",   specialite="Cardiologie",          telephone="77 444 55 66", email="dr.fall@tropical.sn",    username="dr.fall",    est_chef=True,  teleconsult_actif=False, id_service=s_car.id, id_centre=c1.id),
        Medecin(matricule="MED006", nom="Ba",      prenom="Oumar",     specialite="Cardiologie",          telephone="76 555 66 77", email="dr.ba@tropical.sn",      username="dr.ba",      est_chef=False, teleconsult_actif=True,  id_service=s_car.id, id_centre=c1.id),
        Medecin(matricule="MED007", nom="Gueye",   prenom="Aminata",   specialite="Urgences",             telephone="70 666 77 88", email="dr.gueye@tropical.sn",   username="dr.gueye",   est_chef=True,  teleconsult_actif=False, id_service=s_urg.id, id_centre=c1.id),
        Medecin(matricule="MED008", nom="Diop",    prenom="Moussa",    specialite="Biologie medicale",    telephone="77 777 88 99", email="dr.diop@tropical.sn",    username="dr.diop",    est_chef=True,  teleconsult_actif=False, id_service=s_lab.id, id_centre=c1.id),
    ]
    db.session.add_all(medecins); db.session.flush()

    # ── PATIENTS ─────────────────────────────────────────────────
    p1 = Patient(nom="Sow",    prenom="Ibrahima", sexe="M", date_naissance=date(1990,5,12),  telephone="77 123 45 67", email="ibra@email.com",    adresse="Dakar, Plateau", assurance="IPRES", groupe_sanguin="O+",       statut="Actif", username="ibra.sow")
    p2 = Patient(nom="Diallo", prenom="Aminata",  sexe="F", date_naissance=date(1985,11,23), telephone="76 234 56 78", email="aminata@email.com", adresse="Thies",          assurance="CSS",   groupe_sanguin="A+",       statut="Actif", username="aminata.d")
    p3 = Patient(nom="Ndiaye", prenom="Moussa",   sexe="M", date_naissance=date(2000,3,7),   telephone="70 345 67 89", email="moussa@email.com",  adresse="Ziguinchor",     assurance="Aucune",groupe_sanguin="Non connu", statut="Actif")
    db.session.add_all([p1,p2,p3]); db.session.flush()

    # update users id_ref for patients
    next((u for u in users if u.username=="ibra.sow"),None).id_ref=str(p1.id)
    next((u for u in users if u.username=="aminata.d"),None).id_ref=str(p2.id)

    # ── DOSSIERS ────────────────────────────────────────────────
    db.session.add_all([
        Dossier(num_dossier="DOS-0001", date_creation=date(2026,6,6), diagnostic_general="Hypertension arterielle",   id_patient=p1.id),
        Dossier(num_dossier="DOS-0002", date_creation=date(2026,6,4), diagnostic_general="Aucune pathologie chronique", id_patient=p2.id),
    ]); db.session.flush()

    # ── MÉDICAMENTS + STOCKS ────────────────────────────────────
    meds = [
        Medicament(libelle="Amlodipine 5mg",    type="Antihypertenseur",   dosage="5mg",   prix=900,  contre_indication="Insuffisance hepatique", notice="Prendre le soir"),
        Medicament(libelle="Amoxicilline 250mg", type="Antibiotique",       dosage="250mg", prix=1200, contre_indication="Allergie penicilline",   notice="Completer le traitement"),
        Medicament(libelle="Paracetamol 500mg",  type="Antalgique",         dosage="500mg", prix=500,  contre_indication="Insuffisance hepatique", notice="Max 4g/jour"),
        Medicament(libelle="Metformine 500mg",   type="Antidiabetique",     dosage="500mg", prix=600,  contre_indication="Insuffisance renale",    notice="Prendre pendant les repas"),
        Medicament(libelle="Ibuprofene 400mg",   type="Anti-inflammatoire", dosage="400mg", prix=800,  contre_indication="Ulcere gastrique",       notice="Max 3 prises/jour"),
    ]
    db.session.add_all(meds); db.session.flush()

    stocks = [
        Stock(id_medicament=meds[0].id, quantite=80,  statut="Normal", seuil_alerte=20),
        Stock(id_medicament=meds[1].id, quantite=15,  statut="Faible", seuil_alerte=20),
        Stock(id_medicament=meds[2].id, quantite=200, statut="Normal", seuil_alerte=30),
        Stock(id_medicament=meds[3].id, quantite=150, statut="Normal", seuil_alerte=20),
        Stock(id_medicament=meds[4].id, quantite=0,   statut="Epuise", seuil_alerte=20),
    ]
    db.session.add_all(stocks)

    # ── RDVs ────────────────────────────────────────────────────
    rdv1 = Rdv(id_patient=p1.id, matricule="MED002", date=date(2026,6,10), heure="08:00", type="Presentiel",      statut="Confirme", motif="Douleur thoracique")
    rdv2 = Rdv(id_patient=p2.id, matricule="MED001", date=date(2026,6,11), heure="09:00", type="Presentiel",      statut="En attente", motif="Vaccination")
    rdv3 = Rdv(id_patient=p1.id, matricule="MED002", date=date(2026,6,10), heure="10:00", type="Teleconsultation", statut="Confirme", motif="Suivi tension", lien_teleconsult="https://meet.google.com/abc-defg-hij")
    db.session.add_all([rdv1,rdv2,rdv3]); db.session.flush()

    # ── CONSULTATION + ORDONNANCE + FACTURE ─────────────────────
    cons1 = Consultation(id_patient=p1.id, matricule="MED002", date=date(2026,6,5), observation="Pression 140/90", diagnostic="Hypertension arterielle", type="Presentiel", id_rdv=rdv1.id)
    cons2 = Consultation(id_patient=p2.id, matricule="MED001", date=date(2026,6,4), observation="Bonne sante generale", diagnostic="Bilan normal", type="Presentiel", id_rdv=rdv2.id)
    db.session.add_all([cons1,cons2]); db.session.flush()

    ord1 = Ordonnance(id_patient=p1.id, matricule="MED002", date=date(2026,6,5), duree=30, id_consultation=cons1.id)
    db.session.add(ord1); db.session.flush()
    db.session.add_all([
        LigneOrdonnance(id_ordonnance=ord1.id, id_medicament=meds[0].id, posologie="1 cp le soir",          duree="30 jours"),
        LigneOrdonnance(id_ordonnance=ord1.id, id_medicament=meds[3].id, posologie="1 cp matin et soir",    duree="30 jours"),
    ])

    fac1 = Facture(id_patient=p1.id, id_consultation=cons1.id, num_facture="FAC-0001", montant=15000, part_assurance=6000, part_patient=9000, montant_paye=9000, reste_a_payer=0, statut="Payee", mode_paiement="Especes", date=date(2026,6,5))
    fac2 = Facture(id_patient=p2.id, id_consultation=cons2.id, num_facture="FAC-0002", montant=8500,  part_assurance=4250, part_patient=4250, montant_paye=0,    reste_a_payer=4250, statut="Impayee", mode_paiement="-", date=date(2026,6,4))
    db.session.add_all([fac1,fac2]); db.session.flush()
    db.session.add(Paiement(id_facture=fac1.id, id_patient=p1.id, montant=9000, date=date(2026,6,5), mode="Especes", statut="Valide"))

    # ── CONTRATS ASSURANCE ──────────────────────────────────────
    db.session.add_all([
        ContratAssurance(id_patient=p1.id, assureur="IPRES", num_contrat="IPRES-2024-001", date_debut=date(2024,1,1), date_fin=date(2026,12,31), plafond_annuel=500000, montant_utilise=15000, taux_prise_en_charge=40, statut="Actif"),
        ContratAssurance(id_patient=p2.id, assureur="CSS",   num_contrat="CSS-2025-002",   date_debut=date(2025,1,1), date_fin=date(2027,12,31), plafond_annuel=750000, montant_utilise=8500,  taux_prise_en_charge=50, statut="Actif"),
    ])

    # ── TELECONSULTATION ────────────────────────────────────────
    db.session.add(Teleconsultation(id_patient=p1.id, matricule="MED001", id_rdv=rdv3.id, date_debut="2026-06-10 10:00", statut="Planifiee", lien="https://meet.google.com/abc-defg-hij", lien_envoye=True))

    # ── ALLERGIES ───────────────────────────────────────────────
    db.session.add_all([
        AllergiePatient(id_patient=p1.id, libelle="Ibuprofene", type="Medicament", severite="Elevee",   date_constatee=date(2025,1,15)),
        AllergiePatient(id_patient=p2.id, libelle="Penicilline", type="Medicament", severite="Critique", date_constatee=date(2024,6,1)),
    ])

    # ── INTERACTIONS ────────────────────────────────────────────
    db.session.add_all([
        InteractionMedicamenteuse(id_med1=meds[0].id, id_med2=meds[3].id, niveau="modere",   description="Amlodipine + Metformine : surveiller glycemie"),
        InteractionMedicamenteuse(id_med1=meds[1].id, id_med2=meds[4].id, niveau="eleve",    description="Amoxicilline + Ibuprofene : risque hemorragie digestive"),
        InteractionMedicamenteuse(id_med1=meds[2].id, id_med2=meds[4].id, niveau="modere",   description="Paracetamol + Ibuprofene : eviter association prolongee"),
        InteractionMedicamenteuse(id_med1=meds[0].id, id_med2=meds[4].id, niveau="eleve",    description="Amlodipine + Ibuprofene : diminution effet antihypertenseur"),
    ])

    # ── NOTIFICATIONS ───────────────────────────────────────────
    db.session.add_all([
        Notification(type="Rappel RDV",         objet="RDV demain a 08h00",                    contenu="Votre RDV est prevu le 10/06 a 08h00 avec Dr. Diallo.", id_patient=p1.id),
        Notification(type="Resultat disponible", objet="Vos resultats d'examen sont disponibles", contenu="Resultats bilan sanguin du 05/06 disponibles.", id_patient=p1.id, expediteur="dr.diallo"),
        Notification(type="Stock faible",        objet="Alerte stock Amoxicilline",             contenu="Stock Amoxicilline 250mg en dessous du seuil.", dest_role="pharmacien", dest_user="pharmacien", expediteur="system"),
        Notification(type="Info",                objet="Bienvenue sur SGRDMS v12",              contenu="Systeme mis a jour. Nouvelles fonctionnalites disponibles.", dest_role="admin", dest_user="admin", expediteur="system"),
    ])

    # ── HISTORIQUES ─────────────────────────────────────────────
    db.session.add_all([
        Historique(description="Nouveau patient : Ibrahima Sow",           type="Creation patient", id_user="receptionniste", id_patient=p1.id),
        Historique(description="RDV confirme - Ibrahima Sow / Dr. Diallo", type="Rendez-vous",      id_user="receptionniste", id_patient=p1.id, matricule="MED002"),
        Historique(description="Consultation - HTA stade 1",               type="Consultation",     id_user="dr.diallo",      id_patient=p1.id, matricule="MED002"),
    ])

    # ── LISTE ATTENTE ───────────────────────────────────────────
    db.session.add_all([
        ListeAttente(id_patient=p1.id, id_service=s_ped.id, numero_ordre=1, statut="En attente", priorite="Normal",      motif="Consultation"),
        ListeAttente(id_patient=p2.id, id_service=s_gen.id, numero_ordre=2, statut="En attente", priorite="Prioritaire", motif="Suivi"),
    ])

    # ── TRIAGE ──────────────────────────────────────────────────
    db.session.add(Triage(id_patient=p3.id, motif="Douleur abdominale aigue", niveau_urgence="2 - Urgent", tension="130/85", temperature=38.5, saturation=97, frequence_cardiaque=102, statut="En cours", pris_en_charge_par="MED006", observations="Patient agite, douleur 8/10"))

    # ── RÉSULTAT EXAMEN ─────────────────────────────────────────
    db.session.add(ResultatExamen(id_patient=p1.id, id_consultation=cons1.id, matricule="MED002", type="Bilan sanguin", date=date(2026,6,5), commentaire="Glycemie legerement elevee (1.26 g/L). Cholesterol 2.1 g/L.", statut="Disponible"))

    # ── DEMANDE RDV ─────────────────────────────────────────────
    db.session.add(DemandeRdv(id_patient=p1.id, id_service=s_ped.id, type="Presentiel", motif="Renouvellement ordonnance", statut="En attente", date_demande=date(2026,6,6)))

    db.session.commit()
    print("✅ Base de données initialisée avec succès !")
