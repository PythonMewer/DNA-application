import sys
from datetime import datetime

import json
from meter_data import badges  # Import badges from the separate data file


# Validate input data
def validate_data(badge, install_date, service_point, dma, postcode, alert_present, alert_type):
    errors = []

    # Badge validation
    if not isinstance(badge, str) or len(badge) not in [10, 12]:
        # Handle the invalid badge case
        errors.append("Itron meters consist of 10 digits and Sensus are 12.")

    # Check for duplicate badge
    existing_badges = [existing_badge['Badge'] for existing_badge in badges]
    if badge in existing_badges:
        errors.append(f"Badge {badge} already exists.")

    # Install Date validation
    try:
        install_date_obj = datetime.strptime(install_date, "%d/%m/%Y")
        if install_date_obj > datetime.now():
            errors.append("Install Date cannot be in the future.")
    except ValueError:
        errors.append("Invalid Install Date format.")

    # Service Point validation
    if not isinstance(service_point, (str, int)) or len(str(service_point)) != 10:
        errors.append("Service Point must be a valid ten-digit integer or string.")

    # DMA validation
    if not isinstance(dma, float) or not (38.0 <= dma <= 90.0):
        errors.append("DMA must be a float between 38.0 and 90.0.")

    # Postcode validation
    if not isinstance(postcode, str) or not postcode.startswith(("NR", "IP", "CM")):
        errors.append("Invalid Postcode format (must start with NR, IP, or CM).")

    # Alert Present validation
    if alert_present not in ["Y", "N"]:
        errors.append("Alert Present must be 'Y' or 'N'.")

    # Alert Type validation
    if alert_present == "Y" and not alert_type:
        errors.append("Alert Type must be provided if Alert Present is 'Y'.")

    return errors


# Process badge alert
def process_badge(badge, alert_present, alert_type, under_investigation, sr_code):
    result = {
        "Badge": badge,
        "Under Investigation": under_investigation,
        "SR Code": sr_code,
        "Alert Present": alert_present,
        "Alert Type": alert_type,
    }

    if under_investigation:
        result["Message"] = f"Badge {badge}: Under investigation (SR Code: {sr_code})."
        return result

    if alert_present == 'Y':
        if alert_type == "Leakage":
            result["Message"] = f"Badge {badge}: Immediate action required for leakage."
        elif alert_type == "No consumption":
            result["Message"] = f"Badge {badge}: Investigate no consumption issue."
        elif alert_type == "High consumption":
            result["Message"] = f"Badge {badge}: Investigate high consumption alert."
        elif alert_type == "Low battery":
            result["Message"] = f"Badge {badge}: Battery needs replacement."
        else:
            result["Message"] = f"Badge {badge}: Alert present but type not recognised."
    else:
        result["Message"] = f"Badge {badge}: No alerts present, no action needed."

    return result


# Display alerts for badges
def display_alerts():
    for badge_info in badges:
        result = process_badge(badge_info['Badge'], badge_info['Alert present'],
                               badge_info['Alert Type'], badge_info['Under Investigation'], badge_info['SR Code'])
        print(result)


# Generate reports (dummy report function)
def generate_reports():
    print("Generating report...")
    print("Report generated successfully.")


# Manage alerts (Display or update alerts or add new badge)
def manage_alerts():
    print("1. Check for existing alerts")
    print("2. Update an existing alert")
    print("3. Add a new badge")
    choice = input("Enter your choice: ")

    if choice == '1':
        existing_alerts()
    elif choice == '2':
        update_alert()
    elif choice == '3':
        add_new_badge()
    else:
        print("Invalid option selected.")


# Existing alerts (Display or create service request)
def existing_alerts():
    badge_to_check = input("Enter badge to manage: ")
    for badge in badges:
        if badge["Badge"] == badge_to_check:
            if badge["Alert present"] == "Y":
                print(f"Alert found for badge {badge_to_check}.")
                create_service_request(badge)
            else:
                print(f"No alerts for badge {badge_to_check}.")
            return
    print(f"Badge {badge_to_check} not found.")


# Update an existing badge alert
def update_alert():
    badge_to_check = input("Enter badge to update: ")
    for badge in badges:
        if badge["Badge"] == badge_to_check:
            if badge["Alert present"] == "Y":
                print(f"Updating alert for Badge {badge_to_check}.")
                badge["Alert present"] = "N"
                badge["Alert Type"] = ""
                badge["Under Investigation"] = False
                badge["SR Code"] = ""
                print(f"Badge {badge_to_check} alert cleared (Alert present set to 'N', Alert Type cleared).")
            else:
                print(f"No active alerts for Badge {badge_to_check}.")
            return
    print(f"Badge {badge_to_check} not found.")


# Add a new badge
def add_new_badge():
    print("Add new badge details:")
    new_badge = {}
    new_badge["Badge"] = input("Enter Badge ID: ")
    new_badge["Install Date"] = input("Enter Install Date (DD/MM/YYYY): ")
    new_badge["Service Point"] = input("Enter Service Point: ")
    new_badge["DMA"] = float(input("Enter DMA: "))
    new_badge["Postcode"] = input("Enter Postcode: ")
    new_badge["Region"] = input("Enter Region: ")
    new_badge["Alert present"] = input("Is Alert present? (Y/N): ")
    new_badge["Alert Type"] = input("Enter Alert Type (Leave blank if none): ")
    new_badge["Under Investigation"] = False
    new_badge["SR Code"] = ""

    # Validate the new badge data
    errors = validate_data(new_badge["Badge"], new_badge["Install Date"], new_badge["Service Point"],
                           new_badge["DMA"], new_badge["Postcode"], new_badge["Alert present"], new_badge["Alert Type"])
    if errors:
        print(f"Errors found: {', '.join(errors)}")
    else:
        # Append the new badge to the list
        badges.append(new_badge)
        print(f"New badge {new_badge['Badge']} added successfully!")

        # Update the meter_data.py file with the new badge
        update_data_file(badges)


def update_data_file(badges):
    try:
        # Convert the badges list into a string of valid Python code
        badges_data = json.dumps(badges, indent=4)

        # Replace JSON's true/false with Python's True/False
        badges_data = badges_data.replace("true", "True").replace("false", "False")

        # Format the data as a Python assignment statement
        badges_data = f"badges = {badges_data}"

        # Write the new data to the data.py file
        with open('meter_data.py', 'w') as f:
            f.write(badges_data)

        print("Data file updated successfully.")
    except Exception as e:
        print(f"Error updating the data file: {e}")


# Create service request based on alert type and update badge with SR code
def create_service_request(badge):
    service_request_mapping = {
        "Leakage": "LKTC",
        "High consumption": "HCN-LT",
        "No consumption": "SMIN",
        "Low battery": "SMRP"
    }

    alert_type = badge["Alert Type"]
    sr_code = service_request_mapping.get(alert_type, "No service request")

    badge["Under Investigation"] = True
    badge["SR Code"] = sr_code

    print(f"Created Service Request for Badge {badge['Badge']} in {badge['Region']}: {alert_type} (SR Code: {sr_code})")


# Exit the program
def exit_program():
    print("Exiting program...")
    sys.exit()


# Main User Interface
def user_interface():
    while True:
        print("\n*** Dashboard ***")
        print("1. Display Alerts")
        print("2. Generate Reports")
        print("3. Manage Alerts")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            display_alerts()
        elif choice == '2':
            generate_reports()
        elif choice == '3':
            manage_alerts()
        elif choice == '4':
            exit_program()
        else:
            print("Invalid choice. Please try again.")


# Only run the user interface if this script is run directly
if __name__ == "__main__":
    user_interface()
