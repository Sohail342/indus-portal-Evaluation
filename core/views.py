from django.shortcuts import render
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs
import time


def home(request):
    if request.method == 'POST':
        Username = request.POST.get('username')
        Password = request.POST.get('password')
        Options = request.POST.get('options')

        # Start Playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            try:
                # Open the login page
                page.goto("http://lms.induscms.com:81/ords/r/erasoft/student-app1400450/login")
                page.wait_for_selector("#P9999_USERNAME", timeout=30000)

                # Login
                if Username and Password:
                    page.fill("#P9999_USERNAME", str(Username))
                    page.fill("#P9999_PASSWORD", str(Password))
                    page.click("#B325920686219386643")
                    print("Logged in successfully!")

                # Wait for the page to load completely
                page.wait_for_load_state("networkidle", timeout=30000)

                # Extract session ID from the current URL
                current_url = page.url
                print("Current URL after login:", current_url)

                # Check if the session ID is present in the URL
                if "session=" not in current_url:
                    raise Exception("Session ID not found in the URL.")

                session_id = parse_qs(urlparse(current_url).query).get("session", [None])[0]
                if not session_id:
                    raise Exception("Session ID not found in the URL.")
                print("Extracted Session ID:", session_id)

                # Navigate to QEC Proforma
                page.goto(f"http://lms.induscms.com:81/ords/r/erasoft/student-app1400450/qec-evaluation?session={session_id}")
                page.wait_for_selector("#P40_CHOICE", timeout=30000)

                # Select options from dropdown
                ''' Course Evaluation, Teacher Evaluation'''
                options = ['TE', "CE"]
                evaluated_items = []

                for option in options:
                    dropdown = page.locator("#P40_CHOICE")
                    dropdown.select_option(value=option)
                    print(f"Selected option: {option}")

                    # Wait for the page to reload after selecting the dropdown option
                    page.wait_for_load_state("networkidle", timeout=30000)

                    # Re-locate the rows after the page reloads
                    rows = page.locator("//table[@class='t-Report-report']//tbody/tr")
                    row_count = rows.count()
                    print(f"Number of rows found: {row_count}")

                    for i in range(row_count):
                        row = rows.nth(i)

                        try:
                            # Locate "Go for Evaluation" link
                            link_element = row.locator(".//td[@headers='START_EVALUATION_000']/a")

                            if link_element.is_visible() and "Go for Evaluation" in link_element.inner_text():
                                link_element.click()
                                print("Navigated to evaluation page.")

                                # Wait for the evaluation page to load
                                page.wait_for_selector("#B323259646833575587", timeout=30000)

                                # Start Evaluation
                                start_button = page.locator("#B323259646833575587")
                                if start_button.is_visible():
                                    start_button.click()
                                    print("Clicked 'Start Evaluation'")

                                # Fill radio buttons
                                radio_buttons = page.locator("input[type='radio']")
                                for j in range(radio_buttons.count()):
                                    button = radio_buttons.nth(j)
                                    if not button.is_checked():
                                        button.check()

                                # Fill text fields
                                text_fields = page.locator("textarea")
                                for j in range(text_fields.count()):
                                    text_fields.nth(j).fill("Good")

                                # Submit the form
                                submit_button = page.locator("//button[contains(@class, 't-Button--hot') and contains(@onclick, 'apex.submit')]")
                                submit_button.click()
                                print(f"Evaluation submitted for option {option}.")

                                # Append evaluated items
                                evaluated_items.append(f"Evaluated item from {option} option")

                                # Navigate back to the main page
                                page.goto(f"http://lms.induscms.com:81/ords/r/erasoft/student-app1400450/qec-evaluation?session={session_id}")
                                page.wait_for_selector("//table[@class='t-Report-report']//tbody/tr", timeout=30000)

                        except Exception as e:
                            print(f"Error processing row {i + 1}: {e}")

                # Print the evaluated items
                print("Evaluated Items:", evaluated_items)

            except Exception as e:
                print("Error:", e)
                # Debugging: Print page content or take a screenshot
                print(page.content())
                page.screenshot(path="error_screenshot.png")

            finally:
                browser.close()

    return render(request, 'core/home.html')