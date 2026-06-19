#!/usr/bin/env python3
# =============================================================
# SGRDMS LE TROPICAL v12 — Application Flask complète
# Déploiement : Render (PostgreSQL via DATABASE_URL)
# =============================================================
# =======================================================
# Imports & initialisation Flask
# =======================================================

#!/usr/bin/env python3
# SGRDMS LE TROPICAL v5 — Part 1: imports + DB complet
from flask import Flask,render_template_string,request,redirect,url_for,session,flash,jsonify,Response
from functools import wraps
from datetime import datetime,date,timedelta
import json,copy,os,base64,io
from dotenv import load_dotenv

load_dotenv()  # charge .env en local, ignoré sur Render (variables injectées directement)

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","tropical_sgrdms_v12_2026_change_me")

# ─── Configuration SMS (renseigner les variables d'environnement) ───
SMS_CONFIG={
    "provider":  os.environ.get("SMS_PROVIDER",""),
    "api_key":   os.environ.get("SMS_API_KEY",""),
    "api_secret":os.environ.get("SMS_API_SECRET",""),
    "sender_id": os.environ.get("SMS_SENDER_ID","LE TROPICAL"),
    "base_url":  os.environ.get("SMS_BASE_URL",""),
}

def send_sms(numero, message):
    """Envoie un SMS via le provider configure dans SMS_CONFIG.
    Si aucun provider n'est configure, le message est journalise (historique)
    et marque comme 'en attente de configuration' sans bloquer l'application."""
    if not SMS_CONFIG.get("provider") or not SMS_CONFIG.get("api_key"):
        return {"success":False,"status":"non_configure","detail":"Provider SMS non configure (renseigner SMS_CONFIG)."}
    try:
        import requests
        # --- A adapter selon le provider choisi (Twilio, Orange SMS API, etc.) ---
        # Exemple generique :
        # resp = requests.post(SMS_CONFIG["base_url"], data={...}, auth=(...), timeout=10)
        # return {"success": resp.ok, "status": resp.status_code, "detail": resp.text}
        return {"success":False,"status":"non_implemente","detail":"Logique d'envoi a implementer pour ce provider."}
    except Exception as e:
        return {"success":False,"status":"erreur","detail":str(e)}

# =======================================================
# DB — Base de données complète (utilisateurs, clinique, pharmacie, opérations)
# =======================================================

# =======================================================
# DB — Comptes utilisateurs (admin, médecins, réceptionniste, pharmacien, patients)
# =======================================================

DB={
    "users":{
        "admin":{"password":"admin123","role":"admin","nom":"Systeme","prenom":"Admin","email":"admin@tropical.sn","telephone":"33 951 00 00","photo":"","id_ref":0},
        "dr.diallo":{"password":"med123","role":"medecin","nom":"Diallo","prenom":"Cheikh","email":"dr.diallo@tropical.sn","telephone":"77 111 22 33","photo":"","id_ref":"MED002","status_med":"Disponible","teleconsult_actif":True},
        "dr.ndiaye":{"password":"med123","role":"medecin","nom":"Ndiaye","prenom":"Rokhaya","email":"dr.ndiaye@tropical.sn","telephone":"76 222 33 44","photo":"","id_ref":"MED001","status_med":"Disponible","teleconsult_actif":False},
        "dr.sarr":{"password":"med123","role":"medecin","nom":"Sarr","prenom":"Abdoulaye","email":"dr.sarr@tropical.sn","telephone":"70 333 44 55","photo":"","id_ref":"MED004","status_med":"En conge","teleconsult_actif":True},
        "dr.fall":{"password":"med123","role":"medecin","nom":"Fall","prenom":"Mariama","email":"dr.fall@tropical.sn","telephone":"77 444 55 66","photo":"","id_ref":"MED005","status_med":"Disponible","teleconsult_actif":False},
        "dr.ba":{"password":"med123","role":"medecin","nom":"Ba","prenom":"Oumar","email":"dr.ba@tropical.sn","telephone":"76 555 66 77","photo":"","id_ref":"MED006","status_med":"Disponible","teleconsult_actif":True},
        "dr.gueye":{"password":"med123","role":"medecin","nom":"Gueye","prenom":"Aminata","email":"dr.gueye@tropical.sn","telephone":"70 666 77 88","photo":"","id_ref":"MED007","status_med":"Disponible","teleconsult_actif":False},
        "dr.diop":{"password":"med123","role":"medecin","nom":"Diop","prenom":"Moussa","email":"dr.diop@tropical.sn","telephone":"77 777 88 99","photo":"","id_ref":"MED008","status_med":"Disponible","teleconsult_actif":False},
        "dr.toure":{"password":"med123","role":"medecin","nom":"Toure","prenom":"Fatou","email":"dr.toure@tropical.sn","telephone":"76 888 99 00","photo":"","id_ref":"MED003","status_med":"Disponible","teleconsult_actif":True},
        "receptionniste":{"password":"recep123","role":"receptionniste","nom":"Ndiaye","prenom":"Fatou","email":"recep@tropical.sn","telephone":"77 444 55 66","photo":"","id_ref":1},
        "pharmacien":{"password":"pharma123","role":"pharmacien","nom":"Fall","prenom":"Mamadou","email":"pharma@tropical.sn","telephone":"76 555 66 77","photo":"","id_ref":1},
        "ibra.sow":{"password":"patient123","role":"patient","nom":"Sow","prenom":"Ibrahima","email":"ibra@email.com","telephone":"77 123 45 67","photo":"","id_ref":1},
        "aminata.d":{"password":"patient123","role":"patient","nom":"Diallo","prenom":"Aminata","email":"aminata@email.com","telephone":"76 234 56 78","photo":"","id_ref":2},
    },
    "patients":[
        {"id":1,"nom":"Sow","prenom":"Ibrahima","sexe":"M","telephone":"77 123 45 67","email":"ibra@email.com","date_naissance":"1990-05-12","adresse":"Dakar, Plateau","assurance":"IPRES","username":"ibra.sow","statut":"Actif","groupe_sanguin":"O+","photo":""},
        {"id":2,"nom":"Diallo","prenom":"Aminata","sexe":"F","telephone":"76 234 56 78","email":"aminata@email.com","date_naissance":"1985-11-23","adresse":"Thies","assurance":"CSS","username":"aminata.d","statut":"Actif","groupe_sanguin":"A+","photo":""},
        {"id":3,"nom":"Ndiaye","prenom":"Moussa","sexe":"M","telephone":"70 345 67 89","email":"moussa@email.com","date_naissance":"2000-03-07","adresse":"Ziguinchor","assurance":"Aucune","username":"","statut":"Actif","groupe_sanguin":"Non connu","photo":""},
    ],
    "medecins":[
        {"matricule":"MED001","nom":"Ndiaye","prenom":"Rokhaya","specialite":"Pediatrie","telephone":"76 222 33 44","email":"dr.ndiaye@tropical.sn","id_service":1,"username":"dr.ndiaye","est_chef":True,"teleconsult_actif":False,"id_centre":1},
        {"matricule":"MED002","nom":"Diallo","prenom":"Cheikh","specialite":"Medecine Generaliste","telephone":"77 111 22 33","email":"dr.diallo@tropical.sn","id_service":2,"username":"dr.diallo","est_chef":True,"teleconsult_actif":True,"id_centre":1},
        {"matricule":"MED003","nom":"Toure","prenom":"Fatou","specialite":"Medecine Generaliste","telephone":"76 888 99 00","email":"dr.toure@tropical.sn","id_service":2,"username":"dr.toure","est_chef":False,"teleconsult_actif":True,"id_centre":1},
        {"matricule":"MED004","nom":"Sarr","prenom":"Abdoulaye","specialite":"Gynecologie","telephone":"70 333 44 55","email":"dr.sarr@tropical.sn","id_service":3,"username":"dr.sarr","est_chef":True,"teleconsult_actif":True,"id_centre":1},
        {"matricule":"MED005","nom":"Fall","prenom":"Mariama","specialite":"Cardiologie","telephone":"77 444 55 66","email":"dr.fall@tropical.sn","id_service":4,"username":"dr.fall","est_chef":True,"teleconsult_actif":False,"id_centre":1},
        {"matricule":"MED006","nom":"Ba","prenom":"Oumar","specialite":"Cardiologie","telephone":"76 555 66 77","email":"dr.ba@tropical.sn","id_service":4,"username":"dr.ba","est_chef":False,"teleconsult_actif":True,"id_centre":1},
        {"matricule":"MED007","nom":"Gueye","prenom":"Aminata","specialite":"Urgences","telephone":"70 666 77 88","email":"dr.gueye@tropical.sn","id_service":5,"username":"dr.gueye","est_chef":True,"teleconsult_actif":False,"id_centre":1},
        {"matricule":"MED008","nom":"Diop","prenom":"Moussa","specialite":"Biologie medicale","telephone":"77 777 88 99","email":"dr.diop@tropical.sn","id_service":6,"username":"dr.diop","est_chef":True,"teleconsult_actif":False,"id_centre":1},
    ],
    "centres":[
        {"id":1,"nom":"LE TROPICAL","ville":"Thies","adresse":"Diaxao, Thies","telephone":"33 951 00 00","tarif_ticket":2000},
    ],
    "disponibilites":[
        {"id":1,"matricule":"MED001","id_centre":1,"jour_semaine":0,"heure_debut":"08:00","heure_fin":"12:00","duree_creneau":30},
        {"id":2,"matricule":"MED001","id_centre":1,"jour_semaine":2,"heure_debut":"08:00","heure_fin":"12:00","duree_creneau":30},
        {"id":3,"matricule":"MED002","id_centre":1,"jour_semaine":1,"heure_debut":"08:00","heure_fin":"13:00","duree_creneau":20},
        {"id":4,"matricule":"MED002","id_centre":1,"jour_semaine":3,"heure_debut":"08:00","heure_fin":"13:00","duree_creneau":20},
    ],
    "sms_envoyes":[],
    "services":[
        {"id":1,"libelle":"Pediatrie","description":"Soins pour enfants (0-15 ans)","id_centre":1},
        {"id":2,"libelle":"Medecine Generaliste","description":"Consultation adulte generale","id_centre":1},
        {"id":3,"libelle":"Gynecologie","description":"Sante de la femme et maternite","id_centre":1},
        {"id":4,"libelle":"Cardiologie","description":"Maladies du coeur et vaisseaux","id_centre":1},
        {"id":5,"libelle":"Urgences","description":"Prise en charge urgente 24h/24","id_centre":1},
        {"id":6,"libelle":"Laboratoire","description":"Analyses biologiques et medicales","id_centre":1},
    ],
    "rdvs":[
        {"id":1,"id_patient":1,"matricule":"MED002","date":"2026-06-10","heure":"08:00","type":"Presentiel","statut":"Confirme","motif":"Douleur thoracique","lien_teleconsult":None},
        {"id":2,"id_patient":2,"matricule":"MED001","date":"2026-06-11","heure":"09:00","type":"Presentiel","statut":"En attente","motif":"Vaccination","lien_teleconsult":None},
        {"id":3,"id_patient":1,"matricule":"MED002","date":"2026-06-10","heure":"10:00","type":"Teleconsultation","statut":"Confirme","motif":"Suivi tension","lien_teleconsult":"https://meet.google.com/abc-defg-hij"},
    ],
    "demandes_rdv":[
        {"id":1,"id_patient":1,"id_service":1,"type":"Presentiel","motif":"Renouvellement ordonnance","statut":"En attente","date_demande":"2026-06-06","traite_par":None},
    ],
    "consultations":[
        {"id":1,"id_patient":1,"matricule":"MED002","date":"2026-06-05","observation":"Pression 140/90","diagnostic":"Hypertension arterielle","type":"Presentiel","id_ordonnance":1,"id_facture":1,"id_resultat":1},
        {"id":2,"id_patient":2,"matricule":"MED001","date":"2026-06-04","observation":"Bonne sante generale","diagnostic":"Bilan normal","type":"Presentiel","id_ordonnance":None,"id_facture":2,"id_resultat":None},
    ],
    "ordonnances":[
        {"id":1,"id_consultation":1,"id_patient":1,"matricule":"MED002","date":"2026-06-05","duree":30,"lignes":[
            {"id_medicament":1,"libelle":"Amlodipine 5mg","posologie":"1 cp le soir","duree":"30 jours"},
            {"id_medicament":4,"libelle":"Metformine 500mg","posologie":"1 cp matin et soir","duree":"30 jours"},
        ]},
    ],
    "resultats_examens":[
        {"id":1,"id_patient":1,"id_consultation":1,"matricule":"MED002","type":"Bilan sanguin","date":"2026-06-05","commentaire":"Glycemie legerement elevee (1.26 g/L). Cholesterol 2.1 g/L.","statut":"Disponible","fichier":""},
    ],
    "documents_patient":[
        {"id":1,"id_patient":1,"type_document":"Resultat examen","nom_fichier":"bilan_sow.pdf","type_fichier":"PDF","date_creation":"2026-06-05","ref_id":1,"ref_type":"resultat"},
        {"id":2,"id_patient":1,"type_document":"Ordonnance","nom_fichier":"ordonnance_0001.pdf","type_fichier":"PDF","date_creation":"2026-06-05","ref_id":1,"ref_type":"ordonnance"},
        {"id":3,"id_patient":1,"type_document":"Facture","nom_fichier":"facture_FAC-0001.pdf","type_fichier":"PDF","date_creation":"2026-06-05","ref_id":1,"ref_type":"facture"},
    ],
    # ✅ v5: part_payee + reste_a_payer
    "factures":[
        {"id":1,"num_facture":"FAC-0001","id_patient":1,"id_consultation":1,"montant":15000,"date":"2026-06-05","statut":"Payee","mode_paiement":"Especes","part_assurance":6000,"part_patient":9000,"montant_paye":9000,"reste_a_payer":0},
        {"id":2,"num_facture":"FAC-0002","id_patient":2,"id_consultation":2,"montant":8500,"date":"2026-06-04","statut":"Impayee","mode_paiement":"-","part_assurance":4250,"part_patient":4250,"montant_paye":0,"reste_a_payer":4250},
    ],
    "paiements":[
        {"id":1,"id_facture":1,"id_patient":1,"montant":9000,"date":"2026-06-05","mode":"Especes","statut":"Valide"},
    ],
    "teleconsultations":[
        {"id":1,"id_patient":1,"matricule":"MED001","id_rdv":3,"date_debut":"2026-06-10 10:00","statut":"Planifiee","lien":"https://meet.google.com/abc-defg-hij","lien_envoye":True},
    ],
    "medicaments":[
        {"id":1,"libelle":"Amlodipine 5mg","type":"Antihypertenseur","dosage":"5mg","prix":900,"id_stock":1,"contre_indication":"Insuffisance hepatique","notice":"Prendre le soir"},
        {"id":2,"libelle":"Amoxicilline 250mg","type":"Antibiotique","dosage":"250mg","prix":1200,"id_stock":2,"contre_indication":"Allergie penicilline","notice":"Completer le traitement"},
        {"id":3,"libelle":"Paracetamol 500mg","type":"Antalgique","dosage":"500mg","prix":500,"id_stock":3,"contre_indication":"Insuffisance hepatique","notice":"Max 4g/jour"},
        {"id":4,"libelle":"Metformine 500mg","type":"Antidiabetique","dosage":"500mg","prix":600,"id_stock":4,"contre_indication":"Insuffisance renale","notice":"Prendre pendant les repas"},
        {"id":5,"libelle":"Ibuprofene 400mg","type":"Anti-inflammatoire","dosage":"400mg","prix":800,"id_stock":5,"contre_indication":"Ulcere gastrique","notice":"Max 3 prises/jour"},
    ],
    "stocks":[
        {"id":1,"id_medicament":1,"quantite":80,"date_stock":"2026-06-01","statut":"Normal","seuil_alerte":20},
        {"id":2,"id_medicament":2,"quantite":15,"date_stock":"2026-06-01","statut":"Faible","seuil_alerte":20},
        {"id":3,"id_medicament":3,"quantite":200,"date_stock":"2026-06-01","statut":"Normal","seuil_alerte":30},
        {"id":4,"id_medicament":4,"quantite":150,"date_stock":"2026-06-01","statut":"Normal","seuil_alerte":20},
        {"id":5,"id_medicament":5,"quantite":0,"date_stock":"2026-06-01","statut":"Epuise","seuil_alerte":20},
    ],
    "alertes_stock":[
        {"id":1,"id_medicament":2,"type_alerte":"Stock faible","date":"2026-06-05","message":"Amoxicilline 250mg : stock faible (15 unites)","quantite_actuel":15,"statut":"Non traite"},
        {"id":2,"id_medicament":5,"type_alerte":"Rupture de stock","date":"2026-06-04","message":"Ibuprofene 400mg : rupture de stock","quantite_actuel":0,"statut":"Non traite"},
    ],
    # ✅ v5: ventes pharmacien
    "ventes_pharmacie":[
        {"id":1,"id_medicament":3,"libelle":"Paracetamol 500mg","quantite":2,"prix_unitaire":500,"montant_total":1000,"date":"2026-06-05","vendeur":"pharmacien","id_patient":None,"nom_acheteur":"Vente libre"},
    ],
    "liste_attente":[
        {"id":1,"id_patient":1,"id_service":1,"numero_ordre":1,"date_arrivee":"2026-06-10 08:05","statut":"En attente","priorite":"Normal","motif":"Consultation"},
        {"id":2,"id_patient":2,"id_service":2,"numero_ordre":2,"date_arrivee":"2026-06-10 08:20","statut":"En attente","priorite":"Prioritaire","motif":"Suivi"},
    ],
    "triage":[
        {"id":1,"id_patient":3,"date_arrivee":"2026-06-10 07:45","motif":"Douleur abdominale aigue","niveau_urgence":"2 - Urgent","tension":"130/85","temperature":38.5,"saturation":97,"frequence_cardiaque":102,"statut":"En cours","pris_en_charge_par":"MED006","observations":"Patient agite, douleur 8/10"},
    ],
    "tickets":[],
    "contrats_assurance":[
        {"id":1,"id_patient":1,"assureur":"IPRES","num_contrat":"IPRES-2024-001","date_debut":"2024-01-01","date_fin":"2026-12-31","plafond_annuel":500000,"montant_utilise":15000,"taux_prise_en_charge":40,"statut":"Actif"},
        {"id":2,"id_patient":2,"assureur":"CSS","num_contrat":"CSS-2025-002","date_debut":"2025-01-01","date_fin":"2027-12-31","plafond_annuel":750000,"montant_utilise":8500,"taux_prise_en_charge":50,"statut":"Actif"},
    ],
    "interactions_medicamenteuses":[
        {"id":1,"id_med1":1,"id_med2":4,"niveau":"modere","description":"Amlodipine + Metformine : surveiller glycemie (potentialisation hypoglycemie)"},
        {"id":2,"id_med1":2,"id_med2":5,"niveau":"eleve","description":"Amoxicilline + Ibuprofene : risque hemorragie digestive eleve"},
        {"id":3,"id_med1":3,"id_med2":5,"niveau":"modere","description":"Paracetamol + Ibuprofene : eviter association prolongee (toxicite renale)"},
        {"id":4,"id_med1":1,"id_med2":5,"niveau":"eleve","description":"Amlodipine + Ibuprofene : diminution de l effet antihypertenseur, risque IRA"},
    ],
    "allergies_patient":[
        {"id":1,"id_patient":1,"libelle":"Ibuprofene","type":"Medicament","severite":"Elevee","date_constatee":"2025-01-15"},
        {"id":2,"id_patient":2,"libelle":"Penicilline","type":"Medicament","severite":"Critique","date_constatee":"2024-06-01"},
    ],
    "dossiers":[
        {"id":1,"id_patient":1,"num_dossier":"DOS-0001","date_creation":"2026-06-06","diagnostic_general":"Hypertension arterielle"},
        {"id":2,"id_patient":2,"num_dossier":"DOS-0002","date_creation":"2026-06-04","diagnostic_general":"Aucune pathologie chronique"},
    ],
    "notifications":[
        {"id":1,"type":"Rappel RDV","objet":"RDV demain a 08h00","contenu":"Votre RDV est prevu le 10/06 a 08h00 avec Dr. Diallo.","id_patient":1,"date":"2026-06-09","lu":False,"dest_role":None,"dest_user":None,"expediteur":None},
        {"id":2,"type":"Resultat disponible","objet":"Vos resultats d'examen sont disponibles","contenu":"Vos resultats de bilan sanguin du 05/06 sont disponibles.","id_patient":1,"date":"2026-06-05","lu":False,"dest_role":None,"dest_user":None,"expediteur":"dr.diallo"},
        {"id":3,"type":"Stock faible","objet":"Alerte stock Amoxicilline","contenu":"Stock Amoxicilline 250mg en dessous du seuil (15 unites).","id_patient":None,"date":"2026-06-05","lu":False,"dest_role":"pharmacien","dest_user":"pharmacien","expediteur":"system"},
        {"id":4,"type":"Info","objet":"Bienvenue sur SGRDMS v5","contenu":"Le systeme a ete mis a jour. Nouvelles fonctionnalites disponibles.","id_patient":None,"date":"2026-06-10","lu":False,"dest_role":"admin","dest_user":"admin","expediteur":"system"},
    ],
    "historiques":[
        {"id":1,"date_action":"2026-06-06 08:00","description":"Nouveau patient : Ibrahima Sow","type":"Creation patient","id_user":"receptionniste","id_patient":1,"matricule":None},
        {"id":2,"date_action":"2026-06-06 09:00","description":"RDV confirme - Ibrahima Sow / Dr. Diallo","type":"Rendez-vous","id_user":"receptionniste","id_patient":1,"matricule":"MED001"},
        {"id":3,"date_action":"2026-06-05 10:00","description":"Consultation - HTA stade 1","type":"Consultation","id_user":"dr.diallo","id_patient":1,"matricule":"MED001"},
    ],
    "_c":{"rdvs":3,"patients":3,"cons":2,"ords":1,"facts":2,"teles":1,"notifs":4,"hists":3,"docs":3,"demandes":1,"stocks":5,"meds":5,"services":6,"medecins":8,"dossiers":2,"paiements":1,"tickets":0,"attente":2,"triage":1,"ventes":1,"contrats":2,"interactions":4,"allergies":2,"centres":1,"sms":0,"disponibilites":4}
}
# SGRDMS v5 — Part 2: helpers, auth, CSS, layout, PDF, Login

# =======================================================
# Fonctions utilitaires, authentification (login_required, role_required)
# =======================================================

def nid(k): DB["_c"][k]+=1; return DB["_c"][k]
def pname(pid):
    p=next((x for x in DB["patients"] if x["id"]==pid),None)
    return f"{p['prenom']} {p['nom']}" if p else "Inconnu"
def mname(mat):
    m=next((x for x in DB["medecins"] if x["matricule"]==mat),None)
    return f"Dr. {m['prenom']} {m['nom']}" if m else "Inconnu"
def sname(sid):
    s=next((x for x in DB["services"] if x["id"]==sid),None)
    return s["libelle"] if s else "?"
def cname(cid):
    c=next((x for x in DB.get("centres",[]) if x["id"]==cid),None)
    return c["nom"] if c else "?"
def gen_matricule():
    """Génère un matricule MEDxxx unique, sans doublon, en se basant sur le plus grand numéro existant."""
    nums=[]
    for m in DB["medecins"]:
        mat=m.get("matricule","")
        if mat.startswith("MED") and mat[3:].isdigit():
            nums.append(int(mat[3:]))
    nxt=(max(nums)+1) if nums else 1
    while True:
        cand=f"MED{nxt:03d}"
        if not any(m["matricule"]==cand for m in DB["medecins"]):
            return cand
        nxt+=1
def med_centres(m):
    """Retourne la liste des id_centre rattachés à un médecin (multi-centre), avec repli sur id_centre."""
    cs=m.get("centres")
    if cs: return cs
    return [m.get("id_centre",1)]
def med_in_centre(m,cid):
    return int(cid) in [int(x) for x in med_centres(m)]
def tarif_centre(cid):
    c=next((x for x in DB.get("centres",[]) if x["id"]==cid),None)
    return c.get("tarif_ticket",0) if c else 0
JOURS_SEMAINE=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
def creneaux_disponibles(matricule,date_str,id_centre=None):
    """Calcule les créneaux libres d'un médecin pour une date donnée, à partir de ses disponibilités
    et des RDV déjà pris (hors annulés)."""
    try:
        d=datetime.strptime(date_str,"%Y-%m-%d")
    except (ValueError,TypeError):
        return []
    jour=d.weekday()
    disp_list=[x for x in DB.get("disponibilites",[]) if x["matricule"]==matricule and x["jour_semaine"]==jour]
    if id_centre:
        disp_list=[x for x in disp_list if x["id_centre"]==int(id_centre)]
    pris=set(r["heure"] for r in DB["rdvs"] if r["matricule"]==matricule and r["date"]==date_str and r["statut"]!="Annule")
    creneaux=[]
    for disp in disp_list:
        hd=datetime.strptime(disp["heure_debut"],"%H:%M")
        hf=datetime.strptime(disp["heure_fin"],"%H:%M")
        pas=disp.get("duree_creneau",30)
        cur=hd
        while cur<hf:
            hh=cur.strftime("%H:%M")
            if hh not in pris:
                creneaux.append(hh)
            cur+=timedelta(minutes=pas)
    return sorted(set(creneaux))
def get_pat(username):
    uid=DB["users"].get(username,{}).get("id_ref")
    return next((p for p in DB["patients"] if p["id"]==uid),None)
def get_med(username):
    mat=DB["users"].get(username,{}).get("id_ref")
    return next((m for m in DB["medecins"] if m["matricule"]==mat),None)
def add_hist(desc,typ,username,id_patient=None,matricule=None):
    DB["historiques"].append({"id":nid("hists"),"date_action":datetime.now().strftime("%Y-%m-%d %H:%M"),"description":desc,"type":typ,"id_user":username,"id_patient":id_patient,"matricule":matricule})
