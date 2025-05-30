from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# ------------------ Page Objects ------------------

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username = (By.NAME, "username")
        self.password = (By.NAME, "password")
        self.login_btn = (By.CSS_SELECTOR, "button[type='submit']")

    def login(self, user, pwd):
        self.driver.find_element(*self.username).send_keys(user)
        self.driver.find_element(*self.password).send_keys(pwd)
        self.driver.find_element(*self.login_btn).click()


class DashboardPage:
    def __init__(self, driver):
        self.driver = driver

        self.pim_menu = (By.XPATH, "//span[text()='PIM']")

    def go_to_pim(self):
        self.driver.find_element(*self.pim_menu).click()

    def logout(self):
        self.driver.find_element(By.CLASS_NAME, "oxd-userdropdown-tab").click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//a[text()='Logout']").click()


class PIMPage:
    def __init__(self, driver):
        self.driver = driver
        

        self.add_employee_btn = (By.XPATH, "//button[text()=' Add ']")
        self.first_name = (By.NAME, "firstName")
        self.last_name = (By.NAME, "lastName")
        self.save_btn = (By.XPATH, "//button[text()=' Save ']")
        self.employee_list_link = (By.XPATH, "//a[text()='Employee List']")

    def add_employee(self, fname, lname):
        self.driver.find_element(*self.add_employee_btn).click()
        time.sleep(1)
        self.driver.find_element(*self.first_name).send_keys(fname)
        self.driver.find_element(*self.last_name).send_keys(lname)
        self.driver.find_element(*self.save_btn).click()
        time.sleep(2)

    def go_to_employee_list(self):
        self.driver.find_element(*self.employee_list_link).click()


class EmployeeListPage:
    def __init__(self, driver):
        self.driver = driver

    def verify_employee(self, full_name):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='rowgroup']/div"))
        )
        rows = self.driver.find_elements(By.XPATH, "//div[@role='rowgroup']/div")
        found = False
        for row in rows:
            if full_name in row.text:
                print(f"{full_name} - Name Verified")
                found = True
                break
        if not found:
            print(f"{full_name} - NOT Found")

# ------------------ Main Test Script ------------------

if __name__ == "__main__":

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(10)
    driver.maximize_window()
    driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")

    try:
        login_page = LoginPage(driver)
        dashboard_page = DashboardPage(driver)
        pim_page = PIMPage(driver)
        employee_list_page = EmployeeListPage(driver)

        # Step 1: Login
        login_page.login("Admin", "admin123")
        time.sleep(2)

        # Step 2: Navigate to PIM
        dashboard_page.go_to_pim()
        time.sleep(2)

        # Step 3: Add Employees
        employees = [
            ("Admin111", "Test"),
            ("Admin112", "Test"),
            ("Admin113", "Test"),
            ("Admin114", "Test")
        ]

        for fname, lname in employees:
            pim_page.add_employee(fname, lname)
            dashboard_page.go_to_pim()

        # Step 4: Go to Employee List and Verify
        pim_page.go_to_employee_list()
        time.sleep(2)
        for fname, lname in employees:
            employee_list_page.verify_employee(f"{fname} {lname}")

        # Step 5: Logout
        dashboard_page.logout()
        time.sleep(2)

    finally:
        driver.quit()