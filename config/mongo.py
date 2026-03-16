import sys

import certifi
from django.conf import settings
from mongoengine import connect
from mongoengine.connection import get_connection


_IS_CONNECTED = False


def _build_connection_options():
    connection_options = {
        "uuidRepresentation": "standard",
        "serverSelectionTimeoutMS": settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
        "connectTimeoutMS": settings.MONGO_CONNECT_TIMEOUT_MS,
        "socketTimeoutMS": settings.MONGO_SOCKET_TIMEOUT_MS,
    }

    tls_ca_file = settings.MONGO_TLS_CA_FILE.strip() or certifi.where()
    if tls_ca_file:
        connection_options["tlsCAFile"] = tls_ca_file

    return connection_options


def connect_mongo():
    global _IS_CONNECTED

    if _IS_CONNECTED:
        return

    try:
        get_connection(alias="default")
        _IS_CONNECTED = True
        return
    except Exception:
        pass

    mongo_uri = settings.MONGO_DB_URI
    db_name = settings.MONGO_DB_NAME

    if not mongo_uri or not db_name:
        _IS_CONNECTED = False
        return

    if "test" in sys.argv:
        try:
            import mongomock

            connect(
                db=db_name,
                host=mongo_uri,
                alias="default",
                mongo_client_class=mongomock.MongoClient,
                uuidRepresentation="standard",
            )
            _IS_CONNECTED = True
            return
        except Exception:
            pass

    try:
        connection_options = _build_connection_options()
        connect(
            db=db_name,
            host=mongo_uri,
            alias="default",
            **connection_options,
        )

        client = get_connection(alias="default")
        client.admin.command("ping")
        _IS_CONNECTED = True
    except Exception:
        _IS_CONNECTED = False


def is_mongo_connected():
    try:
        client = get_connection(alias="default")
        client.admin.command("ping")
        return True
    except Exception:
        return False