def add_notif(id_patient,typ,objet,contenu,dest_user=None,dest_role=None,expediteur=None):
    DB["notifications"].append({"id":nid("notifs"),"type":typ,"objet":objet,"contenu":contenu,"id_patient":id_patient,"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"lu":False,"dest_role":dest_role,"dest_user":dest_user,"expediteur":expediteur})
def get_notifs_user(username,role,id_patient=None):
    res=[]
    for n in DB["notifications"]:
        if n.get("dest_user")==username: res.append(n); continue
        if n.get("dest_role")==role and not n.get("dest_user"): res.append(n); continue
        if role=="patient" and id_patient and n.get("id_patient")==id_patient and not n.get("dest_role") and not n.get("dest_user"): res.append(n); continue
    return sorted(res,key=lambda x:x["date"],reverse=True)
def unread_count(username,role,id_patient=None):
    return sum(1 for n in get_notifs_user(username,role,id_patient) if not n["lu"])

def get_contrat_assurance(id_patient):
    """Retourne le contrat assurance actif d un patient"""
    today=date.today().strftime("%Y-%m-%d")
    return next((c for c in DB.get("contrats_assurance",[]) if c["id_patient"]==id_patient and c.get("date_debut","")<=today<=c.get("date_fin","2099-12-31") and c.get("statut")=="Actif"),None)

def reste_plafond(id_patient):
    """Calcule le montant restant du plafond annuel"""
    c=get_contrat_assurance(id_patient)
    if not c: return 0
    return max(0, c["plafond_annuel"] - c.get("montant_utilise",0))

def verifier_interactions_ordonnance(id_patient, ids_medicaments):
    """
    Verifie interactions, contre-indications et allergies.
    Retourne (bloquant:bool, alertes:list[dict])
    """
    alertes = []
    bloquant = False
    ids = [int(x) for x in ids_medicaments if x]
    meds = [m for m in DB["medicaments"] if m["id"] in ids]
    allergies = [a for a in DB.get("allergies_patient",[]) if a["id_patient"]==id_patient]
    # Verifier allergies
    for med in meds:
        for al in allergies:
            if al["libelle"].lower() in med["libelle"].lower() or med["libelle"].lower() in al["libelle"].lower():
                sev = al.get("severite","Elevee")
                alertes.append({"niveau": "critique" if sev=="Critique" else "eleve",
                    "message": f"ALLERGIE : {med['libelle']} — Patient allergique ({sev}). Constatee le {al['date_constatee']}.",
                    "bloquant": True})
                bloquant = True
    # Verifier contre-indications du patient (via diagnostic dossier)
    doss = next((d for d in DB.get("dossiers",[]) if d["id_patient"]==id_patient), None)
    diagn = (doss.get("diagnostic_general","") if doss else "").lower()
    ci_map = {
        "insuffisance hepatique": [1,3],   # Amlodipine, Paracetamol
        "insuffisance renale":    [4],      # Metformine
        "ulcere gastrique":       [5],      # Ibuprofene
        "allergie penicilline":   [2],      # Amoxicilline
    }
    for ci_diag, ci_meds in ci_map.items():
        if ci_diag in diagn:
            for mid in ci_meds:
                if mid in ids:
                    med_obj = next((m for m in DB["medicaments"] if m["id"]==mid), None)
                    if med_obj:
                        alertes.append({"niveau":"eleve",
                            "message": f"CONTRE-INDICATION : {med_obj['libelle']} — Patient : {ci_diag.upper()}.",
                            "bloquant": True})
                        bloquant = True
    # Verifier interactions entre les medicaments prescrits
    for inter in DB.get("interactions_medicamenteuses",[]):
        if inter["id_med1"] in ids and inter["id_med2"] in ids:
            niv = inter["niveau"]
            est_bloquant = niv in ("eleve","critique")
            alertes.append({"niveau": niv,
                "message": f"INTERACTION {niv.upper()} : {inter['description']}",
                "bloquant": est_bloquant})
            if est_bloquant:
                bloquant = True
    # Verifier traitements en cours (ordonnances actives)
    from datetime import date as _date
    today = _date.today().strftime("%Y-%m-%d")
    ords_actives = [o for o in DB.get("ordonnances",[]) if o["id_patient"]==id_patient]
    if ords_actives:
        last_ordo = max(ords_actives, key=lambda x: x["date"])
        ids_en_cours = [l["id_medicament"] for l in last_ordo.get("lignes",[])]
        for mid in ids:
            if mid in ids_en_cours:
                med_obj = next((m for m in DB["medicaments"] if m["id"]==mid), None)
                if med_obj:
                    alertes.append({"niveau":"modere",
                        "message": f"TRAITEMENT EN COURS : {med_obj['libelle']} est deja prescrit (ordonnance du {last_ordo['date']}).",
                        "bloquant": False})
    return bloquant, alertes

def verifier_plafond_assurance(id_patient, montant_nouveau):
    """
    Verifie si le plafond annuel est atteint avant prise en charge.
    Retourne (bloque:bool, contrat, message:str)
    """
    contrat = get_contrat_assurance(id_patient)
    if not contrat:
        return False, None, ""
    utilise = contrat.get("montant_utilise", 0)
    plafond = contrat["plafond_annuel"]
    taux = contrat["taux_prise_en_charge"] / 100
    part_ass_nouvelle = int(montant_nouveau * taux)
    if utilise + part_ass_nouvelle > plafond:
        reste = max(0, plafond - utilise)
        msg = (f"PLAFOND ATTEINT : Assurance {contrat['assureur']} — "
               f"Plafond annuel : {plafond:,} FCFA. "
               f"Deja utilise : {utilise:,} FCFA. "
               f"Reste disponible : {reste:,} FCFA. "
               f"Montant demande (part assurance) : {part_ass_nouvelle:,} FCFA. "
               f"La prise en charge assurance ne peut pas etre accordee.")
        return True, contrat, msg
    return False, contrat, ""

def login_required(f):
    @wraps(f)
    def d(*a,**k):
        if "user" not in session: return redirect(url_for("login"))
        return f(*a,**k)
    return d
def role_required(*roles):
    def dec(f):
        @wraps(f)
        def d(*a,**k):
            if session.get("role") not in roles:
                flash("Acces non autorise.","danger"); return redirect(url_for("dashboard"))
            return f(*a,**k)
        return d
    return dec

# =======================================================
# CSS, Sidebar, Topbar, Page builder, PDF (gen_pdf), Page Login
# =======================================================

CSS="""<style>
:root{--g1:#16a34a;--g2:#15803d;--g3:#14532d;--gl:#dcfce7;--gm:#bbf7d0;--gd:#86efac;--acc:#0ea5e9;--warn:#f59e0b;--err:#ef4444;--bg:#f0fdf4;--card:#ffffff;--txt:#1a2e1a;--muted:#4b7a4b;--sw:260px;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);font-family:'Segoe UI',system-ui,sans-serif;color:var(--txt);}
#sb{position:fixed;top:0;left:0;width:var(--sw);height:100vh;background:var(--g3);overflow-y:auto;z-index:1040;display:flex;flex-direction:column;}
#sb .logo{padding:20px 16px 14px;border-bottom:1px solid rgba(255,255,255,.15);}
#sb .logo .brand{display:flex;align-items:center;gap:10px;}
#sb .logo .ico{width:38px;height:38px;background:var(--g1);border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
#sb .logo h6{color:#fff;font-size:.95rem;font-weight:700;margin:0;}
#sb .logo small{color:#86efac;font-size:.68rem;}
#sb .sec{padding:12px 14px 4px;font-size:.6rem;letter-spacing:1.8px;color:#86efac;text-transform:uppercase;}
#sb a.nl{display:flex;align-items:center;gap:9px;padding:9px 14px;color:#dcfce7;border-radius:8px;margin:1px 8px;font-size:.83rem;text-decoration:none;transition:.15s;}
#sb a.nl:hover,#sb a.nl.active{background:var(--g1);color:#fff;}
#sb a.nl i{width:16px;text-align:center;font-size:.85rem;}
#sb .sb-foot{padding:14px;border-top:1px solid rgba(255,255,255,.15);margin-top:auto;}
#tb{position:fixed;top:0;left:var(--sw);right:0;height:56px;background:#fff;border-bottom:1px solid #d1fae5;display:flex;align-items:center;padding:0 22px;z-index:1030;justify-content:space-between;box-shadow:0 1px 4px rgba(0,0,0,.06);}
#tb .pt{font-weight:600;color:var(--g3);font-size:.95rem;display:flex;align-items:center;gap:8px;}
#mc{margin-left:var(--sw);margin-top:56px;padding:24px 26px;min-height:calc(100vh - 56px);}
.card{background:var(--card);border:1px solid #d1fae5;border-radius:12px;box-shadow:0 1px 6px rgba(0,0,0,.05);}
.card-hdr{padding:14px 18px;border-bottom:1px solid #d1fae5;display:flex;align-items:center;justify-content:space-between;background:#f0fdf4;border-radius:12px 12px 0 0;}
.card-hdr .title{font-weight:600;color:var(--g3);font-size:.9rem;display:flex;align-items:center;gap:8px;}
.card-body{padding:18px;}
.sc{border-radius:12px;padding:18px;color:#fff;border:none;}
.sc .sv{font-size:1.9rem;font-weight:700;line-height:1;}
.sc .sl{font-size:.74rem;opacity:.9;margin-top:3px;}
.bg-g{background:linear-gradient(135deg,#16a34a,#15803d);}
.bg-b{background:linear-gradient(135deg,#0ea5e9,#0284c7);}
.bg-o{background:linear-gradient(135deg,#f59e0b,#d97706);}
.bg-r{background:linear-gradient(135deg,#ef4444,#dc2626);}
.bg-v{background:linear-gradient(135deg,#8b5cf6,#7c3aed);}
.bg-t{background:linear-gradient(135deg,#06b6d4,#0891b2);}
.bg-pk{background:linear-gradient(135deg,#ec4899,#db2777);}
.table{width:100%;border-collapse:collapse;}
.table th{background:#f0fdf4;font-size:.72rem;letter-spacing:.6px;text-transform:uppercase;color:var(--g2);padding:10px 12px;border-bottom:2px solid #d1fae5;text-align:left;}
.table td{padding:10px 12px;font-size:.85rem;border-bottom:1px solid #f0fdf4;vertical-align:middle;}
.table tr:hover td{background:#f0fdf4;}
.bk{display:inline-block;font-size:.7rem;padding:3px 10px;border-radius:20px;font-weight:600;}
.ok{background:#dcfce7;color:#14532d;}.att{background:#fef3c7;color:#78350f;}
.err{background:#fee2e2;color:#7f1d1d;}.inf{background:#dbeafe;color:#1e3a8a;}
.vio{background:#ede9fe;color:#3b0764;}.grey{background:#f3f4f6;color:#374151;}
.form-label{font-size:.82rem;font-weight:600;color:var(--g3);margin-bottom:4px;display:block;}
.form-control,.form-select{border:1.5px solid #d1fae5;border-radius:8px;padding:9px 12px;font-size:.87rem;width:100%;transition:.15s;background:#fff;color:var(--txt);}
.form-control:focus,.form-select:focus{border-color:var(--g1);outline:none;box-shadow:0 0 0 3px rgba(22,163,74,.12);}
.ig-text{background:#f0fdf4;border:1.5px solid #d1fae5;border-right:none;border-radius:8px 0 0 8px;padding:9px 12px;}
.btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:8px;font-size:.83rem;font-weight:600;cursor:pointer;border:none;transition:.15s;text-decoration:none;}
.btn:hover{filter:brightness(.94);}
.btn-g{background:var(--g1);color:#fff;}.btn-r{background:var(--err);color:#fff;}
.btn-o{background:var(--warn);color:#fff;}.btn-b{background:var(--acc);color:#fff;}
.btn-v{background:#8b5cf6;color:#fff;}
.btn-outline-g{background:transparent;border:1.5px solid var(--g1);color:var(--g1);}
.btn-outline-g:hover{background:var(--g1);color:#fff;}
.btn-outline-b{background:transparent;border:1.5px solid var(--acc);color:var(--acc);}
.btn-outline-b:hover{background:var(--acc);color:#fff;}
.btn-outline-r{background:transparent;border:1.5px solid var(--err);color:var(--err);}
.btn-outline-r:hover{background:var(--err);color:#fff;}
.btn-sm{padding:5px 10px;font-size:.76rem;border-radius:6px;}
.al{border-radius:8px;padding:10px 14px;font-size:.85rem;margin-bottom:10px;display:flex;align-items:center;gap:8px;}
.al-s{background:#dcfce7;border:1px solid #86efac;color:#14532d;}
.al-e{background:#fee2e2;border:1px solid #fca5a5;color:#7f1d1d;}
.al-w{background:#fef3c7;border:1px solid #fde047;color:#78350f;}
.al-i{background:#dbeafe;border:1px solid #93c5fd;color:#1e3a8a;}
.notif-wrap{position:relative;}
.notif-dot{position:absolute;top:-4px;right:-4px;width:18px;height:18px;background:var(--err);border-radius:50%;font-size:.6rem;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;border:2px solid #fff;}
.avatar{width:42px;height:42px;border-radius:50%;object-fit:cover;background:var(--gm);display:flex;align-items:center;justify-content:center;border:2px solid var(--gd);}
.nav-tabs{display:flex;gap:4px;border-bottom:2px solid var(--gd);margin-bottom:16px;}
.nav-tab{padding:8px 16px;border-radius:8px 8px 0 0;font-size:.84rem;font-weight:600;cursor:pointer;border:none;background:transparent;color:var(--muted);border-bottom:2px solid transparent;margin-bottom:-2px;}
.nav-tab.active{background:#fff;color:var(--g1);border:2px solid var(--gd);border-bottom:2px solid #fff;}
.urg-1{background:#7f1d1d;color:#fff;}.urg-2{background:#ef4444;color:#fff;}
.urg-3{background:#f59e0b;color:#fff;}.urg-4{background:#16a34a;color:#fff;}.urg-5{background:#dbeafe;color:#1e3a8a;}
.stat-dispo{background:#dcfce7;color:#14532d;}.stat-occ{background:#fef3c7;color:#78350f;}.stat-conge{background:#dbeafe;color:#1e3a8a;}
/* Charts */
.chart-bar{display:flex;align-items:flex-end;gap:8px;height:120px;padding:8px 0;}
.bar{flex:1;border-radius:6px 6px 0 0;min-width:20px;transition:.3s;position:relative;}
.bar-lbl{font-size:.6rem;color:var(--muted);text-align:center;margin-top:4px;}
.donut-wrap{display:inline-flex;align-items:center;gap:16px;}
@media(max-width:992px){
  #sb{transform:translateX(-100%);transition:transform .25s ease;}
  #sb.show{transform:translateX(0);}
  #tb,#mc{margin-left:0;}
  #tb .pt button{display:inline-flex!important;}
  .sb-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:1035;}
  .sb-overlay.show{display:block;}
}
@media(max-width:768px){
  #mc{padding:14px;}
  #tb{padding:0 12px;height:52px;}
  #tb .pt{font-size:.85rem;gap:6px;}
  #tb .pt i.fa-heartbeat{display:none;}
  #tb > div:last-child > span{display:none;}
  .card-body{padding:12px;}
  .card-hdr{padding:10px 12px;flex-wrap:wrap;gap:8px;}
  .card-hdr .title{font-size:.85rem;}
  .row.g-3>[class*="col-"]{margin-bottom:10px;}
  .table{font-size:.78rem;}
  .table th,.table td{padding:7px 8px;}
  .nav-tabs{flex-wrap:wrap;}
  .sc .sv{font-size:1.5rem;}
  .form-control,.form-select{font-size:.85rem;padding:8px 10px;}
  .btn{padding:7px 12px;font-size:.8rem;}
}
@media(max-width:576px){
  .table-responsive-stack table, .table-responsive-stack thead, .table-responsive-stack tbody, .table-responsive-stack th, .table-responsive-stack td, .table-responsive-stack tr{display:block;}
  .table-responsive-stack thead tr{position:absolute;top:-9999px;left:-9999px;}
  .table-responsive-stack tr{border:1px solid #d1fae5;border-radius:8px;margin-bottom:8px;padding:6px;}
  .table-responsive-stack td{border:none;border-bottom:1px solid #f0fdf4;position:relative;padding-left:45%;}
  .table-responsive-stack td:before{position:absolute;left:8px;width:40%;white-space:nowrap;font-weight:600;font-size:.7rem;color:var(--g2);content:attr(data-label);}
}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:#f0fdf4;}::-webkit-scrollbar-thumb{background:var(--gd);border-radius:4px;}
</style>"""

JS_BASE="""<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.3/js/bootstrap.bundle.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
function srch(tid,fid){const v=document.getElementById(fid).value.toLowerCase();document.querySelectorAll('#'+tid+' tbody tr').forEach(r=>{r.style.display=r.textContent.toLowerCase().includes(v)?'':'none';});}
document.querySelectorAll('#sb a.nl').forEach(a=>{try{if(window.location.pathname===new URL(a.href,window.location.origin).pathname)a.classList.add('active');}catch(e){}});
function toggleSB(){document.getElementById('sb').classList.toggle('show');document.getElementById('sbOverlay').classList.toggle('show');}
function showTab(id,btn){document.querySelectorAll('.tab-pane').forEach(t=>t.style.display='none');document.querySelectorAll('.nav-tab').forEach(b=>b.classList.remove('active'));document.getElementById(id).style.display='block';btn.classList.add('active');}
document.querySelectorAll('.al:not(.al-keep)').forEach(a=>{setTimeout(()=>{a.style.transition='opacity .5s';a.style.opacity='0';setTimeout(()=>a.remove(),500);},5000);});
function confirmAction(msg,form){if(confirm(msg)){form.submit();}return false;}
</script>"""

def fhtml():
    msgs=[]
    for cat,msg in session.pop("_flashes",[]):
        cls={"success":"al-s","danger":"al-e","warning":"al-w","info":"al-i"}.get(cat,"al-i")
        ic={"success":"check-circle","danger":"times-circle","warning":"exclamation-triangle","info":"info-circle"}.get(cat,"info-circle")
        keep=" al-keep" if "IDENTIFIANT" in msg or "MOT DE PASSE" in msg else ""
        close_btn=' <button type="button" onclick="this.parentElement.remove()" style="float:right;background:none;border:none;font-size:1rem;cursor:pointer;color:inherit;line-height:1;">&times;</button>' if keep else ""
        msgs.append(f'<div class="al {cls}{keep}"><i class="fas fa-{ic}"></i>{msg}{close_btn}</div>')
    return "\n".join(msgs)

def sidebar(role,username):
    ud=DB["users"].get(username,{})
    nom=f"{ud.get('prenom','')} {ud.get('nom','')}".strip() or username
    rl={"patient":"Patient","medecin":"Medecin","receptionniste":"Receptionniste","pharmacien":"Pharmacien","admin":"Administrateur"}.get(role,role)
    menus={
        "patient":[
            ("","Tableau de bord","tachometer-alt","dashboard"),("","Mon espace","---",""),
            ("","Mon Dossier","folder-open","p_dossier"),("","Mes Documents","file-pdf","p_documents"),
            ("","Mes RDV","calendar-check","p_rdvs"),("","Mes Consultations","stethoscope","p_consultations"),
            ("","Mes Teleconsultations","video","p_teleconsult"),("","Mes Resultats","microscope","p_resultats"),
            ("","Mes Factures","file-invoice-dollar","p_factures"),("","Mes Paiements","credit-card","p_paiements"),
            ("","Acheter un ticket","ticket-alt","p_tickets"),("","Notifications","bell","p_notifs"),("","Mon Profil","user-cog","profil"),
        ],
        "medecin":[
            ("","Tableau de bord","tachometer-alt","dashboard"),("","Mon espace","---",""),
            ("","Mes Patients","users","m_patients"),("","Mes RDV","calendar-check","m_rdvs"),
            ("","Mes Consultations","stethoscope","m_consultations"),("","Mes Teleconsultations","video","m_teleconsult"),
            ("","Mon Service","building","m_service"),("","Messagerie","paper-plane","m_notifs"),("","Mon Profil","user-cog","profil"),
        ],
        "receptionniste":[
            ("","Tableau de bord","tachometer-alt","dashboard"),("","Gestion","---",""),
            ("","Patients","users","r_patients"),("","Rendez-vous","calendar-check","r_rdvs"),
            ("","Demandes RDV","inbox","r_demandes"),("","Tickets","ticket-alt","r_tickets"),
            ("","Liste d'attente","clock","r_attente"),("","Urgences / Triage","ambulance","r_triage"),
            ("","Teleconsultations","video","r_teleconsult"),("","Facturation","file-invoice","r_facturation"),
            ("","Paiements","cash-register","r_paiements"),("","Messagerie","paper-plane","r_notifs"),
            ("","Historique","history","r_historique"),("","Mon Profil","user-cog","profil"),
        ],
        "pharmacien":[
            ("","Tableau de bord","tachometer-alt","dashboard"),("","Pharmacie","---",""),
            ("","Medicaments & Stock","pills","ph_medicaments"),("","Vente medicaments","shopping-cart","ph_ventes"),
            ("","Historique ventes","receipt","ph_historique_ventes"),
            ("","Alertes Stock","exclamation-triangle","ph_alertes"),("","Ordonnances","prescription","ph_ordonnances"),
            ("","Notifications","bell","ph_notifs"),("","Mon Profil","user-cog","profil"),
        ],
        "admin":[
            ("","Tableau de bord","tachometer-alt","dashboard"),("","Administration","---",""),
            ("","Medecins","user-md","a_medecins"),("","Services","building","a_services"),
            ("","Centres","hospital","a_centres"),
            ("","Creneaux medecins","clock","a_creneaux"),
            ("","Patients","users","a_patients"),("","Toutes factures","file-invoice","a_factures"),
            ("","Assurances","shield-alt","a_assurances"),
            ("","Notifications globales","bell","a_notifs"),
            ("","Historiques","history","a_historiques"),("","Mon Profil","user-cog","profil"),
        ],
    }
    pat=get_pat(username); pid=pat["id"] if pat else None
    nc=unread_count(username,role,pid)
    links=""
    for _,label,icon,ep in menus.get(role,[]):
        if icon=="---": links+=f'<div class="sec">{label}</div>'; continue
        notif_eps=("p_notifs","m_notifs","r_notifs","ph_notifs","a_notifs")
        nb=f'<span style="background:var(--err);color:#fff;border-radius:10px;font-size:.6rem;padding:1px 6px;margin-left:auto;">{nc}</span>' if ep in notif_eps and nc>0 else ""
        href=f"/{ep.replace('_','-')}"
        links+=f'<a href="{href}" class="nl"><i class="fas fa-{icon}"></i>{label}{nb}</a>\n'
    ph=f'<img src="{ud["photo"]}" style="width:34px;height:34px;border-radius:50%;object-fit:cover;border:2px solid var(--gd);" alt="">' if ud.get("photo") else f'<div style="width:34px;height:34px;background:var(--g1);border-radius:50%;display:flex;align-items:center;justify-content:center;"><i class="fas fa-user" style="color:#fff;font-size:.85rem;"></i></div>'
    return f"""<nav id="sb"><div class="logo"><div class="brand"><div class="ico"><i class="fas fa-heartbeat" style="color:#fff;font-size:1rem;"></i></div><div><h6>LE TROPICAL</h6><small>Centre de Sante LE TROPICAL</small></div></div></div><div style="flex:1;overflow-y:auto;padding-bottom:10px;">{links}</div><div class="sb-foot"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">{ph}<div><div style="font-size:.82rem;color:#fff;font-weight:600;">{nom}</div><div style="font-size:.68rem;color:#86efac;text-transform:uppercase;">{rl}</div></div></div><a href="/logout" class="btn btn-sm" style="background:rgba(255,255,255,.15);color:#fff;width:100%;justify-content:center;"><i class="fas fa-sign-out-alt"></i>Deconnexion</a></div></nav>"""

def topbar(title,role,username):
    ud=DB["users"].get(username,{})
    nom=f"{ud.get('prenom','')} {ud.get('nom','')}".strip() or username
    pat=get_pat(username); pid=pat["id"] if pat else None
    nc=unread_count(username,role,pid)
    ep={"patient":"p-notifs","medecin":"m-notifs","receptionniste":"r-notifs","pharmacien":"ph-notifs","admin":"a-notifs"}.get(role,"")
    nb=f'<div class="notif-wrap"><a href="/{ep}" class="btn btn-sm btn-outline-g"><i class="fas fa-bell"></i><span class="notif-dot">{nc}</span></a></div>' if ep and nc>0 else (f'<a href="/{ep}" class="btn btn-sm btn-outline-g"><i class="fas fa-bell"></i></a>' if ep else "")
    ph=f'<img src="{ud["photo"]}" class="avatar" alt="">' if ud.get("photo") else f'<div class="avatar"><i class="fas fa-user" style="color:var(--g2);font-size:.9rem;"></i></div>'
    return f'<div id="tb"><div class="pt"><button class="btn btn-sm btn-outline-g" onclick="toggleSB()" style="display:none;" id="sbToggleBtn"><i class="fas fa-bars"></i></button><i class="fas fa-heartbeat" style="color:var(--g1);"></i>{title}</div><div style="display:flex;align-items:center;gap:10px;">{nb}{ph}<span style="font-size:.82rem;font-weight:600;color:var(--g3);">{nom}</span></div></div>'

def page(title,role,username,body,extra_js=""):
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.3/css/bootstrap.min.css" rel="stylesheet"><link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet"><title>{title} — LE TROPICAL</title>{CSS}</head><body>{sidebar(role,username)}<div id="sbOverlay" class="sb-overlay" onclick="toggleSB()"></div>{topbar(title,role,username)}<div id="mc">{fhtml()}{body}</div>{JS_BASE}{extra_js}</body></html>"""

def gen_pdf(titre,lignes):
    """Genere un PDF brut (multi-pages) - positionnement absolu via Tm corrige."""
    all_lines=["CENTRE DE SANTE LE TROPICAL","Thies, Senegal | Tel: +221 33 000 00 00","="*58,"",f"  {titre}","="*58,""]+[f"  {l}" for l in lignes]+["","-"*58,"  Genere par SGRDMS v7 | "+date.today().strftime("%d/%m/%Y")]

    LINES_PER_PAGE = 54  # ~ (800-40)/14
    pages_lines = [all_lines[i:i+LINES_PER_PAGE] for i in range(0, len(all_lines), LINES_PER_PAGE)] or [[]]

    def build_content(lines_chunk):
        ops=b"BT\n/F1 10 Tf\n"
        y=800
        for line in lines_chunk:
            clean=line.replace("(","[").replace(")","]").replace("\\","")
            try: enc=clean.encode("latin-1","replace")
            except: enc=b""
            # Tm = positionnement ABSOLU (corrige le bug Td cumulatif)
            ops+=f"1 0 0 1 50 {y} Tm\n".encode()+b"("+enc+b") Tj\n"
            y-=14
        ops+=b"ET\n"
        return ops

    n_pages=len(pages_lines)
    # Numerotation des objets PDF (contigue, 1-indexee):
    # 1 = Catalog, 2 = Pages
    # 3..(2+n_pages)            -> objets Page
    # (3+n_pages)..(2+2*n_pages) -> objets Content (stream) associes
    # dernier objet              -> Font
    page_obj_nums=[3+i for i in range(n_pages)]
    content_obj_nums=[3+n_pages+i for i in range(n_pages)]
    font_obj=3+2*n_pages

    p=b"%PDF-1.4\n"
    objects={}  # num -> bytes

    kids=" ".join(f"{n} 0 R" for n in page_obj_nums)
    objects[1]=b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    objects[2]=f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {n_pages} >>\nendobj\n".encode()

    for i, chunk in enumerate(pages_lines):
        ops=build_content(chunk)
        page_num=page_obj_nums[i]
        content_num=content_obj_nums[i]
        objects[page_num]=f"{page_num} 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Contents {content_num} 0 R /Resources << /Font << /F1 {font_obj} 0 R >> >> >>\nendobj\n".encode()
        objects[content_num]=f"{content_num} 0 obj\n<< /Length {len(ops)} >>\nstream\n".encode()+ops+b"\nendstream\nendobj\n"

    objects[font_obj]=f"{font_obj} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n".encode()

    total_objs=font_obj  # nombre d objets reels (1..font_obj)
    offs={}; pos=len(p)
    for num in range(1, total_objs+1):
        offs[num]=pos
        pos+=len(objects[num])

    xr=f"xref\n0 {total_objs+1}\n0000000000 65535 f \n".encode()
    for num in range(1, total_objs+1):
        xr+=f"{offs[num]:010d} 00000 n \n".encode()
    tr=f"trailer\n<< /Size {total_objs+1} /Root 1 0 R >>\nstartxref\n{pos}\n%%EOF\n".encode()

    out=p
    for num in range(1, total_objs+1):
        out+=objects[num]
    out+=xr+tr
    return out

LOGIN_HTML=f"""<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.3/css/bootstrap.min.css" rel="stylesheet"><link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet"><title>Connexion — LE TROPICAL</title>{CSS}<style>.lw{{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#14532d,#16a34a 60%,#0d9488);}}.lc{{background:#fff;border-radius:20px;box-shadow:0 25px 60px rgba(0,0,0,.3);width:100%;max-width:420px;overflow:hidden;}}.lh{{background:linear-gradient(135deg,#14532d,#16a34a);padding:30px;text-align:center;color:#fff;}}.li{{width:70px;height:70px;background:rgba(255,255,255,.2);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:1.8rem;margin-bottom:10px;}}</style></head><body><div class="lw"><div class="lc"><div class="lh"><div class="li"><i class="fas fa-heartbeat"></i></div><h4 class="mb-0 fw-bold">LE TROPICAL</h4><p class="mb-0 mt-1" style="opacity:.8;font-size:.82rem;">SGRDMS — Centre de Sante</p></div><div style="padding:28px 30px;">{{ERR}}<div class="mb-3"><label class="form-label fw-semibold" style="font-size:.83rem;">Identifiant</label><div style="display:flex;"><span class="ig-text"><i class="fas fa-user" style="color:#16a34a;"></i></span><input type="text" id="usr" class="form-control" placeholder="Votre identifiant" required autofocus style="border-radius:0 8px 8px 0;border-left:none;"></div></div><div class="mb-3"><label class="form-label fw-semibold" style="font-size:.83rem;">Mot de passe</label><div style="display:flex;"><span class="ig-text"><i class="fas fa-lock" style="color:#16a34a;"></i></span><input type="password" id="pwd" class="form-control" placeholder="Mot de passe" required style="border-radius:0 8px 8px 0;border-left:none;"><button type="button" onclick="tp()" class="btn btn-sm btn-outline-g" style="margin-left:6px;"><i class="fas fa-eye" id="ei"></i></button></div></div><button type="button" onclick="doLogin()" class="btn btn-g w-100 mt-1" style="justify-content:center;padding:11px;font-size:.92rem;"><i class="fas fa-sign-in-alt"></i>Se connecter</button><p style="text-align:center;font-size:.74rem;color:var(--muted);margin-top:16px;"><i class="fas fa-shield-alt me-1"></i>Acces reserve au personnel autorise</p></div></div></div><script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.3/js/bootstrap.bundle.min.js"></script><script>function doLogin(){{const u=document.getElementById('usr').value,p=document.getElementById('pwd').value;if(!u||!p){{alert('Remplir tous les champs');return;}}const f=document.createElement('form');f.method='POST';f.action='/login';[['username',u],['password',p]].forEach(([k,v])=>{{const i=document.createElement('input');i.name=k;i.value=v;f.appendChild(i);}});document.body.appendChild(f);f.submit();}}document.addEventListener('keydown',e=>{{if(e.key==='Enter')doLogin();}});function tp(){{const p=document.getElementById('pwd'),e=document.getElementById('ei');p.type=p.type==='password'?'text':'password';e.className='fas fa-eye'+(p.type==='text'?'-slash':'');}}</script></body></html>"""
# SGRDMS v7 — Part 3: Login, Dashboard admin (stats + charts), Admin complet

# =======================================================
# Routes : Login / Logout / Dashboard (tous rôles) / Administration complète
# =======================================================

@app.route("/",methods=["GET","POST"])
@app.route("/view-doc/<ref_type>/<int:ref_id>")
@login_required
def view_doc(ref_type, ref_id):
    """Visionneuse universelle de documents (ordonnance, resultat, facture)"""
    role = session.get("role","patient")
    # Construire le contenu HTML du document
    titre = "Document"
    contenu = ""
    dl_url = ""
    if ref_type == "ordonnance":
        o = next((x for x in DB["ordonnances"] if x["id"]==ref_id), None)
        if not o: flash("Document introuvable","danger"); return redirect(url_for("dashboard"))
        pat = next((p for p in DB["patients"] if p["id"]==o["id_patient"]), None)
        titre = f"Ordonnance ORD-{o['id']:04d}"
        dl_url = f"/p-download/ordonnance/{ref_id}"
        lignes_html = "".join(f'<div style="background:#f0fdf4;border-radius:8px;padding:12px 16px;margin-bottom:8px;border-left:4px solid var(--g1);"><strong>{l["libelle"]}</strong><br><small style="color:var(--muted);">Posologie : {l["posologie"]} &nbsp;|&nbsp; Durée : {l["duree"]}</small></div>' for l in o["lignes"])
        contenu = f"""<div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:28px;max-width:640px;margin:0 auto;font-family:sans-serif;">
  <div style="text-align:center;margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid var(--g1);">
    <div style="font-size:1.3rem;font-weight:800;color:var(--g3);">CENTRE DE SANTE LE TROPICAL</div>
    <div style="font-size:.85rem;color:var(--muted);">ORDONNANCE MÉDICALE</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;font-size:.88rem;">
    <div><span style="color:var(--muted);">Patient</span><div style="font-weight:700;">{"" if not pat else pat["prenom"]+" "+pat["nom"]}</div></div>
    <div><span style="color:var(--muted);">Date naissance</span><div>{"" if not pat else pat["date_naissance"]}</div></div>
    <div><span style="color:var(--muted);">Médecin</span><div style="font-weight:700;">{mname(o["matricule"])}</div></div>
    <div><span style="color:var(--muted);">Date prescription</span><div>{o["date"]}</div></div>
    <div><span style="color:var(--muted);">Téléphone</span><div>{"" if not pat else pat["telephone"]}</div></div>
    <div><span style="color:var(--muted);">Assurance</span><div>{"" if not pat else pat["assurance"]}</div></div>
  </div>
  <div style="font-weight:700;color:var(--g3);margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid #e5e7eb;"><i class="fas fa-pills me-2"></i>Médicaments prescrits — Durée : {o["duree"]} jours</div>
  {lignes_html}
  {"<div style='margin-top:12px;padding:10px;background:#fef9c3;border-radius:6px;font-size:.78rem;'><i class='fas fa-exclamation-triangle' style='color:#d97706;'></i> <strong>Avertissements :</strong> "+"; ".join(a["message"][:80] for a in o.get("alertes_interactions",[]))+"</div>" if o.get("alertes_interactions") else ""}
</div>"""
    elif ref_type == "resultat":
        r = next((x for x in DB["resultats_examens"] if x["id"]==ref_id), None)
        if not r: flash("Document introuvable","danger"); return redirect(url_for("dashboard"))
        pat = next((p for p in DB["patients"] if p["id"]==r["id_patient"]), None)
        titre = f"Résultat — {r['type']}"
        contenu = f"""<div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:28px;max-width:640px;margin:0 auto;">
  <div style="text-align:center;margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid var(--g1);">
    <div style="font-size:1.3rem;font-weight:800;color:var(--g3);">CENTRE DE SANTE LE TROPICAL</div>
    <div style="font-size:.85rem;color:var(--muted);">RÉSULTAT D'EXAMEN</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;font-size:.88rem;">
    <div><span style="color:var(--muted);">Patient</span><div style="font-weight:700;">{"" if not pat else pat["prenom"]+" "+pat["nom"]}</div></div>
    <div><span style="color:var(--muted);">Date naissance</span><div>{"" if not pat else pat["date_naissance"]}</div></div>
    <div><span style="color:var(--muted);">Type d'examen</span><div style="font-weight:700;">{r["type"]}</div></div>
    <div><span style="color:var(--muted);">Date</span><div>{r["date"]}</div></div>
    <div><span style="color:var(--muted);">Médecin</span><div>{mname(r["matricule"])}</div></div>
    <div><span style="color:var(--muted);">Statut</span><div><span class="bk ok">{r["statut"]}</span></div></div>
  </div>
  <div style="background:#f0fdf4;border-radius:10px;padding:18px;border-left:4px solid var(--g1);margin-top:12px;">
    <div style="font-weight:700;color:var(--g3);margin-bottom:8px;"><i class="fas fa-flask me-2"></i>Résultats et observations</div>
    <div style="line-height:1.8;">{r["commentaire"]}</div>
  </div>
</div>"""
    elif ref_type == "facture":
        fac = next((x for x in DB["factures"] if x["id"]==ref_id), None)
        if not fac: flash("Document introuvable","danger"); return redirect(url_for("dashboard"))
        pat = next((p for p in DB["patients"] if p["id"]==fac["id_patient"]), None)
        titre = f"Facture {fac['num_facture']}"
        dl_url = f"/p-download/facture/{ref_id}"
        contenu = f"""<div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:28px;max-width:640px;margin:0 auto;">
  <div style="text-align:center;margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid var(--g1);">
    <div style="font-size:1.3rem;font-weight:800;color:var(--g3);">CENTRE DE SANTE LE TROPICAL</div>
    <div style="font-size:.85rem;color:var(--muted);">FACTURE — {fac["num_facture"]}</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;font-size:.88rem;">
    <div><span style="color:var(--muted);">Patient</span><div style="font-weight:700;">{"" if not pat else pat["prenom"]+" "+pat["nom"]}</div></div>
    <div><span style="color:var(--muted);">Date naissance</span><div>{"" if not pat else pat["date_naissance"]}</div></div>
    <div><span style="color:var(--muted);">Téléphone</span><div>{"" if not pat else pat["telephone"]}</div></div>
    <div><span style="color:var(--muted);">Assurance</span><div>{"" if not pat else pat["assurance"]}</div></div>
    <div><span style="color:var(--muted);">Groupe sanguin</span><div>{"" if not pat else pat.get("groupe_sanguin","-")}</div></div>
    <div><span style="color:var(--muted);">Email</span><div>{"" if not pat else pat.get("email","-")}</div></div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px;">
    <div style="background:#f0fdf4;border-radius:8px;padding:14px;text-align:center;">
      <div style="font-size:1.1rem;font-weight:800;color:var(--g3);">{fac["montant"]:,} F</div>
      <div style="font-size:.75rem;color:var(--muted);">Total</div>
    </div>
    <div style="background:#eff6ff;border-radius:8px;padding:14px;text-align:center;">
      <div style="font-size:1.1rem;font-weight:800;color:#1d4ed8;">{fac["part_assurance"]:,} F</div>
      <div style="font-size:.75rem;color:var(--muted);">Assurance</div>
    </div>
    <div style="background:#fff7ed;border-radius:8px;padding:14px;text-align:center;">
      <div style="font-size:1.1rem;font-weight:800;color:#c2410c;">{fac["part_patient"]:,} F</div>
      <div style="font-size:.75rem;color:var(--muted);">Part patient</div>
    </div>
  </div>
  <table style="width:100%;font-size:.88rem;">
    <tr style="background:#f9fafb;"><td style="padding:8px;">Montant payé</td><td style="font-weight:700;color:var(--g3);text-align:right;">{fac["montant_paye"]:,} FCFA</td></tr>
    <tr><td style="padding:8px;">Reste à payer</td><td style="font-weight:700;color:{"var(--err)" if fac["reste_a_payer"]>0 else "var(--g1)"};text-align:right;">{fac["reste_a_payer"]:,} FCFA</td></tr>
    <tr style="background:#f9fafb;"><td style="padding:8px;">Mode paiement</td><td style="text-align:right;">{fac["mode_paiement"]}</td></tr>
    <tr><td style="padding:8px;">Statut</td><td style="text-align:right;"><span class="bk {"ok" if fac["statut"]=="Payee" else "att" if fac["statut"]=="Partielle" else "err"}">{fac["statut"]}</span></td></tr>
  </table>
</div>"""
    else:
        flash("Type de document non reconnu","warning")
        return redirect(url_for("dashboard"))
    dl_btn = f'<a href="{dl_url}" class="btn btn-g"><i class="fas fa-download"></i>Telecharger PDF</a>' if (dl_url and role=="patient") else ""
    body=f"""<div class="row justify-content-center"><div class="col-lg-8">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
    <h5 style="color:var(--g3);margin:0;"><i class="fas fa-file-alt me-2"></i>{titre}</h5>
    <div style="display:flex;gap:8px;">{dl_btn}<a href="javascript:history.back()" class="btn btn-outline-g"><i class="fas fa-arrow-left"></i>Retour</a></div>
  </div>
  {contenu}
</div></div>"""
    return page(titre, role, session["user"], body)

@app.route("/login",methods=["GET","POST"])
def login():
    err=""
    if request.method=="POST":
        u=request.form.get("username",""); pw=request.form.get("password","")
        ud=DB["users"].get(u)
        if ud and ud["password"]==pw:
            session["user"]=u; session["role"]=ud["role"]
            return redirect(url_for("dashboard"))
        err='<div class="al al-e"><i class="fas fa-times-circle"></i>Identifiant ou mot de passe incorrect.</div>'
    return LOGIN_HTML.replace("{ERR}",err)

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

# ── DASHBOARD ────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    role=session["role"]; u=session["user"]

    if role=="admin":
        # Statistiques globales
        nb_p=len(DB["patients"]); nb_m=len(DB["medecins"]); nb_s=len(DB["services"])
        nb_rdv=len(DB["rdvs"]); nb_cons=len(DB["consultations"])
        total_fact=sum(f["montant"] for f in DB["factures"])
        total_enc=sum(f["montant_paye"] for f in DB["factures"])
        nb_imp=len([f for f in DB["factures"] if f["statut"]=="Impayee"])
        nb_urg=len([t for t in DB["triage"] if t["statut"] in ["En attente","En cours"]])
        nb_att=len([a for a in DB["liste_attente"] if a["statut"]=="En attente"])
        nb_stock_pb=len([s for s in DB["stocks"] if s["statut"] in ["Faible","Epuise"]])

        # Données pour graphique consultations par service
        cons_by_svc={}
        for c in DB["consultations"]:
            med=next((m for m in DB["medecins"] if m["matricule"]==c["matricule"]),None)
            if med:
                sv=sname(med["id_service"])
                cons_by_svc[sv]=cons_by_svc.get(sv,0)+1
        chart_labels=list(cons_by_svc.keys()); chart_vals=list(cons_by_svc.values())

        # Données pour graphique statuts RDV
        rdv_stats={"Confirme":0,"En attente":0,"Annule":0,"Termine":0}
        for r in DB["rdvs"]: rdv_stats[r["statut"]]=rdv_stats.get(r["statut"],0)+1

        # Médecins par statut
        med_stats={"Disponible":0,"Occupe":0,"En conge":0}
        for username,ud in DB["users"].items():
            if ud["role"]=="medecin": med_stats[ud.get("status_med","Disponible")]=med_stats.get(ud.get("status_med","Disponible"),0)+1

        extra_js=f"""<script>
// Graphique consultations par service
const ctx1=document.getElementById('chartCons');
if(ctx1){{new Chart(ctx1,{{type:'bar',data:{{labels:{json.dumps(chart_labels)},datasets:[{{label:'Consultations',data:{json.dumps(chart_vals)},backgroundColor:['#16a34a','#0ea5e9','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#ec4899'],borderRadius:6}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,ticks:{{stepSize:1}}}}}}}}}})}}

// Graphique RDV par statut
const ctx2=document.getElementById('chartRdv');
if(ctx2){{new Chart(ctx2,{{type:'doughnut',data:{{labels:{json.dumps(list(rdv_stats.keys()))},datasets:[{{data:{json.dumps(list(rdv_stats.values()))},backgroundColor:['#16a34a','#f59e0b','#ef4444','#06b6d4'],borderWidth:2}}]}},options:{{responsive:true,plugins:{{legend:{{position:'right'}}}}}}}})}}

// Graphique stocks
const ctxS=document.getElementById('chartStock');
if(ctxS){{const sn=[{','.join([repr(next((m["libelle"] for m in DB["medicaments"] if m["id_stock"]==s["id"]),"?")) for s in DB["stocks"]])}];const sv=[{','.join([str(s["quantite"]) for s in DB["stocks"]])}];new Chart(ctxS,{{type:'bar',data:{{labels:sn,datasets:[{{label:'Quantite',data:sv,backgroundColor:sv.map(v=>v==0?'#ef4444':v<20?'#f59e0b':'#16a34a'),borderRadius:4}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true}}}}}}}})}}
</script>"""

        body=f"""
<div class="row g-3 mb-3">
  <div class="col-md-2"><div class="sc bg-g"><div class="sv">{nb_p}</div><div class="sl">Patients</div></div></div>
  <div class="col-md-2"><div class="sc bg-b"><div class="sv">{nb_m}</div><div class="sl">Medecins</div></div></div>
  <div class="col-md-2"><div class="sc bg-v"><div class="sv">{nb_s}</div><div class="sl">Services</div></div></div>
  <div class="col-md-2"><div class="sc bg-o"><div class="sv">{nb_rdv}</div><div class="sl">RDV total</div></div></div>
  <div class="col-md-2"><div class="sc bg-r"><div class="sv">{nb_urg}</div><div class="sl">Urgences actives</div></div></div>
  <div class="col-md-2"><div class="sc bg-t"><div class="sv">{nb_att}</div><div class="sl">En attente</div></div></div>
</div>
<div class="row g-3 mb-3">
  <div class="col-md-3"><div class="sc bg-g"><div class="sv">{total_enc:,} FCFA</div><div class="sl">Recettes encaissees</div></div></div>
  <div class="col-md-3"><div class="sc bg-o"><div class="sv">{total_fact-total_enc:,} FCFA</div><div class="sl">Reste a encaisser</div></div></div>
  <div class="col-md-3"><div class="sc bg-r"><div class="sv">{nb_imp}</div><div class="sl">Factures impayees</div></div></div>
  <div class="col-md-3"><div class="sc bg-pk"><div class="sv">{nb_stock_pb}</div><div class="sl">Alertes stock</div></div></div>
</div>
<div class="row g-3 mb-3">
  <div class="col-md-6"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-chart-bar"></i>Consultations par service</div></div>
    <div class="card-body"><canvas id="chartCons" height="180"></canvas></div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-chart-pie"></i>Statuts RDV</div></div>
    <div class="card-body"><canvas id="chartRdv" height="200"></canvas></div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-user-md"></i>Medecins</div></div>
    <div class="card-body">
      {"".join(f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--gl);"><span style="color:var(--muted);font-size:.82rem;">{m["prenom"]} {m["nom"]}</span><span class="bk {"ok" if DB["users"].get(m["username"],{}).get("status_med","Disponible")=="Disponible" else "att" if DB["users"].get(m["username"],{}).get("status_med")=="Occupe" else "inf"}">{DB["users"].get(m["username"],{}).get("status_med","Disponible")}</span></div>' for m in DB["medecins"])}
    </div></div></div>
</div>
<div class="row g-3">
  <div class="col-md-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-chart-bar"></i>Etat des stocks medicaments</div></div>
    <div class="card-body"><canvas id="chartStock" height="150"></canvas></div></div></div>
  <div class="col-md-4"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-building"></i>Services</div></div>
    <div class="card-body">
      {"".join(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid var(--gl);"><span style="font-size:.82rem;"><strong>{s["libelle"]}</strong></span><span class="bk inf">{len([m for m in DB["medecins"] if m["id_service"]==s["id"]])} med.</span></div>' for s in DB["services"])}
    </div></div></div>
</div>"""
        return page("Tableau de bord — Administration","admin",u,body,extra_js)

    if role=="patient":
        pat=get_pat(u); pid=pat["id"] if pat else 0
        dos=next((d for d in DB["dossiers"] if d["id_patient"]==pid),None)
        nb_rdv=len([r for r in DB["rdvs"] if r["id_patient"]==pid and r["statut"]=="Confirme"])
        nb_imp=len([f for f in DB["factures"] if f["id_patient"]==pid and f["statut"] in ["Impayee","Partielle"]])
        nb_notif=unread_count(u,"patient",pid)
        body=f"""<div class="row g-3 mb-3">
  <div class="col-md-3"><div class="sc bg-g"><div class="sv">{nb_rdv}</div><div class="sl">RDV confirmes</div></div></div>
  <div class="col-md-3"><div class="sc bg-b"><div class="sv">{len([c for c in DB["consultations"] if c["id_patient"]==pid])}</div><div class="sl">Consultations</div></div></div>
  <div class="col-md-3"><div class="sc bg-o"><div class="sv">{nb_imp}</div><div class="sl">Factures en attente</div></div></div>
  <div class="col-md-3"><div class="sc bg-r"><div class="sv">{nb_notif}</div><div class="sl">Notifications</div></div></div>
</div>
<div class="row g-3">
  <div class="col-md-3"><a href="/p-dossier" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-folder-open fa-2x" style="color:var(--g1);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Mon Dossier</div><div style="font-size:.78rem;color:var(--muted);">{dos["num_dossier"] if dos else "-"}</div></div></a></div>
  <div class="col-md-3"><a href="/p-rdvs" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-calendar-check fa-2x" style="color:var(--acc);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Mes RDV</div></div></a></div>
  <div class="col-md-3"><a href="/p-factures" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-file-invoice-dollar fa-2x" style="color:var(--warn);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Mes Factures</div><div style="font-size:.78rem;color:var(--muted);">{nb_imp} en attente</div></div></a></div>
  <div class="col-md-3"><a href="/p-tickets" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-ticket-alt fa-2x" style="color:#8b5cf6;"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Acheter un ticket</div></div></a></div>
</div>"""
        return page("Tableau de bord","patient",u,body)

    if role=="medecin":
        med=get_med(u); mat=med["matricule"] if med else ""
        ud=DB["users"][u]
        st=ud.get("status_med","Disponible")
        tc=ud.get("teleconsult_actif",False)
        nb_rdv=len([r for r in DB["rdvs"] if r["matricule"]==mat and r["statut"]=="Confirme"])
        nb_cons=len([c for c in DB["consultations"] if c["matricule"]==mat])
        st_cls="stat-dispo" if st=="Disponible" else "stat-conge" if "conge" in st.lower() else "stat-occ"
        # Médecins du même service pour vérification chef
        mes_med=[m for m in DB["medecins"] if m["id_service"]==med["id_service"]] if med else []
        chef_section=""
        if med and med.get("est_chef"):
            rows_m="".join(f'<tr><td>Dr. {m["prenom"]} {m["nom"]}</td><td>{m["specialite"]}</td><td><span class="bk {"ok" if DB["users"].get(m["username"],{}).get("status_med","Disponible")=="Disponible" else "att"}">{DB["users"].get(m["username"],{}).get("status_med","Disponible")}</span></td><td><span class="bk {"ok" if DB["users"].get(m["username"],{}).get("teleconsult_actif",False) else "err"}">{"Actif" if DB["users"].get(m["username"],{}).get("teleconsult_actif",False) else "Inactif"}</span></td></tr>' for m in mes_med)
            chef_section=f'<div class="col-12"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-crown" style="color:var(--warn);"></i>Mon equipe (chef de service)</div></div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Medecin</th><th>Specialite</th><th>Statut</th><th>Teleconsult</th></tr></thead><tbody>{rows_m}</tbody></table></div></div></div>'
        body=f"""<div class="row g-3 mb-3">
  <div class="col-md-3"><div class="sc bg-g"><div class="sv">{nb_rdv}</div><div class="sl">RDV confirmes</div></div></div>
  <div class="col-md-3"><div class="sc bg-b"><div class="sv">{nb_cons}</div><div class="sl">Consultations</div></div></div>
  <div class="col-md-3"><div class="sc {"bg-g" if st=="Disponible" else "bg-o" if "conge" not in st.lower() else "bg-b"}"><div class="sv" style="font-size:1rem;">{st}</div><div class="sl">Mon statut</div></div></div>
  <div class="col-md-3"><div class="sc {"bg-g" if tc else "bg-r"}"><div class="sv" style="font-size:1rem;">{"Active" if tc else "Inactive"}</div><div class="sl">Teleconsultation</div></div></div>
</div>
<div class="row g-3 mb-3">
  <div class="col-md-4">
    <div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-toggle-on"></i>Mon statut</div></div><div class="card-body">
      <form method="POST" action="/m-status"><div class="mb-2"><select name="status" class="form-select"><option {"selected" if st=="Disponible" else ""}>Disponible</option><option {"selected" if st=="Occupe" else ""}>Occupe</option><option {"selected" if "conge" in st.lower() else ""}>En conge</option></select></div><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-save"></i>Mettre a jour</button></form>
      <hr style="border-color:var(--gl);margin:12px 0;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:.85rem;font-weight:600;color:var(--g3);">Teleconsultation</span>
        <a href="/m-teleconsult-toggle" class="btn btn-sm {"btn-r" if tc else "btn-g"}">{"Desactiver" if tc else "Activer"}</a>
      </div>
    </div></div>
  </div>
  <div class="col-md-4"><a href="/m-patients" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-users fa-2x" style="color:var(--g1);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Mes Patients</div></div></a></div>
  <div class="col-md-4"><a href="/m-nouvelle-consultation" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-stethoscope fa-2x" style="color:var(--acc);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Nouvelle Consultation</div></div></a></div>
  {chef_section}
</div>"""
        return page("Tableau de bord","medecin",u,body)

    if role=="receptionniste":
        nb_att=len([a for a in DB["liste_attente"] if a["statut"]=="En attente"])
        nb_urg=len([t for t in DB["triage"] if t["statut"] in ["En attente","En cours"]])
        body=f"""<div class="row g-3 mb-3">
  <div class="col-md-3"><div class="sc bg-g"><div class="sv">{len(DB["patients"])}</div><div class="sl">Patients</div></div></div>
  <div class="col-md-3"><div class="sc bg-b"><div class="sv">{len([r for r in DB["rdvs"] if r["statut"]=="Confirme"])}</div><div class="sl">RDV confirmes</div></div></div>
  <div class="col-md-3"><div class="sc bg-o"><div class="sv">{nb_att}</div><div class="sl">En attente</div></div></div>
  <div class="col-md-3"><div class="sc bg-r"><div class="sv">{nb_urg}</div><div class="sl">Urgences actives</div></div></div>
</div>
<div class="row g-3">
  <div class="col-md-3"><a href="/r-patients" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-user-plus fa-2x" style="color:var(--g1);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Patients</div></div></a></div>
  <div class="col-md-3"><a href="/r-tickets" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-ticket-alt fa-2x" style="color:var(--warn);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Tickets</div></div></a></div>
  <div class="col-md-3"><a href="/r-attente" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-clock fa-2x" style="color:var(--acc);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Liste d'attente</div><div style="font-size:.78rem;color:var(--muted);">{nb_att} patient(s)</div></div></a></div>
  <div class="col-md-3"><a href="/r-triage" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-ambulance fa-2x" style="color:var(--err);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Urgences</div><div style="font-size:.78rem;color:var(--muted);">{nb_urg} en cours</div></div></a></div>
</div>"""
        return page("Tableau de bord","receptionniste",u,body)

    # pharmacien
    ruptures=len([s for s in DB["stocks"] if s["statut"]=="Epuise"])
    faibles=len([s for s in DB["stocks"] if s["statut"]=="Faible"])
    ventes_today=[v for v in DB.get("ventes_pharmacie",[]) if v["date"]==date.today().strftime("%Y-%m-%d")]
    body=f"""<div class="row g-3 mb-3">
  <div class="col-md-3"><div class="sc bg-g"><div class="sv">{len(DB["medicaments"])}</div><div class="sl">Medicaments</div></div></div>
  <div class="col-md-3"><div class="sc bg-o"><div class="sv">{faibles}</div><div class="sl">Stocks faibles</div></div></div>
  <div class="col-md-3"><div class="sc bg-r"><div class="sv">{ruptures}</div><div class="sl">Ruptures</div></div></div>
  <div class="col-md-3"><div class="sc bg-b"><div class="sv">{len(ventes_today)}</div><div class="sl">Ventes aujourd'hui</div></div></div>
</div>
<div class="row g-3">
  <div class="col-md-4"><a href="/ph-ventes" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-shopping-cart fa-2x" style="color:var(--g1);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Vendre medicaments</div></div></a></div>
  <div class="col-md-4"><a href="/ph-medicaments" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-pills fa-2x" style="color:var(--acc);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Stock</div></div></a></div>
  <div class="col-md-4"><a href="/ph-historique-ventes" class="card" style="text-decoration:none;display:block;"><div class="card-body text-center py-4"><i class="fas fa-receipt fa-2x" style="color:var(--warn);"></i><div style="font-weight:600;color:var(--g3);margin-top:8px;">Historique ventes</div></div></a></div>
</div>"""
    return page("Tableau de bord","pharmacien",u,body)

# ── ADMIN COMPLET ────────────────────────────────────────────
@app.route("/a-medecins",methods=["GET","POST"])
@login_required
@role_required("admin")
def a_medecins():
    if request.method=="POST":
        d=request.form
        mat=gen_matricule(); nom=d["nom"]; prenom=d["prenom"]
        spec=d["specialite"]; tel=d.get("tel",""); email=d.get("email","")
        sid=int(d.get("service",1)); uname=d.get("uname",""); pwd=d.get("pwd","med123")
        centres_sel=[int(x) for x in d.getlist("centres")] or [int(d.get("centre",1))]
        cid=centres_sel[0]
        chef=d.get("chef")=="on"
        nm={"matricule":mat,"nom":nom,"prenom":prenom,"specialite":spec,"telephone":tel,"email":email,"id_service":sid,"username":uname,"est_chef":chef,"teleconsult_actif":False,"id_centre":cid,"centres":centres_sel}
        DB["medecins"].append(nm)
        if uname:
            DB["users"][uname]={"password":pwd,"role":"medecin","nom":nom,"prenom":prenom,"email":email,"telephone":tel,"photo":"","id_ref":mat,"status_med":"Disponible","teleconsult_actif":False}
        add_hist(f"Nouveau medecin : Dr. {prenom} {nom} ({spec}) — matricule {mat}","Creation medecin",session["user"])
        flash(f"Dr. {prenom} {nom} ajoute avec le matricule {mat}.","success"); return redirect(url_for("a_medecins"))
    opts_s="".join(f'<option value="{s["id"]}">{s["libelle"]}</option>' for s in DB["services"])
    chk_c="".join(f'<label style="display:flex;align-items:center;gap:6px;font-size:.8rem;"><input type="checkbox" name="centres" value="{c["id"]}" {"checked" if c["id"]==1 else ""}>{c["nom"]}</label>' for c in DB.get("centres",[]))
    filtre_centre=request.args.get("centre","")
    # Tableau détaillé médecins
    rows=""
    meds_list=DB["medecins"]
    if filtre_centre:
        meds_list=[m for m in meds_list if med_in_centre(m,filtre_centre)]
    for m in meds_list:
        ud=DB["users"].get(m["username"],{})
        st=ud.get("status_med","Disponible")
        tc=ud.get("teleconsult_actif",False)
        st_c="ok" if st=="Disponible" else "inf" if "conge" in st.lower() else "att"
        centres_lbl=", ".join(cname(c) for c in med_centres(m))
        rows+=f"""<tr>
          <td><strong>{m["matricule"]}</strong></td>
          <td><strong>Dr. {m["prenom"]} {m["nom"]}</strong></td>
          <td>{m["specialite"]}</td>
          <td>{m["telephone"]}</td>
          <td>{m["email"]}</td>
          <td>{sname(m["id_service"])}</td>
          <td><span class="bk inf">{centres_lbl}</span></td>
          <td><span class="bk {"vio" if m.get("est_chef") else "grey"}">{"Chef" if m.get("est_chef") else "Med."}</span></td>
          <td><span class="bk {st_c}">{st}</span></td>
          <td><span class="bk {"ok" if tc else "err"}">{"Oui" if tc else "Non"}</span></td>
        </tr>"""
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-user-md"></i>Medecins ({len(meds_list)})</div>
    <form method="GET" style="display:flex;gap:6px;align-items:center;">
      <select name="centre" class="form-select form-select-sm" style="width:auto;" onchange="this.form.submit()">
        <option value="">Tous les centres</option>
        {"".join(f'<option value="{c["id"]}" {"selected" if filtre_centre==str(c["id"]) else ""}>{c["nom"]}</option>' for c in DB.get("centres",[]))}
      </select>
    </form>
    <button class="btn btn-sm btn-g" onclick="document.getElementById('fm').classList.toggle('d-none')"><i class="fas fa-plus"></i>Ajouter</button>
  </div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Matricule</th><th>Nom complet</th><th>Specialite</th><th>Telephone</th><th>Email</th><th>Service</th><th>Centre</th><th>Fonction</th><th>Statut</th><th>Teleconsult</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>
  <div class="col-lg-4"><div id="fm" class="card"><div class="card-hdr"><div class="title">Ajouter un medecin</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-6"><label class="form-label">Matricule</label><input type="text" class="form-control" value="{gen_matricule()}" disabled><div style="font-size:.7rem;color:var(--muted);">Genere automatiquement</div></div>
      <div class="col-6"><label class="form-label">Specialite *</label><select name="specialite" class="form-select"><option>Medecine Generale</option><option>Pediatrie</option><option>Gynecologie-Obstetrique</option><option>Cardiologie</option><option>Chirurgie Generale</option><option>Urgences</option><option>Biologie medicale</option><option>Dermatologie</option><option>Neurologie</option></select></div>
      <div class="col-6"><label class="form-label">Nom *</label><input type="text" name="nom" class="form-control" required></div>
      <div class="col-6"><label class="form-label">Prenom *</label><input type="text" name="prenom" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Telephone *</label><input type="text" name="tel" class="form-control" required placeholder="77 000 00 00"></div>
      <div class="col-12"><label class="form-label">Email</label><input type="email" name="email" class="form-control"></div>
      <div class="col-12"><label class="form-label">Service</label><select name="service" class="form-select">{opts_s}</select></div>
      <div class="col-12"><label class="form-label">Centre(s) *</label><div style="display:flex;flex-direction:column;gap:4px;padding:8px;border:1px solid var(--gl);border-radius:6px;">{chk_c}</div><div style="font-size:.7rem;color:var(--muted);">Un medecin peut etre rattache a plusieurs centres</div></div>
      <div class="col-8"><label class="form-label">Identifiant</label><input type="text" name="uname" class="form-control" placeholder="dr.prenom"></div>
      <div class="col-4"><label class="form-label">Mot de passe</label><input type="text" name="pwd" class="form-control" value="med123"></div>
      <div class="col-12"><label style="display:flex;align-items:center;gap:8px;font-size:.82rem;cursor:pointer;"><input type="checkbox" name="chef"> Chef de service</label></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-save"></i>Ajouter</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Medecins","admin",session["user"],body)

@app.route("/a-centres",methods=["GET","POST"])
@login_required
@role_required("admin")
def a_centres():
    if request.method=="POST":
        d=request.form
        nc={"id":nid("centres"),"nom":d["nom"],"ville":d.get("ville",""),"adresse":d.get("adresse",""),"telephone":d.get("telephone",""),"tarif_ticket":int(d.get("tarif_ticket",0) or 0)}
        DB["centres"].append(nc)
        add_hist(f"Nouveau centre : {nc['nom']} (ticket {nc['tarif_ticket']} FCFA)","Creation centre",session["user"])
        flash(f"Centre '{nc['nom']}' cree.","success"); return redirect(url_for("a_centres"))
    rows=""
    for c in DB.get("centres",[]):
        meds_c=[m for m in DB["medecins"] if med_in_centre(m,c["id"])]
        srv_c=[s for s in DB["services"] if s.get("id_centre",1)==c["id"]]
        rows += f"""<tr><td><strong>{c["nom"]}</strong></td><td>{c["ville"]}</td><td>{c["adresse"]}</td><td>{c["telephone"]}</td>
        <td><form method="POST" action="{url_for('a_centre_tarif',cid=c['id'])}" style="display:flex;gap:4px;align-items:center;">
          <input type="number" name="tarif_ticket" value="{c.get('tarif_ticket',0)}" class="form-control form-control-sm" style="width:90px;">
          <button type="submit" class="btn btn-sm btn-outline-b"><i class="fas fa-save"></i></button>
        </form></td>
        <td><span class="bk inf">{len(meds_c)} medecin(s)</span></td><td><span class="bk inf">{len(srv_c)} service(s)</span></td></tr>"""
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-hospital"></i>Centres ({len(DB.get("centres",[]))})</div>
    <button class="btn btn-sm btn-g" onclick="document.getElementById('fc').classList.toggle('d-none')"><i class="fas fa-plus"></i>Nouveau</button>
  </div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Nom</th><th>Ville</th><th>Adresse</th><th>Telephone</th><th>Tarif ticket (FCFA)</th><th>Medecins</th><th>Services</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>
  <div class="col-lg-4"><div id="fc" class="card"><div class="card-hdr"><div class="title">Nouveau centre</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Nom *</label><input type="text" name="nom" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Ville</label><input type="text" name="ville" class="form-control"></div>
      <div class="col-12"><label class="form-label">Adresse</label><input type="text" name="adresse" class="form-control"></div>
      <div class="col-12"><label class="form-label">Telephone</label><input type="text" name="telephone" class="form-control"></div>
      <div class="col-12"><label class="form-label">Tarif ticket (FCFA) *</label><input type="number" name="tarif_ticket" class="form-control" value="2000" required></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-save"></i>Creer</button></div>
    </div></form>
    <div class="al al-i mt-3" style="font-size:.76rem;"><i class="fas fa-info-circle"></i>Les medecins et services peuvent ensuite etre rattaches a ce centre.</div>
  </div></div></div>
</div>"""
    return page("Centres","admin",session["user"],body)

@app.route("/a-centres/<int:cid>/tarif",methods=["POST"])
@login_required
@role_required("admin")
def a_centre_tarif(cid):
    c=next((x for x in DB.get("centres",[]) if x["id"]==cid),None)
    if c:
        c["tarif_ticket"]=int(request.form.get("tarif_ticket",0) or 0)
        add_hist(f"Tarif ticket du centre {c['nom']} fixe a {c['tarif_ticket']} FCFA","Modification tarif",session["user"])
        flash(f"Tarif ticket de {c['nom']} mis a jour ({c['tarif_ticket']} FCFA).","success")
    return redirect(url_for("a_centres"))

@app.route("/a-creneaux",methods=["GET","POST"])
@login_required
@role_required("admin")
def a_creneaux():
    if request.method=="POST":
        d=request.form
        nd={"id":nid("disponibilites"),"matricule":d["matricule"],"id_centre":int(d["centre"]),
            "jour_semaine":int(d["jour"]),"heure_debut":d["heure_debut"],"heure_fin":d["heure_fin"],
            "duree_creneau":int(d.get("duree",30))}
        DB["disponibilites"].append(nd)
        add_hist(f"Disponibilite ajoutee — {mname(nd['matricule'])} le {JOURS_SEMAINE[nd['jour_semaine']]} {nd['heure_debut']}-{nd['heure_fin']}","Creneau medecin",session["user"])
        flash("Disponibilite ajoutee.","success"); return redirect(url_for("a_creneaux"))
    filtre_med=request.args.get("medecin","")
    disp_list=DB.get("disponibilites",[])
    if filtre_med:
        disp_list=[x for x in disp_list if x["matricule"]==filtre_med]
    rows=""
    for x in sorted(disp_list,key=lambda v:(v["matricule"],v["jour_semaine"])):
        rows+=f"""<tr><td><strong>{mname(x["matricule"])}</strong></td><td>{cname(x["id_centre"])}</td>
        <td>{JOURS_SEMAINE[x["jour_semaine"]]}</td><td>{x["heure_debut"]} - {x["heure_fin"]}</td><td>{x["duree_creneau"]} min</td>
        <td><form method="POST" action="{url_for('a_creneau_suppr',did=x['id'])}" style="display:inline;"><button class="btn btn-sm btn-outline-r" onclick="return confirm('Supprimer cette disponibilite ?')"><i class="fas fa-trash"></i></button></form></td></tr>"""
    opts_m="".join(f'<option value="{m["matricule"]}" {"selected" if filtre_med==m["matricule"] else ""}>Dr. {m["prenom"]} {m["nom"]}</option>' for m in DB["medecins"])
    opts_c="".join(f'<option value="{c["id"]}">{c["nom"]}</option>' for c in DB.get("centres",[]))
    opts_j="".join(f'<option value="{i}">{j}</option>' for i,j in enumerate(JOURS_SEMAINE))
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-clock"></i>Creneaux medecins ({len(disp_list)})</div>
    <form method="GET" style="display:flex;gap:6px;align-items:center;">
      <select name="medecin" class="form-select form-select-sm" style="width:auto;" onchange="this.form.submit()">
        <option value="">Tous les medecins</option>{opts_m}
      </select>
    </form>
  </div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Medecin</th><th>Centre</th><th>Jour</th><th>Horaire</th><th>Duree creneau</th><th></th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucune disponibilite definie</td></tr>"}
  </tbody></table></div></div></div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title">Ajouter une disponibilite</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Medecin *</label><select name="matricule" class="form-select" required><option value="">--</option>{opts_m}</select></div>
      <div class="col-12"><label class="form-label">Centre *</label><select name="centre" class="form-select" required>{opts_c}</select></div>
      <div class="col-12"><label class="form-label">Jour *</label><select name="jour" class="form-select" required>{opts_j}</select></div>
      <div class="col-6"><label class="form-label">Heure debut *</label><input type="time" name="heure_debut" class="form-control" required></div>
      <div class="col-6"><label class="form-label">Heure fin *</label><input type="time" name="heure_fin" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Duree d'un creneau (min)</label><input type="number" name="duree" class="form-control" value="30"></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-save"></i>Ajouter</button></div>
    </div></form>
    <div class="al al-i mt-3" style="font-size:.76rem;"><i class="fas fa-info-circle"></i>Seuls les creneaux definis ici (et non deja pris) seront proposes lors de la prise de RDV.</div>
  </div></div></div>
</div>"""
    return page("Creneaux medecins","admin",session["user"],body)

@app.route("/a-creneaux/<int:did>/suppr",methods=["POST"])
@login_required
@role_required("admin")
def a_creneau_suppr(did):
    DB["disponibilites"]=[x for x in DB.get("disponibilites",[]) if x["id"]!=did]
    flash("Disponibilite supprimee.","success")
    return redirect(url_for("a_creneaux"))

@app.route("/api/creneaux")
@login_required
def api_creneaux():
    mat=request.args.get("medecin",""); dte=request.args.get("date","")
    if not mat or not dte:
        return jsonify({"creneaux":[]})
    return jsonify({"creneaux":creneaux_disponibles(mat,dte)})

@app.route("/a-services",methods=["GET","POST"])
@login_required
@role_required("admin")
def a_services():
    if request.method=="POST":
        d=request.form
        ns={"id":nid("services"),"libelle":d["libelle"],"description":d.get("desc",""),"id_centre":int(d.get("centre",1))}
        DB["services"].append(ns)
        add_hist(f"Nouveau service : {ns['libelle']}","Creation service",session["user"])
        flash(f"Service '{ns['libelle']}' cree.","success"); return redirect(url_for("a_services"))
    filtre_centre=request.args.get("centre","")
    opts_c="".join(f'<option value="{c["id"]}">{c["nom"]}</option>' for c in DB.get("centres",[]))
    services_list=DB["services"]
    if filtre_centre:
        services_list=[s for s in services_list if s.get("id_centre",1)==int(filtre_centre)]
    rows=""
    for s in services_list:
        meds_s=[m for m in DB["medecins"] if m["id_service"]==s["id"]]
        chef=next((m for m in meds_s if m.get("est_chef")),None)
        cons_s=len([c for c in DB["consultations"] if any(m["matricule"]==c["matricule"] for m in meds_s)])
        chef_str = ("Dr. " + chef["prenom"] + " " + chef["nom"]) if chef else "-"
        rows += "<tr><td><strong>" + s["libelle"] + "</strong></td><td>" + s["description"] + "</td><td><span class=\"bk inf\">" + cname(s.get("id_centre",1)) + "</span></td><td>" + str(len(meds_s)) + " medecin(s)</td><td>" + chef_str + "</td><td><span class=\"bk inf\">" + str(cons_s) + " consultation(s)</span></td></tr>"
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-building"></i>Services ({len(services_list)})</div>
    <form method="GET" style="display:flex;gap:6px;align-items:center;">
      <select name="centre" class="form-select form-select-sm" style="width:auto;" onchange="this.form.submit()">
        <option value="">Tous les centres</option>
        {"".join(f'<option value="{c["id"]}" {"selected" if filtre_centre==str(c["id"]) else ""}>{c["nom"]}</option>' for c in DB.get("centres",[]))}
      </select>
    </form>
    <button class="btn btn-sm btn-g" onclick="document.getElementById('fs').classList.toggle('d-none')"><i class="fas fa-plus"></i>Nouveau</button>
  </div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Libelle</th><th>Description</th><th>Centre</th><th>Medecins</th><th>Chef</th><th>Activite</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>
  <div class="col-lg-4"><div id="fs" class="card"><div class="card-hdr"><div class="title">Nouveau service</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Libelle *</label><input type="text" name="libelle" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Description</label><textarea name="desc" class="form-control" rows="2"></textarea></div>
      <div class="col-12"><label class="form-label">Centre</label><select name="centre" class="form-select">{opts_c}</select></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-save"></i>Creer</button></div>
    </div></form>
    <div class="al al-i mt-3" style="font-size:.76rem;"><i class="fas fa-info-circle"></i>Nouveau service apparait automatiquement dans les tickets.</div>
  </div></div></div>
</div>"""
    return page("Services","admin",session["user"],body)

@app.route("/a-patients")
@login_required
@role_required("admin")
def a_patients():
    def row_p(p):
        dos=next((d for d in DB["dossiers"] if d["id_patient"]==p["id"]),None)
        nb_c=len([c for c in DB["consultations"] if c["id_patient"]==p["id"]])
        nb_f=len([f for f in DB["factures"] if f["id_patient"]==p["id"]])
        gs=p.get("groupe_sanguin","?")
        gs_cls="att" if gs in ("Non connu","?","") else "ok"
        f_cls="err" if nb_f>0 else "grey"
        return (f'<tr><td><strong>{p["prenom"]} {p["nom"]}</strong></td><td>{p["sexe"]}</td>'
                f'<td>{p["date_naissance"]}</td><td>{p["telephone"]}</td><td>{p.get("email","-") or "-"}</td>'
                f'<td><span class="bk {gs_cls}">{gs}</span></td><td>{p["assurance"]}</td><td>{p["adresse"]}</td>'
                f'<td>{dos["num_dossier"] if dos else "-"}</td>'
                f'<td><span class="bk inf">{nb_c} cons.</span></td>'
                f'<td><span class="bk {f_cls}">{nb_f} fact.</span></td></tr>')
    rows="".join(row_p(p) for p in DB["patients"])
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-users"></i>Tous les patients ({len(DB["patients"])})</div></div>
<div style="padding:10px 18px;"><input type="text" id="sp" class="form-control" placeholder="Rechercher..." oninput="srch('tp','sp')" style="max-width:300px;"></div>
<div style="overflow-x:auto;"><table class="table" id="tp"><thead><tr><th>Nom Prenom</th><th>Sexe</th><th>Naissance</th><th>Telephone</th><th>Email</th><th>Groupe sg.</th><th>Assurance</th><th>Adresse</th><th>Dossier</th><th>Cons.</th><th>Fact.</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=11 class='text-center' style='color:var(--muted);padding:20px;'>Aucun patient</td></tr>"}
</tbody></table></div></div>"""
    return page("Patients","admin",session["user"],body)

@app.route("/a-factures")
@login_required
@role_required("admin")
def a_factures():
    total=sum(f["montant"] for f in DB["factures"])
    encaisse=sum(f["montant_paye"] for f in DB["factures"])
    reste_total=sum(f["reste_a_payer"] for f in DB["factures"])
    def row_af(f):
        cls="ok" if f["statut"]=="Payee" else "att" if f["statut"]=="Partielle" else "err"
        voir=f'<a href="/view-doc/facture/{f["id"]}" class="btn btn-sm btn-outline-b ms-1"><i class="fas fa-eye"></i></a>'
        return (f'<tr><td><strong>{f["num_facture"]}</strong></td><td>{pname(f["id_patient"])}</td>'
                f'<td>{f["date"]}</td><td><strong>{f["montant"]:,}</strong></td>'
                f'<td>{f["part_assurance"]:,}</td><td>{f["part_patient"]:,}</td>'
                f'<td>{f["montant_paye"]:,}</td><td>{f["reste_a_payer"]:,}</td>'
                f'<td><span class="bk {cls}">{f["statut"]}</span></td>'
                f'<td style="white-space:nowrap;">{voir}</td></tr>')
    rows="".join(row_af(f) for f in DB["factures"])
    body=f"""<div class="row g-3 mb-3">
  <div class="col-md-4"><div class="sc bg-g"><div class="sv">{total:,} F</div><div class="sl">Total facture</div></div></div>
  <div class="col-md-4"><div class="sc bg-b"><div class="sv">{encaisse:,} F</div><div class="sl">Encaisse</div></div></div>
  <div class="col-md-4"><div class="sc bg-o"><div class="sv">{reste_total:,} F</div><div class="sl">Reste a recouvrer</div></div></div>
</div>
<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-file-invoice-dollar"></i>Toutes les factures ({len(DB["factures"])})</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Facture</th><th>Patient</th><th>Date</th><th>Total</th><th>Assur.</th><th>Patient</th><th>Paye</th><th>Reste</th><th>Statut</th><th>Actions</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=10 class='text-center' style='color:var(--muted);padding:20px;'>Aucune facture</td></tr>"}
</tbody></table></div></div>"""
    return page("Toutes les factures","admin",session["user"],body)

@app.route("/a-notifs",methods=["GET","POST"])
@login_required
@role_required("admin")
def a_notifs():
    if request.method=="POST":
        d=request.form
        dest_role=d.get("dest_role","")
        dest_user=d.get("dest_user","")
        id_pat=int(d.get("id_patient",0)) if d.get("id_patient") else None
        add_notif(id_pat,d["type"],d["objet"],d["contenu"],dest_user=dest_user or None,dest_role=dest_role or None,expediteur="admin")
        flash("Notification envoyee.","success"); return redirect(url_for("a_notifs"))
    # Admin voit toutes les notifications
    notifs=get_notifs_user("admin","admin")
    for n in notifs: n["lu"]=True
    all_notifs=sorted(DB["notifications"],key=lambda x:x["date"],reverse=True)
    opts_p="".join(f'<option value="{p["id"]}">{p["prenom"]} {p["nom"]}</option>' for p in DB["patients"])
    opts_u="".join(f'<option value="{u}">({DB["users"][u]["role"]}) {DB["users"][u].get("prenom","")} {DB["users"][u].get("nom","")}</option>' for u in DB["users"] if u!="admin")
    rows="".join(f'<tr><td><small>{n["date"]}</small></td><td>{n.get("expediteur","-") or "-"}</td><td>{n.get("dest_user","-") or n.get("dest_role","-") or ("Patient:"+pname(n["id_patient"]) if n.get("id_patient") else "-")}</td><td><strong>{n["type"]}</strong></td><td>{n["objet"]}</td><td><span class="bk {"ok" if n["lu"] else "att"}">{"Lu" if n["lu"] else "Non lu"}</span></td></tr>' for n in all_notifs)
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-bell"></i>Toutes les notifications ({len(all_notifs)})</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Expediteur</th><th>Destinataire</th><th>Type</th><th>Objet</th><th>Statut</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title">Envoyer une notification</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Envoyer a (utilisateur)</label><select name="dest_user" class="form-select"><option value="">-- Choisir un utilisateur --</option>{opts_u}</select></div>
      <div class="col-12"><label class="form-label">Ou par role</label><select name="dest_role" class="form-select"><option value="">-- Par role --</option><option value="medecin">Tous les medecins</option><option value="receptionniste">Receptionniste</option><option value="pharmacien">Pharmacien</option><option value="patient">Tous les patients</option></select></div>
      <div class="col-12"><label class="form-label">Patient concerne</label><select name="id_patient" class="form-select"><option value="">-- Aucun --</option>{opts_p}</select></div>
      <div class="col-12"><label class="form-label">Type</label><select name="type" class="form-select"><option>Information</option><option>Urgence</option><option>Rappel</option><option>Alerte</option></select></div>
      <div class="col-12"><label class="form-label">Objet *</label><input type="text" name="objet" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Message *</label><textarea name="contenu" class="form-control" rows="3" required></textarea></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-paper-plane"></i>Envoyer</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Notifications globales","admin",session["user"],body)

@app.route("/a-historiques")
@login_required
@role_required("admin")
def a_historiques():
    hists=sorted(DB["historiques"],key=lambda x:x["date_action"],reverse=True)
    rows="".join(f'<tr><td><small>{h["date_action"]}</small></td><td><span class="bk inf">{h["type"]}</span></td><td>{h["description"]}</td><td>{pname(h["id_patient"]) if h.get("id_patient") else "-"}</td><td>{h.get("id_user","-")}</td></tr>' for h in hists)
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-history"></i>Historique general ({len(hists)} actions)</div></div>
<div style="padding:10px 18px;"><input type="text" id="sh" class="form-control" placeholder="Rechercher..." oninput="srch('th','sh')" style="max-width:300px;"></div>
<div style="overflow-x:auto;"><table class="table" id="th"><thead><tr><th>Date/Heure</th><th>Type</th><th>Description</th><th>Patient</th><th>Utilisateur</th></tr></thead><tbody>{rows}</tbody></table></div></div>"""
    return page("Historiques","admin",session["user"],body)
# ── ASSURANCES (admin voit tout, patient voit le sien) ───────
@app.route("/a-assurances",methods=["GET","POST"])
@login_required
@role_required("admin")
def a_assurances():
    if request.method=="POST":
        d=request.form
        nc={"id":nid("contrats"),"id_patient":int(d["patient"]),"assureur":d["assureur"],"num_contrat":d["num_contrat"],"date_debut":d["date_debut"],"date_fin":d["date_fin"],"plafond_annuel":int(d.get("plafond",500000)),"montant_utilise":0,"taux_prise_en_charge":int(d.get("taux",40)),"statut":"Actif"}
        DB["contrats_assurance"].append(nc)
        flash(f"Contrat {nc['num_contrat']} cree pour {pname(nc['id_patient'])}.","success")
        return redirect(url_for("a_assurances"))
    rows=""
    for c in DB.get("contrats_assurance",[]):
        reste=max(0,c["plafond_annuel"]-c.get("montant_utilise",0))
        pct=int((c.get("montant_utilise",0)/c["plafond_annuel"])*100) if c["plafond_annuel"]>0 else 0
        rows+=f'<tr><td><strong>{c["num_contrat"]}</strong></td><td>{pname(c["id_patient"])}</td><td><span class="bk inf">{c["assureur"]}</span></td><td>{c["taux_prise_en_charge"]}%</td><td>{c["plafond_annuel"]:,}</td><td style="color:var(--warn);font-weight:600;">{c.get("montant_utilise",0):,}</td><td style="color:{f"var(--g1)" if reste>0 else "var(--err)"};font-weight:700;">{reste:,}</td><td>{c["date_debut"]} → {c["date_fin"]}</td><td><span class="bk {"ok" if c["statut"]=="Actif" else "err"}">{c["statut"]}</span></td><td><div style="background:#e5e7eb;border-radius:20px;height:8px;min-width:80px;"><div style="background:{"var(--g1)" if pct<80 else "var(--warn)" if pct<100 else "var(--err)"};width:{min(pct,100)}%;height:8px;border-radius:20px;"></div></div><small>{pct}%</small></td></tr>'
    opts_p="".join(f'<option value="{p["id"]}">{p["prenom"]} {p["nom"]}</option>' for p in DB["patients"])
    body=f"""<div class="card mb-3"><div class="card-hdr"><div class="title"><i class="fas fa-shield-alt"></i>Contrats d assurance ({len(DB.get("contrats_assurance",[]))})</div>
    <button class="btn btn-sm btn-g" onclick="document.getElementById('fc').classList.toggle('d-none')"><i class="fas fa-plus"></i>Nouveau</button>
  </div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>N Contrat</th><th>Patient</th><th>Assureur</th><th>Taux</th><th>Plafond</th><th>Utilise</th><th>Reste</th><th>Validite</th><th>Statut</th><th>Utilisation</th></tr></thead><tbody>{rows if rows else "<tr><td colspan=10 class='text-center' style='color:var(--muted);padding:20px;'>Aucun contrat</td></tr>"}</tbody></table></div></div>
  <div id="fc" class="card d-none"><div class="card-hdr"><div class="title">Nouveau contrat</div></div><div class="card-body">
    <form method="POST"><div class="row g-3">
      <div class="col-md-6"><label class="form-label">Patient *</label><select name="patient" class="form-select" required><option value="">--</option>{opts_p}</select></div>
      <div class="col-md-6"><label class="form-label">Assureur *</label><select name="assureur" class="form-select" required><option>IPRES</option><option>CSS</option><option>LONASE</option><option>IPM</option><option>Autre</option></select></div>
      <div class="col-md-6"><label class="form-label">N Contrat *</label><input type="text" name="num_contrat" class="form-control" required placeholder="IPRES-2026-XXX"></div>
      <div class="col-md-3"><label class="form-label">Taux prise en charge (%)</label><input type="number" name="taux" class="form-control" value="40" min="0" max="100"></div>
      <div class="col-md-3"><label class="form-label">Plafond annuel (FCFA)</label><input type="number" name="plafond" class="form-control" value="500000" min="0"></div>
      <div class="col-md-6"><label class="form-label">Date debut</label><input type="date" name="date_debut" class="form-control" required></div>
      <div class="col-md-6"><label class="form-label">Date fin</label><input type="date" name="date_fin" class="form-control" required></div>
      <div class="col-12"><button type="submit" class="btn btn-g"><i class="fas fa-save"></i>Creer le contrat</button></div>
    </div></form>
  </div></div>"""
    return page("Contrats Assurance","admin",session["user"],body)

# ── ALLERGIES PATIENT (admin) ───────────────────────────────
@app.route("/a-allergies",methods=["GET","POST"])
@login_required
@role_required("admin","medecin")
def a_allergies():
    if request.method=="POST":
        d=request.form
        na={"id":nid("allergies"),"id_patient":int(d["patient"]),"libelle":d["libelle"],"type":d.get("type","Medicament"),"severite":d.get("severite","Elevee"),"date_constatee":d.get("date_constatee",date.today().strftime("%Y-%m-%d"))}
        DB["allergies_patient"].append(na)
        flash(f"Allergie {na['libelle']} enregistree pour {pname(na['id_patient'])}.","success")
        return redirect(url_for("a_allergies"))
    rows=""
    for a in DB.get("allergies_patient",[]):
        sev_cls={"Critique":"err","Elevee":"warn","Moderee":"att"}.get(a.get("severite","Elevee"),"att")
        rows+=f'<tr><td>{pname(a["id_patient"])}</td><td><strong>{a["libelle"]}</strong></td><td><span class="bk inf">{a["type"]}</span></td><td><span class="bk {sev_cls}">{a["severite"]}</span></td><td>{a["date_constatee"]}</td></tr>'
    opts_p="".join(f'<option value="{p["id"]}">{p["prenom"]} {p["nom"]}</option>' for p in DB["patients"])
    body=f"""<div class="card mb-3"><div class="card-hdr"><div class="title"><i class="fas fa-allergies"></i>Allergies patients ({len(DB.get("allergies_patient",[]))})</div>
    <button class="btn btn-sm btn-g" onclick="document.getElementById('fa').classList.toggle('d-none')"><i class="fas fa-plus"></i>Ajouter</button>
  </div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Patient</th><th>Allergie</th><th>Type</th><th>Severite</th><th>Date</th></tr></thead><tbody>{rows if rows else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucune allergie enregistree</td></tr>"}</tbody></table></div></div>
  <div id="fa" class="card d-none"><div class="card-hdr"><div class="title">Nouvelle allergie</div></div><div class="card-body">
    <form method="POST"><div class="row g-3">
      <div class="col-md-6"><label class="form-label">Patient *</label><select name="patient" class="form-select" required><option value="">--</option>{opts_p}</select></div>
      <div class="col-md-6"><label class="form-label">Allergie *</label><input type="text" name="libelle" class="form-control" required placeholder="ex: Penicilline, Ibuprofene..."></div>
      <div class="col-md-4"><label class="form-label">Type</label><select name="type" class="form-select"><option>Medicament</option><option>Aliment</option><option>Environnement</option><option>Autre</option></select></div>
      <div class="col-md-4"><label class="form-label">Severite</label><select name="severite" class="form-select"><option>Moderee</option><option>Elevee</option><option>Critique</option></select></div>
      <div class="col-md-4"><label class="form-label">Date constatee</label><input type="date" name="date_constatee" class="form-control"></div>
      <div class="col-12"><button type="submit" class="btn btn-g"><i class="fas fa-save"></i>Enregistrer</button></div>
    </div></form>
  </div></div>"""
    return page("Allergies Patients","admin" if session.get("role")=="admin" else "medecin",session["user"],body)

# ── INTERACTIONS MÉDICAMENTEUSES (admin) ────────────────────
@app.route("/a-interactions",methods=["GET","POST"])
@login_required
@role_required("admin","medecin")
def a_interactions():
    if request.method=="POST":
        d=request.form
        m1=int(d["med1"]); m2=int(d["med2"])
        ni={"id":nid("interactions"),"id_med1":m1,"id_med2":m2,"niveau":d.get("niveau","modere"),"description":d.get("description","")}
        DB["interactions_medicamenteuses"].append(ni)
        flash("Interaction enregistree.","success")
        return redirect(url_for("a_interactions"))
    meds_map={m["id"]:m["libelle"] for m in DB["medicaments"]}
    rows=""
    for inter in DB.get("interactions_medicamenteuses",[]):
        niv=inter["niveau"]
        cls={"eleve":"err","critique":"err","modere":"att"}.get(niv,"inf")
        rows+=f'<tr><td><strong>{meds_map.get(inter["id_med1"],"?")}</strong></td><td><strong>{meds_map.get(inter["id_med2"],"?")}</strong></td><td><span class="bk {cls}">{niv.upper()}</span></td><td style="font-size:.82rem;">{inter["description"]}</td></tr>'
    opts_m="".join(f'<option value="{m["id"]}">{m["libelle"]}</option>' for m in DB["medicaments"])
    body=f"""<div class="card mb-3"><div class="card-hdr"><div class="title"><i class="fas fa-pills"></i>Interactions medicamenteuses ({len(DB.get("interactions_medicamenteuses",[]))})</div>
  <button class="btn btn-sm btn-g" onclick="document.getElementById('fi').classList.toggle('d-none')"><i class="fas fa-plus"></i>Ajouter</button>
  </div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Medicament 1</th><th>Medicament 2</th><th>Niveau</th><th>Description</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=4 class='text-center' style='color:var(--muted);padding:20px;'>Aucune interaction</td></tr>"}
  </tbody></table></div></div>
  <div id="fi" class="card d-none"><div class="card-hdr"><div class="title">Nouvelle interaction</div></div><div class="card-body">
    <form method="POST"><div class="row g-3">
      <div class="col-md-5"><label class="form-label">Medicament 1 *</label><select name="med1" class="form-select" required><option value="">--</option>{opts_m}</select></div>
      <div class="col-md-5"><label class="form-label">Medicament 2 *</label><select name="med2" class="form-select" required><option value="">--</option>{opts_m}</select></div>
      <div class="col-md-2"><label class="form-label">Niveau</label><select name="niveau" class="form-select"><option value="modere">Modere</option><option value="eleve">Eleve</option><option value="critique">Critique</option></select></div>
      <div class="col-12"><label class="form-label">Description *</label><input type="text" name="description" class="form-control" required placeholder="ex: Medicament A + B : risque ..."></div>
      <div class="col-12"><button type="submit" class="btn btn-g"><i class="fas fa-save"></i>Enregistrer</button></div>
    </div></form>
  </div></div>"""
    return page("Interactions Medicamenteuses","admin" if session.get("role")=="admin" else "medecin",session["user"],body)

# SGRDMS v7 — Part 4: Routes Médecin complet

# =======================================================
# Routes Médecin : statut, téléconsult, patients, dossiers, RDV, consultations, ordonnances, messagerie
# =======================================================

@app.route("/m-status",methods=["POST"])
@login_required
@role_required("medecin")
def m_status():
    DB["users"][session["user"]]["status_med"]=request.form.get("status","Disponible")
    flash("Statut mis a jour.","success"); return redirect(url_for("dashboard"))

@app.route("/m-teleconsult-toggle")
@login_required
@role_required("medecin")
def m_teleconsult_toggle():
    u=DB["users"][session["user"]]
    u["teleconsult_actif"]=not u.get("teleconsult_actif",False)
    med=get_med(session["user"])
    if med: med["teleconsult_actif"]=u["teleconsult_actif"]
    flash("Teleconsultation "+("activee." if u["teleconsult_actif"] else "desactivee."),"success")
    return redirect(url_for("dashboard"))

@app.route("/m-patients")
@login_required
@role_required("medecin")
def m_patients():
    med=get_med(session["user"]); mat=med["matricule"]
    pids=list(set(r["id_patient"] for r in DB["rdvs"] if r["matricule"]==mat))
    pats=[p for p in DB["patients"] if p["id"] in pids]
    rows="".join(f'<tr><td><strong>{p["prenom"]} {p["nom"]}</strong></td><td>{p["telephone"]}</td><td><span class="bk {"att" if p.get("groupe_sanguin")=="Non connu" else "ok"}">{p.get("groupe_sanguin","?")}</span></td><td>{p["assurance"]}</td><td><a href="/m-dossier/{p["id"]}" class="btn btn-sm btn-g"><i class="fas fa-folder-open"></i>Dossier</a></td></tr>' for p in pats)
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-users"></i>Mes Patients ({len(pats)})</div></div>
<div style="padding:10px 18px;"><input type="text" id="smp" class="form-control" placeholder="Rechercher..." oninput="srch('tmp','smp')" style="max-width:300px;"></div>
<div style="overflow-x:auto;"><table class="table" id="tmp"><thead><tr><th>Nom Prenom</th><th>Telephone</th><th>Groupe sg.</th><th>Assurance</th><th>Dossier</th></tr></thead><tbody>{rows if rows else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucun patient assigne</td></tr>"}</tbody></table></div></div>"""
    return page("Mes Patients","medecin",session["user"],body)

@app.route("/m-dossier/<int:pid>")
@login_required
@role_required("medecin")
def m_dossier(pid):
    pat=next((p for p in DB["patients"] if p["id"]==pid),None)
    if not pat: flash("Patient introuvable","danger"); return redirect(url_for("m_patients"))
    dos=next((d for d in DB["dossiers"] if d["id_patient"]==pid),None)
    conss=[c for c in DB["consultations"] if c["id_patient"]==pid]
    ress=[r for r in DB["resultats_examens"] if r["id_patient"]==pid]
    ords=[o for o in DB["ordonnances"] if o["id_patient"]==pid]
    allergies=[a for a in DB.get("allergies_patient",[]) if a["id_patient"]==pid]
    gs=pat.get("groupe_sanguin","Non connu"); gc="att" if gs=="Non connu" else "ok"
    rows_c="".join(f'<tr><td>{c["date"]}</td><td>{c["diagnostic"]}</td><td>{c["observation"][:60]}</td><td><a href="/m-ordo/{c["id"]}" class="btn btn-sm btn-outline-b"><i class="fas fa-prescription"></i></a></td></tr>' for c in conss)
    rows_r="".join(f'<tr><td>{r["date"]}</td><td>{r["type"]}</td><td>{r["commentaire"][:60]}</td><td><span class="bk ok">{r["statut"]}</span></td></tr>' for r in ress)
    rows_o="".join(f'<tr><td>ORD-{o["id"]:04d}</td><td>{o["date"]}</td><td>{", ".join(l["libelle"] for l in o["lignes"])}</td><td>{o["duree"]} j</td></tr>' for o in ords)
    infos="".join(f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--gl);font-size:.82rem;"><span style="color:var(--muted);">{k}</span><span style="font-weight:600;">{v}</span></div>' for k,v in [("Sexe",pat["sexe"]),("Naissance",pat["date_naissance"]),("Groupe sg.",f'<span class="bk {gc}">{gs}</span>'),("Assurance",pat["assurance"]),("Telephone",pat["telephone"]),("Email",pat.get("email","-")),("Adresse",pat.get("adresse","-")),("Dossier",dos["num_dossier"] if dos else "-"),("Diagnostic gen.",dos["diagnostic_general"] if dos else "-")])
    if allergies:
        allergies_html="".join(f'<span class="badge" style="background:{"#dc3545" if a["severite"] in ("Elevee","Critique") else "#ffc107"};color:#fff;margin:2px;padding:4px 8px;border-radius:6px;font-size:.75rem;display:inline-block;"><i class="fas fa-exclamation-triangle"></i> {a["libelle"]} ({a["severite"]})</span>' for a in allergies)
    else:
        allergies_html='<span style="color:var(--muted);font-size:.8rem;">Aucune allergie connue</span>'
    body=f"""<div class="row g-3">
  <div class="col-md-3"><div class="card"><div class="card-body p-4 text-center">
    <i class="fas fa-user-circle fa-3x" style="color:var(--g1);"></i>
    <h5 style="color:var(--g3);margin-top:10px;">{pat['prenom']} {pat['nom']}</h5>
    <div style="margin-top:12px;text-align:left;">{infos}</div>
    <div style="margin-top:12px;text-align:left;">
      <div style="font-size:.8rem;color:var(--muted);font-weight:600;margin-bottom:4px;"><i class="fas fa-allergies"></i> Allergies</div>
      {allergies_html}
    </div>
    <a href="/m-nouvelle-consultation?pid={pid}" class="btn btn-g w-100 mt-3" style="justify-content:center;"><i class="fas fa-stethoscope"></i>Nouvelle Consultation</a>
  </div></div></div>
  <div class="col-md-9">
    <div class="nav-tabs">
      <button class="nav-tab active" onclick="showTab('dc1',this)">Consultations ({len(conss)})</button>
      <button class="nav-tab" onclick="showTab('dc2',this)">Ordonnances ({len(ords)})</button>
      <button class="nav-tab" onclick="showTab('dc3',this)">Resultats ({len(ress)})</button>
    </div>
    <div id="dc1" class="tab-pane"><div class="card"><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Diagnostic</th><th>Observation</th><th>Ordo</th></tr></thead><tbody>{rows_c if rows_c else "<tr><td colspan=4 class='text-center' style='color:var(--muted);padding:20px;'>Aucune</td></tr>"}</tbody></table></div></div></div>
    <div id="dc2" class="tab-pane" style="display:none;"><div class="card"><div style="overflow-x:auto;"><table class="table"><thead><tr><th>N</th><th>Date</th><th>Medicaments</th><th>Duree</th></tr></thead><tbody>{rows_o if rows_o else "<tr><td colspan=4 class='text-center' style='color:var(--muted);padding:20px;'>Aucune</td></tr>"}</tbody></table></div></div></div>
    <div id="dc3" class="tab-pane" style="display:none;"><div class="card"><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Type</th><th>Resultat</th><th>Statut</th></tr></thead><tbody>{rows_r if rows_r else "<tr><td colspan=4 class='text-center' style='color:var(--muted);padding:20px;'>Aucun</td></tr>"}</tbody></table></div></div></div>
  </div>
</div>"""
    return page(f"Dossier — {pat['prenom']} {pat['nom']}","medecin",session["user"],body)

@app.route("/m-rdvs",methods=["GET","POST"])
@login_required
@role_required("medecin")
def m_rdvs():
    med=get_med(session["user"]); mat=med["matricule"]
    if request.method=="POST":
        rid=int(request.form["rid"]); motif_ann=request.form.get("motif_ann","Empechement")
        r=next((x for x in DB["rdvs"] if x["id"]==rid and x["matricule"]==mat),None)
        if r:
            r["statut"]="Annule"
            add_notif(r["id_patient"],"RDV annule",f"RDV du {r['date']} annule par le medecin",f"Votre RDV du {r['date']} a {r['heure']} avec {mname(mat)} a ete annule. Motif : {motif_ann}. Contactez la reception pour reprogrammer.",expediteur=session["user"])
            add_notif(None,"RDV annule medecin",f"Dr. {med['prenom']} {med['nom']} a annule un RDV",f"RDV du {r['date']} pour {pname(r['id_patient'])} annule. Motif : {motif_ann}",dest_role="receptionniste",expediteur=session["user"])
            add_hist(f"RDV annule par medecin - {pname(r['id_patient'])} - {r['date']}","RDV annule",session["user"],r["id_patient"],mat)
            flash("RDV annule. Patient et receptionniste notifies.","success")
        return redirect(url_for("m_rdvs"))
    rdvs=sorted([r for r in DB["rdvs"] if r["matricule"]==mat],key=lambda x:x["date"],reverse=True)
    rows=""
    for r in rdvs:
        sc="ok" if r["statut"]=="Confirme" else "att" if r["statut"]=="En attente" else "err" if r["statut"]=="Annule" else "grey"
        ann_btn=""
        if r["statut"] in ["Confirme","En attente"]:
            ann_btn=f"""<button class="btn btn-sm btn-outline-r" onclick="document.getElementById('ann_{r['id']}').style.display='block'"><i class="fas fa-times"></i>Annuler</button>
            <div id="ann_{r['id']}" style="display:none;margin-top:6px;">
              <form method="POST">
                <input type="hidden" name="rid" value="{r['id']}">
                <input type="text" name="motif_ann" class="form-control form-control-sm mb-1" placeholder="Motif annulation" required>
                <button type="submit" class="btn btn-sm btn-r"><i class="fas fa-check"></i>Confirmer</button>
              </form>
            </div>"""
        lien=f'<a href="{r["lien_teleconsult"]}" target="_blank" class="btn btn-sm btn-b"><i class="fas fa-video"></i>Rejoindre</a>' if r.get("lien_teleconsult") and r["statut"]=="Confirme" else ""
        rows+=f'<tr><td><strong>{r["date"]}</strong></td><td>{r["heure"]}</td><td>{pname(r["id_patient"])}</td><td>{r.get("motif","")}</td><td><span class="bk inf">{r["type"]}</span></td><td><span class="bk {sc}">{r["statut"]}</span></td><td>{lien}{ann_btn}</td></tr>'
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-calendar-check"></i>Mes Rendez-vous</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Heure</th><th>Patient</th><th>Motif</th><th>Type</th><th>Statut</th><th>Actions</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=7 class='text-center' style='color:var(--muted);padding:20px;'>Aucun RDV</td></tr>"}
</tbody></table></div></div>"""
    return page("Mes Rendez-vous","medecin",session["user"],body)

@app.route("/m-consultations")
@login_required
@role_required("medecin")
def m_consultations():
    med=get_med(session["user"]); mat=med["matricule"]
    conss=[c for c in DB["consultations"] if c["matricule"]==mat]
    rows="".join(f'<tr><td>{c["date"]}</td><td>{pname(c["id_patient"])}</td><td>{c["diagnostic"]}</td><td>{c["type"]}</td><td><a href="/m-dossier/{c["id_patient"]}" class="btn btn-sm btn-outline-g me-1"><i class="fas fa-folder-open"></i>Dossier</a><a href="/m-ordo/{c["id"]}" class="btn btn-sm btn-outline-b"><i class="fas fa-prescription"></i>Ordo</a></td></tr>' for c in conss)
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-stethoscope"></i>Mes Consultations ({len(conss)})</div>
<a href="/m-nouvelle-consultation" class="btn btn-sm btn-g"><i class="fas fa-plus"></i>Nouvelle</a></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Patient</th><th>Diagnostic</th><th>Type</th><th>Actions</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucune consultation</td></tr>"}
</tbody></table></div></div>"""
    return page("Mes Consultations","medecin",session["user"],body)

@app.route("/m-nouvelle-consultation",methods=["GET","POST"])
@login_required
@role_required("medecin")
def m_nouvelle_consultation():
    med=get_med(session["user"]); mat=med["matricule"]
    pid_pre=request.args.get("pid","")
    if request.method=="POST":
        d=request.form; pid=int(d["patient"])
        nc={"id":nid("cons"),"id_patient":pid,"matricule":mat,"date":date.today().strftime("%Y-%m-%d"),"observation":d.get("obs",""),"diagnostic":d.get("diag",""),"type":d.get("type","Presentiel"),"id_ordonnance":None,"id_facture":None,"id_resultat":None}
        DB["consultations"].append(nc)
        mnt=int(d.get("montant",15000))
        pat=next((p for p in DB["patients"] if p["id"]==pid),None)
        ass=pat.get("assurance","Aucune") if pat else "Aucune"
        taux={"IPRES":0.4,"CSS":0.5,"LONASE":0.3}.get(ass,0)
        part_ass=int(mnt*taux); part_pat=mnt-part_ass
        # ── Vérification plafond annuel assurance ──
        plafond_bloque, contrat_ass, msg_plafond = verifier_plafond_assurance(pid, mnt)
        if plafond_bloque:
            part_ass=0; part_pat=mnt  # Plafond atteint : patient paie tout
            add_notif(pid,"Plafond assurance atteint","Depassement plafond annuel",msg_plafond,expediteur=session["user"])
            flash(f"⚠️ {msg_plafond} — La consultation est enregistree mais SANS prise en charge assurance.","warning")
        elif contrat_ass and part_ass>0:
            # Mettre à jour le montant utilisé du contrat
            contrat_ass["montant_utilise"]=contrat_ass.get("montant_utilise",0)+part_ass
        nf={"id":nid("facts"),"num_facture":f"FAC-{DB['_c']['facts']:04d}","id_patient":pid,"id_consultation":nc["id"],"montant":mnt,"date":date.today().strftime("%Y-%m-%d"),"statut":"Impayee","mode_paiement":"-","part_assurance":part_ass,"part_patient":part_pat,"montant_paye":0,"reste_a_payer":part_pat,"plafond_depasse":plafond_bloque}
        DB["factures"].append(nf); nc["id_facture"]=nf["id"]
        DB["documents_patient"].append({"id":nid("docs"),"id_patient":pid,"type_document":"Facture","nom_fichier":f"facture_{nf['num_facture']}.pdf","type_fichier":"PDF","date_creation":date.today().strftime("%Y-%m-%d"),"ref_id":nf["id"],"ref_type":"facture"})
        if d.get("type_exam") and d.get("commentaire_exam"):
            nr={"id":nid("docs"),"id_patient":pid,"id_consultation":nc["id"],"matricule":mat,"type":d["type_exam"],"date":date.today().strftime("%Y-%m-%d"),"commentaire":d["commentaire_exam"],"statut":"Disponible","fichier":""}
            DB["resultats_examens"].append(nr); nc["id_resultat"]=nr["id"]
            DB["documents_patient"].append({"id":nid("docs"),"id_patient":pid,"type_document":"Resultat examen","nom_fichier":f"resultat_{nr['id']:04d}.pdf","type_fichier":"PDF","date_creation":date.today().strftime("%Y-%m-%d"),"ref_id":nr["id"],"ref_type":"resultat"})
            add_notif(pid,"Resultat disponible","Vos resultats sont disponibles",f"Resultat de {d['type_exam']} disponible dans votre espace.",expediteur=session["user"])
        add_hist(f"Consultation - {d.get('diag','')} - {pname(pid)}","Consultation",session["user"],pid,mat)
        add_notif(pid,"Facture generee",f"Facture {nf['num_facture']}",f"Consultation du {nc['date']} : {mnt:,} FCFA. Part assurance : {part_ass:,} FCFA. A payer : {part_pat:,} FCFA.",expediteur=session["user"])
        flash(f"Consultation enregistree. Facture {nf['num_facture']} (a payer : {part_pat:,} FCFA).","success")
        return redirect(url_for("m_consultations"))
    pids_mes=list(set(r["id_patient"] for r in DB["rdvs"] if r["matricule"]==mat))
    pats=[p for p in DB["patients"] if p["id"] in pids_mes]
    opts="".join(f'<option value="{p["id"]}" {"selected" if str(p["id"])==str(pid_pre) else ""}>{p["prenom"]} {p["nom"]}</option>' for p in pats)
    body=f"""<div class="row justify-content-center"><div class="col-lg-8"><div class="card">
<div class="card-hdr"><div class="title"><i class="fas fa-stethoscope"></i>Nouvelle Consultation</div></div>
<div class="card-body"><form method="POST"><div class="row g-3">
  <div class="col-md-6"><label class="form-label">Patient *</label><select name="patient" class="form-select" required><option value="">--</option>{opts}</select></div>
  <div class="col-md-6"><label class="form-label">Type</label><select name="type" class="form-select"><option>Presentiel</option><option>Teleconsultation</option></select></div>
  <div class="col-12"><label class="form-label">Observations cliniques</label><textarea name="obs" class="form-control" rows="3" placeholder="Symptomes, examen clinique..."></textarea></div>
  <div class="col-12"><label class="form-label">Diagnostic *</label><input type="text" name="diag" class="form-control" required placeholder="Diagnostic principal..."></div>
  <div class="col-md-6"><label class="form-label">Montant facture (FCFA)</label><input type="number" name="montant" class="form-control" value="15000" min="0"></div>
  <div class="col-12"><div class="al al-i"><i class="fas fa-info-circle"></i>Part assurance : IPRES 40%, CSS 50%, LONASE 30%</div></div>
  <div class="col-12" style="border-top:1px solid var(--gl);padding-top:12px;"><p style="font-weight:600;color:var(--g3);font-size:.85rem;"><i class="fas fa-microscope me-1"></i>Resultat d'examen (optionnel)</p></div>
  <div class="col-md-6"><label class="form-label">Type d'examen</label><input type="text" name="type_exam" class="form-control" placeholder="Ex: Bilan sanguin..."></div>
  <div class="col-md-6"><label class="form-label">Commentaire</label><input type="text" name="commentaire_exam" class="form-control" placeholder="Resultats..."></div>
  <div class="col-12" style="display:flex;gap:8px;"><button type="submit" class="btn btn-g"><i class="fas fa-save"></i>Enregistrer</button><a href="/m-consultations" class="btn btn-outline-g">Annuler</a></div>
</div></form></div></div></div></div>"""
    return page("Nouvelle Consultation","medecin",session["user"],body)

@app.route("/m-ordo/<int:cid>",methods=["GET","POST"])
@login_required
@role_required("medecin")
def m_ordo(cid):
    med=get_med(session["user"]); mat=med["matricule"]
    cons=next((c for c in DB["consultations"] if c["id"]==cid),None)
    if not cons: flash("Consultation introuvable","danger"); return redirect(url_for("m_consultations"))
    if request.method=="POST":
        mids=request.form.getlist("med_id[]"); poses=request.form.getlist("pos[]"); dures=request.form.getlist("dur[]")
        # ── Vérification interactions / contre-indications / allergies ──
        ids_valides=[mid for mid in mids if mid]
        bloquant, alertes = verifier_interactions_ordonnance(cons["id_patient"], ids_valides)
        if bloquant and not request.form.get("force_confirm"):
            # Construire le HTML d alerte et reafficher le formulaire
            opts="".join(f'<option value="{m["id"]}">{m["libelle"]}</option>' for m in DB["medicaments"])
            alerte_html="".join(f'<div class="al {"al-d" if a["bloquant"] else "al-w"} mb-2"><i class="fas fa-{"exclamation-triangle" if a["bloquant"] else "info-circle"}"></i><span style="font-size:.83rem;">{a["message"]}</span></div>' for a in alertes)
            body=f"""<div class="row justify-content-center"><div class="col-lg-7"><div class="card">
<div class="card-hdr" style="background:#dc2626;"><div class="title" style="color:#fff;"><i class="fas fa-exclamation-triangle"></i>ALERTE — Interactions detectees</div></div>
<div class="card-body">
  <div class="al al-d mb-3"><i class="fas fa-ban"></i><strong>Validation bloquee.</strong> Des interactions a risque eleve ou critique ont ete detectees. Vous devez modifier la prescription.</div>
  {alerte_html}
  <div style="margin-top:16px;padding:12px;background:#fef2f2;border-radius:8px;border-left:4px solid #dc2626;">
    <p style="font-weight:700;color:#991b1b;font-size:.85rem;margin:0;">Regles metier : Les prescriptions doivent etre verifiees contre le module d interactions. Si le niveau de risque est eleve ou critique, le systeme bloque la validation.</p>
  </div>
  <div style="display:flex;gap:8px;margin-top:16px;">
    <a href="/m-ordo/{cid}" class="btn btn-g"><i class="fas fa-edit"></i>Modifier la prescription</a>
    <a href="/m-consultations" class="btn btn-outline-g">Annuler</a>
  </div>
</div></div></div></div>"""
            return page("Alerte Ordonnance","medecin",session["user"],body)
        lignes=[]
        for mid,pos,dur in zip(mids,poses,dures):
            if mid:
                m=next((x for x in DB["medicaments"] if x["id"]==int(mid)),None)
                if m: lignes.append({"id_medicament":int(mid),"libelle":m["libelle"],"posologie":pos,"duree":dur})
        no={"id":nid("ords"),"id_consultation":cid,"id_patient":cons["id_patient"],"matricule":mat,"date":date.today().strftime("%Y-%m-%d"),"duree":int(request.form.get("duree",7)),"lignes":lignes,"alertes_interactions":alertes}
        DB["ordonnances"].append(no); cons["id_ordonnance"]=no["id"]
        DB["documents_patient"].append({"id":nid("docs"),"id_patient":cons["id_patient"],"type_document":"Ordonnance","nom_fichier":f"ordonnance_{no['id']:04d}.pdf","type_fichier":"PDF","date_creation":date.today().strftime("%Y-%m-%d"),"ref_id":no["id"],"ref_type":"ordonnance"})
        add_hist(f"Ordonnance prescrite — {pname(cons['id_patient'])}","Ordonnance",session["user"],cons["id_patient"],mat)
        # Avertissement si alertes moderees (non bloquantes) — affiche dans le detail de l ordonnance, pas en flash
        if alertes:
            flash("Ordonnance prescrite avec avertissements (voir le detail de l'ordonnance).","warning")
        else:
            flash("Ordonnance prescrite.","success")
        return redirect(url_for("m_consultations"))
    opts="".join(f'<option value="{m["id"]}">{m["libelle"]}</option>' for m in DB["medicaments"])
    # Afficher les allergies connues du patient
    allergies_pat=[a for a in DB.get("allergies_patient",[]) if a["id_patient"]==cons["id_patient"]]
    allergie_html=""
    if allergies_pat:
        items="".join(f'<span class="bk err" style="margin:2px;">{a["libelle"]} ({a["severite"]})</span>' for a in allergies_pat)
        allergie_html=f'<div class="al al-d mb-3"><i class="fas fa-allergies"></i><strong>Allergies connues :</strong> {items}</div>'
    body=f"""<div class="row justify-content-center"><div class="col-lg-7"><div class="card">
<div class="card-hdr"><div class="title"><i class="fas fa-prescription"></i>Prescrire une Ordonnance</div></div>
<div class="card-body">
  <div class="al al-i mb-2"><i class="fas fa-info-circle"></i>Consultation #{cid} — Patient : <strong>{pname(cons["id_patient"])}</strong></div>
  {allergie_html}
  <div class="al al-w mb-3" style="font-size:.78rem;"><i class="fas fa-shield-alt"></i>Le systeme verifiera automatiquement les interactions medicamenteuses, contre-indications et allergies avant validation.</div>
<form method="POST">
  <div class="mb-3"><label class="form-label">Duree traitement (jours)</label><input type="number" name="duree" class="form-control" value="7" min="1"></div>
  <div id="lignes"><div class="row g-2 mb-2 ligne">
    <div class="col-md-5"><select name="med_id[]" class="form-select"><option value="">-- Medicament --</option>{opts}</select></div>
    <div class="col-md-4"><input type="text" name="pos[]" class="form-control" placeholder="Posologie"></div>
    <div class="col-md-3"><input type="text" name="dur[]" class="form-control" placeholder="Duree"></div>
  </div></div>
  <button type="button" class="btn btn-sm btn-outline-g mb-3" onclick="addLigne()"><i class="fas fa-plus"></i>Ajouter medicament</button>
  <div style="display:flex;gap:8px;"><button type="submit" class="btn btn-g"><i class="fas fa-shield-check"></i>Verifier et prescrire</button><a href="/m-consultations" class="btn btn-outline-g">Annuler</a></div>
</form></div></div></div></div>
<script>function addLigne(){{const c=document.getElementById('lignes');const t=c.querySelector('.ligne').cloneNode(true);t.querySelectorAll('input,select').forEach(e=>e.value='');c.appendChild(t);}}</script>"""
    return page("Ordonnance","medecin",session["user"],body)

@app.route("/m-teleconsult",methods=["GET","POST"])
@login_required
@role_required("medecin")
def m_teleconsult():
    med=get_med(session["user"]); mat=med["matricule"]
    if request.method=="POST":
        d=request.form; rdv_id=int(d.get("rdv",0)); lien=d.get("lien","")
        rdv=next((r for r in DB["rdvs"] if r["id"]==rdv_id and r["matricule"]==mat),None)
        if rdv and lien:
            existing=next((t for t in DB["teleconsultations"] if t["id_rdv"]==rdv_id),None)
            if existing:
                existing["lien"]=lien; existing["lien_envoye"]=True; existing["statut"]="Planifiee"
            else:
                nt={"id":nid("teles"),"id_patient":rdv["id_patient"],"matricule":mat,"id_rdv":rdv_id,"date_debut":f"{rdv['date']} {rdv['heure']}","statut":"Planifiee","lien":lien,"lien_envoye":True}
                DB["teleconsultations"].append(nt)
            rdv["lien_teleconsult"]=lien
            add_notif(rdv["id_patient"],"Lien teleconsultation",f"Lien du {rdv['date']}",f"Votre teleconsultation du {rdv['date']} a {rdv['heure']} avec {mname(mat)} est prete. Lien : {lien}",expediteur=session["user"])
            flash("Lien cree et patient notifie.","success")
        else:
            flash("RDV ou lien invalide.","danger")
        return redirect(url_for("m_teleconsult"))

    teles=[t for t in DB["teleconsultations"] if t["matricule"]==mat]
    # RDV teleconsultation confirmes sans lien encore cree
    rdv_sans_lien=[r for r in DB["rdvs"] if r["matricule"]==mat and r["type"]=="Teleconsultation" and r["statut"]=="Confirme" and not any(t["id_rdv"]==r["id"] for t in teles)]
    opts_r="".join(f'<option value="{r["id"]}">{r["date"]} {r["heure"]} — {pname(r["id_patient"])}</option>' for r in rdv_sans_lien)
    rows="".join(f'<tr><td>{t["date_debut"]}</td><td>{pname(t["id_patient"])}</td><td><span class="bk att">{t["statut"]}</span></td><td>{"<a href="+repr(t["lien"])+" target=_blank class=btn btn-sm btn-b><i class=fas fa-video></i>Rejoindre</a>" if t.get("lien_envoye") else "-"}</td></tr>' for t in teles)
    form_html=""
    if rdv_sans_lien:
        form_html=f"""<div class="card mb-3"><div class="card-hdr"><div class="title"><i class="fas fa-link"></i>Creer un lien de visioconference</div></div><div class="card-body">
  <form method="POST"><div class="row g-2">
    <div class="col-md-6"><label class="form-label">RDV teleconsultation *</label><select name="rdv" class="form-select" required><option value="">-- Choisir --</option>{opts_r}</select></div>
    <div class="col-md-6"><label class="form-label">Lien Meet/Zoom *</label><input type="url" name="lien" class="form-control" placeholder="https://meet.google.com/..." required></div>
    <div class="col-12"><button type="submit" class="btn btn-g"><i class="fas fa-video"></i>Creer le lien et notifier le patient</button></div>
  </div></form>
</div></div>"""
    body=f"""{form_html}<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-video"></i>Mes Teleconsultations</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Patient</th><th>Statut</th><th>Lien</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=4 class='text-center' style='color:var(--muted);padding:20px;'>Aucune teleconsultation</td></tr>"}
</tbody></table></div></div>"""
    return page("Mes Teleconsultations","medecin",session["user"],body)

@app.route("/m-service")
@login_required
@role_required("medecin")
def m_service():
    med=get_med(session["user"])
    svc=next((s for s in DB["services"] if s["id"]==med["id_service"]),None)
    meds=[m for m in DB["medecins"] if m["id_service"]==med["id_service"]]
    rows="".join(f'<tr><td>{m["matricule"]}</td><td><strong>Dr. {m["prenom"]} {m["nom"]}</strong></td><td>{m["specialite"]}</td><td>{m["telephone"]}</td><td>{m["email"]}</td><td><span class="bk {"vio" if m.get("est_chef") else "grey"}">{"Chef" if m.get("est_chef") else "Medecin"}</span></td><td><span class="bk {"ok" if DB["users"].get(m["username"],{}).get("status_med","Disponible")=="Disponible" else "att"}">{DB["users"].get(m["username"],{}).get("status_med","Disponible")}</span></td></tr>' for m in meds)
    body=f"""<div class="card mb-3"><div class="card-body p-4"><h5 style="color:var(--g3);">{svc["libelle"] if svc else "?"}</h5><p style="color:var(--muted);">{svc["description"] if svc else ""}</p>{"<span class='bk vio' style='margin-top:8px;display:inline-block;'><i class='fas fa-crown'></i> Chef de service</span>" if med.get("est_chef") else ""}</div></div>
<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-user-md"></i>Medecins du service</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Matricule</th><th>Nom</th><th>Specialite</th><th>Telephone</th><th>Email</th><th>Fonction</th><th>Statut</th></tr></thead><tbody>{rows}</tbody></table></div></div>"""
    return page("Mon Service","medecin",session["user"],body)

@app.route("/m-facture-pdf/<int:fid>")
@login_required
@role_required("medecin")
def m_facture_pdf(fid):
    med=get_med(session["user"])
    f=next((x for x in DB["factures"] if x["id"]==fid),None)
    if not f: flash("Facture introuvable","danger"); return redirect(url_for("m_consultations"))
    pat=next((p for p in DB["patients"] if p["id"]==f["id_patient"]),None)
    lignes=[
        f"Patient      : {pat['prenom']} {pat['nom']}" if pat else "Patient : -",
        f"Date naiss.  : {pat['date_naissance']}  |  Sexe : {pat['sexe']}" if pat else "",
        f"Groupe sg.   : {pat.get('groupe_sanguin','-')}" if pat else "",
        f"Assurance    : {pat['assurance']}" if pat else "",
        f"Telephone    : {pat['telephone']}" if pat else "",
        "",
        f"FACTURE {f['num_facture']}","-"*50,
        f"Date            : {f['date']}",
        f"Montant total   : {f['montant']:,} FCFA",
        f"Part assurance  : {f['part_assurance']:,} FCFA",
        f"Part patient    : {f['part_patient']:,} FCFA",
        f"Montant paye    : {f['montant_paye']:,} FCFA",
        f"Reste a payer   : {f['reste_a_payer']:,} FCFA",
        f"Mode paiement   : {f['mode_paiement']}",
        f"Statut          : {f['statut']}",
    ]
    pdf=gen_pdf(f"FACTURE {f['num_facture']}",lignes)
    return Response(pdf,mimetype="application/pdf",headers={"Content-Disposition":f"attachment; filename=facture_{f['num_facture']}.pdf"})

@app.route("/m-ordo-pdf/<int:oid>")
@login_required
@role_required("medecin")
def m_ordo_pdf(oid):
    o=next((x for x in DB["ordonnances"] if x["id"]==oid),None)
    if not o: flash("Ordonnance introuvable","danger"); return redirect(url_for("m_consultations"))
    pat=next((p for p in DB["patients"] if p["id"]==o["id_patient"]),None)
    lignes=[
        f"Patient      : {pat['prenom']} {pat['nom']}" if pat else "Patient : -",
        f"Date naiss.  : {pat['date_naissance']}  |  Sexe : {pat['sexe']}" if pat else "",
        f"Assurance    : {pat['assurance']}" if pat else "",
        f"Telephone    : {pat['telephone']}" if pat else "",
        "",
        "ORDONNANCE MEDICALE","-"*50,
        f"N           : ORD-{o['id']:04d}",
        f"Date        : {o['date']}",
        f"Medecin     : {mname(o['matricule'])}",
        f"Duree trait.: {o['duree']} jours",
        "","Medicaments prescrits :","="*50,
    ]
    for l in o["lignes"]:
        lignes+=[f"  Medicament  : {l['libelle']}",f"  Posologie   : {l['posologie']}",f"  Duree       : {l['duree']}",""]
    pdf=gen_pdf(f"ORDONNANCE ORD-{o['id']:04d}",lignes)
    return Response(pdf,mimetype="application/pdf",headers={"Content-Disposition":f"attachment; filename=ordonnance_{o['id']:04d}.pdf"})

@app.route("/m-notifs",methods=["GET","POST"])
@login_required
@role_required("medecin")
def m_notifs():
    u=session["user"]; med=get_med(u)
    if request.method=="POST":
        d=request.form; dest=d.get("dest","")
        # Peut envoyer à un autre médecin ou à la réceptionniste
        if dest=="receptionniste":
            add_notif(None,d["type"],d["objet"],d["contenu"],dest_user="receptionniste",dest_role="receptionniste",expediteur=u)
            flash("Message envoye a la receptionniste.","success")
        elif dest.startswith("dr.") or dest in DB["users"]:
            add_notif(None,d["type"],d["objet"],d["contenu"],dest_user=dest,expediteur=u)
            flash(f"Message envoye a {DB['users'].get(dest,{}).get('prenom',dest)}.","success")
        else:
            flash("Destinataire invalide.","danger")
        return redirect(url_for("m_notifs"))
    notifs=get_notifs_user(u,"medecin")
    for n in notifs: n["lu"]=True
    # Autres médecins + receptionniste comme destinataires possibles
    autres_med=[m for m in DB["medecins"] if m["username"]!=u]
    opts_dest='<option value="receptionniste">Receptionniste — Fatou Ndiaye</option>'
    opts_dest+="".join(f'<option value="{m["username"]}">Dr. {m["prenom"]} {m["nom"]} ({m["specialite"]})</option>' for m in autres_med)
    rows="".join(f'<tr><td><small>{n["date"]}</small></td><td>{n.get("expediteur","-") or "systeme"}</td><td><strong>{n["type"]}</strong></td><td>{n["objet"]}</td><td>{n["contenu"][:60]}</td></tr>' for n in notifs)
    body=f"""<div class="row g-3">
  <div class="col-lg-7"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-inbox"></i>Messages recus ({len(notifs)})</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Expediteur</th><th>Type</th><th>Objet</th><th>Message</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucun message</td></tr>"}
  </tbody></table></div></div></div>
  <div class="col-lg-5"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-paper-plane"></i>Envoyer un message</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Destinataire *</label><select name="dest" class="form-select" required><option value="">-- Choisir --</option>{opts_dest}</select></div>
      <div class="col-12"><label class="form-label">Type</label><select name="type" class="form-select"><option>Information</option><option>Urgence</option><option>Consultation</option><option>Demande</option></select></div>
      <div class="col-12"><label class="form-label">Objet *</label><input type="text" name="objet" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Message *</label><textarea name="contenu" class="form-control" rows="3" required></textarea></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-paper-plane"></i>Envoyer</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Messagerie","medecin",u,body)
# SGRDMS v5 — Part 5: Routes Patient complet

# =======================================================
# Routes Patient : dossier, documents, PDF, RDV, consultations, factures, paiements, tickets, notifications
# =======================================================

@app.route("/p-dossier")
@login_required
@role_required("patient")
def p_dossier():
    pat=get_pat(session["user"]); pid=pat["id"]
    dos=next((d for d in DB["dossiers"] if d["id_patient"]==pid),None)
    conss=[c for c in DB["consultations"] if c["id_patient"]==pid]
    allergies=[a for a in DB.get("allergies_patient",[]) if a["id_patient"]==pid]
    gs=pat.get("groupe_sanguin","Non connu"); gc="att" if gs=="Non connu" else "ok"
    rows_c="".join(f'<tr><td>{c["date"]}</td><td>{mname(c["matricule"])}</td><td><strong>{c["diagnostic"]}</strong></td><td>{c.get("observation","")[:60]}</td><td>{c["type"]}</td></tr>' for c in conss)
    infos="".join(f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--gl);font-size:.82rem;"><span style="color:var(--muted);">{k}</span><span style="font-weight:600;">{v}</span></div>' for k,v in [("Nom complet",f'{pat["prenom"]} {pat["nom"]}'),("Sexe",pat["sexe"]),("Naissance",pat["date_naissance"]),("Telephone",pat["telephone"]),("Email",pat.get("email","-")),("Adresse",pat.get("adresse","-")),("Assurance",pat["assurance"]),("Groupe sanguin",f'<span class="bk {gc}">{gs}</span>'),("Statut",pat.get("statut","Actif")),("N° Dossier",dos["num_dossier"] if dos else "-"),("Depuis",dos["date_creation"] if dos else "-"),("Diagnostic gen.",dos["diagnostic_general"] if dos else "-")])
    if allergies:
        allergies_html="".join(f'<span class="badge" style="background:{"#dc3545" if a["severite"] in ("Elevee","Critique") else "#ffc107"};color:#fff;margin:2px;padding:4px 8px;border-radius:6px;font-size:.75rem;display:inline-block;"><i class="fas fa-exclamation-triangle"></i> {a["libelle"]} ({a["severite"]})</span>' for a in allergies)
    else:
        allergies_html='<span style="color:var(--muted);font-size:.8rem;">Aucune allergie connue</span>'
    body=f"""<div class="row g-3">
  <div class="col-md-4"><div class="card"><div class="card-body p-4">
    <div style="text-align:center;margin-bottom:16px;">
      <div style="width:70px;height:70px;background:linear-gradient(135deg,var(--g1),var(--g2));border-radius:50%;display:inline-flex;align-items:center;justify-content:center;"><i class="fas fa-user" style="color:#fff;font-size:1.8rem;"></i></div>
      <h5 style="color:var(--g3);margin-top:10px;">{pat["prenom"]} {pat["nom"]}</h5>
      <span class="bk inf">{pat["assurance"]}</span>
    </div>
    {infos}
    <div style="margin-top:12px;text-align:left;">
      <div style="font-size:.8rem;color:var(--muted);font-weight:600;margin-bottom:4px;"><i class="fas fa-allergies"></i> Allergies</div>
      {allergies_html}
    </div>
  </div></div></div>
  <div class="col-md-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-stethoscope"></i>Historique de mes consultations ({len(conss)})</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Medecin</th><th>Diagnostic</th><th>Observation</th><th>Type</th></tr></thead><tbody>
  {rows_c if rows_c else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucune consultation</td></tr>"}
  </tbody></table></div></div></div>
</div>"""
    return page("Mon Dossier","patient",session["user"],body)

@app.route("/p-documents")
@login_required
@role_required("patient")
def p_documents():
    pat=get_pat(session["user"]); pid=pat["id"]
    docs=[d for d in DB["documents_patient"] if d["id_patient"]==pid]
    view_id=request.args.get("voir")
    viewer_html=""
    if view_id:
        doc_v=next((d for d in docs if str(d["id"])==str(view_id)),None)
        if doc_v:
            # Generer le contenu inline du document
            ref_type=doc_v["ref_type"]; ref_id=doc_v["ref_id"]
            contenu_lignes=[]
            if ref_type=="ordonnance":
                o=next((x for x in DB["ordonnances"] if x["id"]==ref_id),None)
                if o:
                    contenu_lignes=[f"<div style='font-weight:700;font-size:1.05rem;color:var(--g3);margin-bottom:12px;'>ORDONNANCE — ORD-{o['id']:04d}</div>",
                        f"<div class='row g-2'><div class='col-md-6'><small style='color:var(--muted);'>Date</small><div>{o['date']}</div></div><div class='col-md-6'><small style='color:var(--muted);'>Médecin</small><div><strong>{mname(o['matricule'])}</strong></div></div><div class='col-md-6'><small style='color:var(--muted);'>Durée traitement</small><div>{o['duree']} jours</div></div></div>",
                        "<hr style='margin:12px 0;'>","<div style='font-weight:600;color:var(--g3);margin-bottom:8px;'><i class='fas fa-pills me-1'></i>Médicaments prescrits</div>",
                    ]
                    for l in o["lignes"]:
                        contenu_lignes.append(f"<div style='background:#f0fdf4;border-radius:8px;padding:10px 14px;margin-bottom:8px;border-left:3px solid var(--g1);'><strong>{l['libelle']}</strong><br><small>Posologie : {l['posologie']} | Durée : {l['duree']}</small></div>")
            elif ref_type=="resultat":
                r=next((x for x in DB["resultats_examens"] if x["id"]==ref_id),None)
                if r:
                    contenu_lignes=[f"<div style='font-weight:700;font-size:1.05rem;color:var(--g3);margin-bottom:12px;'>RÉSULTAT D'EXAMEN</div>",
                        f"<div class='row g-2'><div class='col-md-6'><small style='color:var(--muted);'>Type</small><div><strong>{r['type']}</strong></div></div><div class='col-md-6'><small style='color:var(--muted);'>Date</small><div>{r['date']}</div></div><div class='col-12'><small style='color:var(--muted);'>Médecin</small><div>{mname(r['matricule'])}</div></div></div>",
                        "<hr style='margin:12px 0;'>",
                        f"<div style='background:#f0fdf4;border-radius:8px;padding:14px;'><i class='fas fa-microscope me-2' style='color:var(--g3);'></i>{r['commentaire']}</div>",
                        f"<div class='mt-2'><span class='bk ok'>{r['statut']}</span></div>",
                    ]
            elif ref_type=="facture":
                f_=next((x for x in DB["factures"] if x["id"]==ref_id),None)
                if f_:
                    contenu_lignes=[f"<div style='font-weight:700;font-size:1.05rem;color:var(--g3);margin-bottom:12px;'>FACTURE — {f_['num_facture']}</div>",
                        f"<div class='row g-3'><div class='col-md-4'><div class='sc bg-g'><div class='sv'>{f_['montant']:,} F</div><div class='sl'>Montant total</div></div></div><div class='col-md-4'><div class='sc bg-b'><div class='sv'>{f_['part_assurance']:,} F</div><div class='sl'>Part assurance</div></div></div><div class='col-md-4'><div class='sc bg-o'><div class='sv'>{f_['part_patient']:,} F</div><div class='sl'>Part patient</div></div></div></div>",
                        f"<hr style='margin:12px 0;'><div class='row g-2' style='font-size:.9rem;'><div class='col-md-6'><small style='color:var(--muted);'>Date</small><div>{f_['date']}</div></div><div class='col-md-6'><small style='color:var(--muted);'>Mode paiement</small><div>{f_['mode_paiement']}</div></div><div class='col-md-6'><small style='color:var(--muted);'>Montant payé</small><div style='color:var(--g3);font-weight:600;'>{f_['montant_paye']:,} FCFA</div></div><div class='col-md-6'><small style='color:var(--muted);'>Reste à payer</small><div style='color:var(--err);font-weight:600;'>{f_['reste_a_payer']:,} FCFA</div></div></div>",
                        f"<div class='mt-2'><span class='bk {"ok" if f_["statut"]=="Payee" else "att" if f_["statut"]=="Partiel" else "err"}'>{f_['statut']}</span></div>",
                    ]
            if contenu_lignes:
                viewer_html=f"""<div class="card mb-3" style="border:2px solid var(--g1);"><div class="card-hdr" style="background:var(--g3);"><div class="title" style="color:#fff;"><i class="fas fa-eye"></i>Visualisation — {doc_v['type_document']}</div><a href="/p-documents" class="btn btn-sm" style="background:rgba(255,255,255,.2);color:#fff;"><i class="fas fa-times"></i>Fermer</a></div><div class="card-body">{"".join(contenu_lignes)}<div style="margin-top:16px;display:flex;gap:8px;"><a href="/p-download/{doc_v['ref_type']}/{doc_v['ref_id']}" class="btn btn-g"><i class="fas fa-download"></i>Telecharger PDF</a></div></div></div>"""
    rows="".join(f'<tr><td><i class="fas fa-{"file-pdf" if d["type_fichier"]=="PDF" else "image"}" style="color:var(--{"err" if d["type_fichier"]=="PDF" else "b1"});"></i> {d["nom_fichier"]}</td><td><span class="bk inf">{d["type_document"]}</span></td><td>{d["date_creation"]}</td><td style="white-space:nowrap;"><a href="/p-documents?voir={d["id"]}" class="btn btn-sm btn-outline-g me-1"><i class="fas fa-eye"></i>Voir</a><a href="/p-download/{d["ref_type"]}/{d["ref_id"]}" class="btn btn-sm btn-g"><i class="fas fa-download"></i>PDF</a></td></tr>' for d in docs)
    body=f"""
{viewer_html}
<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-folder-open"></i>Mes Documents ({len(docs)})</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Fichier</th><th>Type</th><th>Date</th><th>Actions</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=4 class='text-center' style='color:var(--muted);padding:20px;'>Aucun document</td></tr>"}
</tbody></table></div></div>"""
    return page("Mes Documents","patient",session["user"],body)

@app.route("/p-download/<ref_type>/<int:ref_id>")
@login_required
@role_required("patient")
def p_download(ref_type,ref_id):
    pat=get_pat(session["user"]); pid=pat["id"]
    gs=pat.get("groupe_sanguin","Non connu")
    entete=[
        f"Patient      : {pat['prenom']} {pat['nom']}",
        f"Date naiss.  : {pat['date_naissance']}  |  Sexe : {pat['sexe']}",
        f"Groupe sg.   : {gs}",
        f"Assurance    : {pat['assurance']}",
        f"Telephone    : {pat['telephone']}",
        f"Email        : {pat.get('email','-')}",
        f"Adresse      : {pat.get('adresse','-')}",
        "",
    ]
    fname="document.pdf"; lignes=entete[:]
    if ref_type=="ordonnance":
        o=next((x for x in DB["ordonnances"] if x["id"]==ref_id and x["id_patient"]==pid),None)
        if not o: flash("Document introuvable","danger"); return redirect(url_for("p_documents"))
        lignes+=["ORDONNANCE MEDICALE","-"*50,f"N           : ORD-{o['id']:04d}",f"Date        : {o['date']}",f"Medecin     : {mname(o['matricule'])}",f"Duree trait.: {o['duree']} jours","","Medicaments prescrits :","="*50]
        for l in o["lignes"]: lignes+=[f"  Medicament  : {l['libelle']}",f"  Posologie   : {l['posologie']}",f"  Duree       : {l['duree']}",""]
        fname=f"ordonnance_{o['id']:04d}.pdf"; titre=f"ORDONNANCE ORD-{o['id']:04d}"
    elif ref_type=="resultat":
        r=next((x for x in DB["resultats_examens"] if x["id"]==ref_id and x["id_patient"]==pid),None)
        if not r: flash("Document introuvable","danger"); return redirect(url_for("p_documents"))
        lignes+=["RESULTAT D'EXAMEN","-"*50,f"Type examen : {r['type']}",f"Date        : {r['date']}",f"Medecin     : {mname(r['matricule'])}",f"Statut      : {r['statut']}","","Commentaire du medecin :","="*50,r["commentaire"]]
        fname=f"resultat_{r['id']:04d}.pdf"; titre=f"RESULTAT {r['type'].upper()}"
    elif ref_type=="facture":
        f=next((x for x in DB["factures"] if x["id"]==ref_id and x["id_patient"]==pid),None)
        if not f: flash("Document introuvable","danger"); return redirect(url_for("p_documents"))
        lignes+=[f"FACTURE {f['num_facture']}","-"*50,f"Date            : {f['date']}",f"Montant total   : {f['montant']:,} FCFA",f"Part assurance  : {f['part_assurance']:,} FCFA",f"Part patient    : {f['part_patient']:,} FCFA",f"Montant paye    : {f['montant_paye']:,} FCFA",f"Reste a payer   : {f['reste_a_payer']:,} FCFA","",f"Mode paiement   : {f['mode_paiement']}",f"Statut          : {f['statut']}"]
        fname=f"facture_{f['num_facture']}.pdf"; titre=f"FACTURE {f['num_facture']}"
    else:
        titre="DOCUMENT"
    pdf=gen_pdf(titre,lignes)
    return Response(pdf,mimetype="application/pdf",headers={"Content-Disposition":f"attachment; filename={fname}"})

@app.route("/p-rdvs",methods=["GET","POST"])
@login_required
@role_required("patient")
def p_rdvs():
    pat=get_pat(session["user"]); pid=pat["id"]
    if request.method=="POST":
        d=request.form
        nd={"id":nid("demandes"),"id_patient":pid,"id_service":int(d.get("service",1)),"type":d.get("type","Presentiel"),"motif":d.get("motif",""),"statut":"En attente","date_demande":date.today().strftime("%Y-%m-%d"),"traite_par":None}
        DB["demandes_rdv"].append(nd)
        add_notif(None,"Demande RDV",f"Nouvelle demande RDV — {pname(pid)}",f"{pname(pid)} demande un RDV ({sname(nd['id_service'])}) — Motif : {nd['motif']}",dest_role="receptionniste",expediteur=f"patient:{pid}")
        add_hist(f"Demande RDV - {sname(nd['id_service'])} - {pname(pid)}","Demande RDV",session["user"],pid)
        flash("Demande envoyee. La receptionniste vous repondra.","success")
        return redirect(url_for("p_rdvs"))
    rdvs=sorted([r for r in DB["rdvs"] if r["id_patient"]==pid],key=lambda x:x["date"],reverse=True)
    rows=""
    for r in rdvs:
        sc="ok" if r["statut"]=="Confirme" else "att" if r["statut"]=="En attente" else "err"
        lien=f'<a href="{r["lien_teleconsult"]}" target="_blank" class="btn btn-sm btn-b"><i class="fas fa-video"></i>Rejoindre</a>' if r.get("lien_teleconsult") and r["statut"]=="Confirme" else ""
        rows+=f'<tr><td><strong>{r["date"]}</strong></td><td>{r["heure"]}</td><td>{mname(r["matricule"])}</td><td>{r.get("motif","")}</td><td><span class="bk inf">{r["type"]}</span></td><td><span class="bk {sc}">{r["statut"]}</span></td><td>{lien}</td></tr>'
    opts_s="".join(f'<option value="{s["id"]}">{s["libelle"]}</option>' for s in DB["services"])
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-calendar-check"></i>Mes Rendez-vous</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Heure</th><th>Medecin</th><th>Motif</th><th>Type</th><th>Statut</th><th>Lien</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=7 class='text-center' style='color:var(--muted);padding:20px;'>Aucun RDV</td></tr>"}
  </tbody></table></div></div></div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-plus"></i>Prendre un RDV</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Service *</label><select name="service" class="form-select">{opts_s}</select></div>
      <div class="col-12"><label class="form-label">Type</label><select name="type" class="form-select"><option>Presentiel</option><option>Teleconsultation</option></select></div>
      <div class="col-12"><label class="form-label">Motif *</label><textarea name="motif" class="form-control" rows="3" required placeholder="Decrivez votre motif..."></textarea></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-paper-plane"></i>Envoyer la demande</button></div>
    </div></form>
    <div class="al al-i mt-2" style="font-size:.76rem;"><i class="fas fa-info-circle"></i>La receptionniste traitera votre demande et vous notifiera.</div>
  </div></div></div>
</div>"""
    return page("Mes Rendez-vous","patient",session["user"],body)

@app.route("/p-consultations")
@login_required
@role_required("patient")
def p_consultations():
    pat=get_pat(session["user"]); pid=pat["id"]
    conss=[c for c in DB["consultations"] if c["id_patient"]==pid]
    rows="".join(f'<tr><td>{c["date"]}</td><td>{mname(c["matricule"])}</td><td><strong>{c["diagnostic"]}</strong></td><td>{c.get("observation","")[:60]}</td><td>{c["type"]}</td></tr>' for c in conss)
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-stethoscope"></i>Mes Consultations ({len(conss)})</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Medecin</th><th>Diagnostic</th><th>Observation</th><th>Type</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucune consultation</td></tr>"}
</tbody></table></div></div>"""
    return page("Mes Consultations","patient",session["user"],body)

@app.route("/p-teleconsult")
@login_required
@role_required("patient")
def p_teleconsult():
    pat=get_pat(session["user"]); pid=pat["id"]
    teles=[t for t in DB["teleconsultations"] if t["id_patient"]==pid]
    rows="".join(f'<tr><td>{t["date_debut"]}</td><td>{mname(t["matricule"])}</td><td><span class="bk att">{t["statut"]}</span></td><td>{"<a href="+repr(t["lien"])+" target=_blank class=btn btn-sm btn-b><i class=fas fa-video></i>Rejoindre</a>" if t.get("lien_envoye") else "-"}</td></tr>' for t in teles)
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-video"></i>Mes Teleconsultations</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Medecin</th><th>Statut</th><th>Lien</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=4 class='text-center' style='color:var(--muted);padding:20px;'>Aucune teleconsultation</td></tr>"}
</tbody></table></div></div>"""
    return page("Mes Teleconsultations","patient",session["user"],body)

@app.route("/p-resultats")
@login_required
@role_required("patient")
def p_resultats():
    pat=get_pat(session["user"]); pid=pat["id"]
    ress=[r for r in DB["resultats_examens"] if r["id_patient"]==pid]
    voir_id=request.args.get("voir")
    voir_html=""
    if voir_id:
        r=next((x for x in ress if str(x["id"])==str(voir_id)),None)
        if r:
            voir_html=f"""<div class="card mb-3" style="border:2px solid var(--g1);"><div class="card-hdr" style="background:var(--g3);"><div class="title" style="color:#fff;"><i class="fas fa-microscope"></i>Resultat — {r["type"]}</div><a href="/p-resultats" class="btn btn-sm" style="background:rgba(255,255,255,.2);color:#fff;"><i class="fas fa-times"></i>Fermer</a></div><div class="card-body">
  <div class="row g-3 mb-3">
    <div class="col-md-4"><small style="color:var(--muted);">Type d examen</small><div style="font-weight:700;color:var(--g3);">{r["type"]}</div></div>
    <div class="col-md-4"><small style="color:var(--muted);">Date</small><div>{r["date"]}</div></div>
    <div class="col-md-4"><small style="color:var(--muted);">Medecin</small><div>{mname(r["matricule"])}</div></div>
  </div>
  <div style="background:#f0fdf4;border-radius:10px;padding:18px;border-left:4px solid var(--g1);">
    <div style="font-weight:600;color:var(--g3);margin-bottom:8px;"><i class="fas fa-flask me-2"></i>Résultats et commentaires</div>
    <div style="font-size:.93rem;line-height:1.7;">{r["commentaire"]}</div>
  </div>
  <div class="mt-3"><span class="bk ok">{r["statut"]}</span></div>
</div></div>"""
    rows="".join(f'<tr><td>{r["date"]}</td><td>{r["type"]}</td><td>{mname(r["matricule"])}</td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{r["commentaire"][:70]}...</td><td><span class="bk ok">{r["statut"]}</span></td><td><a href="/p-resultats?voir={r["id"]}" class="btn btn-sm btn-outline-g"><i class="fas fa-eye"></i>Voir</a></td></tr>' for r in ress)
    body=f"""
{voir_html}
<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-microscope"></i>Mes Resultats d examens ({len(ress)})</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Type</th><th>Medecin</th><th>Apercu</th><th>Statut</th><th>Action</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucun resultat</td></tr>"}
</tbody></table></div></div>"""
    return page("Mes Resultats","patient",session["user"],body)

@app.route("/p-factures",methods=["GET","POST"])
@login_required
@role_required("patient")
def p_factures():
    pat=get_pat(session["user"]); pid=pat["id"]
    if request.method=="POST":
        d=request.form; fid=int(d["fid"]); montant=int(d.get("montant",0))
        f=next((x for x in DB["factures"] if x["id"]==fid and x["id_patient"]==pid),None)
        if f and montant>0 and montant<=f["reste_a_payer"]:
            mode=d.get("mode","Especes")
            f["montant_paye"]+=montant; f["reste_a_payer"]-=montant
            if f["reste_a_payer"]==0: f["statut"]="Payee"; f["mode_paiement"]=mode
            else: f["statut"]="Partielle"; f["mode_paiement"]=mode
            DB["paiements"].append({"id":nid("paiements"),"id_facture":fid,"id_patient":pid,"montant":montant,"date":date.today().strftime("%Y-%m-%d"),"mode":mode,"statut":"Valide"})
            add_hist(f"Paiement {montant:,} FCFA ({mode}) - {f['num_facture']}","Paiement",session["user"],pid)
            add_notif(None,"Paiement recu",f"Paiement {f['num_facture']} — {pname(pid)}",f"{pname(pid)} a paye {montant:,} FCFA pour {f['num_facture']}. Reste : {f['reste_a_payer']:,} FCFA.",dest_role="receptionniste",expediteur=session["user"])
            flash(f"Paiement de {montant:,} FCFA enregistre. Reste : {f['reste_a_payer']:,} FCFA.","success")
        else:
            flash("Montant invalide ou superieur au reste a payer.","danger")
        return redirect(url_for("p_factures"))
    facts=[f for f in DB["factures"] if f["id_patient"]==pid]
    rows=""
    for f in facts:
        sc="ok" if f["statut"]=="Payee" else "att" if f["statut"]=="Partielle" else "err"
        pay_btn=""
        if f["reste_a_payer"]>0:
            pay_btn=f"""<button class="btn btn-sm btn-g" onclick="document.getElementById('pf_{f['id']}').style.display='block'"><i class="fas fa-credit-card"></i>Payer</button>
            <div id="pf_{f['id']}" style="display:none;margin-top:6px;padding:10px;background:var(--gl);border-radius:8px;">
              <form method="POST">
                <input type="hidden" name="fid" value="{f['id']}">
                <div class="mb-1"><label class="form-label">Montant (max {f["reste_a_payer"]:,} FCFA)</label>
                <input type="number" name="montant" class="form-control form-control-sm" value="{f["reste_a_payer"]}" min="1" max="{f["reste_a_payer"]}" required></div>
                <div class="mb-2"><select name="mode" class="form-select form-select-sm"><option>Wave</option><option>Orange Money</option><option>Free Money</option><option>Especes</option><option>Carte bancaire</option></select></div>
                <button type="submit" class="btn btn-sm btn-g"><i class="fas fa-check"></i>Valider</button>
              </form>
            </div>"""
        dl_btn=f'<a href="/view-doc/facture/{f["id"]}" class="btn btn-sm btn-outline-g"><i class="fas fa-eye"></i>Voir</a>'
        rows+=f'<tr><td><strong>{f["num_facture"]}</strong></td><td>{f["date"]}</td><td>{f["montant"]:,}</td><td>{f["part_assurance"]:,}</td><td>{f["part_patient"]:,}</td><td style="color:var(--g1);font-weight:600;">{f["montant_paye"]:,}</td><td style="color:{"var(--err)" if f["reste_a_payer"]>0 else "var(--g1)"};font-weight:700;">{f["reste_a_payer"]:,}</td><td><span class="bk {sc}">{f["statut"]}</span></td><td>{pay_btn} {dl_btn}</td></tr>'
    # Infos contrat assurance
    contrat=get_contrat_assurance(pid)
    contrat_html=""
    if contrat:
        reste_plaf=reste_plafond(pid)
        pct=int((contrat.get("montant_utilise",0)/contrat["plafond_annuel"])*100) if contrat["plafond_annuel"]>0 else 0
        contrat_html=f'''<div class="card mb-3"><div class="card-hdr"><div class="title"><i class="fas fa-shield-alt" style="color:var(--acc);"></i>Mon contrat assurance — {contrat["assureur"]}</div></div>
<div class="card-body"><div class="row g-3">
  <div class="col-md-3"><div class="sc bg-b"><div class="sv" style="font-size:1rem;">{contrat["taux_prise_en_charge"]}%</div><div class="sl">Taux prise en charge</div></div></div>
  <div class="col-md-3"><div class="sc bg-g"><div class="sv" style="font-size:.95rem;">{contrat["plafond_annuel"]:,} F</div><div class="sl">Plafond annuel</div></div></div>
  <div class="col-md-3"><div class="sc bg-o"><div class="sv" style="font-size:.95rem;">{contrat.get("montant_utilise",0):,} F</div><div class="sl">Utilise cette annee</div></div></div>
  <div class="col-md-3"><div class="sc {"bg-g" if reste_plaf>0 else "bg-r"}"><div class="sv" style="font-size:.95rem;">{reste_plaf:,} F</div><div class="sl">Reste disponible</div></div></div>
  <div class="col-12"><div style="background:#f0fdf4;border-radius:8px;padding:10px 14px;font-size:.82rem;"><b>N° Contrat :</b> {contrat["num_contrat"]} &nbsp;|&nbsp; <b>Validite :</b> {contrat["date_debut"]} au {contrat["date_fin"]} &nbsp;|&nbsp; <b>Statut :</b> <span class="bk ok">{contrat["statut"]}</span></div></div>
  <div class="col-12"><label style="font-size:.8rem;color:var(--muted);">Utilisation plafond ({pct}%)</label><div style="background:#e5e7eb;border-radius:20px;height:10px;margin-top:4px;"><div style="background:{"var(--g1)" if pct<80 else "var(--warn)" if pct<100 else "var(--err)"};width:{min(pct,100)}%;height:10px;border-radius:20px;transition:.4s;"></div></div></div>
</div></div></div>'''
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-file-invoice-dollar"></i>Mes Factures ({len(facts)})</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Facture</th><th>Date</th><th>Total FCFA</th><th>Part assur.</th><th>A payer</th><th>Paye</th><th>Reste</th><th>Statut</th><th>Actions</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=9 class='text-center' style='color:var(--muted);padding:20px;'>Aucune facture</td></tr>"}
</tbody></table></div></div>
{contrat_html}"""
    return page("Mes Factures","patient",session["user"],body)

@app.route("/p-paiements")
@login_required
@role_required("patient")
def p_paiements():
    pat=get_pat(session["user"]); pid=pat["id"]
    pays=sorted([p for p in DB["paiements"] if p["id_patient"]==pid],key=lambda x:x["date"],reverse=True)
    rows="".join(f'<tr><td>{p["date"]}</td><td>{next((f["num_facture"] for f in DB["factures"] if f["id"]==p["id_facture"]),"?")}</td><td><strong>{p["montant"]:,} FCFA</strong></td><td><span class="bk inf">{p["mode"]}</span></td><td><span class="bk ok">{p["statut"]}</span></td></tr>' for p in pays)
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-credit-card"></i>Mes Paiements ({len(pays)})</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Facture</th><th>Montant</th><th>Mode</th><th>Statut</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucun paiement</td></tr>"}
</tbody></table></div></div>"""
    return page("Mes Paiements","patient",session["user"],body)

