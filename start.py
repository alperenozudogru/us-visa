import time
import pickle
import requests
import schedule
import re
import locale
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from config import USER_EMAIL, USER_PASSWORD, TELEGRAM_TOKEN, CHAT_IDS, APPOINTMENT_ID, IS_GROUP

# Setup WebDriver
def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--detach")
    # chrome_options.add_argument("--enable-features=WebContentsForceDark")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Log in to the system
def login(driver):
    driver.get("https://ais.usvisa-info.com/en-tr/niv/users/sign_in")
    # check user_email and user_password fields are created
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user_email")))
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

def get_appointment_date(driver):
    try:
        print("DateTime Now: ", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        driver.get(f"https://ais.usvisa-info.com/en-tr/niv/account")
        # Check if <li role="menuitem"><a class="button primary small" href="/tr-tr/niv/schedule/60933952/continue_actions">Devam Et</a></li> clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@role='menuitem']//a[@class='button primary small']")))

        # Locate the <p> element with the class 'consular-appt'
        consular_appt_element = driver.find_element(By.CSS_SELECTOR, "p.consular-appt")

        # Extract the text content
        consular_appt_text = consular_appt_element.text
        # Use a regular expression to extract the date
        date_match = re.search(r'(\d{1,2} \w+, \d{4})', consular_appt_text)
        if date_match:
            appointment_date_str = date_match.group(1)
            # Parse the extracted date string to a datetime object
            appointment_date = datetime.strptime(appointment_date_str, "%d %B, %Y")
            print(f"Current Appointment Date: {appointment_date.strftime('%d-%m-%Y')}")
        else:
            print("No date found in the consular appointment text.")
        return appointment_date
    except Exception as e:
        raise Exception(f"Failed to get appointment date: {e}")

# Send a Telegram message
def telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    return response.json()

# Find the first available day for the appointment
def find_first_available_day(driver, appointment_date: datetime):
    try:
        driver.get(f"https://ais.usvisa-info.com/en-tr/niv/schedule/{APPOINTMENT_ID}/appointment")
        
        # if you are receiving the appointment limit message, you can use the following line otherwise you can use the above line
        # driver.get(f"https://ais.usvisa-info.com/en-tr/niv/schedule/{APPOINTMENT_ID}/appointment?confirmed_limit_message=1&commit=Continue")
        #time.sleep(1)

        if IS_GROUP == "True":
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'commit')))
            group_commit = driver.find_element(By.NAME, 'commit')
            group_commit.click()

        # check if appointments_consulate_appointment_date is clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'appointments_consulate_appointment_date')))

        date_picker = driver.find_element(By.ID, 'appointments_consulate_appointment_date')
        # Wait for the date picker to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'appointments_consulate_appointment_date')))
        date_picker.click()

        # Check available dates
        while True:
            available_days = driver.find_elements(By.XPATH, "//td[not(contains(@class, 'ui-state-disabled'))]//a")
            if available_days:
                available_days[0].click()  # Select the first available date
                clicked_date = driver.find_element(By.ID, 'appointments_consulate_appointment_date').get_attribute('value') ## yyyy-mm-dd formatında

                selected_date = datetime.strptime(clicked_date, "%Y-%m-%d")
                current_day_diff_rate = (appointment_date - datetime.now()).days / 5
                appointment_day_diff = (appointment_date - selected_date).days
                selected_date_current_date_diff = (selected_date - datetime.now()).days

                print(f"Selected date: {selected_date.strftime('%d-%m-%Y')}")
                print(f"selected_date_current_date_diff: {selected_date_current_date_diff}")

                if(current_day_diff_rate > appointment_day_diff and selected_date_current_date_diff > 1):
                    print("No earlier date available, waiting next call...")
                    print("")
                    break

                time.sleep(1)
                # Wait for the time dropdown to be present
                time_dropdown = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'appointments_consulate_appointment_time'))
                )

                # Select an available time
                select = Select(time_dropdown)

                # Wait until the select element has more than one option
                WebDriverWait(driver, 10).until(lambda d: len(select.options) > 1)

                # Check if there are enough options
                if len(select.options) > 1:
                    select.select_by_index(1)  # Skip the first index as it's usually empty
                    selected_time = select.first_selected_option.text

                    print(f"Selected date time: {selected_date.strftime('%d-%m-%Y')} Time: {selected_time}")
                    
                    message = f"{USER_EMAIL} Available date found and taken: {selected_date.strftime('%d-%m-%Y')} Time: {selected_time}"
                    print(message)
                    submit = driver.find_element(By.ID, 'appointments_submit')
                    submit.click()
                    time.sleep(1)
                    
                    # Click the "Confirm" button in the confirmation modal
                    confirm_button = driver.find_element(By.XPATH, "//a[@class='button alert' and text()='Confirm']")
                    confirm_button.click()
                    print("Confirmed the appointment")
                    time.sleep(1)

                    # Send message to all specified chat IDs
                    for chat_id in CHAT_IDS:
                        telegram_message(TELEGRAM_TOKEN, chat_id, message)
                        
                    break    
            else:
                # iterating to next month
                next_button = driver.find_element(By.CLASS_NAME, 'ui-datepicker-next')
                next_button.click()
    except Exception as e:
        raise Exception(f"Failed to check for appointments: {e}")

# Main function to run the scheduler
def main():

    try:
        print(f"Starting attempt...")

        # Setup the driver and login
        driver = setup_driver()
        login(driver)
        time.sleep(2)

        # Get the current appointment date
        find_first_available_day(driver, get_appointment_date(driver))

        # run the scheduler every x minute
        schedule.every(4).minutes.do(lambda: find_first_available_day(driver, get_appointment_date(driver)))

        # run the scheduler for 4 hours
        end_time = datetime.now() + timedelta(hours=4)
        while datetime.now() < end_time:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        print(f"Error occurred on main : {e}")
        time.sleep(10)
    finally:
        # quit the driver
        try:
            schedule.clear()
            driver.quit()
        except Exception as e:
            print(f"Failed to close driver: {e}")

        print("Restarting browser and retrying...")
        time.sleep(900)
        main()

if __name__ == "__main__":
    main()
