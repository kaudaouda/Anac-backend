#!/usr/bin/env python3
"""
Script de test pour l'authentification JWT + Cookies
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = urljoin(BASE_URL, "/auth/login/")
REGISTER_URL = urljoin(BASE_URL, "/auth/register/")
CHECK_AUTH_URL = urljoin(BASE_URL, "/auth/check-auth/")
LOGOUT_URL = urljoin(BASE_URL, "/auth/logout/")
REFRESH_URL = urljoin(BASE_URL, "/auth/refresh-token/")

def test_register():
    """Tester l'inscription d'un utilisateur"""
    print("🔐 Test d'inscription...")
    
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(REGISTER_URL, json=user_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Inscription réussie")
            print("Cookies reçus:")
            for cookie in response.cookies:
                print(f"  - {cookie.name}: {cookie.value[:50]}...")
            return response.cookies
        else:
            print(f"❌ Échec de l'inscription: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de l'inscription: {e}")
        return None

def test_login():
    """Tester la connexion d'un utilisateur"""
    print("\n🔑 Test de connexion...")
    
    credentials = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=credentials)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Connexion réussie")
            print("Cookies reçus:")
            for cookie in response.cookies:
                print(f"  - {cookie.name}: {cookie.value[:50]}...")
            return response.cookies
        else:
            print(f"❌ Échec de la connexion: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None

def test_check_auth(cookies):
    """Tester la vérification de l'authentification"""
    print("\n🔍 Test de vérification d'authentification...")
    
    if not cookies:
        print("❌ Aucun cookie disponible")
        return False
    
    try:
        response = requests.get(CHECK_AUTH_URL, cookies=cookies)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Authentification vérifiée")
            print(f"Utilisateur: {data.get('user', {}).get('email', 'N/A')}")
            return True
        else:
            print(f"❌ Échec de la vérification: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def test_refresh_token(cookies):
    """Tester le rafraîchissement du token"""
    print("\n🔄 Test de rafraîchissement du token...")
    
    if not cookies:
        print("❌ Aucun cookie disponible")
        return False
    
    try:
        response = requests.post(REFRESH_URL, cookies=cookies)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token rafraîchi avec succès")
            print("Nouveaux cookies:")
            for cookie in response.cookies:
                print(f"  - {cookie.name}: {cookie.value[:50]}...")
            return True
        else:
            print(f"❌ Échec du rafraîchissement: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du rafraîchissement: {e}")
        return False

def test_logout(cookies):
    """Tester la déconnexion"""
    print("\n🚪 Test de déconnexion...")
    
    if not cookies:
        print("❌ Aucun cookie disponible")
        return False
    
    try:
        response = requests.post(LOGOUT_URL, cookies=cookies)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Déconnexion réussie")
            return True
        else:
            print(f"❌ Échec de la déconnexion: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la déconnexion: {e}")
        return False

def test_protected_endpoint(cookies):
    """Tester un endpoint protégé"""
    print("\n🛡️ Test d'endpoint protégé...")
    
    if not cookies:
        print("❌ Aucun cookie disponible")
        return False
    
    # Tester un endpoint qui nécessite une authentification
    try:
        response = requests.get(CHECK_AUTH_URL, cookies=cookies)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Accès à l'endpoint protégé réussi")
            return True
        else:
            print(f"❌ Accès refusé: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'accès: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'authentification JWT + Cookies")
    print("=" * 60)
    
    # Test 1: Inscription
    cookies = test_register()
    
    if not cookies:
        print("\n⚠️ Impossible de continuer sans cookies d'authentification")
        return
    
    # Test 2: Connexion
    cookies = test_login()
    
    if not cookies:
        print("\n⚠️ Impossible de continuer sans cookies d'authentification")
        return
    
    # Test 3: Vérification de l'authentification
    auth_ok = test_check_auth(cookies)
    
    if not auth_ok:
        print("\n⚠️ L'authentification n'a pas fonctionné")
        return
    
    # Test 4: Endpoint protégé
    test_protected_endpoint(cookies)
    
    # Test 5: Rafraîchissement du token
    test_refresh_token(cookies)
    
    # Test 6: Déconnexion
    test_logout(cookies)
    
    print("\n" + "=" * 60)
    print("🏁 Tests terminés")
    
    # Vérification finale
    print("\n🔍 Vérification finale de l'authentification...")
    final_check = test_check_auth(cookies)
    
    if not final_check:
        print("✅ L'utilisateur a été correctement déconnecté")
    else:
        print("❌ L'utilisateur est toujours connecté")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Erreur inattendue: {e}")
        sys.exit(1)