@app.route("/p-tickets",methods=["GET","POST"])
@login_required
@role_required("patient")
def p_tickets():
    pat=get_pat(session["user"]); pid=pat["id"]
    if request.method=="POST":
        d=request.form
        nt={"id":nid("tickets"),"id_patient":pid,"type_ticket":d["type"],"num_ticket":f"TKT-{DB['_c']['tickets']:03d}","statut":"Emis","date_emission":date.today().strftime("%Y-%m-%d"),"prix":int(d.get("prix",500))}
        DB["tickets"].append(nt)
        add_hist(f"Ticket {nt['num_ticket']} — {nt['type_ticket']}","Ticket",session["user"],pid)
        add_notif(None,"Nouveau ticket",f"Ticket {nt['num_ticket']}",f"{pname(pid)} a achete un ticket pour {nt['type_ticket']}.",dest_role="receptionniste",expediteur=session["user"])
        flash(f"Ticket {nt['num_ticket']} emis pour {nt['type_ticket']}.","success")
        return redirect(url_for("p_tickets"))
    mes_tickets=[t for t in DB.get("tickets",[]) if t["id_patient"]==pid]
    voir_id=request.args.get("voir")
    voir_html=""
    if voir_id:
        t=next((x for x in mes_tickets if str(x["id"])==str(voir_id)),None)
        if t:
            contrat=get_contrat_assurance(pid)
            voir_html=f"""<div class="card mb-3" style="border:2px solid var(--g1);"><div class="card-hdr" style="background:var(--g3);"><div class="title" style="color:#fff;"><i class="fas fa-ticket-alt"></i>Detail Ticket — {t['num_ticket']}</div><a href="/p-tickets" class="btn btn-sm" style="background:rgba(255,255,255,.2);color:#fff;"><i class="fas fa-times"></i>Fermer</a></div>
<div class="card-body"><div style="text-align:center;margin-bottom:20px;">
  <div style="background:linear-gradient(135deg,#14532d,#16a34a);border-radius:14px;padding:24px 32px;color:#fff;display:inline-block;min-width:240px;">
    <div style="font-size:2.2rem;font-weight:800;letter-spacing:3px;">{t['num_ticket']}</div>
    <div style="font-size:1.05rem;margin-top:6px;opacity:.9;">{t['type_ticket']}</div>
    <div style="font-size:.75rem;opacity:.65;margin-top:4px;">Centre de Sante LE TROPICAL</div>
  </div>
</div>
<table style="width:100%;font-size:.9rem;border-collapse:separate;border-spacing:0 4px;">
  <tr><td style="padding:8px 10px;color:var(--muted);width:45%;">Numero ticket</td><td style="font-weight:700;color:var(--g3);">{t['num_ticket']}</td></tr>
  <tr style="background:#f0fdf4;"><td style="padding:8px 10px;color:var(--muted);">Service</td><td style="font-weight:600;">{t['type_ticket']}</td></tr>
  <tr><td style="padding:8px 10px;color:var(--muted);">Patient</td><td><strong>{pat['prenom']} {pat['nom']}</strong></td></tr>
  <tr style="background:#f0fdf4;"><td style="padding:8px 10px;color:var(--muted);">Telephone</td><td>{pat['telephone']}</td></tr>
  <tr><td style="padding:8px 10px;color:var(--muted);">Assurance</td><td><span class="bk inf">{pat['assurance']}</span></td></tr>
  <tr style="background:#f0fdf4;"><td style="padding:8px 10px;color:var(--muted);">Prix</td><td style="font-weight:700;">{t['prix']:,} FCFA</td></tr>
  <tr><td style="padding:8px 10px;color:var(--muted);">Date emission</td><td>{t['date_emission']}</td></tr>
  <tr style="background:#f0fdf4;"><td style="padding:8px 10px;color:var(--muted);">Statut</td><td><span class="bk att">{t['statut']}</span></td></tr>
  {"<tr><td style='padding:8px 10px;color:var(--muted);'>Contrat assur.</td><td>"+contrat['num_contrat']+" ("+contrat['assureur']+")</td></tr>" if contrat else ""}
</table>
<div class="al al-i mt-3" style="font-size:.78rem;"><i class="fas fa-info-circle"></i>Montrez cet ecran au receptionniste pour validation. Le ticket sera visible dans son interface.</div>
</div></div>"""
    opts_s="".join(f'<option value="{s["libelle"]}">{s["libelle"]}</option>' for s in DB["services"])
    rows="".join(f'<tr><td><strong style="color:var(--g3);">{t["num_ticket"]}</strong></td><td>{t["type_ticket"]}</td><td>{t["prix"]:,} FCFA</td><td>{t["date_emission"]}</td><td><span class="bk att">{t["statut"]}</span></td><td><a href="/p-tickets?voir={t["id"]}" class="btn btn-sm btn-outline-g"><i class="fas fa-eye"></i>Voir</a></td></tr>' for t in sorted(mes_tickets,key=lambda x:x["id"],reverse=True))
    body=f"""
{voir_html}
<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-ticket-alt"></i>Mes Tickets ({len(mes_tickets)})</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Numero</th><th>Service</th><th>Prix</th><th>Date</th><th>Statut</th><th>Detail</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucun ticket — Achetez votre premier ticket ci-contre.</td></tr>"}
  </tbody></table></div></div></div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-plus-circle"></i>Acheter un ticket</div></div><div class="card-body">
    <div class="al al-i mb-3" style="font-size:.78rem;"><i class="fas fa-info-circle"></i>Apres achat, cliquez sur <strong>Voir</strong> pour afficher le detail a presenter a la reception.</div>
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Service *</label><select name="type" class="form-select">{opts_s}</select></div>
      <div class="col-12"><label class="form-label">Prix (FCFA)</label><input type="number" name="prix" class="form-control" value="500" min="0"></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-ticket-alt"></i>Acheter le ticket</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Mes Tickets","patient",session["user"],body)


@app.route("/p-notifs",methods=["GET","POST"])
@login_required
@role_required("patient")
def p_notifs():
    pat=get_pat(session["user"]); pid=pat["id"]
    if request.method=="POST":
        d=request.form
        add_notif(pid,d["type"],d["objet"],d["contenu"],dest_role="receptionniste",expediteur=session["user"])
        flash("Message envoye a la receptionniste.","success")
        return redirect(url_for("p_notifs"))
    notifs=get_notifs_user(session["user"],"patient",pid)
    for n in notifs: n["lu"]=True
    rows="".join(f'<tr><td><small>{n["date"]}</small></td><td>{n.get("expediteur","-") or "systeme"}</td><td><strong>{n["type"]}</strong></td><td>{n["objet"]}</td><td>{n["contenu"][:60]}</td></tr>' for n in notifs)
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-bell"></i>Mes Notifications ({len(notifs)})</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>De</th><th>Type</th><th>Objet</th><th>Message</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucune notification</td></tr>"}
  </tbody></table></div></div></div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-paper-plane"></i>Contacter la reception</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Type</label><select name="type" class="form-select"><option>Question</option><option>Demande RDV</option><option>Reclamation</option><option>Information</option></select></div>
      <div class="col-12"><label class="form-label">Objet *</label><input type="text" name="objet" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Message *</label><textarea name="contenu" class="form-control" rows="3" required></textarea></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-paper-plane"></i>Envoyer</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Notifications","patient",session["user"],body)
# SGRDMS v5 — Part 6: Receptionniste complet (sans accès dossier médical)

# =======================================================
# Routes Réceptionniste : patients, RDV (reprogrammation/annulation), triage, attente, facturation, messagerie
# =======================================================

@app.route("/r-patients",methods=["GET","POST"])
@login_required
@role_required("receptionniste")
def r_patients():
    if request.method=="POST":
        d=request.form
        np={"id":nid("patients"),"nom":d["nom"],"prenom":d["prenom"],"sexe":d.get("sexe","M"),"telephone":d.get("tel",""),"email":d.get("email",""),"date_naissance":d.get("ddn",""),"adresse":d.get("adr",""),"assurance":d.get("ass","Aucune"),"username":"","statut":"Actif","groupe_sanguin":d.get("gs","Non connu"),"photo":""}
        DB["patients"].append(np)
        ndo={"id":nid("dossiers"),"id_patient":np["id"],"num_dossier":f"DOS-{DB['_c']['dossiers']:04d}","date_creation":date.today().strftime("%Y-%m-%d"),"diagnostic_general":"Nouveau patient"}
        DB["dossiers"].append(ndo)
        # Créer un compte utilisateur automatiquement
        prenom_clean=d["prenom"].lower().replace(" ","").replace("é","e").replace("è","e").replace("ê","e").replace("à","a")
        nom_clean=d["nom"].lower().replace(" ","")[:4]
        uname=f"{prenom_clean}.{nom_clean}"
        # S assurer que l identifiant est unique
        base_uname=uname; counter=1
        while uname in DB["users"]:
            uname=f"{base_uname}{counter}"; counter+=1
        pwd_gen=f"pat{np['id']:03d}trop"
        DB["users"][uname]={"password":pwd_gen,"role":"patient","nom":d["nom"],"prenom":d["prenom"],"email":d.get("email",""),"telephone":d.get("tel",""),"photo":"","id_ref":np["id"]}
        np["username"]=uname
        add_hist(f"Nouveau patient : {np['prenom']} {np['nom']} — Compte : {uname}","Creation patient",session["user"],np["id"])
        flash(f"Patient {np['prenom']} {np['nom']} enregistre ! Dossier : {ndo['num_dossier']}. IDENTIFIANT : {uname} | MOT DE PASSE : {pwd_gen}","success")
        return redirect(url_for("r_patients"))
    # ✅ Pas d'icône dossier médical pour la réceptionniste
    rows="".join(f'<tr><td><strong>{p["prenom"]} {p["nom"]}</strong></td><td>{p["sexe"]}</td><td>{p["telephone"]}</td><td>{p.get("email","-")}</td><td><span class="bk {"att" if p.get("groupe_sanguin","")=="Non connu" else "ok"}">{p.get("groupe_sanguin","Non connu")}</span></td><td>{p["assurance"]}</td><td><a href="/r-rdvs?pid={p["id"]}" class="btn btn-sm btn-outline-g"><i class="fas fa-calendar-plus"></i>RDV</a></td></tr>' for p in DB["patients"])
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-users"></i>Patients ({len(DB["patients"])})</div>
    <button class="btn btn-sm btn-g" onclick="document.getElementById('fp').classList.toggle('d-none')"><i class="fas fa-user-plus"></i>Nouveau</button>
  </div>
  <div style="padding:10px 18px;"><input type="text" id="srch_p" class="form-control" placeholder="Rechercher..." oninput="srch('tbl_p','srch_p')" style="max-width:300px;"></div>
  <div style="overflow-x:auto;"><table class="table" id="tbl_p"><thead><tr><th>Nom Prenom</th><th>Sexe</th><th>Telephone</th><th>Email</th><th>Groupe sg.</th><th>Assurance</th><th>Actions</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>
  <div class="col-lg-4"><div id="fp" class="card d-none"><div class="card-hdr"><div class="title">Nouveau patient</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-6"><label class="form-label">Nom *</label><input type="text" name="nom" class="form-control" required></div>
      <div class="col-6"><label class="form-label">Prenom *</label><input type="text" name="prenom" class="form-control" required></div>
      <div class="col-6"><label class="form-label">Sexe</label><select name="sexe" class="form-select"><option value="M">M</option><option value="F">F</option></select></div>
      <div class="col-6"><label class="form-label">Groupe sanguin</label><select name="gs" class="form-select"><option value="Non connu" selected>Non connu</option><option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>O+</option><option>O-</option><option>AB+</option><option>AB-</option></select></div>
      <div class="col-12"><label class="form-label">Telephone *</label><input type="text" name="tel" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Email</label><input type="email" name="email" class="form-control"></div>
      <div class="col-12"><label class="form-label">Date naissance</label><input type="date" name="ddn" class="form-control"></div>
      <div class="col-12"><label class="form-label">Adresse</label><input type="text" name="adr" class="form-control"></div>
      <div class="col-12"><label class="form-label">Assurance</label><select name="ass" class="form-select"><option>Aucune</option><option>IPRES</option><option>CSS</option><option>LONASE</option><option>Autre</option></select></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-save"></i>Enregistrer</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Patients","receptionniste",session["user"],body)

@app.route("/r-rdvs",methods=["GET","POST"])
@login_required
@role_required("receptionniste")
def r_rdvs():
    if request.method=="POST":
        d=request.form; action=d.get("action","creer")
        if action=="creer":
            rdv_type=d.get("type","Presentiel")
            if rdv_type=="Teleconsultation":
                med_check=next((m for m in DB["medecins"] if m["matricule"]==d["medecin"]),None)
                if not (med_check and med_check.get("teleconsult_actif")):
                    flash("Ce medecin n'a pas active la teleconsultation. Choisissez un RDV presentiel ou un autre medecin.","danger")
                    return redirect(url_for("r_rdvs"))
            libres=creneaux_disponibles(d["medecin"],d["date"])
            if libres and d["heure"] not in libres:
                flash("Ce creneau n'est plus disponible pour ce medecin. Veuillez choisir un creneau libre.","danger")
                return redirect(url_for("r_rdvs"))
            nr={"id":nid("rdvs"),"id_patient":int(d["patient"]),"matricule":d["medecin"],"date":d["date"],"heure":d["heure"],"type":rdv_type,"statut":"Confirme","motif":d.get("motif",""),"lien_teleconsult":None}
            DB["rdvs"].append(nr)
            # Vérifier si c'est pour une demande existante
            dem_id=int(d.get("dem_id",0))
            if dem_id:
                dem=next((x for x in DB["demandes_rdv"] if x["id"]==dem_id),None)
                if dem: dem["statut"]="Traite"; dem["traite_par"]=session["user"]
            add_hist(f"RDV cree — {pname(nr['id_patient'])} / {mname(nr['matricule'])} le {nr['date']}","Rendez-vous",session["user"],nr["id_patient"],nr["matricule"])
            add_notif(nr["id_patient"],"RDV confirme",f"Votre RDV est confirme le {nr['date']} a {nr['heure']}",f"RDV avec {mname(nr['matricule'])} confirme le {nr['date']} a {nr['heure']}.",expediteur=session["user"])
            flash("RDV cree. Patient notifie.","success")
        elif action=="reprogrammer":
            rid=int(d["rid"])
            r=next((x for x in DB["rdvs"] if x["id"]==rid),None)
            if r:
                old_date=r["date"]; old_heure=r["heure"]
                r["date"]=d["new_date"]; r["heure"]=d["new_heure"]; r["statut"]="Confirme"
                motif_rep=d.get("motif_rep","Reprogrammation")
                add_notif(r["id_patient"],"RDV reprogramme",f"RDV reprogramme au {r['date']}",f"Votre RDV initialement prevu le {old_date} a {old_heure} a ete reprogramme au {r['date']} a {r['heure']}. Motif : {motif_rep}",expediteur=session["user"])
                add_notif(None,"RDV reprogramme",f"RDV de {pname(r['id_patient'])} reprogramme",f"RDV reprogramme du {old_date} au {r['date']} pour {pname(r['id_patient'])}.",dest_user=r["matricule"].replace("MED","dr.").lower(),expediteur=session["user"])
                add_hist(f"RDV reprogramme — {old_date} -> {r['date']} — {pname(r['id_patient'])}","RDV reprogramme",session["user"],r["id_patient"])
                flash("RDV reprogramme. Patient et medecin notifies.","success")
        elif action=="annuler":
            rid=int(d["rid"]); motif_ann=d.get("motif_ann","Annulation")
            r=next((x for x in DB["rdvs"] if x["id"]==rid),None)
            if r:
                r["statut"]="Annule"
                add_notif(r["id_patient"],"RDV annule",f"Votre RDV du {r['date']} a ete annule",f"Votre RDV du {r['date']} a {r['heure']} avec {mname(r['matricule'])} a ete annule. Motif : {motif_ann}",expediteur=session["user"])
                med_obj=next((m for m in DB["medecins"] if m["matricule"]==r["matricule"]),None)
                if med_obj:
                    add_notif(None,"RDV annule",f"Votre RDV du {r['date']} annule",f"RDV du {r['date']} pour {pname(r['id_patient'])} annule par la reception. Motif : {motif_ann}",dest_user=med_obj["username"],expediteur=session["user"])
                add_hist(f"RDV annule — {r['date']} — {pname(r['id_patient'])}","RDV annule",session["user"],r["id_patient"])
                # Auto-proposer le 1er patient prioritaire en liste d attente du meme service
                med_svc=med_obj["id_service"] if med_obj else None
                if med_svc:
                    att_list=sorted([a for a in DB["liste_attente"] if a["id_service"]==med_svc and a["statut"]=="En attente"],key=lambda x:(0 if x["priorite"]=="Urgent" else 1 if x["priorite"]=="Prioritaire" else 2,x["numero_ordre"]))
                    if att_list:
                        prochain=att_list[0]
                        add_notif(prochain["id_patient"],"Creneau disponible",f"Un creneau est disponible le {r['date']}",f"Suite a l annulation d un RDV, un creneau est maintenant disponible le {r['date']} a {r['heure']} avec {mname(r['matricule'])}. Contactez la reception pour confirmer.",expediteur=session["user"])
                        add_notif(None,"Proposition automatique","Patient en attente propose pour slot libere",f"RDV annule pour {pname(r['id_patient'])}. Patient propose automatiquement : {pname(prochain['id_patient'])} (priorite: {prochain['priorite']}) — service {sname(med_svc)}.",dest_role="receptionniste",expediteur="system")
                        flash(f"RDV annule. Patient et medecin notifies. {pname(prochain['id_patient'])} (liste d attente) a ete propose automatiquement pour le creneau libere.","success")
                    else:
                        flash("RDV annule. Patient et medecin notifies.","success")
                else:
                    flash("RDV annule. Patient et medecin notifies.","success")
        return redirect(url_for("r_rdvs"))
    pid_pre=request.args.get("pid",""); dem_pre=request.args.get("dem","0")
    rows=""
    for r in sorted(DB["rdvs"],key=lambda x:x["date"],reverse=True):
        sc="ok" if r["statut"]=="Confirme" else "att" if r["statut"]=="En attente" else "err"
        actions=""
        if r["statut"] in ["Confirme","En attente"]:
            actions+=f"""<button class="btn btn-sm btn-outline-b" onclick="document.getElementById('rep_{r['id']}').style.display='block'"><i class="fas fa-redo"></i></button>
            <div id="rep_{r['id']}" style="display:none;margin-top:6px;padding:8px;background:#dbeafe;border-radius:6px;">
              <form method="POST"><input type="hidden" name="action" value="reprogrammer"><input type="hidden" name="rid" value="{r['id']}">
                <div class="row g-1"><div class="col-6"><input type="date" name="new_date" class="form-control form-control-sm" required></div><div class="col-6"><input type="time" name="new_heure" class="form-control form-control-sm" required></div></div>
                <input type="text" name="motif_rep" class="form-control form-control-sm mt-1" placeholder="Motif reprogrammation">
                <button type="submit" class="btn btn-sm btn-b mt-1"><i class="fas fa-check"></i>Confirmer</button>
              </form></div>
            <button class="btn btn-sm btn-outline-r ms-1" onclick="document.getElementById('ann_{r['id']}').style.display='block'"><i class="fas fa-times"></i></button>
            <div id="ann_{r['id']}" style="display:none;margin-top:6px;padding:8px;background:#fee2e2;border-radius:6px;">
              <form method="POST"><input type="hidden" name="action" value="annuler"><input type="hidden" name="rid" value="{r['id']}">
                <input type="text" name="motif_ann" class="form-control form-control-sm mb-1" placeholder="Motif annulation" required>
                <button type="submit" class="btn btn-sm btn-r"><i class="fas fa-check"></i>Confirmer</button>
              </form></div>"""
        rows+=f'<tr><td><strong>{r["date"]}</strong></td><td>{r["heure"]}</td><td>{pname(r["id_patient"])}</td><td>{mname(r["matricule"])}</td><td>{r.get("motif","")}</td><td><span class="bk inf">{r["type"]}</span></td><td><span class="bk {sc}">{r["statut"]}</span></td><td>{actions}</td></tr>'
    opts_p="".join(f'<option value="{p["id"]}" {"selected" if str(p["id"])==pid_pre else ""}>{p["prenom"]} {p["nom"]}</option>' for p in DB["patients"])
    opts_m="".join(f'<option value="{m["matricule"]}">Dr. {m["prenom"]} {m["nom"]} ({m["specialite"]})</option>' for m in DB["medecins"])
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-calendar-check"></i>Tous les RDV ({len(DB["rdvs"])})</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Heure</th><th>Patient</th><th>Medecin</th><th>Motif</th><th>Type</th><th>Statut</th><th>Actions</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=8 class='text-center' style='color:var(--muted);padding:20px;'>Aucun RDV</td></tr>"}
  </tbody></table></div></div></div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title">Nouveau RDV</div></div><div class="card-body">
    <form method="POST"><input type="hidden" name="action" value="creer"><input type="hidden" name="dem_id" value="{dem_pre}"><div class="row g-2">
      <div class="col-12"><label class="form-label">Patient *</label><select name="patient" class="form-select" required><option value="">--</option>{opts_p}</select></div>
      <div class="col-12"><label class="form-label">Medecin *</label><select name="medecin" id="selMed" class="form-select" required onchange="majCreneaux()"><option value="">--</option>{opts_m}</select></div>
      <div class="col-6"><label class="form-label">Date *</label><input type="date" name="date" id="selDate" class="form-control" required onchange="majCreneaux()"></div>
      <div class="col-6"><label class="form-label">Heure *</label><select name="heure" id="selHeure" class="form-select" required><option value="">-- Choisir une date/medecin --</option></select></div>
      <div class="col-12"><label class="form-label">Type</label><select name="type" class="form-select"><option>Presentiel</option><option>Teleconsultation</option></select></div>
      <div class="col-12"><label class="form-label">Motif</label><input type="text" name="motif" class="form-control"></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-save"></i>Creer le RDV</button></div>
    </div></form>
  </div></div></div>
</div>
<script>
function majCreneaux(){{
  const med=document.getElementById('selMed').value;
  const dte=document.getElementById('selDate').value;
  const sel=document.getElementById('selHeure');
  if(!med||!dte){{sel.innerHTML='<option value="">-- Choisir une date/medecin --</option>';return;}}
  sel.innerHTML='<option value="">Chargement...</option>';
  fetch('/api/creneaux?medecin='+encodeURIComponent(med)+'&date='+encodeURIComponent(dte))
    .then(r=>r.json()).then(data=>{{
      if(!data.creneaux || data.creneaux.length===0){{
        sel.innerHTML='<option value="">Aucun creneau libre — saisir manuellement</option>';
        const opt=document.createElement('option');
        sel.removeAttribute('disabled');
      }} else {{
        sel.innerHTML='<option value="">-- Choisir un creneau --</option>'+data.creneaux.map(h=>'<option value="'+h+'">'+h+'</option>').join('');
      }}
    }});
}}
</script>"""
    return page("Rendez-vous","receptionniste",session["user"],body)

