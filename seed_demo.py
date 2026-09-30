"""
SGRDMS LE TROPICAL — Phase 10 : jeu de données de démonstration enrichi.

Objectif : faire ressembler la base à un système réellement utilisé,
sans toucher au schéma (models.py), sans inventer de nouvelles tables,
et sans jamais supprimer de données existantes.

Utilise UNIQUEMENT les modèles déjà définis dans models.py. N'ajoute
aucun champ, aucune table. S'appuie sur seed.py::run_seed() pour le
socle (centre, services, comptes de référence) puis vient l'enrichir.

Reproductible : random.seed(42) fixe -> mêmes données à chaque exécution.
Idempotent : un marqueur (Historique.type == MARKER) empêche de rejouer
le remplissage massif deux fois sur la même base.

Utilisation :
    python seed_demo.py
"""
import random
from datetime import date, timedelta, datetime
from werkzeug.security import generate_password_hash

from models import (
    db, Centre, Service, User, Medecin, Patient, Dossier, Rdv, DemandeRdv,
    Consultation, Ordonnance, LigneOrdonnance, Medicament, Stock,
    VentePharmacie, Facture, FactureLigne, Paiement, ContratAssurance,
    Teleconsultation, ResultatExamen, DocumentPatient, Antecedent,
    ConstanteVitale, Lit, Hospitalisation, NoteSuivi, Vaccination,
    ListeAttente, Triage, InteractionMedicamenteuse, AllergiePatient,
    Notification, Historique, Creneau, AlerteStock, SmsEnvoye,
)

MARKER = "seed_demo_v1_applique"
random.seed(42)

# ───────────────────────── Pools de données réalistes (Sénégal) ─────────
PRENOMS_M = ["Amadou","Moussa","Ibrahima","Cheikh","Oumar","Mamadou","Abdoulaye",
    "Ousmane","Pape","Serigne","Mor","Alioune","Modou","Babacar","Idrissa",
    "Lamine","Souleymane","El Hadji","Assane","Malick","Thierno","Demba",
    "Boubacar","Ismaila","Aliou","Daouda","Gora","Landing","Sidy","Cheikhou"]
PRENOMS_F = ["Fatou","Awa","Aminata","Aissatou","Khady","Mariama","Ndeye",
    "Rokhaya","Coumba","Astou","Bineta","Marième","Adama","Fatoumata","Sokhna",
    "Dieynaba","Khadidiatou","Yacine","Ndella","Absa","Seynabou","Aida",
    "Nabou","Ramatoulaye","Oumou","Penda","Fama","Aby","Maimouna","Diarra"]
NOMS = ["Diop","Ndiaye","Fall","Diallo","Sow","Sarr","Ba","Gueye","Diagne",
    "Faye","Sy","Ndoye","Toure","Kane","Seck","Diatta","Mbaye","Cisse",
    "Thiam","Ndour","Sane","Gaye","Mendy","Diouf","Sagna","Camara","Lo",
    "Wade","Badji","Coly"]
VILLES = ["Dakar, Plateau","Dakar, Medina","Dakar, Parcelles Assainies",
    "Dakar, Grand Yoff","Pikine","Guediawaye","Rufisque","Thies, Centre",
    "Thies, Randoulene","Mbour","Touba","Kaolack","Saint-Louis","Ziguinchor",
    "Kolda","Diourbel","Louga","Tambacounda","Fatick","Kaffrine"]
ASSUREURS = ["IPRES","CSS","NSIA Assurances","AXA Senegal","Aucune","Aucune"]
GROUPES   = ["O+","O-","A+","A-","B+","B-","AB+","AB-","Non connu"]
SPECIALITES = ["Medecine Generaliste","Pediatrie","Gynecologie","Cardiologie",
    "Urgences","Biologie medicale","Dermatologie","Neurologie","Chirurgie Generale"]
DIAGNOSTICS = ["Hypertension arterielle","Paludisme simple","Infection respiratoire",
    "Gastro-enterite aigue","Diabete type 2 dessequilibre","Lombalgie",
    "Bilan de routine normal","Anemie moderee","Rhinopharyngite","Dermite allergique",
    "Suivi de grossesse","Migraine","Douleur abdominale","Bronchite aigue","Entorse"]
