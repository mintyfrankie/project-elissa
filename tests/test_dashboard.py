"""
Test the streamlit dashboard.
"""

from streamlit.testing.v1 import AppTest


def test_dashboard():
    test = AppTest("dashboard/hello.py", default_timeout=60)
    test.run()

    assert not test.exception