@app.route("/r-demandes")
@login_required
@role_required("receptionniste")
def r_demandes():
    rows="".join(f'<tr><td>{d["date_demande"]}</td><td>{pname(d["id_patient"])}</td><td>{sname(d["id_service"])}</td><td>{d["type"]}</td><td>{d["motif"][:50]}</td><td><span class="bk {"ok" if d["statut"]=="Traite" else "att"}">{d["statut"]}</span></td><td>{"<a href=/r-rdvs?pid="+str(d["id_patient"])+"&dem="+str(d["id"])+" class=btn btn-sm btn-g><i class=fas fa-calendar-plus></i>Creer RDV</a>" if d["statut"]=="En attente" else "-"}</td></tr>' for d in DB["demandes_rdv"])
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-inbox"></i>Demandes de RDV ({len(DB["demandes_rdv"])})</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Patient</th><th>Service</th><th>Type</th><th>Motif</th><th>Statut</th><th>Action</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=7 class='text-center' style='color:var(--muted);padding:20px;'>Aucune demande</td></tr>"}
</tbody></table></div></div>"""
    return page("Demandes RDV","receptionniste",session["user"],body)

@app.route("/r-tickets",methods=["GET","POST"])
@login_required
@role_required("receptionniste")
def r_tickets():
    if request.method=="POST":
        d=request.form
        cid=int(d.get("centre",1))
        prix=tarif_centre(cid)
        nt={"id":nid("tickets"),"id_patient":int(d["patient"]),"type_ticket":d["type"],"num_ticket":f"TKT-{DB['_c']['tickets']:03d}","statut":"Emis","date_emission":date.today().strftime("%Y-%m-%d"),"prix":prix,"id_centre":cid}
        DB["tickets"].append(nt)
        add_hist(f"Ticket {nt['num_ticket']} — {nt['type_ticket']} — {pname(nt['id_patient'])} — {prix} FCFA ({cname(cid)})","Ticket",session["user"],nt["id_patient"])
        flash(f"Ticket {nt['num_ticket']} emis ({prix:,} FCFA).","success"); return redirect(url_for("r_tickets"))
    rows="".join(f'<tr><td><strong>{t["num_ticket"]}</strong></td><td>{pname(t["id_patient"])}</td><td>{t["type_ticket"]}</td><td>{t["prix"]:,} FCFA</td><td>{t["date_emission"]}</td><td><span class="bk att">{t["statut"]}</span></td><td><a href="/r-ticket-detail/{t["id"]}" class="btn btn-sm btn-outline-g"><i class="fas fa-eye"></i>Voir</a></td></tr>' for t in sorted(DB.get("tickets",[]),key=lambda x:x["id"],reverse=True))
    opts_p="".join(f'<option value="{p["id"]}">{p["prenom"]} {p["nom"]}</option>' for p in DB["patients"])
    opts_s="".join(f'<option value="{s["libelle"]}">{s["libelle"]}</option>' for s in DB["services"])
    opts_c="".join(f'<option value="{c["id"]}" data-tarif="{c.get("tarif_ticket",0)}">{c["nom"]} ({c.get("tarif_ticket",0):,} FCFA)</option>' for c in DB.get("centres",[]))
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-ticket-alt"></i>Tickets emis</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Numero</th><th>Patient</th><th>Service</th><th>Prix</th><th>Date</th><th>Statut</th><th>Detail</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucun ticket</td></tr>"}
  </tbody></table></div></div></div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title">Vendre un ticket</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Patient *</label><select name="patient" class="form-select" required><option value="">--</option>{opts_p}</select></div>
      <div class="col-12"><label class="form-label">Service *</label><select name="type" class="form-select">{opts_s}</select></div>
      <div class="col-12"><label class="form-label">Centre *</label><select name="centre" id="selCentreTkt" class="form-select" onchange="document.getElementById('prixAff').innerText=this.options[this.selectedIndex].dataset.tarif+' FCFA';">{opts_c}</select></div>
      <div class="col-12"><label class="form-label">Prix (FCFA)</label><div class="form-control" style="background:var(--bg2,#f8f9fa);" id="prixAff">{tarif_centre(1):,} FCFA</div><div style="font-size:.7rem;color:var(--muted);">Tarif fixe defini par l'admin pour ce centre</div></div>
      <div class="col-12"><button type="submit" class="btn btn-o w-100" style="justify-content:center;color:#fff;"><i class="fas fa-ticket-alt"></i>Emettre</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Tickets","receptionniste",session["user"],body)

@app.route("/r-ticket-detail/<int:tid>")
@login_required
@role_required("receptionniste")
def r_ticket_detail(tid):
    t=next((x for x in DB.get("tickets",[]) if x["id"]==tid),None)
    if not t: flash("Ticket introuvable","danger"); return redirect(url_for("r_tickets"))
    pat=next((p for p in DB["patients"] if p["id"]==t["id_patient"]),None)
    contrat=get_contrat_assurance(t["id_patient"]) if pat else None
    body=f"""<div class="row justify-content-center"><div class="col-lg-6">
  <div class="card" style="border:2px solid var(--g1);">
    <div class="card-hdr" style="background:var(--g3);"><div class="title" style="color:#fff;"><i class="fas fa-ticket-alt" style="color:#86efac;"></i>Detail Ticket {t['num_ticket']}</div></div>
    <div class="card-body">
      <div style="text-align:center;margin-bottom:20px;">
        <div style="background:linear-gradient(135deg,#14532d,#16a34a);border-radius:14px;padding:24px;color:#fff;display:inline-block;min-width:220px;">
          <div style="font-size:2rem;font-weight:700;letter-spacing:2px;">{t['num_ticket']}</div>
          <div style="font-size:1rem;margin-top:4px;opacity:.9;">{t['type_ticket']}</div>
          <div style="font-size:.8rem;opacity:.7;margin-top:6px;">Centre de Sante LE TROPICAL</div>
        </div>
      </div>
      <table style="width:100%;font-size:.9rem;">
        <tr><td style="padding:7px;color:var(--muted);width:40%;">Numero ticket</td><td style="font-weight:700;color:var(--g3);">{t['num_ticket']}</td></tr>
        <tr style="background:#f0fdf4;"><td style="padding:7px;color:var(--muted);">Service</td><td style="font-weight:600;">{t['type_ticket']}</td></tr>
        <tr><td style="padding:7px;color:var(--muted);">Patient</td><td><strong>{"" if not pat else pat["prenom"]+" "+pat["nom"]}</strong></td></tr>
        <tr style="background:#f0fdf4;"><td style="padding:7px;color:var(--muted);">Telephone</td><td>{"" if not pat else pat["telephone"]}</td></tr>
        <tr><td style="padding:7px;color:var(--muted);">Assurance</td><td><span class="bk inf">{"" if not pat else pat["assurance"]}</span></td></tr>
        <tr style="background:#f0fdf4;"><td style="padding:7px;color:var(--muted);">Prix</td><td style="font-weight:700;">{t['prix']:,} FCFA</td></tr>
        <tr><td style="padding:7px;color:var(--muted);">Date emission</td><td>{t['date_emission']}</td></tr>
        <tr style="background:#f0fdf4;"><td style="padding:7px;color:var(--muted);">Statut</td><td><span class="bk att">{t['statut']}</span></td></tr>
        {"<tr><td style=padding:7px;color:var(--muted);>Contrat assur.</td><td>"+contrat['num_contrat']+" ("+contrat['assureur']+")</td></tr>" if contrat else ""}
      </table>
      <div class="al al-i mt-3" style="font-size:.78rem;"><i class="fas fa-info-circle"></i>Le patient a presente ce ticket depuis son espace personnel. Verifiez les informations avant validation.</div>
      <div style="margin-top:16px;display:flex;gap:8px;justify-content:center;">
        <a href="/r-ticket-valider/{t['id']}" class="btn btn-g"><i class="fas fa-check"></i>Valider le ticket</a>
        <a href="/r-tickets" class="btn btn-outline-g">Retour</a>
      </div>
    </div>
  </div></div></div>"""
    return page(f"Ticket {t['num_ticket']}","receptionniste",session["user"],body)

@app.route("/r-ticket-valider/<int:tid>")
@login_required
@role_required("receptionniste")
def r_ticket_valider(tid):
    t=next((x for x in DB.get("tickets",[]) if x["id"]==tid),None)
    if t: t["statut"]="Valide"; flash(f"Ticket {t['num_ticket']} valide.","success")
    return redirect(url_for("r_tickets"))

@app.route("/r-attente",methods=["GET","POST"])
@login_required
@role_required("receptionniste")
def r_attente():
    if request.method=="POST":
        d=request.form; action=d.get("action")
        if action=="add":
            pid=int(d["patient"]); sid=int(d.get("service",1))
            deja=next((a for a in DB["liste_attente"] if a["id_patient"]==pid and a["statut"]=="En attente"),None)
            if deja: flash(f"{pname(pid)} est deja dans la file.","warning")
            else:
                ordre=len([a for a in DB["liste_attente"] if a["statut"]=="En attente" and a["id_service"]==sid])+1
                na={"id":nid("attente"),"id_patient":pid,"id_service":sid,"numero_ordre":ordre,"date_arrivee":datetime.now().strftime("%Y-%m-%d %H:%M"),"statut":"En attente","priorite":d.get("priorite","Normal"),"motif":d.get("motif","Consultation")}
                DB["liste_attente"].append(na)
                add_hist(f"Patient {pname(pid)} ajoute a la file ({sname(sid)})","Attente",session["user"],pid)
                flash(f"{pname(pid)} ajoute — N{ordre} dans la file de {sname(sid)}.","success")
        elif action=="appeler":
            att=next((a for a in DB["liste_attente"] if a["id"]==int(d["id"])),None)
            if att: att["statut"]="Appele"; flash(f"Patient N{att['numero_ordre']} appele.","success")
        elif action=="terminer":
            att=next((a for a in DB["liste_attente"] if a["id"]==int(d["id"])),None)
            if att: att["statut"]="Termine"
        return redirect(url_for("r_attente"))

    # ✅ Liste d'attente par service
    opts_p="".join(f'<option value="{p["id"]}">{p["prenom"]} {p["nom"]}</option>' for p in DB["patients"])
    opts_s="".join(f'<option value="{s["id"]}">{s["libelle"]}</option>' for s in DB["services"])
    def row_att(a,show_btn=True):
        pc="err" if a["priorite"]=="Urgent" else "att" if a["priorite"]=="Prioritaire" else "ok"
        act=f'<form method="POST" style="display:inline;"><input type="hidden" name="action" value="appeler"><input type="hidden" name="id" value="{a["id"]}"><button type="submit" class="btn btn-sm btn-g"><i class="fas fa-bullhorn"></i>Appeler</button></form>' if show_btn else f'<form method="POST" style="display:inline;"><input type="hidden" name="action" value="terminer"><input type="hidden" name="id" value="{a["id"]}"><button type="submit" class="btn btn-sm btn-outline-r btn-sm"><i class="fas fa-check"></i>Termine</button></form>'
        return f'<tr><td><strong>N{a["numero_ordre"]}</strong></td><td>{pname(a["id_patient"])}</td><td>{a["motif"]}</td><td><span class="bk {pc}">{a["priorite"]}</span></td><td><small>{a["date_arrivee"]}</small></td><td>{act}</td></tr>'

    # Onglets par service
    tabs_nav=""; tabs_content=""
    for i,s in enumerate(DB["services"]):
        en_att=[a for a in DB["liste_attente"] if a["id_service"]==s["id"] and a["statut"]=="En attente"]
        app=[a for a in DB["liste_attente"] if a["id_service"]==s["id"] and a["statut"]=="Appele"]
        active="active" if i==0 else ""
        tabs_nav+=f'<button class="nav-tab {active}" onclick="showTab(\'att_{s["id"]}\',this)">{s["libelle"]} ({len(en_att)})</button>'
        inner_rows="".join(row_att(a) for a in sorted(en_att,key=lambda x:x["numero_ordre"]))
        app_rows="".join(row_att(a,False) for a in app)
        disp="block" if i==0 else "none"
        tabs_content+=f'<div id="att_{s["id"]}" class="tab-pane" style="display:{disp};"><div class="card"><div class="card-hdr"><div class="title">{s["libelle"]} — En attente</div></div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>N</th><th>Patient</th><th>Motif</th><th>Priorite</th><th>Arrivee</th><th>Action</th></tr></thead><tbody>{inner_rows if inner_rows else "<tr><td colspan=6 class=text-center style=color:var(--muted);padding:20px;>File vide</td></tr>"}</tbody></table></div></div>{"<div class=card style=margin-top:12px;><div class=card-hdr><div class=title>Appeles</div></div><div style=overflow-x:auto;><table class=table><thead><tr><th>N</th><th>Patient</th><th>Motif</th><th>Priorite</th><th>Arrivee</th><th>Action</th></tr></thead><tbody>"+app_rows+"</tbody></table></div></div>" if app_rows else ""}</div>'

    total_att=len([a for a in DB["liste_attente"] if a["statut"]=="En attente"])
    body=f"""<div class="row g-3 mb-3">
  <div class="col-md-4"><div class="sc bg-o"><div class="sv">{total_att}</div><div class="sl">Total en attente</div></div></div>
