import csv
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module

main_server = load_spike_module("004_csv_data", "main_server")
PostOfficeDatabase = main_server.PostOfficeDatabase
main = main_server.main
mcp_factory = main_server.mcp_factory
setup_clean_logging = main_server.setup_clean_logging


class TestPostOfficeDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, newline="")
        writer = csv.writer(self.temp_file)
        writer.writerow(
            [
                "package_id",
                "delivery_guy",
                "weight_kg",
                "size_cm",
                "sender_name",
                "sender_address",
                "receiver_name",
                "receiver_address",
                "label",
            ]
        )
        writer.writerow(["PKG001", "1", "2.5", "10x10x10", "Alice", "123 St", "Bob", "456 Ave", "FRAGILE"])
        writer.writerow(["PKG002", "1", "1.0", "5x5x5", "Charlie", "789 Rd", "Dave", "101 Blvd", "STANDARD"])
        writer.writerow(["PKG003", "2", "5.0", "20x20x20", "Eve", "202 Ln", "Frank", "303 Dr", "URGENT"])
        self.temp_file.close()

        self.db = PostOfficeDatabase(csv_path=self.temp_file.name)

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_load_packages(self):
        self.assertEqual(len(self.db.packages), 3)

    def test_get_packages_for_delivery_guy(self):
        packages = self.db.get_packages_for_delivery_guy(1)
        self.assertEqual(len(packages), 2)
        self.assertEqual(packages[0]["package_id"], "PKG001")

        packages = self.db.get_packages_for_delivery_guy(2)
        self.assertEqual(len(packages), 1)

        packages = self.db.get_packages_for_delivery_guy(3)
        self.assertEqual(len(packages), 0)

    def test_get_package_details(self):
        pkg = self.db.get_package_details("PKG001")
        self.assertIsNotNone(pkg)
        self.assertEqual(pkg["sender_name"], "Alice")

        pkg = self.db.get_package_details("PKG999")
        self.assertIsNone(pkg)

    def test_get_delivery_guy_stats(self):
        stats = self.db.get_delivery_guy_stats(1)
        self.assertEqual(stats["delivery_guy"], 1)
        self.assertEqual(stats["total_packages"], 2)
        self.assertEqual(stats["total_weight_kg"], 3.5)
        self.assertEqual(stats["fragile_packages"], 1)
        self.assertEqual(stats["urgent_packages"], 0)

    def test_get_all_delivery_guys(self):
        guys = self.db.get_all_delivery_guys()
        self.assertEqual(guys, [1, 2])

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            PostOfficeDatabase(csv_path="non_existent.csv")


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.tools = {}

        def tool_decorator():
            def wrapper(func):
                self.tools[func.__name__] = func
                return func

            return wrapper

        self.fastmcp_patcher = patch.object(main_server, "FastMCP")
        self.mock_fastmcp_class = self.fastmcp_patcher.start()
        self.mock_mcp_instance = MagicMock()
        self.mock_fastmcp_class.return_value = self.mock_mcp_instance
        self.mock_mcp_instance.tool.side_effect = tool_decorator

        # Mock PostOfficeDatabase
        self.db_patcher = patch.object(main_server, "PostOfficeDatabase")
        self.mock_db_class = self.db_patcher.start()
        self.mock_db = MagicMock()
        self.mock_db_class.return_value = self.mock_db

    def tearDown(self):
        self.fastmcp_patcher.stop()
        self.db_patcher.stop()

    def test_mcp_factory(self):
        mcp = mcp_factory("test_app")
        self.assertEqual(mcp, self.mock_mcp_instance)

        # Test tools exist
        self.assertIn("get_packages_for_delivery_guy", self.tools)
        self.assertIn("get_package_details", self.tools)

        # Test get_packages_for_delivery_guy tool
        tool = self.tools["get_packages_for_delivery_guy"]
        self.mock_db.get_packages_for_delivery_guy.return_value = [
            {
                "package_id": "PKG001",
                "label": "FRAGILE",
                "weight_kg": "2.5",
                "size_cm": "10x10",
                "sender_name": "A",
                "sender_address": "B",
                "receiver_name": "C",
                "receiver_address": "D",
            }
        ]
        result = tool(1)
        self.assertIn("PKG001", result)
        self.assertIn("FRAGILE", result)

        # Test empty result
        self.mock_db.get_packages_for_delivery_guy.return_value = []
        result = tool(1)
        self.assertIn("No packages found", result)

        # Test get_package_details tool
        tool = self.tools["get_package_details"]
        self.mock_db.get_package_details.return_value = {
            "package_id": "PKG001",
            "delivery_guy": "1",
            "label": "FRAGILE",
            "weight_kg": "2.5",
            "size_cm": "10x10",
            "sender_name": "A",
            "sender_address": "B",
            "receiver_name": "C",
            "receiver_address": "D",
        }
        result = tool("PKG001")
        self.assertIn("PKG001", result)
        self.assertIn("Delivery Guy 1", result)

        # Test not found
        self.mock_db.get_package_details.return_value = None
        result = tool("PKG999")
        self.assertIn("not found", result)

    def test_get_delivery_guy_stats_tool(self):
        mcp_factory("test_app")
        tool = self.tools["get_delivery_guy_stats"]

        self.mock_db.get_delivery_guy_stats.return_value = {
            "total_packages": 10,
            "total_weight_kg": 50.5,
            "fragile_packages": 2,
            "urgent_packages": 1,
        }

        result = tool(1)
        self.assertIn("Total Packages: 10", result)

    def test_get_all_delivery_guys_tool(self):
        mcp_factory("test_app")
        tool = self.tools["get_all_delivery_guys"]

        self.mock_db.get_all_delivery_guys.return_value = [1, 2, 3]

        result = tool()
        self.assertIn("1, 2, 3", result)

    def test_search_packages_by_label_tool(self):
        mcp_factory("test_app")
        tool = self.tools["search_packages_by_label"]

        # Mock db.packages as a list
        self.mock_db.packages = [
            {
                "package_id": "P1",
                "label": "FRAGILE",
                "delivery_guy": 1,
                "state": "pending",
                "weight_kg": 1.0,
                "receiver_name": "R1",
            },
            {
                "package_id": "P2",
                "label": "STANDARD",
                "delivery_guy": 2,
                "state": "delivered",
                "weight_kg": 2.0,
                "receiver_name": "R2",
            },
        ]

        result = tool("FRAGILE")
        self.assertIn("P1", result)
        self.assertNotIn("P2", result)

        result = tool("UNKNOWN")
        self.assertIn("No packages found", result)

    def test_get_packages_by_state_tool(self):
        mcp_factory("test_app")
        tool = self.tools["get_packages_by_state"]

        self.mock_db.packages = [
            {
                "package_id": "P1",
                "state": "pending",
                "delivery_guy": 1,
                "label": "L1",
                "weight_kg": 1.0,
                "receiver_name": "R1",
            },
            {
                "package_id": "P2",
                "state": "delivered",
                "delivery_guy": 2,
                "label": "L2",
                "weight_kg": 2.0,
                "receiver_name": "R2",
            },
        ]

        result = tool("pending")
        self.assertIn("P1", result)
        self.assertNotIn("P2", result)

    def test_get_packages_by_state_no_match(self):
        mcp_factory("test_app")
        tool = self.tools["get_packages_by_state"]
        self.mock_db.packages = [{"state": "delivered"}]
        result = tool("pending")
        self.assertIn("No packages found with state: pending", result)

    def test_update_package_state_tool(self):
        mcp_factory("test_app")
        tool = self.tools["update_package_state"]

        pkg = {"package_id": "P1", "state": "pending", "key": "val"}
        self.mock_db.get_package_details.return_value = pkg
        self.mock_db.csv_path = "dummy.csv"
        self.mock_db.packages = [pkg]

        with patch("builtins.open", unittest.mock.mock_open()), patch("csv.DictWriter"):
            result = tool("P1", "delivered")

        self.assertIn("updated from pending to delivered", result)
        self.assertEqual(pkg["state"], "delivered")

    def test_add_new_package_tool(self):
        mcp_factory("test_app")
        tool = self.tools["add_new_package"]

        self.mock_db.packages = []
        self.mock_db.csv_path = "dummy.csv"

        new_pkg = {"package_id": "P1", "val": "test"}

        with patch("builtins.open", unittest.mock.mock_open()), patch("csv.DictWriter"):
            result = tool(new_pkg)

        self.assertIn("added successfully", result)
        self.assertEqual(len(self.mock_db.packages), 1)

    def test_delete_package_tool(self):
        mcp_factory("test_app")
        tool = self.tools["delete_package"]

        pkg = {"package_id": "P1"}
        self.mock_db.packages = [pkg]
        self.mock_db.get_package_details.return_value = pkg
        self.mock_db.csv_path = "dummy.csv"

        with patch("builtins.open", unittest.mock.mock_open()), patch("csv.DictWriter"):
            result = tool("P1")

        self.assertIn("deleted successfully", result)
        self.assertEqual(len(self.mock_db.packages), 0)

    def test_delete_packages_tool(self):
        mcp_factory("test_app")
        tool = self.tools["delete_packages"]

        pkg1 = {"package_id": "P1"}
        pkg2 = {"package_id": "P2"}
        self.mock_db.packages = [pkg1, pkg2]

        def get_details(pid):
            if pid == "P1":
                return pkg1
            if pid == "P2":
                return pkg2
            return None

        self.mock_db.get_package_details.side_effect = get_details
        self.mock_db.csv_path = "dummy.csv"

        with patch("builtins.open", unittest.mock.mock_open()), patch("csv.DictWriter"):
            result = tool(["P1", "P2"])

        self.assertIn("Deleted 2 packages", result)
        self.assertEqual(len(self.mock_db.packages), 0)

    @patch.object(main_server, "logging")
    def test_setup_clean_logging(self, mock_logging):
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        logger = setup_clean_logging()
        self.assertEqual(logger, mock_logger)

    def test_setup_clean_logging_options(self):
        # setup_clean_logging is already imported at module level
        with patch.object(main_server, "logging") as mock_logging:
            mock_logger = MagicMock()
            mock_logging.getLogger.return_value = mock_logger

            setup_clean_logging(show_uvicorn=True, show_mcp_internals=True)

            # Verify calls
            mock_logging.getLogger.assert_called()

    def test_setup_clean_logging_fallback(self):
        # Mock LOGGING_CONFIG to cause KeyError
        with patch.dict(main_server.LOGGING_CONFIG, {}, clear=True):
            logger = setup_clean_logging()
            self.assertIsNotNone(logger)

    @patch.object(main_server, "mcp_factory")
    @patch.object(main_server, "setup_clean_logging")
    def test_main(self, mock_logging, mock_factory):
        mock_mcp = MagicMock()
        mock_factory.return_value = mock_mcp

        main()

        mock_factory.assert_called()
        mock_mcp.run.assert_called()

    @patch.object(main_server, "mcp_factory")
    @patch.object(main_server, "setup_clean_logging")
    def test_main_keyboard_interrupt(self, mock_logging, mock_factory):
        mock_mcp = MagicMock()
        mock_mcp.run.side_effect = KeyboardInterrupt
        mock_factory.return_value = mock_mcp

        main()

        mock_mcp.run.assert_called()

    @patch.object(main_server, "mcp_factory")
    @patch.object(main_server, "setup_clean_logging")
    def test_main_error(self, mock_logging, mock_factory):
        mock_mcp = MagicMock()
        mock_mcp.run.side_effect = ValueError("Fatal error")
        mock_factory.return_value = mock_mcp

        with self.assertRaises(ValueError):
            main()

    def test_get_packages_for_delivery_guy_error(self):
        mcp_factory("test_app")
        tool = self.tools["get_packages_for_delivery_guy"]

        self.mock_db.get_packages_for_delivery_guy.side_effect = Exception("DB Error")

        result = tool(1)
        self.assertIn("Error: DB Error", result)

    def test_get_package_details_error(self):
        mcp_factory("test_app")
        tool = self.tools["get_package_details"]

        self.mock_db.get_package_details.side_effect = Exception("DB Error")

        result = tool("PKG001")
        self.assertIn("Error: DB Error", result)

    def test_get_delivery_guy_stats_error(self):
        mcp_factory("test_app")
        tool = self.tools["get_delivery_guy_stats"]
        self.mock_db.get_delivery_guy_stats.side_effect = Exception("DB Error")
        result = tool(1)
        self.assertIn("Error: DB Error", result)

    def test_get_all_delivery_guys_error(self):
        mcp_factory("test_app")
        tool = self.tools["get_all_delivery_guys"]
        self.mock_db.get_all_delivery_guys.side_effect = Exception("DB Error")
        result = tool()
        self.assertIn("Error: DB Error", result)

    def test_search_packages_by_label_error(self):
        mcp_factory("test_app")
        tool = self.tools["search_packages_by_label"]

        # Mock db.packages to raise error on iteration
        mock_packages = MagicMock()
        mock_packages.__iter__.side_effect = Exception("DB Error")
        self.mock_db.packages = mock_packages

        result = tool("FRAGILE")
        self.assertIn("Error: DB Error", result)

    def test_update_package_state_error(self):
        mcp_factory("test_app")
        tool = self.tools["update_package_state"]
        self.mock_db.get_package_details.side_effect = Exception("DB Error")
        result = tool("P1", "delivered")
        self.assertIn("Error: DB Error", result)

    def test_add_new_package_error(self):
        mcp_factory("test_app")
        tool = self.tools["add_new_package"]

        # Make db.packages.append raise error
        self.mock_db.packages = MagicMock()
        self.mock_db.packages.append.side_effect = Exception("DB Error")

        result = tool({})
        self.assertIn("Error: DB Error", result)

    def test_delete_package_error(self):
        mcp_factory("test_app")
        tool = self.tools["delete_package"]
        self.mock_db.get_package_details.side_effect = Exception("DB Error")
        result = tool("P1")
        self.assertIn("Error: DB Error", result)

    def test_delete_packages_error(self):
        mcp_factory("test_app")
        tool = self.tools["delete_packages"]
        self.mock_db.get_package_details.side_effect = Exception("DB Error")
        result = tool(["P1"])
        self.assertIn("Error: DB Error", result)

    def test_get_packages_by_state_error(self):
        mcp_factory("test_app")
        tool = self.tools["get_packages_by_state"]

        # Mock db.packages to raise error on iteration
        mock_packages = MagicMock()
        mock_packages.__iter__.side_effect = Exception("DB Error")
        self.mock_db.packages = mock_packages

        result = tool("pending")
        self.assertIn("Error: DB Error", result)

    def test_update_package_state_not_found(self):
        mcp_factory("test_app")
        tool = self.tools["update_package_state"]
        self.mock_db.get_package_details.return_value = None
        result = tool("P1", "delivered")
        self.assertIn("Package P1 not found", result)

    @patch.object(main_server, "mcp_factory")
    @patch.object(main_server, "setup_clean_logging")
    def test_main_closed_resource_error(self, mock_logging, mock_factory):
        mock_mcp = MagicMock()
        mock_mcp.run.side_effect = Exception("ClosedResourceError: connection closed")
        mock_factory.return_value = mock_mcp

        main()
        # Should not raise exception


class TestLogging(unittest.TestCase):
    def test_setup_clean_logging_error(self):
        # Mock logging.Formatter to return a mock on first call, and raise on second
        mock_formatter = MagicMock()
        with patch("logging.Formatter", side_effect=[mock_formatter, KeyError("Config Error")]):
            setup_clean_logging()


if __name__ == "__main__":
    unittest.main()
