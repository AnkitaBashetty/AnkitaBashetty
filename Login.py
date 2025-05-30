from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import time
import sys
import io

# Fix Unicode error in Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

# ------------------ DB Setup ------------------

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def seed_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    test_users = [
        ("Admin111", "Test"),
        ("Admin112", "Test"),
        ("Admin113", "Test"),
        ("Admin114", "Test")
    ]
    # Avoid inserting duplicates
    for user in test_users:
        cursor.execute("SELECT * FROM users WHERE first_name = ? AND last_name = ?", user)
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users (first_name, last_name) VALUES (?, ?)", user)
    conn.commit()
    conn.close()

def check_user_in_db(first_name, last_name):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE first_name = ? AND last_name = ?
    """, (first_name, last_name))
    result = cursor.fetchone()
    conn.close()
    return result is not None

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

    def verify_employee(self, full_name, fname, lname):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='rowgroup']/div"))
        )
        rows = self.driver.find_elements(By.XPATH, "//div[@role='rowgroup']/div")
        found = False
        for row in rows:
            if full_name in row.text:
                if check_user_in_db(fname, lname):
                    print(f"{full_name} - Found and Verified in DB ✅")
                else:
                    print(f"{full_name} - Found in UI but NOT in DB ❌")
                found = True
                break
        if not found:
            print(f"{full_name} - NOT Found in UI ❌")

# ------------------ Main Test Script ------------------

if __name__ == "__main__":
    init_db()
    seed_users()  # Comment this line if users already exist

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
            time.sleep(1)
            dashboard_page.go_to_pim()  # Re-navigate if needed

        # Step 4: Go to Employee List and Verify
        pim_page.go_to_employee_list()
        time.sleep(2)
        for fname, lname in employees:
            full_name = f"{fname} {lname}"
            employee_list_page.verify_employee(full_name, fname, lname)

        # Step 5: Logout
        dashboard_page.logout()
        time.sleep(2)

    finally:
        driver.quit()