</div>
<div class="row g-3">
  <div class="col-lg-8"><div class="nav-tabs">{tabs_nav}</div>{tabs_content}</div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-user-plus"></i>Ajouter a la file</div></div><div class="card-body">
    <form method="POST"><input type="hidden" name="action" value="add"><div class="row g-2">
      <div class="col-12"><label class="form-label">Patient *</label><select name="patient" class="form-select" required><option value="">--</option>{opts_p}</select></div>
      <div class="col-12"><label class="form-label">Service *</label><select name="service" class="form-select">{opts_s}</select></div>
      <div class="col-12"><label class="form-label">Motif</label><input type="text" name="motif" class="form-control" value="Consultation"></div>
      <div class="col-12"><label class="form-label">Priorite</label><select name="priorite" class="form-select"><option value="Normal">Normal</option><option value="Prioritaire">Prioritaire</option><option value="Urgent">Urgent</option></select></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-plus"></i>Ajouter</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Liste d'attente","receptionniste",session["user"],body)

@app.route("/r-triage",methods=["GET","POST"])
@login_required
@role_required("receptionniste")
def r_triage():
    if request.method=="POST":
        d=request.form; action=d.get("action","add")
        if action=="add":
            nt={"id":nid("triage"),"id_patient":int(d["patient"]),"date_arrivee":datetime.now().strftime("%Y-%m-%d %H:%M"),"motif":d.get("motif",""),"niveau_urgence":d.get("niveau","3 - Semi-urgent"),"tension":d.get("tension",""),"temperature":float(d.get("temperature",37.0)),"saturation":int(d.get("saturation",98)),"frequence_cardiaque":int(d.get("fc",80)),"statut":"En attente","pris_en_charge_par":d.get("medecin",""),"observations":d.get("obs","")}
            DB["triage"].append(nt)
            add_hist(f"Triage : {pname(nt['id_patient'])} — {nt['niveau_urgence']}","Triage",session["user"],nt["id_patient"])
            flash(f"Patient {pname(nt['id_patient'])} enregistre aux urgences.","success")
        elif action=="update":
            t=next((x for x in DB["triage"] if x["id"]==int(d["tid"])),None)
            if t: t["statut"]=d.get("statut",t["statut"])
        elif action=="transferer":
            t=next((x for x in DB["triage"] if x["id"]==int(d["tid"])),None)
            sid=int(d.get("service_dest",0))
            if t and sid:
                old_svc=t.get("service_dest_nom","Urgences")
                new_svc=sname(sid)
                t["statut"]="Transfere"
                t["service_dest"]=sid
                # Ajouter a la liste d attente du service de destination
                ordre=len([a for a in DB["liste_attente"] if a["statut"]=="En attente" and a["id_service"]==sid])+1
                DB["liste_attente"].append({"id":nid("attente"),"id_patient":t["id_patient"],"id_service":sid,"numero_ordre":ordre,"date_arrivee":datetime.now().strftime("%Y-%m-%d %H:%M"),"statut":"En attente","priorite":"Urgent","motif":f"Transfert urgences vers {new_svc}"})
                add_hist(f"Transfert urgences vers {new_svc} — {pname(t['id_patient'])}","Transfert",session["user"],t["id_patient"])
                add_notif(None,"Transfert urgences",f"Patient transfere vers {new_svc}",f"{pname(t['id_patient'])} transfere depuis Urgences vers {new_svc}. Priorite Urgente.",dest_role="medecin",expediteur=session["user"])
                flash(f"{pname(t['id_patient'])} transfere vers {new_svc}.","success")
        return redirect(url_for("r_triage"))
    actifs=[t for t in DB["triage"] if t["statut"] in ["En attente","En cours"]]
    archives=[t for t in DB["triage"] if t["statut"] not in ["En attente","En cours"]]
    nc_map={"1 - Reanimation":"urg-1","2 - Urgent":"urg-2","3 - Semi-urgent":"urg-3","4 - Peu urgent":"urg-4","5 - Non urgent":"urg-5"}
    opts_transfer_svc="".join(f'<option value="{s["id"]}">{s["libelle"]}</option>' for s in DB["services"] if s["libelle"]!="Urgences")
    def row_t(t):
        nc=nc_map.get(t["niveau_urgence"],"att")
        transfer_btn=f'''<button class="btn btn-sm btn-outline-b ms-1" onclick="document.getElementById(\'tr_{t["id"]}\').style.display=\'block\'"><i class="fas fa-exchange-alt"></i></button>
        <div id="tr_{t["id"]}" style="display:none;margin-top:6px;padding:8px;background:#dbeafe;border-radius:6px;">
          <form method="POST"><input type="hidden" name="action" value="transferer"><input type="hidden" name="tid" value="{t["id"]}">
            <select name="service_dest" class="form-select form-select-sm mb-1">{opts_transfer_svc}</select>
            <button type="submit" class="btn btn-sm btn-b"><i class="fas fa-check"></i>Transferer</button>
          </form></div>''' if t["statut"] in ["En attente","En cours"] else ""
        return f'<tr><td><small>{t["date_arrivee"]}</small></td><td><strong>{pname(t["id_patient"])}</strong></td><td>{t["motif"]}</td><td><span class="bk {nc}">{t["niveau_urgence"]}</span></td><td style="font-size:.76rem;">{t["tension"]} | {t["temperature"]}C | SpO2:{t["saturation"]}% | FC:{t["frequence_cardiaque"]}</td><td><form method="POST" style="display:inline;"><input type="hidden" name="action" value="update"><input type="hidden" name="tid" value="{t["id"]}"><select name="statut" class="form-select form-select-sm" style="width:120px;display:inline;" onchange="this.form.submit()"><option>En attente</option><option>En cours</option><option>Termine</option><option>Transfere</option></select></form>{transfer_btn}</td></tr>'
    rows_a="".join(row_t(t) for t in sorted(actifs,key=lambda x:x["niveau_urgence"]))
    rows_arch="".join(row_t(t) for t in sorted(archives,key=lambda x:x["date_arrivee"],reverse=True)[:20])
    opts_p="".join(f'<option value="{p["id"]}">{p["prenom"]} {p["nom"]}</option>' for p in DB["patients"])
    opts_m="".join(f'<option value="{m["matricule"]}">Dr. {m["prenom"]} {m["nom"]}</option>' for m in DB["medecins"])
    body=f"""<div class="row g-3 mb-3">
  <div class="col-md-2"><div class="sc" style="background:#7f1d1d;"><div class="sv">{len([t for t in actifs if t["niveau_urgence"].startswith("1")])}</div><div class="sl">Reanimation</div></div></div>
  <div class="col-md-2"><div class="sc bg-r"><div class="sv">{len([t for t in actifs if t["niveau_urgence"].startswith("2")])}</div><div class="sl">Urgent</div></div></div>
  <div class="col-md-2"><div class="sc bg-o"><div class="sv">{len([t for t in actifs if t["niveau_urgence"].startswith("3")])}</div><div class="sl">Semi-urgent</div></div></div>
  <div class="col-md-2"><div class="sc bg-g"><div class="sv">{len([t for t in actifs if not any(t["niveau_urgence"].startswith(x) for x in ["1","2","3"])])}</div><div class="sl">Peu/Non urgent</div></div></div>
  <div class="col-md-4"><div class="sc bg-b"><div class="sv">{len(actifs)}</div><div class="sl">Total actifs</div></div></div>
</div>
<div class="row g-3">
  <div class="col-lg-8">
    <div class="nav-tabs"><button class="nav-tab active" onclick="showTab('tt1',this)">Actifs ({len(actifs)})</button><button class="nav-tab" onclick="showTab('tt2',this)">Archives</button></div>
    <div id="tt1" class="tab-pane"><div class="card"><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Arrivee</th><th>Patient</th><th>Motif</th><th>Niveau</th><th>Parametres</th><th>Statut</th></tr></thead><tbody>{rows_a if rows_a else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucun patient aux urgences</td></tr>"}</tbody></table></div></div></div>
    <div id="tt2" class="tab-pane" style="display:none;"><div class="card"><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Arrivee</th><th>Patient</th><th>Motif</th><th>Niveau</th><th>Parametres</th><th>Statut</th></tr></thead><tbody>{rows_arch if rows_arch else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucun archive</td></tr>"}</tbody></table></div></div></div>
  </div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-plus-circle" style="color:var(--err);"></i>Nouveau patient urgences</div></div><div class="card-body">
    <form method="POST"><input type="hidden" name="action" value="add"><div class="row g-2">
      <div class="col-12"><label class="form-label">Patient *</label><select name="patient" class="form-select" required><option value="">--</option>{opts_p}</select></div>
      <div class="col-12"><label class="form-label">Motif *</label><input type="text" name="motif" class="form-control" required placeholder="Ex: Douleur thoracique"></div>
      <div class="col-12"><label class="form-label">Niveau (Triage)</label><select name="niveau" class="form-select"><option value="1 - Reanimation">1 - Reanimation</option><option value="2 - Urgent">2 - Urgent</option><option value="3 - Semi-urgent" selected>3 - Semi-urgent</option><option value="4 - Peu urgent">4 - Peu urgent</option><option value="5 - Non urgent">5 - Non urgent</option></select></div>
      <div class="col-6"><label class="form-label">Tension</label><input type="text" name="tension" class="form-control" placeholder="120/80"></div>
      <div class="col-6"><label class="form-label">Temp (C)</label><input type="number" name="temperature" class="form-control" value="37.0" step="0.1"></div>
      <div class="col-6"><label class="form-label">SpO2 (%)</label><input type="number" name="saturation" class="form-control" value="98"></div>
      <div class="col-6"><label class="form-label">FC (bpm)</label><input type="number" name="fc" class="form-control" value="80"></div>
      <div class="col-12"><label class="form-label">Medecin</label><select name="medecin" class="form-select"><option value="">-- Assigner --</option>{opts_m}</select></div>
      <div class="col-12"><label class="form-label">Observations</label><textarea name="obs" class="form-control" rows="2"></textarea></div>
      <div class="col-12"><button type="submit" class="btn btn-r w-100" style="justify-content:center;"><i class="fas fa-ambulance"></i>Enregistrer</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Urgences / Triage","receptionniste",session["user"],body)

@app.route("/r-teleconsult")
@login_required
@role_required("receptionniste")
def r_teleconsult():
    rdvs_tc=[r for r in DB["rdvs"] if r["type"]=="Teleconsultation" and r["statut"]=="Confirme"]
    def statut_lien(r):
        t=next((t for t in DB["teleconsultations"] if t["id_rdv"]==r["id"]),None)
        if t and t.get("lien_envoye"):
            return '<span class="bk ok"><i class="fas fa-check"></i> Lien cree par le medecin</span>'
        return '<span class="bk att"><i class="fas fa-clock"></i> En attente du medecin</span>'
    rows="".join(f'<tr><td>{r["date"]} {r["heure"]}</td><td>{pname(r["id_patient"])}</td><td>{mname(r["matricule"])}</td><td>{statut_lien(r)}</td></tr>' for r in rdvs_tc)
    body=f"""<div class="row g-3">
  <div class="col-12"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-video"></i>Teleconsultations programmees</div></div>
  <div class="al al-i" style="margin:12px 18px 0;"><i class="fas fa-info-circle"></i>Le lien de la visioconference est genere par le medecin lors de l'activation de la teleconsultation. Le patient est notifie automatiquement.</div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Patient</th><th>Medecin</th><th>Statut du lien</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=4 class='text-center' style='color:var(--muted);padding:20px;'>Aucune teleconsultation programmee</td></tr>"}
  </tbody></table></div></div></div>
