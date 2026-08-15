"""
Couche de compatibilité DB <-> ORM.

L'application historique (app.py) a été écrite contre un dictionnaire Python
en mémoire : DB["patients"], DB["rdvs"].append(...), p["nom"], etc.

Plutôt que de réécrire les 288 points d'accès un par un (risque élevé de
régression sur une appli de 3600 lignes), cette couche fournit un objet DB
qui SE COMPORTE comme l'ancien dictionnaire (mêmes accès par crochets,
même .append(), mêmes comparaisons/itérations) mais qui lit et écrit
réellement dans PostgreSQL via les modèles SQLAlchemy de models.py.

Résultat : la logique métier de app.py reste quasi inchangée, mais chaque
écriture est persistée en base réelle, avec de vraies tables relationnelles.
"""
from models import (
    db, Centre, Service, User, Medecin, Patient, Dossier, Rdv, DemandeRdv,
    Consultation, Ordonnance, LigneOrdonnance, Medicament, Stock,
    VentePharmacie, Facture, FactureLigne, Paiement, ContratAssurance, Teleconsultation,
    ResultatExamen, DocumentPatient, ListeAttente, Triage,
    InteractionMedicamenteuse, AllergiePatient, Notification, Historique,
    SmsEnvoye, Creneau, AlerteStock, Ticket, Antecedent, ConstanteVitale, Vaccination,
)

MODEL_MAP = {
    "centres": Centre,
    "services": Service,
    "medecins": Medecin,
    "patients": Patient,
    "dossiers": Dossier,
    "rdvs": Rdv,
    "demandes_rdv": DemandeRdv,
    "consultations": Consultation,
    "resultats_examens": ResultatExamen,
    "documents_patient": DocumentPatient,
    "paiements": Paiement,
    "teleconsultations": Teleconsultation,
    "medicaments": Medicament,
    "stocks": Stock,
    "alertes_stock": AlerteStock,
    "ventes_pharmacie": VentePharmacie,
    "liste_attente": ListeAttente,
    "triage": Triage,
    "tickets": Ticket,
    "contrats_assurance": ContratAssurance,
    "interactions_medicamenteuses": InteractionMedicamenteuse,
    "allergies_patient": AllergiePatient,
    "notifications": Notification,
    "historiques": Historique,
    "sms_envoyes": SmsEnvoye,
    "creneaux": Creneau,
    "antecedents": Antecedent,
    "constantes_vitales": ConstanteVitale,
    "vaccinations": Vaccination,
    # "ordonnances" et "factures" sont gérées à part (lignes imbriquées) —
    # voir OrdonnanceRow / FactureRow
}


import datetime as _dt
from sqlalchemy import inspect as _sa_inspect, text as _sa_text


