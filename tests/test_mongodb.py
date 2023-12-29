"""
For testing the MongoDB pipeline.
"""

import pytest

from mongodb.client import DatabaseClient


@pytest.fixture
def db_client():
    """Create a MongoDB client."""

    return DatabaseClient()


@pytest.fixture
def product():
    """Create a product."""

    return {
        "asin": "B07YQFH15Y",
        "title": "Nana Maxi Goodnight Serviettes Hygiéniques pour la Nuit, 12 Serviettes",
        "image": "https://m.media-amazon.com/images/I/81mY2rB96VL._AC_UL320_.jpg",
    }


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

        logid = db_client.log("Test log by pytest")
        assert logid, "Log is not created"

    def test_update_product(self, db_client, product):
        """Test if the product is updated."""

        updated = db_client.update_product(product)
        assert updated, "Product is not updated"
