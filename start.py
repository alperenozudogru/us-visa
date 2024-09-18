import time
import pickle
import requests
import schedule
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from config import USER_EMAIL, USER_PASSWORD, TELEGRAM_TOKEN, CHAT_IDS, THRESHOLD_DATE, DRIVER_PATH, APPOINTMENT_ID

# Setup WebDriver
def setup_driver():
    chrome_options = Options()
    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Log in to the system
def login(driver):
    driver.get("https://ais.usvisa-info.com/tr-tr/niv/users/sign_in")
    time.sleep(1)

    # Enter email and password
    user_email = driver.find_element(By.ID, "user_email")
    user_email.send_keys(USER_EMAIL)

    user_password = driver.find_element(By.ID, "user_password")
    user_password.send_keys(USER_PASSWORD)

    # Confirm the policy agreement and submit
    policy_confirmed = driver.find_element(By.ID, "policy_confirmed")
    driver.execute_script("arguments[0].click();", policy_confirmed)

    submit_button = driver.find_element(By.NAME, "commit")
    driver.execute_script("arguments[0].click();", submit_button)

# Send a Telegram message
def telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    return response.json()

# Find the first available day for the appointment
def find_first_available_day(driver):
    driver.get(f"https://ais.usvisa-info.com/tr-tr/niv/schedule/{APPOINTMENT_ID}/appointment")
    time.sleep(1)

    try:
        date_picker = driver.find_element(By.ID, 'appointments_consulate_appointment_date')
        # Wait for the date picker to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'appointments_consulate_appointment_date')))
        date_picker.click()
        print("DateTime Now: ", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

        # Check available dates
        while True:
            try:
                available_days = driver.find_elements(By.XPATH, "//td[not(contains(@class, 'ui-state-disabled'))]//a")
                if available_days:
                    available_days[0].click()  # Select the first available date
                    selected_date = driver.find_element(By.ID, 'appointments_consulate_appointment_date').get_attribute('value') ## yyyy-mm-dd formatında

                    time.sleep(1)
                    # Select an available time
                    select = Select(driver.find_element(By.ID, 'appointments_consulate_appointment_time'))
                    select.select_by_index(1)  # Skip the first index as it's usually empty
                    selected_time = select.first_selected_option.text

                    # Parse the selected date and compare with threshold
                    full_date = datetime.strptime(selected_date, "%Y-%m-%d")
                    if full_date < datetime.strptime(THRESHOLD_DATE, "%Y-%m-%d"):
                        message = f"Available date found: {full_date.strftime('%d-%m-%Y')} Time: {selected_time}"
                        print(message)

                        # Send message to all specified chat IDs
                        for chat_id in CHAT_IDS:
                            telegram_message(TELEGRAM_TOKEN, chat_id, message)
                    else:
                        print("No earlier date available, waiting next call...")
                    break    
                else:
                    # iterating to next month
                    next_button = driver.find_element(By.CLASS_NAME, 'ui-datepicker-next')
                    next_button.click()

            except Exception as e:
                print(f"Error occurred: {e}")
                break
    except Exception as e:
        print(f"Failed to check for appointments: {e}")

# Main function to run the scheduler
def main():
    print("Starting the scheduler...")
    driver = setup_driver()
    login(driver)
    time.sleep(2)
    find_first_available_day(driver)

    # Schedule to run every 15 minutes
    schedule.every(6).minutes.do(lambda: find_first_available_day(driver))

    # Run the scheduled tasks for 1 hour
    end_time = datetime.now() + timedelta(hours=4)
    while datetime.now() < end_time:
        schedule.run_pending()
        time.sleep(1)  # Avoid busy-waiting

    # Clean up driver
    driver.quit()

if __name__ == "__main__":
    main()