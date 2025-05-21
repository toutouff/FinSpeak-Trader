import requests
import pandas as pd
import os
import dotenv
import time
import warnings
import logging
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.warnings import MissingPivotFunction

# Supprimer l'avertissement sur le pivot manquant
warnings.simplefilter("ignore", MissingPivotFunction)

# Charger les variables d'environnement
dotenv.load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("influx_populate.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("influx_populate")

# --- CONFIGURATION ---
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_API_KEY")
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "finspeak")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "market_data")

# Liste des tickers
TICKERS = ["AAPL", "MSFT", "GOOGL", "NVDA"]

# --- FONCTIONS PRINCIPALES ---

def get_stock_data(ticker):
    """Fonction simple pour récupérer les données historiques d'un titre."""
    logger.info(f"Récupération des données pour {ticker}...")
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "full",  # Récupère l'historique complet
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()  # Vérifie si la requête a réussi
        data = response.json()
        
        if "Time Series (Daily)" not in data:
            if "Error Message" in data:
                logger.error(f"Erreur Alpha Vantage: {data['Error Message']}")
            elif "Note" in data:
                logger.error(f"Note Alpha Vantage: {data['Note']}")  # Limite d'API atteinte
            else:
                logger.error(f"Format de données inattendu: {list(data.keys())}")
            return None
        
        # Transformer les données en DataFrame
        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient="index")
        
        # Nettoyer les noms de colonnes
        df.columns = [col.split(". ")[1] for col in df.columns]
        
        # Convertir en types numériques
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
        
        # Ajouter la date comme colonne
        df = df.reset_index().rename(columns={"index": "date"})
        df["date"] = pd.to_datetime(df["date"])
        
        # Trier par date (plus récent au plus ancien)
        df = df.sort_values("date", ascending=False)
        
        logger.info(f"Récupéré {len(df)} jours de données pour {ticker}")
        return df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête pour {ticker}: {e}")
        return None
    except (ValueError, KeyError) as e:
        logger.error(f"Erreur lors du traitement des données pour {ticker}: {e}")
        return None

def store_in_influxdb(df, ticker, batch_size=500):
    """Stocke les données du DataFrame dans InfluxDB par lots pour éviter les timeouts."""
    if df is None or df.empty:
        logger.error(f"Pas de données à écrire pour {ticker}")
        return False
    
    logger.info(f"Stockage des données pour {ticker} dans InfluxDB (en lots de {batch_size})...")
    
    # Créer le client InfluxDB avec un timeout plus long
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG,
            timeout=60_000  # 60 secondes de timeout
        )
        
        # Vérifier que le bucket existe
        buckets_api = client.buckets_api()
        buckets = buckets_api.find_buckets().buckets
        bucket_names = [b.name for b in buckets]
        
        if INFLUXDB_BUCKET not in bucket_names:
            logger.warning(f"Le bucket {INFLUXDB_BUCKET} n'existe pas, tentative de création...")
            buckets_api.create_bucket(bucket_name=INFLUXDB_BUCKET, org=INFLUXDB_ORG)
            logger.info(f"Bucket {INFLUXDB_BUCKET} créé avec succès")
        
        # Créer l'API d'écriture
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        # Traiter les données par lots
        total_rows = len(df)
        success_count = 0
        
        for i in range(0, total_rows, batch_size):
            end_idx = min(i + batch_size, total_rows)
            current_batch = df.iloc[i:end_idx]
            logger.info(f"  Traitement du lot {i//batch_size + 1}/{(total_rows-1)//batch_size + 1} ({len(current_batch)} points)...")
            
            # Préparer les points pour ce lot
            points = []
            for _, row in current_batch.iterrows():
                point = Point("stock_price") \
                    .tag("symbol", ticker) \
                    .tag("timeframe", "daily") \
                    .field("open", float(row["open"])) \
                    .field("high", float(row["high"])) \
                    .field("low", float(row["low"])) \
                    .field("close", float(row["close"])) \
                    .field("volume", float(row["volume"])) \
                    .time(row["date"])
                points.append(point)
            
            # Écrire dans InfluxDB avec retry
            max_retries = 3
            retry_delay = 5  # secondes
            
            for attempt in range(max_retries):
                try:
                    write_api.write(bucket=INFLUXDB_BUCKET, record=points)
                    success_count += len(current_batch)
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"  Échec de l'écriture du lot (tentative {attempt+1}/{max_retries}): {e}")
                        logger.info(f"  Nouvelle tentative dans {retry_delay} secondes...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"  Échec définitif de l'écriture du lot après {max_retries} tentatives: {e}")
            
            # Petit délai entre les lots pour éviter de surcharger InfluxDB
            if end_idx < total_rows:
                time.sleep(1)
        
        # Fermer les ressources
        write_api.close()
        client.close()
        
        success_rate = (success_count / total_rows) * 100
        logger.info(f"Données stockées pour {ticker}: {success_count}/{total_rows} points ({success_rate:.1f}%)")
        
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture dans InfluxDB pour {ticker}: {e}")
        return False

def read_from_influxdb(ticker, start_time="-30d"):
    """Lit les données d'un ticker depuis InfluxDB avec un format optimisé."""
    logger.info(f"Lecture des données pour {ticker} depuis InfluxDB...")
    
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG,
            timeout=30_000
        )
        
        query_api = client.query_api()
        
        # Utiliser pivot pour obtenir un meilleur format de données
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: {start_time})
            |> filter(fn: (r) => r._measurement == "stock_price")
            |> filter(fn: (r) => r.symbol == "{ticker}")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        result = query_api.query_data_frame(query)
        client.close()
        
        if result.empty:
            logger.warning(f"Aucune donnée trouvée pour {ticker}")
            return None
        
        # Nettoyer le DataFrame
        if 'result' in result.columns:
            result = result.drop(columns=['result', 'table', '_measurement'])
        
        # Renommer les colonnes pour plus de clarté
        result = result.rename(columns={"_time": "time"})
        
        logger.info(f"Lu {len(result)} points de données pour {ticker}")
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de la lecture pour {ticker}: {e}")
        return None

