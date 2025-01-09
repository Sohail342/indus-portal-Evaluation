from django.shortcuts import render
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from urllib.parse import urlparse, parse_qs
import time

driver = None

def home(request):
    if request.method == 'POST':
        Username = request.POST.get('username')
        Password = request.POST.get('password')
        Options = request.POST.get('options')

        driver = webdriver.Chrome()

        try:
            # Open the login page
            driver.get("http://lms.induscms.com:81/ords/r/erasoft/student-app1400450/login")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "P9999_USERNAME")))

            # Login
            driver.find_element(By.ID, "P9999_USERNAME").send_keys(str(Username))
            driver.find_element(By.ID, "P9999_PASSWORD").send_keys(str(Password))
            driver.find_element(By.ID, "B325920686219386643").click()
            print("Logged in successfully!")

            # Wait for URL to load
            WebDriverWait(driver, 10).until(lambda d: "session" in d.current_url)

            # Extract session ID
            current_url = driver.current_url
            session_id = parse_qs(urlparse(current_url).query).get("session", [None])[0]
            if not session_id:
                raise Exception("Session ID not found in the URL.")

            print("Extracted Session ID:", session_id)

            # Navigate to QEC Proforma
            driver.get(f"http://lms.induscms.com:81/ords/r/erasoft/student-app1400450/qec-evaluation?session={session_id}")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "P40_CHOICE")))

            # Select options from dropdown
            dropdown = Select(driver.find_element(By.ID, "P40_CHOICE"))
            options = [str(Options), "CE", "GS", "AS"]
            
            def fill_evaluation():
                
                # flag for checking if "Go for Evaluation" is found
                go_for_evaluation_found = False
                flag = True
            

                evaluated_items = []  # List to store evaluated items

                for option in options:
                    dropdown.select_by_value(option)
                    print(f"Selected option: {option}")
                    time.sleep(2)

                    try:
                        while flag:
                            # Wait for the table rows to load
                            rows = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.XPATH, "//table[@class='t-Report-report']//tbody/tr"))
                            )

                            # Iterate over rows and locate the "Go for Evaluation" links
                            for index, row in enumerate(rows):
                                try:
                                    # Refresh the table row to prevent stale element exception
                                    row = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, f"(//table[@class='t-Report-report']//tbody/tr)[{index + 1}]"))
                                    )
                                    

                                    # Locate the "Go for Evaluation" link in the current row
                                    link_element = row.find_element(By.XPATH, ".//td[@headers='START_EVALUATION_000']/a")

                                    from icecream import ic
                                    ic("Outside if")
                                    # Check if the link is visible and contains the desired text
                                    if link_element.is_displayed() and "Go for Evaluation" in link_element.text:
                                        go_for_evaluation_found = True
                                        link_element.click()

                                        # Wait for the evaluation page to load and perform actions
                                        time.sleep(2)
                                        
                                        try: 
                                            # Try to locate the "Start Evaluation" button
                                            start_evaluation_button = driver.find_element(By.ID, "B323259646833575587")
                                            
                                            # Check if the button is displayed
                                            if start_evaluation_button.is_displayed():
                                                # Click the button if it is visible
                                                start_evaluation_button.click()
                                                print("Clicked on 'Start Evaluation'")
                                            else:
                                                print("'Start Evaluation' button is not visible")

                                        except Exception as e:
                                            # Handle the case where the button is not found
                                            print("Start Evaluation button not found or an error occurred:", e)
                                            
                                            
                                        # Example of performing actions on the evaluation page
                                        # This can include filling in fields, selecting options, or submitting
                                        # Find all the radio buttons on the page
                                        radio_buttons = driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')

                                        # Loop through all radio buttons and click the first one for each group
                                        for radio_button in radio_buttons:
                                            if not radio_button.is_selected():  # Check if the radio button is not selected
                                                radio_button.click() 
                                                
                                                
                                        
                                        # Find all the text areas (text fields) on the page
                                        text_fields = driver.find_elements(By.TAG_NAME, "textarea")

                                        # Loop through each text field and fill it with "Good"
                                        for text_field in text_fields:
                                            text_field.clear()  # Clear any existing text
                                            text_field.send_keys("Good")  # Fill the text field with "Good"
                                            
                                            
                                        # Find the submit button and click it
                                        # Locate the button using XPATH
                                        submit_button = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 't-Button--hot') and contains(@onclick, 'apex.submit')]"))
                                        )

                                        # Click the button
                                        submit_button.click()

                                        

                                        # Add evaluated item to the list
                                        evaluated_items.append(f"Evaluated item from {option} option")

                                        time.sleep(3)  # Wait for the page to load
                                        # Navigate back to the original page
                                        driver.get(f"http://lms.induscms.com:81/ords/r/erasoft/student-app1400450/qec-evaluation?session={session_id}")

                                        # Wait for the original page to reload
                                        WebDriverWait(driver, 10).until(
                                            EC.presence_of_element_located((By.XPATH, "//table[@class='t-Report-report']//tbody/tr"))
                                        )

                                        # Break the loop to avoid reprocessing rows
                                        

                                except Exception as e:
                                    print(f"Error processing row {index + 1}: {e}")
                            # Break the loop to avoid reprocessing rows
                            if go_for_evaluation_found == False:
                                from icecream import ic
                                ic("No evaluation link found in this row, moving to next option.")
                                flag = False
                                            
                        

                    except Exception as e:
                        print("Error locating table rows:", e)              
                            
                    
                    if go_for_evaluation_found == False:
                        from icecream import ic
                        ic("continue")
                        driver.get(f"http://lms.induscms.com:81/ords/r/erasoft/student-app1400450/home?session={session_id}")
                        flag = True
                        options.pop(0)
                        fill_evaluation()
                        # continue

                # Print out the evaluated items after completing the process
                print("Evaluated Items:", evaluated_items)
                
            fill_evaluation()
        except Exception as e:
            print("Error:", e)

        finally:
            driver.quit()
    return render(request, 'core/home.html')
            
