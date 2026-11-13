"""Static checks on the SQL scripts. No database required."""

import re
import unittest
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[1] / "database"

EXPECTED_TABLES = {
    "genre", "subscription_plan", "artist", "album", "track",
    "app_user", "playlist", "playlist_track", "listening_history",
}
EXPECTED_VIEWS = {
    "bi_dim_plan", "bi_dim_user", "bi_dim_track", "bi_fact_listening",
}


class SchemaTests(unittest.TestCase):

    def test_schema_defines_expected_tables(self):
        sql = (DB_DIR / "schema.sql").read_text()
        tables = set(re.findall(r"CREATE TABLE (\w+)", sql))
        self.assertEqual(tables, EXPECTED_TABLES)

    def test_reporting_views_defined(self):
        sql = (DB_DIR / "powerbi_views.sql").read_text()
        views = set(re.findall(r"CREATE OR REPLACE VIEW (\w+)", sql))
        self.assertEqual(views, EXPECTED_VIEWS)

    def test_views_only_reference_schema_tables(self):
        sql = (DB_DIR / "powerbi_views.sql").read_text()
        sql = re.sub(r"--.*", "", sql)
        referenced = set(re.findall(r"(?:FROM|JOIN)\s+(\w+)", sql))
        self.assertTrue(referenced <= EXPECTED_TABLES, referenced - EXPECTED_TABLES)

    def test_indexes_reference_schema_tables(self):
        sql = (DB_DIR / "indexes.sql").read_text()
        tables = set(re.findall(r"ON (\w+)\(", sql))
        self.assertTrue(tables <= EXPECTED_TABLES, tables - EXPECTED_TABLES)


if __name__ == "__main__":
    unittest.main()
