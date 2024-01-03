"""
For testing the MongoDB pipeline.
"""
from mongodb.client import load_env_uri


def test_load_env_uri():
    """Test if the default MongoDB URI is loaded."""

    uri = load_env_uri()
    assert uri, "Default MongoDB URI is not loaded from .env file"


class TestDatabaseClient:
    """Test the DatabaseClient."""

    def test_check_connection(self, db_client):
        """Test if the connection is established."""
        connected = db_client.check_connection()
        assert connected, "Connection is not established"

    def test_check_product(self, db_client, product):
        """Test if the product is found."""

        found = db_client.check_product(product["asin"])
        assert found, "Product is not found"

    def test_log(self, db_client):
        """Test if the log is created."""

        logid = db_client.log("Pytest: test_log")
        assert logid, "Log is not created"

    def test_update_product(self, db_client, product):
        """Test if the product is updated."""

        updated = db_client.update_product(product)
        assert updated, "Product is not updated"
