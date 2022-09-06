from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.selenium.selenium_Setup import getTimeout

def waitAndGetElement(driver, selector, useSelector=True):
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
    timeout = getTimeout()
    if useSelector:
        return WebDriverWait(driver=driver, timeout=timeout, ignored_exceptions=ignored_exceptions) \
            .until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, selector)))
    else:
        return WebDriverWait(driver=driver, timeout=timeout, ignored_exceptions=ignored_exceptions) \
            .until(EC.visibility_of_element_located(
            (By.XPATH, selector)))

def waitForElementToBeGone(driver, selector):
    timeout = getTimeout()
    return WebDriverWait(driver, timeout) \
        .until(EC.invisibility_of_element(
        (By.CSS_SELECTOR, selector)))

def waitAndClickSelector(driver, selector):
    timeout = getTimeout()
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    element.click()

def waitAndClickID(driver, Id):
    timeout = getTimeout()
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.ID, Id)))
    element.click()


def waitAndClickText(driver, text):
    timeout = getTimeout()
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, f"//*[text()='{text}']")))
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()

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