from apps.ingest.app.store import StoreContext, init_store


def test_init_store_returns_engine_and_session_factory():
    store = init_store("postgresql://localhost/diamond")

    assert isinstance(store, StoreContext)
    assert store.engine.database_url == "postgresql://localhost/diamond"
    assert callable(store.session_factory)


def test_session_factory_returns_connection_dict():
    store = init_store("sqlite:///./diamond_departures.db")

    session = store.session_factory()
    assert session["database_url"] == "sqlite:///./diamond_departures.db"
    assert session["connected"] is True