TYPES_MED = ["Antibiotique","Antalgique","Anti-inflammatoire","Antihypertenseur",
    "Antidiabetique","Antipaludique","Antiseptique","Vitamine/Complement",
    "Antihistaminique","Antispasmodique","Antiacide","Dermatologique"]

def rd(a, b):  # date aléatoire entre deux dates
    return a + timedelta(days=random.randint(0, (b - a).days))

def slug(s):
    return (s.lower().replace(" ", "").replace("-", "")
            .replace("é","e").replace("è","e").replace("ç","c"))


def deja_applique():
    return Historique.query.filter_by(type=MARKER).first() is not None


def run_seed_demo(n_patients=600, n_medecins_new=32, n_medicaments_new=105):
    if deja_applique():
        print("ℹ️  Jeu de données enrichi déjà présent — rien à faire (idempotent).")
        return False

    centre = Centre.query.first()
    services = Service.query.all()
    if not centre or not services:
        raise RuntimeError("Le socle (run_seed) doit être appliqué avant seed_demo.")

    today = date.today()
    d_min, d_max_past = today - timedelta(days=200), today - timedelta(days=1)
    d_max_fut = today + timedelta(days=45)

    # ═══════════════════ 1. MÉDECINS (+ comptes) ═══════════════════
    medecins = Medecin.query.all()
    next_med_num = len(medecins) + 1
    new_medecins = []
    for i in range(n_medecins_new):
        nom, prenom = random.choice(NOMS), random.choice(PRENOMS_M + PRENOMS_F)
        mat = f"MED{next_med_num:03d}"; next_med_num += 1
        uname = f"dr.{slug(nom)}{i}"
        svc = random.choice(services)
        db.session.add(User(username=uname, password=generate_password_hash("med123"),
            role="medecin", nom=nom, prenom=prenom, email=f"{uname}@tropical.sn",
            telephone=f"7{random.randint(0,7)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}",
            id_ref=mat, status_med=random.choice(["Disponible","Disponible","Disponible","En conge"]),
            teleconsult_actif=random.random() < 0.5))
        m = Medecin(matricule=mat, nom=nom, prenom=prenom, specialite=random.choice(SPECIALITES),
            telephone=f"7{random.randint(0,7)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}",
            email=f"{uname}@tropical.sn", username=uname, est_chef=random.random() < 0.15,
            teleconsult_actif=random.random() < 0.5, id_service=svc.id, id_centre=centre.id)
        db.session.add(m); new_medecins.append(m)
    db.session.flush()
    medecins = Medecin.query.all()

    # Créneaux hebdo pour tous les médecins (existants + nouveaux)
    jours = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]
    for m in medecins:
        if Creneau.query.filter_by(matricule=m.matricule).first():
            continue
        for j in random.sample(jours, k=random.randint(3, 5)):
            db.session.add(Creneau(matricule=m.matricule, jour=j, heure_debut="08:00", heure_fin="16:00"))
    db.session.flush()

    # ═══════════════════ 2. PATIENTS (+ dossiers, comptes portail) ══
    patients = Patient.query.all()
    next_dos_num = (Dossier.query.count() or 0) + 1
    new_patients = []
    for i in range(n_patients):
        sexe = random.choice(["M", "F"])
        prenom = random.choice(PRENOMS_M if sexe == "M" else PRENOMS_F)
        nom = random.choice(NOMS)
        assurance = random.choice(ASSUREURS)
        p = Patient(nom=nom, prenom=prenom, sexe=sexe,
            date_naissance=rd(date(1940,1,1), date(2023,1,1)),
            telephone=f"7{random.randint(0,7)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}",
            email=f"{slug(prenom)}.{slug(nom)}{i}@email.com" if random.random() < 0.6 else None,
            adresse=random.choice(VILLES), assurance=assurance,
            groupe_sanguin=random.choice(GROUPES), statut=random.choices(["Actif","Inactif"], weights=[92,8])[0])
        db.session.add(p); new_patients.append(p)
    db.session.flush()

    # 15% des nouveaux patients obtiennent un compte portail
    for i, p in enumerate(random.sample(new_patients, k=int(len(new_patients) * 0.15))):
        uname = f"{slug(p.prenom)}.{slug(p.nom)[0]}{i}"
        db.session.add(User(username=uname, password=generate_password_hash("patient123"),
            role="patient", nom=p.nom, prenom=p.prenom, email=p.email,
            telephone=p.telephone, id_ref=str(p.id)))
        p.username = uname
    db.session.flush()

    patients = Patient.query.all()
    for p in new_patients:
        db.session.add(Dossier(num_dossier=f"DOS-{next_dos_num:04d}",
            date_creation=rd(d_min, d_max_past),
            diagnostic_general=random.choice(DIAGNOSTICS + ["Aucune pathologie chronique"] * 3),
            id_patient=p.id))
        next_dos_num += 1
    db.session.flush()

    # ═══════════════════ 3. MÉDICAMENTS + STOCKS ═══════════════════
    meds = Medicament.query.all()
    new_meds = []
    for i in range(n_medicaments_new):
        typ = random.choice(TYPES_MED)
        dose = random.choice(["5mg","10mg","250mg","500mg","1g","20mg","50mg","2.5mg","100mg"])
        lib = f"{typ.split('/')[0]} {chr(65+i%26)}{i} {dose}"
        m = Medicament(libelle=lib, type=typ, dosage=dose,
            prix=random.choice([300,500,600,800,900,1200,1500,2000,3500]),
            contre_indication=random.choice(["Insuffisance hepatique","Allergie connue au principe actif",
                "Insuffisance renale","Grossesse","Aucune connue"]),
            notice=f"Voie orale, respecter la posologie prescrite ({dose}).",
            code_barre=f"TRP{2000+i:06d}")
        db.session.add(m); new_meds.append(m)
    db.session.flush()
    meds = Medicament.query.all()

    for m in new_meds:
        qte = random.choice([0,5,10,18,25,40,60,90,150,250])
        seuil = random.choice([15,20,25,30])
        statut = "Epuise" if qte == 0 else ("Faible" if qte < seuil else "Normal")
        db.session.add(Stock(id_medicament=m.id, quantite=qte, seuil_alerte=seuil, statut=statut))
    db.session.flush()

    for s in Stock.query.filter(Stock.statut != "Normal").all():
        db.session.add(AlerteStock(id_medicament=s.id_medicament,
            type_alerte="Rupture de stock" if s.quantite == 0 else "Stock faible",
            date=rd(d_min, d_max_past), quantite_actuel=s.quantite,
            message=f"{s.medicament.libelle} : {s.quantite} unites restantes",
            statut=random.choices(["Non traite","Traite"], weights=[40,60])[0]))

    for _ in range(8):
        m1, m2 = random.sample(meds, 2)
        db.session.add(InteractionMedicamenteuse(id_med1=m1.id, id_med2=m2.id,
            niveau=random.choice(["modere","eleve","critique"]),
            description=f"{m1.libelle.split()[0]} + {m2.libelle.split()[0]} : surveillance recommandee"))
    db.session.flush()

    # ═══════════════════ 4. RDV / CONSULTATIONS / ORDONNANCES / FACTURES
    rdv_count = cons_count = ord_count = fac_count = tele_count = 0
    for p in random.sample(patients, k=min(420, len(patients))):
        for _ in range(random.randint(1, 3)):
            m = random.choice(medecins)
            past = random.random() < 0.75
            d = rd(d_min, d_max_past) if past else rd(today, d_max_fut)
            heure = f"{random.randint(8,16):02d}:{random.choice(['00','15','30','45'])}"
            typ = "Teleconsultation" if random.random() < 0.12 else "Presentiel"
            statut = random.choices(["Confirme","Annule","En attente"], weights=[70,10,20])[0] if not past \
                else random.choices(["Confirme","Annule"], weights=[88,12])[0]
            rdv = Rdv(id_patient=p.id, matricule=m.matricule, date=d, heure=heure, type=typ,
                      statut=statut, motif=random.choice(DIAGNOSTICS))
            db.session.add(rdv); db.session.flush(); rdv_count += 1

            if typ == "Teleconsultation":
                st = "Terminee" if (past and statut == "Confirme") else ("Annulee" if statut == "Annule" else "Planifiee")
                db.session.add(Teleconsultation(id_patient=p.id, matricule=m.matricule, id_rdv=rdv.id,
                    date_debut=f"{d} {heure}", statut=st, lien="https://meet.google.com/xyz-demo",
                    lien_envoye=True)); tele_count += 1

            if past and statut == "Confirme" and random.random() < 0.85:
                cons = Consultation(id_patient=p.id, matricule=m.matricule, date=d, id_rdv=rdv.id,
                    type=typ, observation="Examen clinique sans particularite majeure.",
                    diagnostic=random.choice(DIAGNOSTICS))
                db.session.add(cons); db.session.flush(); cons_count += 1

                if random.random() < 0.55:
                    ordo = Ordonnance(id_patient=p.id, matricule=m.matricule, date=d,
                        duree=random.choice([7,10,14,30]), id_consultation=cons.id,
                        statut_delivrance=random.choices(["En attente","Delivree"], weights=[30,70])[0])
                    db.session.add(ordo); db.session.flush(); ord_count += 1
                    for _ in range(random.randint(1, 3)):
                        med = random.choice(meds)
                        db.session.add(LigneOrdonnance(id_ordonnance=ordo.id, id_medicament=med.id,
                            posologie=random.choice(["1 cp matin","1 cp matin et soir","2 cp/jour","1 cp au coucher"]),
                            duree=f"{ordo.duree} jours"))

                montant = random.choice([3000,5000,7500,10000,15000,20000,25000])
                taux = 40 if p.assurance != "Aucune" else 0
                part_ass = int(montant * taux / 100)
                part_pat = montant - part_ass
                paye_total = random.random() < 0.7
                paye_partiel = (not paye_total) and random.random() < 0.5
                montant_paye = part_pat if paye_total else (part_pat // 2 if paye_partiel else 0)
                statut_fac = "Payee" if paye_total else ("Partielle" if paye_partiel else "Impayee")
                fac = Facture(id_patient=p.id, id_consultation=cons.id,
                    num_facture=f"FAC-{fac_count+3:04d}", montant=montant, part_assurance=part_ass,
                    part_patient=part_pat, montant_paye=montant_paye, reste_a_payer=part_pat - montant_paye,
                    statut=statut_fac, mode_paiement=random.choice(["Especes","Mobile Money","Carte","-"]) if montant_paye else "-",
                    date=d, date_echeance=d + timedelta(days=30))
                db.session.add(fac); db.session.flush(); fac_count += 1
                db.session.add(FactureLigne(id_facture=fac.id, libelle="Consultation medicale",
                    type_ligne="Consultation", quantite=1, prix_unitaire=montant, montant=montant))
                if montant_paye:
                    db.session.add(Paiement(id_facture=fac.id, id_patient=p.id, montant=montant_paye,
                        date=d, mode=fac.mode_paiement, statut="Valide"))

                if random.random() < 0.35:
                    db.session.add(ResultatExamen(id_patient=p.id, id_consultation=cons.id, matricule=m.matricule,
                        type=random.choice(["Bilan sanguin","Glycemie","Radio thorax","Echographie abdominale","Bilan lipidique"]),
                        categorie=random.choice(["Laboratoire","Imagerie"]), date=d,
                        statut=random.choice(["Prescrit","Preleve","Disponible"]),
                        commentaire="Resultats dans les valeurs attendues.", anormal=random.random() < 0.2))

                if random.random() < 0.5:
                    db.session.add(ConstanteVitale(id_patient=p.id, id_consultation=cons.id, date=d,
                        poids=round(random.uniform(45,95),1), taille=round(random.uniform(1.45,1.9),2),
                        tension_systolique=random.randint(100,150), tension_diastolique=random.randint(60,95),
                        temperature=round(random.uniform(36.2,38.5),1), frequence_cardiaque=random.randint(60,100),
                        saturation=random.randint(94,100), releve_par=m.username))
        if rdv_count % 400 == 0:
            db.session.flush()
    db.session.flush()

    # ═══════════════════ 5. ANTÉCÉDENTS / ALLERGIES / VACCINATIONS ═
    for p in random.sample(patients, k=int(len(patients) * 0.4)):
        db.session.add(Antecedent(id_patient=p.id, type_antecedent=random.choice(["Medical","Chirurgical","Familial"]),
            libelle=random.choice(DIAGNOSTICS), periode=random.choice(["2019","2021","Enfance","Depuis 2023"]),
            statut=random.choice(["Actif","Resolu"])))
    for p in random.sample(patients, k=int(len(patients) * 0.25)):
        db.session.add(AllergiePatient(id_patient=p.id,
            libelle=random.choice(["Penicilline","Ibuprofene","Arachide","Fruits de mer","Poussiere","Aspirine"]),
            type=random.choice(["Medicament","Aliment","Environnement"]),
            severite=random.choice(["Faible","Moderee","Elevee","Critique"]), date_constatee=rd(d_min, d_max_past)))
    for p in random.sample(patients, k=int(len(patients) * 0.5)):
        for _ in range(random.randint(1, 3)):
            db.session.add(Vaccination(id_patient=p.id,
                vaccin=random.choice(["Fievre jaune","Tetanos","Hepatite B","COVID-19","Rougeole","Meningite"]),
                date_administration=rd(d_min - timedelta(days=800), d_max_past), effectue_par="infirmier"))
    db.session.flush()

    # ═══════════════════ 6. CONTRATS ASSURANCE ═════════════════════
    for p in [p for p in patients if p.assurance != "Aucune"]:
        db.session.add(ContratAssurance(id_patient=p.id, assureur=p.assurance,
            num_contrat=f"{p.assurance[:4].upper()}-{2024+random.randint(0,2)}-{p.id:04d}",
            date_debut=date(2024,1,1), date_fin=date(2027,12,31),
            plafond_annuel=random.choice([300000,500000,750000,1000000]),
            montant_utilise=random.randint(0,150000),
            taux_prise_en_charge=random.choice([30,40,50,60,70]), statut="Actif"))
    db.session.flush()

    # ═══════════════════ 7. LITS / HOSPITALISATIONS ════════════════
    lits = []
    for svc in services:
        for n in range(1, 7):
            l = Lit(numero=f"{svc.libelle[:4]}-Ch{n}", statut="Libre", id_service=svc.id)
            db.session.add(l); lits.append(l)
    db.session.flush()

    for _ in range(70):
        p, m, lit, svc = random.choice(patients), random.choice(medecins), random.choice(lits), random.choice(services)
        entree = rd(d_min, d_max_past)
        en_cours = random.random() < 0.15
        sortie = None if en_cours else entree + timedelta(days=random.randint(1, 10))
        h = Hospitalisation(id_patient=p.id, matricule_medecin=m.matricule, id_lit=lit.id, id_service=svc.id,
            date_entree=entree, date_sortie=sortie, motif_admission=random.choice(DIAGNOSTICS),
            statut="En cours" if en_cours else "Sortie",
            diagnostic_sortie=None if en_cours else random.choice(DIAGNOSTICS), admis_par="receptionniste")
        db.session.add(h); db.session.flush()
        lit.statut = "Occupe" if en_cours else "Libre"
        for _ in range(random.randint(1, 3)):
            db.session.add(NoteSuivi(id_hospitalisation=h.id, note="Etat stable, suivi conforme au protocole.",
                redige_par="infirmier"))
    db.session.flush()

    # ═══════════════════ 8. VENTES PHARMACIE ═══════════════════════
    for _ in range(350):
        med = random.choice(meds)
        qte = random.randint(1, 4)
        db.session.add(VentePharmacie(id_medicament=med.id, quantite=qte, prix_unitaire=med.prix,
            montant_total=med.prix * qte, date=rd(d_min, d_max_past), vendeur="pharmacien",
            nom_acheteur=f"{random.choice(PRENOMS_M+PRENOMS_F)} {random.choice(NOMS)}",
            id_patient=random.choice(patients).id if random.random() < 0.6 else None))

    # ═══════════════════ 9. LISTE D'ATTENTE / TRIAGE / DEMANDES RDV
    for i, svc in enumerate(random.choices(services, k=60)):
        db.session.add(ListeAttente(id_patient=random.choice(patients).id, id_service=svc.id,
            numero_ordre=i+1, statut=random.choice(["En attente","Appele","Traite"]),
            priorite=random.choices(["Normal","Prioritaire","Urgent"], weights=[70,20,10])[0],
            motif=random.choice(DIAGNOSTICS)))
    for _ in range(40):
        db.session.add(Triage(id_patient=random.choice(patients).id, motif=random.choice(DIAGNOSTICS),
            niveau_urgence=random.choice(["1 - Critique","2 - Urgent","3 - Moins urgent"]),
            tension=f"{random.randint(100,150)}/{random.randint(60,95)}",
            temperature=round(random.uniform(36.5,39.5),1), saturation=random.randint(92,100),
            frequence_cardiaque=random.randint(60,120),
            statut=random.choice(["En cours","Traite"]), pris_en_charge_par=random.choice(medecins).matricule))
    for p in random.sample(patients, k=80):
        db.session.add(DemandeRdv(id_patient=p.id, id_service=random.choice(services).id,
            type=random.choice(["Presentiel","Teleconsultation"]), motif=random.choice(DIAGNOSTICS),
            statut=random.choices(["En attente","Traite","Annule"], weights=[30,60,10])[0],
            date_demande=rd(d_min, today)))

    # ═══════════════════ 10. NOTIFICATIONS / HISTORIQUE / SMS ══════
    for p in random.sample(patients, k=150):
        db.session.add(Notification(type=random.choice(["Rappel RDV","Resultat disponible","Info"]),
            objet="Notification automatique", contenu="Mise a jour concernant votre dossier.",
            date=rd(d_min, today).strftime("%Y-%m-%d %H:%M"), id_patient=p.id,
            lu=random.random() < 0.6))
    for p in random.sample(patients, k=300):
        db.session.add(Historique(description=f"Action sur le dossier de {p.prenom} {p.nom}",
            type=random.choice(["Consultation","Rendez-vous","Creation patient","Facturation"]),
            id_user=random.choice(["receptionniste","admin"] + [m.username for m in medecins]),
            id_patient=p.id, date_action=rd(d_min, today).strftime("%Y-%m-%d %H:%M")))
    for p in random.sample(patients, k=100):
        db.session.add(SmsEnvoye(numero=p.telephone, message="Rappel : vous avez un rendez-vous prochainement.",
            date=rd(d_min, today).strftime("%Y-%m-%d %H:%M"), statut="success", par="system", id_patient=p.id))

    # ── Marqueur d'idempotence ──
    db.session.add(Historique(type=MARKER, description="Jeu de donnees de demonstration enrichi genere"))
    db.session.commit()

    print(f"✅ Jeu de données enrichi : {len(new_patients)} patients ajoutés (total {Patient.query.count()}), "
          f"{len(new_medecins)} médecins ajoutés (total {Medecin.query.count()}), "
          f"{len(new_meds)} médicaments ajoutés (total {Medicament.query.count()}), "
          f"{rdv_count} RDV, {cons_count} consultations, {ord_count} ordonnances, {fac_count} factures.")
    return True


if __name__ == "__main__":
    from app import app
    from models import db as _db
    import seed
    with app.app_context():
        _db.create_all()
        if seed.run_seed():
            print("✅ Socle initial créé.")
        else:
            print("ℹ️  Socle déjà présent — inchangé.")
        seed.ensure_default_accounts()
        run_seed_demo()