</div>"""
    return page("Teleconsultations","receptionniste",session["user"],body)

@app.route("/r-facturation")
@login_required
@role_required("receptionniste")
def r_facturation():
    def row_f(f):
        cls="ok" if f["statut"]=="Payee" else "att" if f["statut"]=="Partielle" else "err"
        col="var(--g1)" if f["reste_a_payer"]==0 else "var(--err)"
        btn=f'<a href="/r-paiements?fid={f["id"]}" class="btn btn-sm btn-g"><i class="fas fa-cash-register"></i>Regler</a>' if f["reste_a_payer"]>0 else "<span style=\'color:var(--g1);\'>✓ Solde</span>"
        view=f'<a href="/view-doc/facture/{f["id"]}" class="btn btn-sm btn-outline-b ms-1"><i class="fas fa-eye"></i></a>'
        return (f'<tr><td><strong>{f["num_facture"]}</strong></td><td>{pname(f["id_patient"])}</td>'
                f'<td>{f["date"]}</td><td><strong>{f["montant"]:,}</strong></td>'
                f'<td>{f["part_assurance"]:,}</td><td>{f["part_patient"]:,}</td>'
                f'<td style="color:var(--g1);font-weight:600;">{f["montant_paye"]:,}</td>'
                f'<td style="color:{col};font-weight:700;">{f["reste_a_payer"]:,}</td>'
                f'<td><span class="bk {cls}">{f["statut"]}</span></td>'
                f'<td>{f["mode_paiement"]}</td><td style="white-space:nowrap;">{btn}{view}</td></tr>')
    rows="".join(row_f(f) for f in DB["factures"])
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-file-invoice"></i>Facturation ({len(DB["factures"])})</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Facture</th><th>Patient</th><th>Date</th><th>Total F</th><th>Part assur.</th><th>Part pat.</th><th>Paye</th><th>Reste</th><th>Statut</th><th>Mode</th><th>Actions</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=11 class='text-center' style='color:var(--muted);padding:20px;'>Aucune facture</td></tr>"}
</tbody></table></div></div>"""
    return page("Facturation","receptionniste",session["user"],body)

