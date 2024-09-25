
import pytest
from dna_interface import validate_data, process_badge
from meter_data import badges
from datetime import datetime

# Test validate_data function
@pytest.mark.parametrize("badge, install_date, service_point, dma, postcode, alert_present, alert_type, expected", [
    ("24PA99417050", "01/05/2024", 1234567890, 50.0, "CM7", "Y", "Leak", []),
    ("24PA9", "01/05/2024", 1234567890, 50.0, "CM7", "Y", "Leak", ["Itron meters consist of 10 digits and Sensus are 12."]),
    ("24PA99417050", "01/05/2024", 1234567890, 50.0, "CM7", "Y", "Leak", ["Badge 24PA99417050 already exists."]),
    ("24PA99417050", "32/13/2024", 1234567890, 50.0, "CM7", "Y", "Leak", ["Invalid Install Date format."]),
    ("24PA99417050", "01/05/2030", 1234567890, 50.0, "CM7", "Y", "Leak", ["Install Date cannot be in the future."]),
    ("24PA99417050", "01/05/2024", 12345678, 50.0, "CM7", "Y", "Leak", ["Service Point must be a valid ten-digit integer or string."]),
    ("24PA99417050", "01/05/2024", 1234567890, 100.0, "CM7", "Y", "Leak", ["DMA must be a float between 38.0 and 90.0."]),
    ("24PA99417050", "01/05/2024", 1234567890, 50.0, "AB7", "Y", "Leak", ["Invalid Postcode format (must start with NR, IP, or CM)."]),
    ("24PA99417050", "01/05/2024", 1234567890, 50.0, "CM7", "X", "Leak", ["Alert Present must be 'Y' or 'N'."]),
    ("24PA99417050", "01/05/2024", 1234567890, 50.0, "CM7", "Y", "", ["Alert Type must be provided if Alert Present is 'Y'."]),
])
def test_validate_data(badge, install_date, service_point, dma, postcode, alert_present, alert_type, expected):
    assert validate_data(badge, install_date, service_point, dma, postcode, alert_present, alert_type) == expected


# Test process_badge function
@pytest.mark.parametrize("badge, alert_present, alert_type, under_investigation, sr_code, expected", [
    ("24PA99417050", "Y", "Leak", True, "12345", {"badge": "24PA99417050", "under_investigation": True, "sr_code": "12345"}),
    ("24PA99417050", "N", "", False, "", {"badge": "24PA99417050", "under_investigation": False, "sr_code": ""}),
])
def test_process_badge(badge, alert_present, alert_type, under_investigation, sr_code, expected):
    assert process_badge(badge, alert_present, alert_type, under_investigation, sr_code) == expected


# Test integrity of badge data in meter_data.py
@pytest.mark.parametrize("badge_data", badges)
def test_badge_data_integrity(badge_data):
    # Test valid badge length
    assert len(badge_data["Badge"]) in [10, 12], f"Badge {badge_data['Badge']} has invalid length."
    
    # Test valid DMA
    assert 38.0 <= badge_data["DMA"] <= 90.0, f"Badge {badge_data['Badge']} has an invalid DMA."
    
    # Test valid service point (10 digits)
    assert len(str(badge_data["Service Point"])) == 10, f"Badge {badge_data['Badge']} has an invalid Service Point."
    
    # Test valid install date format
    try:
        datetime.strptime(badge_data["Install Date"], "%d/%m/%Y")
    except ValueError:
        pytest.fail(f"Badge {badge_data['Badge']} has an invalid Install Date format.")
