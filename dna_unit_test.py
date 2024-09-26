import unittest
from datetime import datetime
from meter_data import badges
from DNA_interface import validate_data, process_badge


class TestDNAInterface(unittest.TestCase):

    def test_validate_data_valid(self):
        badge = "24LU987654"
        install_date = "05/05/2024"
        service_point = "0987654321"
        dma = 50.0
        postcode = "CM7"
        alert_present = "N"
        alert_type = ""

        errors = validate_data(badge, install_date, service_point, dma, postcode, alert_present, alert_type)
        self.assertEqual(errors, [], "Should return no errors for valid data")

    def test_validate_data_invalid_badge(self):
        badge = "1234"
        install_date = "05/05/2024"
        service_point = "0987654321"
        dma = 50.0
        postcode = "CM7"
        alert_present = "N"
        alert_type = ""

        errors = validate_data(badge, install_date, service_point, dma, postcode, alert_present, alert_type)
        self.assertIn("Itron meters consist of 10 digits and Sensus are 12.", errors)

    def test_validate_data_duplicate_badge(self):
        badge = "24PA99417656"  # Badge exists in meter_data.py
        install_date = "05/05/2024"
        service_point = "0987654321"
        dma = 50.0
        postcode = "CM7"
        alert_present = "N"
        alert_type = ""

        errors = validate_data(badge, install_date, service_point, dma, postcode, alert_present, alert_type)
        self.assertIn(f"Badge {badge} already exists.", errors)

    def test_validate_data_future_install_date(self):
        badge = "24LU987654"
        future_date = (datetime.now().replace(year=datetime.now().year + 1)).strftime("%d/%m/%Y")
        service_point = "0987654321"
        dma = 50.0
        postcode = "CM7"
        alert_present = "N"
        alert_type = ""

        errors = validate_data(badge, future_date, service_point, dma, postcode, alert_present, alert_type)
        self.assertIn("Install Date cannot be in the future.", errors)

    def test_validate_data_invalid_service_point(self):
        badge = "24LU987654"
        install_date = "05/05/2024"
        service_point = "12345"  # Invalid service point (less than 10 digits)
        dma = 50.0
        postcode = "CM7"
        alert_present = "N"
        alert_type = ""

        errors = validate_data(badge, install_date, service_point, dma, postcode, alert_present, alert_type)
        self.assertIn("Service Point must be a valid ten-digit integer or string.", errors)

    def test_process_badge_under_investigation(self):
        badge = "24LU987654"
        alert_present = "Y"
        alert_type = "High consumption"
        under_investigation = True
        sr_code = "SR123"

        result = process_badge(badge, alert_present, alert_type, under_investigation, sr_code)
        self.assertEqual(result["Under Investigation"], True)
        self.assertEqual(result["SR Code"], sr_code)

    def test_process_badge_no_investigation_no_alert(self):
        badge = "24LU987654"
        alert_present = "N"
        alert_type = ""
        under_investigation = False
        sr_code = ""

        result = process_badge(badge, alert_present, alert_type, under_investigation, sr_code)
        self.assertEqual(result["Under Investigation"], False)
        self.assertEqual(result["SR Code"], "")

    def test_process_badge_alert_present(self):
        badge = "24LU987654"
        alert_present = "Y"
        alert_type = "High consumption"
        under_investigation = False
        sr_code = "SR987"

        result = process_badge(badge, alert_present, alert_type, under_investigation, sr_code)
        self.assertEqual(result["Under Investigation"], False)
        self.assertEqual(result["Alert Type"], alert_type)


if __name__ == "__main__":
    unittest.main()
