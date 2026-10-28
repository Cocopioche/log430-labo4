"""
Test fonctionnel CI du Labo 04.

Deroule le flux complet produit -> stock -> commande -> stock, appelle les deux
rapports, puis verifie que l'endpoint /metrics expose bien les trois Counters
Prometheus et que chacun a ete incremente par les appels ci-dessus.

S'execute dans le conteneur store_manager :
    docker compose -f ci/compose.yml exec -T store_manager python - < ci/smoke.py
"""
import json
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:5000"
COUNTERS = ("orders_total", "highest_spenders_total", "best_sellers_total")


def call(method, path, payload=None):
    """Appelle l'API locale et retourne (statut, corps decode)."""
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise AssertionError(
            f"{method} {path} a repondu {error.code} : {error.read().decode('utf-8')}"
        ) from error


def expect(method, path, status, payload=None):
    """Appelle l'API et exige un code de statut precis."""
    got, body = call(method, path, payload)
    assert got == status, f"{method} {path} : attendu {status}, obtenu {got} ({body})"
    return json.loads(body) if body else None


def read_counters():
    """Lit /metrics et retourne la valeur courante des trois Counters."""
    _, metrics = call("GET", "/metrics")
    values = {}
    for name in COUNTERS:
        for line in metrics.splitlines():
            if line.startswith(f"{name} "):
                values[name] = float(line.split()[1])
                break
        else:
            raise AssertionError(f"Counter {name} absent de /metrics")
    return values


expect("GET", "/health-check", 200)
before = read_counters()
print(f"Counters avant le flux : {before}")

product_id = expect(
    "POST",
    "/products",
    201,
    {"name": "Produit CI", "sku": f"CI-{uuid.uuid4().hex[:8]}", "price": 49.99},
)["product_id"]

expect("POST", "/stocks", 201, {"product_id": product_id, "quantity": 5})

stock = expect("GET", f"/stocks/{product_id}", 200)
assert stock["quantity"] == 5, f"Stock initial attendu 5, obtenu {stock['quantity']}"

user_id = expect(
    "POST",
    "/users",
    201,
    {"name": "Utilisateur CI", "email": f"ci-{uuid.uuid4().hex}@example.com"},
)["user_id"]

order_id = expect(
    "POST",
    "/orders",
    201,
    {"user_id": user_id, "items": [{"product_id": product_id, "quantity": 2}]},
)["order_id"]
assert order_id > 0, "order_id invalide"

stock = expect("GET", f"/stocks/{product_id}", 200)
assert stock["quantity"] == 3, f"Stock apres commande attendu 3, obtenu {stock['quantity']}"

# Les deux rapports sont servis depuis le cache Redis : on verifie le contrat
# HTTP et l'incrementation des Counters, pas le contenu du rapport.
expect("GET", "/orders/reports/highest-spenders", 200)
expect("GET", "/orders/reports/best-sellers", 200)

after = read_counters()
print(f"Counters apres le flux  : {after}")
for name in COUNTERS:
    delta = after[name] - before[name]
    assert delta >= 1, f"{name} n'a pas ete incremente (delta={delta})"

print(f"Flux complet valide : produit {product_id}, utilisateur {user_id}, commande {order_id}")
print("Les trois Counters Prometheus sont exposes et incrementes.")