def sync_schema(app):
    """Ajoute automatiquement les colonnes/tables manquantes en base sans
    toucher aux données existantes. Nécessaire car db.create_all() ne crée
    que les tables absentes — il ne modifie jamais une table déjà existante,
    même si le modèle a évolué depuis (nouvelle colonne ajoutée). Sur le
    plan gratuit Render (pas de Shell, pas d'Alembic), c'est la seule
    manière fiable d'appliquer une migration automatiquement au démarrage."""
    with app.app_context():
        db.create_all()  # crée les tables entièrement nouvelles (ex: lignes_facture)
        insp = _sa_inspect(db.engine)
        existing_tables = set(insp.get_table_names())
        for model in db.Model.registry.mappers:
            table = model.local_table
            if table is None or table.name not in existing_tables:
                continue  # table absente : déjà gérée par create_all() ci-dessus
            existing_cols = {c["name"] for c in insp.get_columns(table.name)}
            for col in table.columns:
                if col.name in existing_cols:
                    continue
                try:
                    col_type = col.type.compile(dialect=db.engine.dialect)
                    with db.engine.begin() as conn:
                        conn.execute(_sa_text(f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" {col_type}'))
                    print(f"🔧 Migration auto : colonne {table.name}.{col.name} ajoutée")
                except Exception as _mig_err:
                    print(f"⚠️  Migration auto ignorée pour {table.name}.{col.name} : {_mig_err}")


def _coerce(col, value):
    """Convertit les valeurs 'à l'ancienne' (chaînes vides, dates en texte)
    vers ce qu'attend une vraie colonne SQLAlchemy typée."""
    is_fk = bool(col.foreign_keys)
    if is_fk and value in ("", 0, "0"):
        return None
    if value == "" and isinstance(col.type, (db.Date, db.DateTime)):
        return None
    if isinstance(col.type, db.Date) and isinstance(value, str) and value:
        try:
            return _dt.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    if isinstance(col.type, db.DateTime) and isinstance(value, str) and value:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return _dt.datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None
    if isinstance(col.type, db.String) and value is not None and not isinstance(value, str):
        return str(value)
    return value


class Row:
    """Enveloppe un objet SQLAlchemy pour qu'il se comporte comme un dict :
    row["champ"], row.get("champ"), row["champ"]=valeur, "champ" in row."""

    __slots__ = ("_obj",)

    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)

    def __getitem__(self, key):
        if not hasattr(self._obj, key):
            raise KeyError(key)
        return getattr(self._obj, key)

    def __setitem__(self, key, value):
        table = getattr(self._obj, "__table__", None)
        col = table.columns.get(key) if table is not None else None
        setattr(self._obj, key, _coerce(col, value) if col is not None else value)

    def __contains__(self, key):
        return hasattr(self._obj, key)

    def get(self, key, default=None):
        return getattr(self._obj, key, default)

    def __getattr__(self, key):
        return getattr(self._obj, key)

    def __setattr__(self, key, value):
        setattr(self._obj, key, value)

    def __eq__(self, other):
        if isinstance(other, Row):
            return self._obj is other._obj
        return self._obj is other

    def __hash__(self):
        return id(self._obj)

    def __repr__(self):
        return f"Row({self._obj!r})"

    def keys(self):
        return [c.name for c in self._obj.__table__.columns]

    def items(self):
        return [(k, getattr(self._obj, k)) for k in self.keys()]


class OrdonnanceRow(Row):
    """L'ancien dict ordonnance avait une clé 'lignes' (liste de dicts).
    On la recompose depuis la relation ORM lignes_ordonnance."""

    def __getitem__(self, key):
        if key == "lignes":
            return [
                {
                    "id_medicament": l.id_medicament,
                    "libelle": l.medicament.libelle if l.medicament else "",
                    "posologie": l.posologie,
                    "duree": l.duree,
                }
                for l in self._obj.lignes
            ]
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == "lignes":
            return self.__getitem__("lignes")
        return super().get(key, default)


class FactureRow(Row):
    """La facture peut désormais avoir des lignes de détail (multi-lignes) :
    clé 'lignes' recomposée depuis la relation ORM lignes_facture."""

    def __getitem__(self, key):
        if key == "lignes":
            return [
                {"id": l.id, "libelle": l.libelle, "type_ligne": l.type_ligne,
                 "quantite": l.quantite, "prix_unitaire": l.prix_unitaire, "montant": l.montant}
                for l in self._obj.lignes
            ]
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == "lignes":
            return self.__getitem__("lignes")
        return super().get(key, default)


class MedicamentRow(Row):
    """L'ancien dict médicament avait une clé 'id_stock' pointant vers la
    ligne de stock. Le modèle réel a la relation inverse (Stock.id_medicament),
    donc on la recalcule via la relation ORM medicament.stock."""

    def __getitem__(self, key):
        if key == "id_stock":
            return self._obj.stock.id if self._obj.stock else None
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == "id_stock":
            return self.__getitem__("id_stock") or default
        return super().get(key, default)


class ConsultationRow(Row):
    """L'ancien dict consultation gardait id_ordonnance/id_facture/id_resultat
    en clés directes. Le modèle réel les retrouve via les relations inverses
    (Ordonnance/Facture/ResultatExamen -> id_consultation)."""

    _REL = {"id_ordonnance": "ordonnance", "id_facture": "facture", "id_resultat": "resultat"}

    def __getitem__(self, key):
        if key in self._REL:
            rel = getattr(self._obj, self._REL[key])
            return rel.id if rel else None
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key in self._REL:
            return self.__getitem__(key) or default
        return super().get(key, default)


class VentePharmacieRow(Row):
    """L'ancien dict vente stockait le libellé du médicament en dur.
    On le retrouve via la relation ORM vente.medicament."""

    def __getitem__(self, key):
        if key == "libelle":
            return self._obj.medicament.libelle if self._obj.medicament else ""
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == "libelle":
            return self.__getitem__("libelle") or default
        return super().get(key, default)


def wrap(obj, table_name):
    if obj is None:
        return None
    if table_name == "ordonnances":
        return OrdonnanceRow(obj)
    if table_name == "medicaments":
        return MedicamentRow(obj)
    if table_name == "consultations":
        return ConsultationRow(obj)
    if table_name == "ventes_pharmacie":
        return VentePharmacieRow(obj)
    if table_name == "factures":
        return FactureRow(obj)
    return Row(obj)


NESTED_LINES = {
    "ordonnances": (LigneOrdonnance, "id_ordonnance"),
    "factures": (FactureLigne, "id_facture"),
}


class TableProxy:
    """Se comporte comme la liste DB["table"] : itérable, filtrable par
    compréhension, .append(dict) insère une vraie ligne en base."""

    def __init__(self, table_name, model):
        self.table_name = table_name
        self.model = model

    def _query(self):
        return self.model.query.all()

    def __iter__(self):
        return iter(wrap(o, self.table_name) for o in self._query())

    def __len__(self):
        return self.model.query.count()

    def __getitem__(self, idx):
        return wrap(self._query()[idx], self.table_name)

    def append(self, d):
        """d est un dict (ancien style). On retire un éventuel 'id' fourni
        manuellement (par nid()) : la base génère l'id réel. On ignore aussi
        toute clé qui ne correspond pas à une colonne réelle du modèle
        (ex: 'alertes_interactions' calculé à la volée, pas persisté).
        IMPORTANT : on modifie le dict d'origine (pas une copie) pour que
        d["id"] soit mis à jour avec le vrai id — le code appelant relit
        souvent cette valeur juste après l'appel à append()."""
        nested = NESTED_LINES.get(self.table_name)
        lignes = d.get("lignes") if nested else None
        valid_cols = {c.name: c for c in self.model.__table__.columns}
        clean = {k: v for k, v in d.items() if k in valid_cols and k != "id"}
        clean = {k: _coerce(valid_cols[k], v) for k, v in clean.items()}
        obj = self.model(**clean)
        db.session.add(obj)
        db.session.flush()  # attribue l'id réel tout de suite
        if lignes:
            child_model, fk_name = nested
            ligne_cols = {c.name for c in child_model.__table__.columns}
            for l in lignes:
                lclean = {k: v for k, v in l.items() if k in ligne_cols}
                db.session.add(child_model(**{fk_name: obj.id}, **lclean))
            db.session.flush()
        pk_name = [c.name for c in self.model.__table__.primary_key.columns][0]
        d[pk_name] = getattr(obj, pk_name)  # pour le code appelant qui relit d["id"]/d["matricule"] juste après
        return wrap(obj, self.table_name)

    def remove_matching(self, keep_predicate):
        """Implémente le pattern DB['x'] = [i for i in DB['x'] if cond]
        en supprimant en base les lignes qui NE vérifient PAS la condition."""
        for obj in self._query():
            if not keep_predicate(wrap(obj, self.table_name)):
                db.session.delete(obj)

    def __repr__(self):
        return f"TableProxy({self.table_name})"


class UsersProxy:
    """Émule l'ancien DB['users'] : dict {username: {...}} appuyé sur User."""

    def get(self, username, default=None):
        u = User.query.filter_by(username=username).first()
        return wrap(u, "users") if u else default

    def __getitem__(self, username):
        u = User.query.filter_by(username=username).first()
        if u is None:
            raise KeyError(username)
        return wrap(u, "users")

    def __setitem__(self, username, d):
        u = User.query.filter_by(username=username).first()
        valid_cols = {c.name: c for c in User.__table__.columns}
        d = {k: _coerce(valid_cols[k], v) for k, v in d.items() if k in valid_cols and k != "username"}
        if u is None:
            u = User(username=username, **d)
            db.session.add(u)
        else:
            for k, v in d.items():
                setattr(u, k, v)
        db.session.flush()

    def __delitem__(self, username):
        u = User.query.filter_by(username=username).first()
        if u is None:
            raise KeyError(username)
        db.session.delete(u)

    def __contains__(self, username):
        return User.query.filter_by(username=username).first() is not None

    def __iter__(self):
        return iter(u.username for u in User.query.all())

    def items(self):
        return [(u.username, wrap(u, "users")) for u in User.query.all()]

    def __len__(self):
        return User.query.count()


class CounterProxy:
    """Émule DB['_c'] (compteurs manuels). Conservé pour compat mais les ids
    réels viennent désormais de l'auto-increment PostgreSQL — ce compteur
    ne sert plus qu'à générer des numéros d'affichage (FAC-000x, DOS-000x...)."""

    def __init__(self):
        self._counts = {}

    def __getitem__(self, key):
        return self._counts.get(key, 0)

    def __setitem__(self, key, value):
        self._counts[key] = value


class DBProxy:
    """Point d'entrée unique : remplace la variable DB = {...} d'origine."""

    def __init__(self):
        self._users = UsersProxy()
        self._counters = CounterProxy()
        self._tables = {name: TableProxy(name, model) for name, model in MODEL_MAP.items()}
        self._tables["ordonnances"] = TableProxy("ordonnances", Ordonnance)
        self._tables["factures"] = TableProxy("factures", Facture)

    def __getitem__(self, key):
        if key == "users":
            return self._users
        if key == "_c":
            return self._counters
        if key in self._tables:
            return self._tables[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        # Pattern DB["table"] = [liste filtrée] -> suppression des lignes absentes
        if key in self._tables and isinstance(value, list):
            table = self._tables[key]
            pk_name = [c.name for c in table.model.__table__.primary_key.columns][0]
            kept_ids = set()
            for item in value:
                pk = item.get(pk_name) if isinstance(item, dict) else getattr(item, pk_name, None)
                if pk is not None:
                    kept_ids.add(pk)
            for obj in table._query():
                if getattr(obj, pk_name) not in kept_ids:
                    db.session.delete(obj)
        elif key == "_c":
            self._counters = value
        else:
            raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def init_counters(self, app):
        """Initialise les compteurs d'affichage (FAC-0001, DOS-0001, ...) à
        partir du nombre de lignes déjà en base, pour éviter que deux
        redémarrages consécutifs du serveur ne réutilisent les mêmes
        numéros (les compteurs eux-mêmes ne vivent qu'en mémoire, l'id réel
        vient toujours de l'auto-increment de la base)."""
        with app.app_context():
            sync_schema(app)
            for key, model in COUNTER_TABLE_MAP.items():
                try:
                    self._counters[key] = model.query.count()
                except Exception:
                    self._counters[key] = 0


COUNTER_TABLE_MAP = {
    "allergies": AllergiePatient, "attente": ListeAttente, "centres": Centre,
    "cons": Consultation, "contrats": ContratAssurance, "creneaux": Creneau,
    "demandes": DemandeRdv, "docs": DocumentPatient, "dossiers": Dossier,
    "facts": Facture, "hists": Historique, "interactions": InteractionMedicamenteuse,
    "meds": Medicament, "notifs": Notification, "ords": Ordonnance,
    "paiements": Paiement, "patients": Patient, "rdvs": Rdv, "services": Service,
    "sms": SmsEnvoye, "stocks": Stock, "teles": Teleconsultation, "tickets": Ticket,
    "triage": Triage, "ventes": VentePharmacie,
}