@app.route("/r-paiements",methods=["GET","POST"])
@login_required
@role_required("receptionniste")
def r_paiements():
    if request.method=="POST":
        d=request.form; fid=int(d["facture"]); montant=int(d.get("montant",0))
        f=next((x for x in DB["factures"] if x["id"]==fid),None)
        if f and montant>0 and montant<=f["reste_a_payer"]:
            mode=d.get("mode","Especes")
            f["montant_paye"]+=montant; f["reste_a_payer"]-=montant
            if f["reste_a_payer"]==0: f["statut"]="Payee"; f["mode_paiement"]=mode
            else: f["statut"]="Partielle"; f["mode_paiement"]=mode
            DB["paiements"].append({"id":nid("paiements"),"id_facture":fid,"id_patient":f["id_patient"],"montant":montant,"date":date.today().strftime("%Y-%m-%d"),"mode":mode,"statut":"Valide"})
            add_hist(f"Paiement {montant:,} FCFA ({mode}) — {f['num_facture']}","Paiement",session["user"],f["id_patient"])
            add_notif(f["id_patient"],"Paiement confirme",f"Paiement {f['num_facture']} enregistre",f"Paiement de {montant:,} FCFA recu. Reste : {f['reste_a_payer']:,} FCFA.",expediteur=session["user"])
            flash(f"Paiement {montant:,} FCFA enregistre. Reste : {f['reste_a_payer']:,} FCFA.","success")
        else:
            flash("Montant invalide ou superieur au reste.","danger")
        return redirect(url_for("r_paiements"))
    fid_pre=request.args.get("fid","")
    imp=[f for f in DB["factures"] if f["reste_a_payer"]>0]
    opts_f="".join(f'<option value="{f["id"]}" {"selected" if str(f["id"])==fid_pre else ""}>{f["num_facture"]} — {pname(f["id_patient"])} — Reste:{f["reste_a_payer"]:,} FCFA</option>' for f in imp)
    rows="".join(f'<tr><td>{p["date"]}</td><td>{next((f["num_facture"] for f in DB["factures"] if f["id"]==p["id_facture"]),"?")}</td><td>{pname(p["id_patient"])}</td><td><strong>{p["montant"]:,} FCFA</strong></td><td><span class="bk inf">{p["mode"]}</span></td><td><span class="bk ok">{p["statut"]}</span></td></tr>' for p in sorted(DB["paiements"],key=lambda x:x["date"],reverse=True))
    body=f"""<div class="row g-3">
  <div class="col-lg-7"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-cash-register"></i>Historique paiements</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Facture</th><th>Patient</th><th>Montant</th><th>Mode</th><th>Statut</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucun paiement</td></tr>"}
  </tbody></table></div></div></div>
  <div class="col-lg-5"><div class="card"><div class="card-hdr"><div class="title">Enregistrer un paiement</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Facture *</label><select name="facture" class="form-select" required><option value="">-- Choisir --</option>{opts_f}</select></div>
      <div class="col-12"><label class="form-label">Montant (FCFA) *</label><input type="number" name="montant" class="form-control" min="1" required placeholder="Montant partiel ou total"></div>
      <div class="col-12"><label class="form-label">Mode *</label><select name="mode" class="form-select" required><option>Especes</option><option>Wave</option><option>Orange Money</option><option>Free Money</option><option>Carte bancaire</option><option>Virement</option></select></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-check"></i>Valider le paiement</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Paiements","receptionniste",session["user"],body)

@app.route("/r-facture-pdf/<int:fid>")
@login_required
@role_required("receptionniste")
def r_facture_pdf(fid):
    f=next((x for x in DB["factures"] if x["id"]==fid),None)
    if not f: flash("Facture introuvable","danger"); return redirect(url_for("r_factures"))
    pat=next((p for p in DB["patients"] if p["id"]==f["id_patient"]),None)
    lignes=[
        "CENTRE DE SANTE LE TROPICAL","="*55,
        f"Patient      : {pat['prenom']} {pat['nom']}" if pat else "Patient : -",
        f"Date naiss.  : {pat['date_naissance']}  |  Sexe : {pat['sexe']}" if pat else "",
        f"Groupe sg.   : {pat.get('groupe_sanguin','-')}" if pat else "",
        f"Assurance    : {pat['assurance']}" if pat else "",
        f"Telephone    : {pat['telephone']}" if pat else "",
        f"Email        : {pat.get('email','-')}" if pat else "",
        "",
        f"FACTURE {f['num_facture']}","="*55,
        f"Date            : {f['date']}",
        f"Montant total   : {f['montant']:,} FCFA",
        f"Part assurance  : {f['part_assurance']:,} FCFA",
        f"Part patient    : {f['part_patient']:,} FCFA",
        f"Montant paye    : {f['montant_paye']:,} FCFA",
        f"Reste a payer   : {f['reste_a_payer']:,} FCFA",
        f"Mode paiement   : {f['mode_paiement']}",
        f"Statut          : {f['statut']}",
        "",
        "LE TROPICAL — Merci de votre confiance.",
    ]
    pdf=gen_pdf(f"FACTURE {f['num_facture']}",lignes)
    return Response(pdf,mimetype="application/pdf",headers={"Content-Disposition":f"attachment; filename=facture_{f['num_facture']}.pdf"})

@app.route("/r-notifs",methods=["GET","POST"])
@login_required
@role_required("receptionniste")
def r_notifs():
    if request.method=="POST":
        d=request.form; dest=d.get("dest","")
        envoyer_sms=d.get("envoyer_sms")=="on"
        if dest.startswith("dr.") or dest in DB["users"]:
            add_notif(None,d["type"],d["objet"],d["contenu"],dest_user=dest,expediteur=session["user"])
            flash(f"Message envoye a {DB['users'].get(dest,{}).get('prenom',dest)}.","success")
        elif d.get("id_patient"):
            pid=int(d["id_patient"])
            add_notif(pid,d["type"],d["objet"],d["contenu"],expediteur=session["user"])
            flash("Message envoye au patient.","success")
            if envoyer_sms:
                pat=next((p for p in DB["patients"] if p["id"]==pid),None)
                if pat and pat.get("telephone"):
                    res=send_sms(pat["telephone"],d["contenu"])
                    DB["sms_envoyes"].append({"id":nid("sms"),"id_patient":pid,"numero":pat["telephone"],"message":d["contenu"],"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"statut":res["status"],"detail":res["detail"],"par":session["user"]})
                    if res["success"]:
                        flash("SMS envoye.","success")
                    else:
                        flash(f"SMS non envoye ({res['detail']}).","warning")
        return redirect(url_for("r_notifs"))
    notifs=get_notifs_user(session["user"],"receptionniste")
    for n in notifs: n["lu"]=True
    opts_med="".join(f'<option value="{m["username"]}">Dr. {m["prenom"]} {m["nom"]} ({m["specialite"]})</option>' for m in DB["medecins"])
    opts_p="".join(f'<option value="{p["id"]}">{p["prenom"]} {p["nom"]}</option>' for p in DB["patients"])
    rows="".join(f'<tr><td><small>{n["date"]}</small></td><td>{n.get("expediteur","-") or "systeme"}</td><td><strong>{n["type"]}</strong></td><td>{n["objet"]}</td><td>{n["contenu"][:60]}</td></tr>' for n in notifs)
    body=f"""<div class="row g-3">
  <div class="col-lg-8">
  <div class="card mb-3"><div class="card-hdr"><div class="title"><i class="fas fa-inbox"></i>Messages recus ({len(notifs)})</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Expediteur</th><th>Type</th><th>Objet</th><th>Message</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucun message</td></tr>"}
  </tbody></table></div></div>
  <div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-sms"></i>Historique SMS envoyes</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Patient</th><th>Numero</th><th>Message</th><th>Statut</th></tr></thead><tbody>
  {"".join(f'<tr><td><small>{s["date"]}</small></td><td>{pname(s["id_patient"])}</td><td>{s["numero"]}</td><td>{s["message"][:50]}</td><td><span class="bk {"ok" if s["statut"]=="success" else "att"}">{s["statut"]}</span></td></tr>' for s in reversed(DB.get("sms_envoyes",[]))) or "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucun SMS envoye</td></tr>"}
  </tbody></table></div></div>
  </div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-paper-plane"></i>Envoyer un message</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Envoyer a un medecin</label><select name="dest" class="form-select"><option value="">-- Choisir medecin --</option>{opts_med}</select></div>
      <div class="col-12" style="text-align:center;color:var(--muted);font-size:.8rem;">— ou a un patient —</div>
      <div class="col-12"><select name="id_patient" class="form-select"><option value="">-- Choisir patient --</option>{opts_p}</select></div>
      <div class="col-12"><label class="form-label">Type</label><select name="type" class="form-select"><option>Rappel RDV</option><option>Information</option><option>Urgence</option><option>Demande</option></select></div>
      <div class="col-12"><label class="form-label">Objet *</label><input type="text" name="objet" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Message *</label><textarea name="contenu" class="form-control" rows="3" required></textarea></div>
      <div class="col-12"><label style="display:flex;align-items:center;gap:8px;font-size:.82rem;cursor:pointer;"><input type="checkbox" name="envoyer_sms"> Envoyer aussi par SMS (si destinataire = patient)</label></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-paper-plane"></i>Envoyer</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Messagerie","receptionniste",session["user"],body)

