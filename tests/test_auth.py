import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

def test_login_page_charge(client):
    """La page de connexion doit s'afficher correctement."""
    response = client.get("/login")
    assert response.status_code == 200

def test_login_mauvais_mot_de_passe(client):
    """Un mauvais mot de passe doit afficher une erreur, pas connecter l'utilisateur."""
    response = client.post("/login", data={
        "username": "admin",
        "password": "faux_mot_de_passe"
    })
    assert b"Identifiant ou mot de passe incorrect" in response.data

def test_dashboard_sans_connexion_redirige(client):
    """Un utilisateur non connecté doit être redirigé vers /login."""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
