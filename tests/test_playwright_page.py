from selenium.webdriver.common.by import By

def test_playwright_page(driver):
    driver.get("https://playwright.dev/")
    try:
        driver.find_element(By.TAG_NAME, "h1")
        # print(f"myElement: {myElement}")
    except:
        print("Got NoSuchElementException")

    
    myElements = driver.find_elements(By.TAG_NAME, "h1")
    print(f"myElements: {myElements}")