@app.route("/r-historique")
@login_required
@role_required("receptionniste","admin")
def r_historique():
    hists=sorted(DB["historiques"],key=lambda x:x["date_action"],reverse=True)
    rows="".join(f'<tr><td><small>{h["date_action"]}</small></td><td><span class="bk inf">{h["type"]}</span></td><td>{h["description"]}</td><td>{pname(h["id_patient"]) if h.get("id_patient") else "-"}</td></tr>' for h in hists)
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-history"></i>Historique</div></div>
<div style="padding:10px 18px;"><input type="text" id="sh" class="form-control" placeholder="Rechercher..." oninput="srch('th','sh')" style="max-width:300px;"></div>
<div style="overflow-x:auto;"><table class="table" id="th"><thead><tr><th>Date/Heure</th><th>Type</th><th>Description</th><th>Patient</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=4 class='text-center' style='color:var(--muted);padding:20px;'>Aucun</td></tr>"}
</tbody></table></div></div>"""
    return page("Historique",session["role"],session["user"],body)
# SGRDMS v5 — Part 7: Pharmacien complet + Profil + Launch

# =======================================================
# Routes Pharmacien : médicaments, ventes, historique, alertes | Profil | Lancement
# =======================================================

@app.route("/ph-medicaments",methods=["GET","POST"])
@login_required
@role_required("pharmacien")
def ph_medicaments():
    if request.method=="POST":
        d=request.form; qte=int(d.get("qte",0)); seuil=int(d.get("seuil",20))
        ns={"id":nid("stocks"),"id_medicament":0,"quantite":qte,"date_stock":date.today().strftime("%Y-%m-%d"),"statut":"Normal" if qte>seuil else ("Faible" if qte>0 else "Epuise"),"seuil_alerte":seuil}
        DB["stocks"].append(ns)
        nm={"id":nid("meds"),"libelle":d["libelle"],"type":d.get("type","Autre"),"dosage":d.get("dosage",""),"prix":int(d.get("prix",0)),"id_stock":ns["id"],"contre_indication":d.get("ci",""),"notice":d.get("notice","")}
        DB["medicaments"].append(nm); ns["id_medicament"]=nm["id"]
        add_hist(f"Medicament ajoute : {nm['libelle']}","Pharmacie",session["user"])
        flash(f"'{nm['libelle']}' ajoute.","success"); return redirect(url_for("ph_medicaments"))
    rows=""
    for m in DB["medicaments"]:
        s=next((x for x in DB["stocks"] if x["id"]==m["id_stock"]),None)
        qte=s["quantite"] if s else 0; stat=s["statut"] if s else "?"
        sc="ok" if stat=="Normal" else "err" if "pui" in stat.lower() else "att"
        rows+=f'<tr><td><strong>{m["libelle"]}</strong></td><td>{m["type"]}</td><td>{m["dosage"]}</td><td>{m["prix"]:,}</td><td><strong>{qte}</strong></td><td><span class="bk {sc}">{stat}</span></td><td>{m.get("notice","-")}</td><td><button class="btn btn-sm btn-outline-g" onclick="openRestock({m["id"]},\'{m["libelle"]}\',{qte})"><i class="fas fa-plus"></i>Stock</button></td></tr>'
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-pills"></i>Medicaments & Stock ({len(DB["medicaments"])})</div>
    <button class="btn btn-sm btn-g" onclick="document.getElementById('fm').classList.toggle('d-none')"><i class="fas fa-plus"></i>Ajouter</button>
  </div><div style="overflow-x:auto;"><table class="table"><thead><tr><th>Medicament</th><th>Type</th><th>Dosage</th><th>Prix FCFA</th><th>Stock</th><th>Statut</th><th>Notice</th><th>Action</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>
  <div class="col-lg-4"><div id="fm" class="card d-none"><div class="card-hdr"><div class="title">Nouveau medicament</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Libelle *</label><input type="text" name="libelle" class="form-control" required></div>
      <div class="col-6"><label class="form-label">Type</label><select name="type" class="form-select"><option>Antalgique</option><option>Antibiotique</option><option>Anti-inflammatoire</option><option>Antidiabetique</option><option>Antihypertenseur</option><option>Antipaludeen</option><option>Autre</option></select></div>
      <div class="col-6"><label class="form-label">Dosage</label><input type="text" name="dosage" class="form-control" placeholder="500mg"></div>
      <div class="col-6"><label class="form-label">Prix (FCFA)</label><input type="number" name="prix" class="form-control" value="0"></div>
      <div class="col-6"><label class="form-label">Quantite initiale</label><input type="number" name="qte" class="form-control" value="0" min="0"></div>
      <div class="col-12"><label class="form-label">Seuil alerte</label><input type="number" name="seuil" class="form-control" value="20"></div>
      <div class="col-12"><label class="form-label">Notice</label><input type="text" name="notice" class="form-control" placeholder="Instructions..."></div>
      <div class="col-12"><label class="form-label">Contre-indications</label><textarea name="ci" class="form-control" rows="2"></textarea></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-save"></i>Ajouter</button></div>
    </div></form>
  </div></div></div>
</div>
<div id="restockModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:2000;align-items:center;justify-content:center;">
  <div style="background:#fff;border-radius:14px;width:100%;max-width:380px;padding:24px;">
    <h6 style="color:var(--g3);margin-bottom:12px;"><i class="fas fa-plus-circle me-2"></i>Mettre a jour le stock</h6>
    <p id="rm_lbl" style="font-size:.85rem;color:var(--muted);margin-bottom:16px;"></p>
    <p id="rm_qte" style="font-size:.85rem;color:var(--g3);margin-bottom:16px;font-weight:600;"></p>
    <form action="/ph-restock" method="POST">
      <input type="hidden" name="mid" id="rm_mid">
      <div class="mb-3"><label class="form-label">Quantite a ajouter</label><input type="number" name="qte" class="form-control" min="1" value="50" required></div>
      <div style="display:flex;gap:8px;">
        <button type="submit" class="btn btn-g"><i class="fas fa-plus"></i>Ajouter</button>
        <button type="button" onclick="document.getElementById('restockModal').style.display='none'" class="btn btn-outline-g">Annuler</button>
      </div>
    </form>
  </div>
</div>
<script>function openRestock(id,lbl,qte){{document.getElementById('rm_mid').value=id;document.getElementById('rm_lbl').textContent=lbl;document.getElementById('rm_qte').textContent='Stock actuel : '+qte+' unites';document.getElementById('restockModal').style.display='flex';}}</script>"""
    return page("Medicaments & Stock","pharmacien",session["user"],body)

@app.route("/ph-restock",methods=["POST"])
@login_required
@role_required("pharmacien")
def ph_restock():
    mid=int(request.form["mid"]); qte=int(request.form["qte"])
    m=next((x for x in DB["medicaments"] if x["id"]==mid),None)
    if m:
        s=next((x for x in DB["stocks"] if x["id"]==m["id_stock"]),None)
        if s:
            s["quantite"]+=qte
            s["statut"]="Normal" if s["quantite"]>=s["seuil_alerte"] else ("Faible" if s["quantite"]>0 else "Epuise")
            for a in DB["alertes_stock"]:
                if a["id_medicament"]==mid: a["statut"]="Traite"; a["quantite_actuel"]=s["quantite"]
            add_hist(f"+{qte} unites — {m['libelle']} (stock:{s['quantite']})","Stock",session["user"])
            flash(f"{qte} unites ajoutees. Stock: {s['quantite']}.","success")
    return redirect(url_for("ph_medicaments"))

# ✅ v5: Vente de médicaments
@app.route("/ph-ventes",methods=["GET","POST"])
@login_required
@role_required("pharmacien")
def ph_ventes():
    if request.method=="POST":
        d=request.form; mid=int(d["medicament"]); qte=int(d.get("quantite",1))
        m=next((x for x in DB["medicaments"] if x["id"]==mid),None)
        if not m: flash("Medicament introuvable.","danger"); return redirect(url_for("ph_ventes"))
        s=next((x for x in DB["stocks"] if x["id"]==m["id_stock"]),None)
        if not s or s["quantite"]<qte:
            flash(f"Stock insuffisant. Disponible : {s['quantite'] if s else 0} unites.","danger")
            return redirect(url_for("ph_ventes"))
        # Déduire du stock
        s["quantite"]-=qte
        s["statut"]="Normal" if s["quantite"]>=s["seuil_alerte"] else ("Faible" if s["quantite"]>0 else "Epuise")
        if s["quantite"]<=s["seuil_alerte"]:
            DB["alertes_stock"].append({"id":nid("stocks"),"id_medicament":mid,"type_alerte":"Stock faible" if s["quantite"]>0 else "Rupture de stock","date":date.today().strftime("%Y-%m-%d"),"message":f"{m['libelle']} : {s['quantite']} unites restantes","quantite_actuel":s["quantite"],"statut":"Non traite"})
        montant=qte*m["prix"]
        nv={"id":nid("ventes"),"id_medicament":mid,"libelle":m["libelle"],"quantite":qte,"prix_unitaire":m["prix"],"montant_total":montant,"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"vendeur":session["user"],"id_patient":int(d["id_patient"]) if d.get("id_patient") else None,"nom_acheteur":d.get("nom_acheteur","Vente libre")}
        DB["ventes_pharmacie"].append(nv)
        add_hist(f"Vente : {qte}x {m['libelle']} = {montant:,} FCFA","Pharmacie",session["user"])
        flash(f"Vente enregistree : {qte}x {m['libelle']} = {montant:,} FCFA. Stock restant : {s['quantite']}.","success")
        return redirect(url_for("ph_ventes"))
    opts_m="".join(f'<option value="{m["id"]}">{m["libelle"]} — {m["dosage"]} — {m["prix"]:,} FCFA — Stock:{next((s["quantite"] for s in DB["stocks"] if s["id"]==m["id_stock"]),0)}</option>' for m in DB["medicaments"])
    opts_p="".join(f'<option value="{p["id"]}">{p["prenom"]} {p["nom"]}</option>' for p in DB["patients"])
    # Dernières ventes du jour
    today=date.today().strftime("%Y-%m-%d")
    ventes_today=[v for v in DB.get("ventes_pharmacie",[]) if v["date"].startswith(today)]
    rows="".join(f'<tr><td><strong>{v["libelle"]}</strong></td><td>{v["quantite"]}</td><td>{v["prix_unitaire"]:,}</td><td><strong>{v["montant_total"]:,}</strong></td><td>{v.get("nom_acheteur","Vente libre") or pname(v["id_patient"]) if v.get("id_patient") else v.get("nom_acheteur","Vente libre")}</td><td><small>{v["date"]}</small></td></tr>' for v in sorted(ventes_today,key=lambda x:x["date"],reverse=True))
    total_j=sum(v["montant_total"] for v in ventes_today)
    body=f"""<div class="row g-3">
  <div class="col-md-3 mb-3"><div class="sc bg-g"><div class="sv">{len(ventes_today)}</div><div class="sl">Ventes aujourd'hui</div></div></div>
  <div class="col-md-3 mb-3"><div class="sc bg-b"><div class="sv">{total_j:,} F</div><div class="sl">CA aujourd'hui</div></div></div>
</div>
<div class="row g-3">
  <div class="col-lg-5"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-shopping-cart"></i>Nouvelle vente</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Medicament *</label><select name="medicament" class="form-select" required><option value="">-- Choisir --</option>{opts_m}</select></div>
      <div class="col-12"><label class="form-label">Quantite *</label><input type="number" name="quantite" class="form-control" value="1" min="1" required></div>
      <div class="col-12" style="border-top:1px solid var(--gl);padding-top:10px;"><p style="font-size:.82rem;color:var(--muted);">Acheteur (optionnel)</p></div>
      <div class="col-12"><label class="form-label">Patient enregistre</label><select name="id_patient" class="form-select"><option value="">-- Vente libre --</option>{opts_p}</select></div>
      <div class="col-12"><label class="form-label">Ou nom acheteur</label><input type="text" name="nom_acheteur" class="form-control" placeholder="Nom de l'acheteur"></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-check"></i>Enregistrer la vente</button></div>
    </div></form>
  </div></div></div>
  <div class="col-lg-7"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-receipt"></i>Ventes d'aujourd'hui ({len(ventes_today)})</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Medicament</th><th>Qte</th><th>Prix unit.</th><th>Total FCFA</th><th>Acheteur</th><th>Heure</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucune vente aujourd'hui</td></tr>"}
  </tbody></table></div></div></div>
</div>"""
    return page("Vente de medicaments","pharmacien",session["user"],body)

# ✅ v5: Historique des ventes
@app.route("/ph-historique-ventes")
@login_required
@role_required("pharmacien")
def ph_historique_ventes():
    ventes=sorted(DB.get("ventes_pharmacie",[]),key=lambda x:x["date"],reverse=True)
    total=sum(v["montant_total"] for v in ventes)
    rows="".join(f'<tr><td><small>{v["date"]}</small></td><td><strong>{v["libelle"]}</strong></td><td>{v["quantite"]}</td><td>{v["prix_unitaire"]:,}</td><td><strong>{v["montant_total"]:,}</strong></td><td>{pname(v["id_patient"]) if v.get("id_patient") else v.get("nom_acheteur","Vente libre")}</td></tr>' for v in ventes)
    body=f"""<div class="row g-3 mb-3">
  <div class="col-md-3"><div class="sc bg-g"><div class="sv">{len(ventes)}</div><div class="sl">Total ventes</div></div></div>
  <div class="col-md-3"><div class="sc bg-b"><div class="sv">{total:,} F</div><div class="sl">CA total</div></div></div>
</div>
<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-receipt"></i>Historique des ventes ({len(ventes)})</div>
</div>
<div style="padding:10px 18px;"><input type="text" id="sv" class="form-control" placeholder="Rechercher..." oninput="srch('tv','sv')" style="max-width:300px;"></div>
<div style="overflow-x:auto;"><table class="table" id="tv"><thead><tr><th>Date/Heure</th><th>Medicament</th><th>Qte</th><th>Prix unit. FCFA</th><th>Total FCFA</th><th>Acheteur</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucune vente</td></tr>"}
</tbody></table></div></div>"""
    return page("Historique des ventes","pharmacien",session["user"],body)

@app.route("/ph-alertes")
@login_required
@role_required("pharmacien")
def ph_alertes():
    rows="".join(f'<tr><td>{a["date"]}</td><td>{next((m["libelle"] for m in DB["medicaments"] if m["id"]==a["id_medicament"]),"?")}</td><td><span class="bk {"err" if "Rupture" in a["type_alerte"] else "att"}">{a["type_alerte"]}</span></td><td>{a["quantite_actuel"]}</td><td>{a["message"]}</td><td><span class="bk {"ok" if a["statut"]=="Traite" else "att"}">{a["statut"]}</span></td></tr>' for a in DB["alertes_stock"])
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-exclamation-triangle" style="color:var(--warn);"></i>Alertes de stock</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Medicament</th><th>Type</th><th>Qte</th><th>Message</th><th>Statut</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=6 class='text-center' style='color:var(--muted);padding:20px;'>Aucune alerte</td></tr>"}
</tbody></table></div></div>"""
    return page("Alertes Stock","pharmacien",session["user"],body)

@app.route("/ph-ordonnances",methods=["GET","POST"])
@login_required
@role_required("pharmacien")
def ph_ordonnances():
    if request.method=="POST":
        oid=int(request.form.get("oid",0))
        ordo=next((o for o in DB["ordonnances"] if o["id"]==oid),None)
        if ordo:
            ids_sel=request.form.getlist("med_sel[]")
            qtes=request.form.getlist("qte[]")
            vendus=[]
            for mid_str,qte_str in zip(ids_sel,qtes):
                try: mid=int(mid_str); qte=int(qte_str)
                except: continue
                if qte<=0: continue
                stock=next((s for s in DB["stocks"] if s["id_medicament"]==mid),None)
                med_obj=next((m for m in DB["medicaments"] if m["id"]==mid),None)
                if stock and med_obj and stock["quantite"]>=qte:
                    stock["quantite"]-=qte
                    prix_total=med_obj["prix"]*qte
                    DB["ventes_pharmacie"].append({"id":nid("ventes"),"id_medicament":mid,"libelle":med_obj["libelle"],"quantite":qte,"prix_unitaire":med_obj["prix"],"montant_total":prix_total,"date":date.today().strftime("%Y-%m-%d"),"id_patient":ordo["id_patient"],"source":"ordonnance","id_ordonnance":oid})
                    vendus.append(f"{med_obj['libelle']} x{qte}")
                else:
                    nm=med_obj["libelle"] if med_obj else "?"
                    flash(f"Stock insuffisant pour {nm}","warning")
            if vendus:
                ordo["statut_delivrance"]="Delivree"
                add_hist(f"Delivrance ORD-{oid:04d} : {', '.join(vendus)}","Pharmacie",session["user"],ordo["id_patient"])
                flash(f"Delivre : {', '.join(vendus)}.","success")
        return redirect(url_for("ph_ordonnances"))
    # ── GET ──
    def row_o(o):
        meds=", ".join(l["libelle"] for l in o["lignes"])
        statut=o.get("statut_delivrance","En attente")
        s_cls="ok" if statut=="Delivree" else "att"
        btn_deliv="" if statut=="Delivree" else f'<button class="btn btn-sm btn-g ms-1" onclick="openDeliv({o["id"]})"><i class="fas fa-pills"></i>Delivrer</button>'
        return (f'<tr><td><strong>ORD-{o["id"]:04d}</strong></td><td>{pname(o["id_patient"])}</td>'
                f'<td>{o["date"]}</td><td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{meds}</td>'
                f'<td>{o["duree"]} j</td><td><span class="bk {s_cls}">{statut}</span></td>'
                f'<td style="white-space:nowrap;"><button class="btn btn-sm btn-outline-g" onclick="showOrdo({o["id"]})"><i class="fas fa-eye"></i>Voir</button>{btn_deliv}</td></tr>')
    rows="".join(row_o(o) for o in DB["ordonnances"])
    import json as _json
    ordo_data={}
    for o in DB["ordonnances"]:
        lignes_enrichies=[]
        for l in o["lignes"]:
            mid=l.get("id_medicament")
            med_obj=next((m for m in DB["medicaments"] if m["id"]==mid),None)
            stock=next((s for s in DB["stocks"] if s["id_medicament"]==mid),None)
            lignes_enrichies.append({"id":mid,"libelle":l["libelle"],"posologie":l["posologie"],"duree":l["duree"],"prix":med_obj["prix"] if med_obj else 0,"stock":stock["quantite"] if stock else 0})
        ordo_data[o["id"]]={"patient":pname(o["id_patient"]),"medecin":mname(o["matricule"]),"date":o["date"],"duree":o["duree"],"lignes":lignes_enrichies}
    ordo_json=_json.dumps(ordo_data)
    body=f"""<div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-prescription"></i>Ordonnances ({len(DB["ordonnances"])})</div></div>
<div style="overflow-x:auto;"><table class="table"><thead><tr><th>Ref</th><th>Patient</th><th>Date</th><th>Medicaments</th><th>Duree</th><th>Statut</th><th>Actions</th></tr></thead><tbody>
{rows if rows else "<tr><td colspan=7 class='text-center' style='color:var(--muted);padding:20px;'>Aucune ordonnance</td></tr>"}
</tbody></table></div></div>
<div id="ordoModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:2000;align-items:center;justify-content:center;">
  <div style="background:#fff;border-radius:14px;width:100%;max-width:520px;padding:24px;max-height:90vh;overflow-y:auto;">
    <div style="display:flex;justify-content:space-between;margin-bottom:16px;"><h6 style="color:var(--g3);margin:0;"><i class="fas fa-prescription me-2"></i>Detail ordonnance</h6>
    <button onclick="document.getElementById('ordoModal').style.display='none'" class="btn btn-sm btn-outline-r"><i class="fas fa-times"></i></button></div>
    <div id="ordo_content"></div>
  </div>
</div>
<div id="delivModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:2000;align-items:center;justify-content:center;">
  <div style="background:#fff;border-radius:14px;width:100%;max-width:580px;padding:24px;max-height:90vh;overflow-y:auto;">
    <div style="display:flex;justify-content:space-between;margin-bottom:16px;"><h6 style="color:var(--g3);margin:0;"><i class="fas fa-pills me-2"></i>Delivrer l ordonnance</h6>
    <button onclick="document.getElementById('delivModal').style.display='none'" class="btn btn-sm btn-outline-r"><i class="fas fa-times"></i></button></div>
    <div id="deliv_content"></div>
  </div>
</div>
<script>
const ORDOS={ordo_json};
function showOrdo(id){{
  const o=ORDOS[id]; if(!o)return;
  let h=`<div class="al al-i mb-2"><strong>Patient :</strong> ${{o.patient}} | <strong>Medecin :</strong> ${{o.medecin}}</div>`;
  h+=`<p style="font-size:.85rem;color:var(--muted);"><strong>Date :</strong> ${{o.date}} &nbsp;|&nbsp; <strong>Duree :</strong> ${{o.duree}} jours</p><hr>`;
  h+='<table class="table table-sm"><thead><tr><th>Medicament</th><th>Posologie</th><th>Duree</th></tr></thead><tbody>';
  o.lignes.forEach(l=>{{h+=`<tr><td>${{l.libelle}}</td><td>${{l.posologie}}</td><td>${{l.duree}}</td></tr>`;}});
  h+='</tbody></table>';
  document.getElementById('ordo_content').innerHTML=h;
  document.getElementById('ordoModal').style.display='flex';
}}
function openDeliv(id){{
  const o=ORDOS[id]; if(!o)return;
  let h=`<div class="al al-i mb-3"><strong>Patient :</strong> ${{o.patient}} | <strong>Date :</strong> ${{o.date}}</div>`;
  h+=`<form method="POST"><input type="hidden" name="oid" value="${{id}}">`;
  h+='<table class="table table-sm"><thead><tr><th><input type="checkbox" id="selAll" onchange="this.closest(&apos;table&apos;).querySelectorAll(&apos;.chk&apos;).forEach(c=>c.checked=this.checked)"> Tout</th><th>Medicament</th><th>Posologie</th><th>Stock</th><th>Prix unit.</th><th>Qte</th></tr></thead><tbody>';
  o.lignes.forEach(l=>{{
    const ok=l.stock>0;
    const sc=l.stock>5?'ok':l.stock>0?'att':'err';
    h+=`<tr style="${{!ok?'opacity:.4;':''}}"><td><input type="checkbox" class="chk" name="med_sel[]" value="${{l.id}}" ${{ok?'checked':''}} ${{!ok?'disabled':''}}></td>`;
    h+=`<td>${{l.libelle}}</td><td style="font-size:.8rem;">${{l.posologie}}</td>`;
    h+=`<td><span class="bk ${{sc}}">${{l.stock}}</span></td>`;
    h+=`<td>${{l.prix.toLocaleString()}} F</td>`;
    h+=`<td><input type="number" name="qte[]" value="1" min="1" max="${{l.stock}}" class="form-control form-control-sm" style="width:70px;" ${{!ok?'disabled':''}}></td></tr>`;
  }});
  h+='</tbody></table><button type="submit" class="btn btn-g w-100"><i class="fas fa-check-circle"></i>Confirmer la delivrance</button></form>';
  document.getElementById('deliv_content').innerHTML=h;
  document.getElementById('delivModal').style.display='flex';
}}
</script>"""
    return page("Ordonnances","pharmacien",session["user"],body)

@app.route("/ph-notifs",methods=["GET","POST"])
@login_required
@role_required("pharmacien")
def ph_notifs():
    if request.method=="POST":
        d=request.form
        add_notif(None,d["type"],d["objet"],d["contenu"],dest_role="receptionniste",expediteur=session["user"])
        flash("Message envoye a la receptionniste.","success")
        return redirect(url_for("ph_notifs"))
    notifs=get_notifs_user(session["user"],"pharmacien")
    for n in notifs: n["lu"]=True
    rows="".join(f'<tr><td><small>{n["date"]}</small></td><td>{n.get("expediteur","-") or "systeme"}</td><td><strong>{n["type"]}</strong></td><td>{n["objet"]}</td><td>{n["contenu"][:60]}</td></tr>' for n in notifs)
    body=f"""<div class="row g-3">
  <div class="col-lg-8"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-bell"></i>Notifications ({len(notifs)})</div></div>
  <div style="overflow-x:auto;"><table class="table"><thead><tr><th>Date</th><th>Expediteur</th><th>Type</th><th>Objet</th><th>Message</th></tr></thead><tbody>
  {rows if rows else "<tr><td colspan=5 class='text-center' style='color:var(--muted);padding:20px;'>Aucune notification</td></tr>"}
  </tbody></table></div></div></div>
  <div class="col-lg-4"><div class="card"><div class="card-hdr"><div class="title"><i class="fas fa-paper-plane"></i>Contacter la reception</div></div><div class="card-body">
    <form method="POST"><div class="row g-2">
      <div class="col-12"><label class="form-label">Type</label><select name="type" class="form-select"><option>Information</option><option>Alerte stock</option><option>Demande</option><option>Urgence</option></select></div>
      <div class="col-12"><label class="form-label">Objet *</label><input type="text" name="objet" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Message *</label><textarea name="contenu" class="form-control" rows="3" required></textarea></div>
      <div class="col-12"><button type="submit" class="btn btn-g w-100" style="justify-content:center;"><i class="fas fa-paper-plane"></i>Envoyer</button></div>
    </div></form>
  </div></div></div>
</div>"""
    return page("Notifications","pharmacien",session["user"],body)

# ── PROFIL (commun tous rôles) ───────────────────────────────
@app.route("/profil",methods=["GET","POST"])
@login_required
def profil():
    u=session["user"]; role=session["role"]; ud=DB["users"][u]
    if request.method=="POST":
        d=request.form; action=d.get("action")
        if action=="pwd":
            if d.get("old")!=ud["password"]: flash("Ancien mot de passe incorrect.","danger"); return redirect(url_for("profil"))
            if d.get("new1")!=d.get("new2"): flash("Mots de passe differents.","danger"); return redirect(url_for("profil"))
            if len(d.get("new1",""))<4: flash("Minimum 4 caracteres.","danger"); return redirect(url_for("profil"))
            ud["password"]=d["new1"]; flash("Mot de passe modifie.","success")
        elif action=="info":
            ud["email"]=d.get("email",ud.get("email",""))
            ud["telephone"]=d.get("tel",ud.get("telephone",""))
            if role!="patient":
                ud["nom"]=d.get("nom",ud.get("nom","")); ud["prenom"]=d.get("prenom",ud.get("prenom",""))
            flash("Informations mises a jour.","success")
        elif action=="photo":
            photo_data=d.get("photo_b64","")
            if photo_data:
                ud["photo"]=photo_data
                if role=="patient":
                    pat=get_pat(u)
                    if pat: pat["photo"]=photo_data
                flash("Photo mise a jour.","success")
            else: flash("Aucune photo selectionnee.","warning")
        return redirect(url_for("profil"))
    nom=f"{ud.get('prenom','')} {ud.get('nom','')}".strip()
    rl={"patient":"Patient","medecin":"Medecin","receptionniste":"Receptionniste","pharmacien":"Pharmacien","admin":"Administrateur"}.get(role,role)
    ph=f'<img src="{ud["photo"]}" style="width:90px;height:90px;border-radius:50%;object-fit:cover;border:3px solid var(--gd);" alt="">' if ud.get("photo") else f'<div style="width:90px;height:90px;background:linear-gradient(135deg,var(--g1),var(--g2));border-radius:50%;display:inline-flex;align-items:center;justify-content:center;"><i class="fas fa-user" style="color:#fff;font-size:2.2rem;"></i></div>'
    body=f"""<div class="row g-3">
  <div class="col-md-3"><div class="card"><div class="card-body text-center p-4">
    {ph}<h5 style="color:var(--g3);margin-top:12px;">{nom}</h5><span class="bk inf">{rl}</span>
    <div style="margin-top:14px;text-align:left;font-size:.8rem;">
      <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--gl);"><span style="color:var(--muted);">Email</span><span>{ud.get("email","-")}</span></div>
      <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--gl);"><span style="color:var(--muted);">Telephone</span><span>{ud.get("telephone","-")}</span></div>
      <div style="display:flex;justify-content:space-between;padding:4px 0;{"border-bottom:1px solid var(--gl);" if role=="medecin" else ""}"><span style="color:var(--muted);">Role</span><span>{rl}</span></div>
      {f'<div style="display:flex;justify-content:space-between;padding:4px 0;"><span style="color:var(--muted);">Centre</span><span>{cname(next((m for m in DB["medecins"] if m["username"]==u),{}).get("id_centre",1))}</span></div>' if role=="medecin" else ""}
    </div>
  </div></div></div>
  <div class="col-md-9">
    <div class="nav-tabs">
      <button class="nav-tab active" onclick="showTab('tp1',this)"><i class="fas fa-user me-1"></i>Informations</button>
      <button class="nav-tab" onclick="showTab('tp2',this)"><i class="fas fa-key me-1"></i>Mot de passe</button>
      <button class="nav-tab" onclick="showTab('tp3',this)"><i class="fas fa-camera me-1"></i>Photo</button>
    </div>
    <div id="tp1" class="tab-pane"><div class="card"><div class="card-body">
      <form method="POST"><input type="hidden" name="action" value="info"><div class="row g-3">
        <div class="col-6"><label class="form-label">Nom</label><input type="text" name="nom" class="form-control" value="{ud.get("nom","")}" {"disabled" if role=="patient" else ""}></div>
        <div class="col-6"><label class="form-label">Prenom</label><input type="text" name="prenom" class="form-control" value="{ud.get("prenom","")}" {"disabled" if role=="patient" else ""}></div>
        <div class="col-6"><label class="form-label">Email</label><input type="email" name="email" class="form-control" value="{ud.get("email","")}"></div>
        <div class="col-6"><label class="form-label">Telephone</label><input type="text" name="tel" class="form-control" value="{ud.get("telephone","")}"></div>
      </div><button type="submit" class="btn btn-g mt-3"><i class="fas fa-save"></i>Enregistrer</button></form>
    </div></div></div>
    <div id="tp2" class="tab-pane" style="display:none;"><div class="card"><div class="card-body">
      <form method="POST"><input type="hidden" name="action" value="pwd"><div class="row g-3">
        <div class="col-md-4"><label class="form-label">Ancien</label><input type="password" name="old" class="form-control" required></div>
        <div class="col-md-4"><label class="form-label">Nouveau</label><input type="password" name="new1" class="form-control" required></div>
        <div class="col-md-4"><label class="form-label">Confirmer</label><input type="password" name="new2" class="form-control" required></div>
      </div><button type="submit" class="btn btn-g mt-3"><i class="fas fa-key"></i>Changer</button></form>
    </div></div></div>
    <div id="tp3" class="tab-pane" style="display:none;"><div class="card"><div class="card-body">
      <form method="POST" id="photoForm"><input type="hidden" name="action" value="photo"><input type="hidden" name="photo_b64" id="photo_b64">
        <div class="mb-3"><label class="form-label"><i class="fas fa-camera me-1"></i>Choisir une photo</label>
          <input type="file" id="photoFile" accept="image/*" class="form-control" onchange="previewPhoto(this)">
          <small style="color:var(--muted);">JPG, PNG — max 1MB recommande</small></div>
        <div id="photo_preview" style="margin-bottom:12px;{"display:block;" if ud.get("photo") else "display:none;"}">
          <img id="preview_img" src="{ud.get("photo","")}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid var(--gd);">
        </div>
        <button type="submit" class="btn btn-g"><i class="fas fa-camera"></i>Mettre a jour</button>
      </form>
    </div></div></div>
  </div>
</div>
<script>function previewPhoto(input){{if(input.files&&input.files[0]){{const r=new FileReader();r.onload=function(e){{document.getElementById('preview_img').src=e.target.result;document.getElementById('photo_preview').style.display='block';document.getElementById('photo_b64').value=e.target.result;}};r.readAsDataURL(input.files[0]);}}}}</script>"""
    return page("Mon Profil",role,u,body)

# ── LANCEMENT ─────────────────────────────────────────────────
