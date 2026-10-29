import firebase_admin
from firebase_admin import credentials, db
from pathlib import Path
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
CREDENTIAL_PATH = BASE_DIR / "hydranexus-service-account.json"

DATABASE_URL = (
    "https://hydranexus-6c14d-default-rtdb."
    "asia-southeast1.firebasedatabase.app"
)


def initialize_firebase():
    """Initialize Firebase Admin SDK once."""

    if firebase_admin._apps:
        return

    service_account_info = None

    try:
        service_account_info = dict(
            st.secrets["firebase_service_account"]
        )
    except Exception:
        service_account_info = None

    if service_account_info:
        credential = credentials.Certificate(
            service_account_info
        )
    elif CREDENTIAL_PATH.exists():
        credential = credentials.Certificate(
            str(CREDENTIAL_PATH)
        )
    else:
        raise FileNotFoundError(
            "Firebase credentials unavailable. "
            "Configure firebase_service_account in "
            "Streamlit Cloud Secrets or provide the local "
            "service-account JSON."
        )

    firebase_admin.initialize_app(
        credential,
        {"databaseURL": DATABASE_URL}
    )


def get_latest_sensor_data():
    """Fetch the latest phone sensor readings."""

    initialize_firebase()

    all_data = db.reference("sensorData").get()

    if not isinstance(all_data, dict):
        return None

    latest_record = None

    for uid, user_data in all_data.items():
        if not isinstance(user_data, dict):
            continue

        record = user_data.get("latest")

        if not isinstance(record, dict):
            continue

        record = dict(record)
        record["uid"] = uid

        if (
            latest_record is None
            or record.get("timestamp", 0)
            > latest_record.get("timestamp", 0)
        ):
            latest_record = record

    return latest_record