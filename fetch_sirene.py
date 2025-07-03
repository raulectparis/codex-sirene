import os
import sys
import requests

TOKEN_URL = "https://api.insee.fr/token"
SIRET_URL = "https://api.insee.fr/entreprises/sirene/V3/siret"

DEPARTMENTS_IDF = ["75", "77", "78", "91", "92", "93", "94", "95"]


def get_token(client_id: str, client_secret: str) -> str:
    """Retrieve an OAuth2 access token using client credentials."""
    try:
        response = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit(f"Token request failed: {exc}") from exc

    token = response.json().get("access_token")
    if not token:
        raise SystemExit("No access token found in response")
    return token


def build_query() -> str:
    """Construct the query for establishments."""
    departments_query = " OR ".join(
        f"codeDepartementEtablissement:{dept}" for dept in DEPARTMENTS_IDF
    )
    query = (
        "etatAdministratifEtablissement:A AND "
        "activitePrincipaleEtablissement:1083Z AND "
        f"({departments_query})"
    )
    return query


def fetch_establishments(token: str, nombre: int = 100):
    """Query the SIRENE API for establishments matching criteria."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": build_query(), "nombre": nombre}
    try:
        response = requests.get(SIRET_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit(f"API request failed: {exc}") from exc
    return response.json().get("etablissements", [])


def format_address(addr: dict) -> str:
    parts = [
        addr.get("numeroVoieEtablissement"),
        addr.get("typeVoieEtablissement"),
        addr.get("libelleVoieEtablissement"),
        addr.get("codePostalEtablissement"),
        addr.get("libelleCommuneEtablissement"),
    ]
    return " ".join(str(p) for p in parts if p)


def extract_rows(data):
    rows = []
    for et in data:
        siren = et.get("siren")
        siret = et.get("siret")
        legal = et.get("uniteLegale", {})
        raison = legal.get("denominationUniteLegale") or " ".join(
            p for p in [
                legal.get("prenomUsuelUniteLegale"),
                legal.get("nomUniteLegale"),
            ]
            if p
        )
        adresse = format_address(et.get("adresseEtablissement", {}))
        rows.append({
            "SIREN": siren,
            "SIRET": siret,
            "Raison sociale": raison,
            "Adresse": adresse,
        })
    return rows


def print_table(rows):
    if not rows:
        print("Aucun résultat.")
        return
    headers = list(rows[0].keys())
    widths = [max(len(str(row[h])) for row in rows + [dict(zip(headers, headers))]) for h in headers]
    row_fmt = " | ".join("{:<" + str(w) + "}" for w in widths)
    separator = "-+-".join("-" * w for w in widths)

    print(row_fmt.format(*headers))
    print(separator)
    for row in rows:
        print(row_fmt.format(*(row[h] for h in headers)))


def main():
    client_id = os.environ.get("SIRENE_CLIENT_ID")
    client_secret = os.environ.get("SIRENE_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("Please set SIRENE_CLIENT_ID and SIRENE_CLIENT_SECRET environment variables.")
        sys.exit(1)

    token = get_token(client_id, client_secret)
    etablissements = fetch_establishments(token)
    rows = extract_rows(etablissements)
    print_table(rows)


if __name__ == "__main__":
    main()
