from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.selenium.selenium_Setup import getTimeout



def waitAndGetElement(driver, selector):
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
    timeout = getTimeout()
    return WebDriverWait(driver=driver, timeout=timeout, ignored_exceptions=ignored_exceptions) \
        .until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, selector)))

def waitForElementToBeGone(driver, selector):
    timeout = getTimeout()
    return WebDriverWait(driver, timeout) \
        .until(EC.invisibility_of_element(
        (By.CSS_SELECTOR, selector)))

def waitAndClick(driver, selector):
    timeout = getTimeout()
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    element.click()

def getElementByValue(driver, value):
    timeout = getTimeout()
    return WebDriverWait(driver, timeout) \
        .until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, f"input[value*='{value}']")))

def getListItems(listElement):
    return listElement.find_elements_by_tag_name("li")

def getTableItems(tableElement):
    return tableElement.find_elements_by_tag_name("a")

def getChildItemsByClass(parentElement, className):
    cleanClass = className.replace(" ", ".")
    return parentElement.find_elements_by_class_name(cleanClass)

def getCurrentURL(driver):
    return driver.current_url