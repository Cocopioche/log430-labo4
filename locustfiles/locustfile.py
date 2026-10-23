"""
Locustfile for load testing store_manager.py
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import random
from locust import task, between
from locust.contrib.fasthttp import FastHttpUser
import logging

class FlaskAPIUser(FastHttpUser):
    # Temps d'attente entre les requêtes (1 à 2 secondes)
    wait_time = between(1, 2)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    # Proportion d'exécution 1:1:1, ce qui signifie : 1/3, 1/3, 1/3 (30 % des appels à chacun)
    @task(1) 
    def orders(self):
        """Test POST /orders endpoint (write)"""
        random_id = random.randrange(1, 3)
        random_id2 = random.randrange(1, 3)
        random_id3 = random.randrange(1, 5)
        mock_order = {
            "user_id": random_id,
            "items": [{"product_id": random_id2, "quantity": random_id3}] 
        }   

        # Ajouter aléatoirement plusieurs articles (30 % des fois)
        if random.randint(1, 10) <= 3:
            random_id = random.randrange(1, 3)
            mock_order["items"].append({"product_id": random_id, "quantity": 1})
            mock_order["items"].append({"product_id": random_id, "quantity": 2})

        with self.client.post("/orders", 
                            json=mock_order, 
                            headers={"Content-Type": "application/json"},
                            catch_response=True) as response:
            try:

                if response is None or response.headers is None:
                    self.environment.events.request.fire(
                        request_type="POST",
                        name="/orders",
                        response_time=0,
                        response_length=0,
                        exception=Exception("Aucune réponse (erreur ou timeout)")
                    )
                    return

                content_type = response.headers.get('content-type', '').lower()
                if 'application/json' not in content_type:
                    response.failure(f"Erreur : {response.status_code} - Aucun JSON dans la réponse. Message : {response.text}")
                    return

                data = response.json()
                if response.status_code == 201:
                    if "order_id" in data:
                        response.success()
                    else:
                        response.failure("Aucun ID renvoyé pour la commande créée")
                else:
                    response.failure(f"Erreur : {response.status_code} - {data.get('error', 'Unknown error')}")
            except ValueError:
                response.failure(f"JSON invalide dans la réponse: {response.text}")

    @task(1) 
    def highest_spenders(self):
        """Test GET /orders/reports/highest-spenders endpoint (read)"""
        self.logger.info("Calling highest_spenders")
        with self.client.get("/orders/reports/highest-spenders", catch_response=True) as response:
            try:

                if response is None or response.headers is None:
                    self.environment.events.request.fire(
                        request_type="GET",
                        name="/orders/reports/highest-spenders",
                        response_time=0,
                        response_length=0,
                        exception=Exception("Aucune réponse (erreur ou timeout)")
                    )
                    return

                content_type = response.headers.get('content-type', '').lower()
                if 'application/json' not in content_type:
                    response.failure(f"Erreur : {response.status_code} - Aucun JSON dans la réponse. Message : {response.text}")
                    return
            
                data = response.json()
                if response.status_code == 200: 
                    if isinstance(data, list): 
                        response.success()
                    else:
                        response.failure("Le résultat n'est pas une liste : " + str(data))
                else:
                    response.failure(f"Erreur : {response.status_code} - {data.get('error', 'Unknown error')}")
            except ValueError:
                response.failure(f"Erreur : {response.status_code} - JSON invalide dans la réponse")

    @task(1) 
    def best_sellers(self):
        """Test GET /orders/reports/best-sellers endpoint (read)"""
        self.logger.info("Calling best_sellers")
        with self.client.get("/orders/reports/best-sellers", catch_response=True) as response:
            try:

                if response is None or response.headers is None:
                    self.environment.events.request.fire(
                        request_type="GET",
                        name="/orders/reports/best-sellers",
                        response_time=0,
                        response_length=0,
                        exception=Exception("Aucune réponse (erreur ou timeout)")
                    )
                    return

                content_type = response.headers.get('content-type', '').lower()
                if 'application/json' not in content_type:
                    response.failure(f"Erreur : {response.status_code} - Aucun JSON dans la réponse. Message : {response.text}")
                    return
            
                data = response.json()
                if response.status_code == 200: 
                    if isinstance(data, list): 
                        response.success()
                    else:
                        response.failure("Le résultat n'est pas une liste : " + str(data))
                else:
                    response.failure(f"Erreur : {response.status_code} - {data.get('error', 'Unknown error')}")
            except ValueError:
                response.failure(f"Erreur : {response.status_code} - JSON invalide dans la réponse")