def verify_data_integrity(ticker):
    """Vérifie l'intégrité des données stockées pour un ticker."""
    logger.info(f"Vérification de l'intégrité des données pour {ticker}...")
    
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        
        query_api = client.query_api()
        
        # 1. Vérifier le nombre total de points
        count_query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: 0)
            |> filter(fn: (r) => r._measurement == "stock_price")
            |> filter(fn: (r) => r.symbol == "{ticker}")
            |> count()
        '''
        
        count_result = query_api.query_data_frame(count_query)
        
        if count_result.empty:
            logger.warning(f"Aucune donnée trouvée pour {ticker}")
            return False
        
        count = count_result.iloc[0]['_value']
        logger.info(f"Nombre total de points pour {ticker}: {count}")
        
        # 2. Vérifier la plage de dates
        range_query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: 0)
            |> filter(fn: (r) => r._measurement == "stock_price")
            |> filter(fn: (r) => r.symbol == "{ticker}")
            |> filter(fn: (r) => r._field == "close")
            |> first()
        '''
        
        first_result = query_api.query_data_frame(range_query)
        
        if not first_result.empty:
            first_date = first_result.iloc[0]['_time']
            logger.info(f"Premier point de données pour {ticker}: {first_date}")
        
        last_query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: 0)
            |> filter(fn: (r) => r._measurement == "stock_price")
            |> filter(fn: (r) => r.symbol == "{ticker}")
            |> filter(fn: (r) => r._field == "close")
            |> last()
        '''
        
        last_result = query_api.query_data_frame(last_query)
        
        if not last_result.empty:
            last_date = last_result.iloc[0]['_time']
            logger.info(f"Dernier point de données pour {ticker}: {last_date}")
        
        client.close()
        return count > 0
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des données pour {ticker}: {e}")
        return False

# --- EXÉCUTION PRINCIPALE ---

def main():
    logger.info("Démarrage du script de peuplement de la base de données")
    
    # Vérifier les variables d'environnement
    if not ALPHA_VANTAGE_API_KEY:
        logger.error("La clé API Alpha Vantage n'est pas définie")
        return
    
    if not INFLUXDB_TOKEN:
        logger.error("Le token InfluxDB n'est pas défini")
        return
    
    # Afficher la configuration
    logger.info(f"URL InfluxDB: {INFLUXDB_URL}")
    logger.info(f"Organisation InfluxDB: {INFLUXDB_ORG}")
    logger.info(f"Bucket InfluxDB: {INFLUXDB_BUCKET}")
    
    # Vérifier la connexion à InfluxDB
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        health = client.health()
        logger.info(f"Connexion à InfluxDB réussie: {health.status}")
        client.close()
    except Exception as e:
        logger.error(f"Impossible de se connecter à InfluxDB: {e}")
        return
    
    # Pour chaque ticker, récupérer et stocker les données
    success_count = 0
    
    for i, ticker in enumerate(TICKERS):
        # Récupérer les données
        df = get_stock_data(ticker)
        
        # Stocker dans InfluxDB
        if df is not None:
            if store_in_influxdb(df, ticker):
                success_count += 1
                logger.info(f"Traitement réussi pour {ticker}")
            else:
                logger.error(f"Échec du traitement pour {ticker}")
        
        # Vérifier l'intégrité des données
        verify_data_integrity(ticker)
        
        # Attendre avant le prochain appel API (sauf pour le dernier ticker)
        if i < len(TICKERS) - 1:
            wait_time = 15  # 15 secondes entre chaque appel pour être sûr
            logger.info(f"Attente de {wait_time} secondes avant le prochain appel API...")
            time.sleep(wait_time)
    
    # Résumé final
    logger.info(f"Script de peuplement terminé. {success_count}/{len(TICKERS)} tickers traités avec succès.")
    
    # Exemple de lecture pour vérifier
    for ticker in TICKERS:
        data = read_from_influxdb(ticker, start_time="-7d")
        if data is not None:
            logger.info(f"Exemple de données récentes pour {ticker}:")
            logger.info(f"{data.head(3)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Erreur non gérée: {e}", exc_info=True)