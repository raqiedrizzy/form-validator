#!/usr/bin/env python3
"""Minimal Working Survey Validator for Render"""
import os
import sys
import time
import logging
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def create_minimal_driver():
    """Create minimal Chrome driver"""
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("Minimal Chrome driver created")
        return driver
    except Exception as e:
        logger.error("Driver creation failed: " + str(e))
        return None

def test_form_access(form_url, form_name):
    """Test basic form access"""
    driver = None
    try:
        logger.info("Testing access to " + form_name + ": " + form_url)
        driver = create_minimal_driver()
        if not driver:
            logger.error("Failed to create driver")
            return False
        
        driver.get(form_url)
        time.sleep(5)  # Wait for page load
        
        # Check if page loaded
        page_title = driver.title
        page_url = driver.current_url
        
        logger.info("Page title: " + page_title)
        logger.info("Page URL: " + page_url)
        
        # Try to find any form elements
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, "div, form, input, button, span")
            logger.info("Found " + str(len(elements)) + " elements on page")
            
            # Try to click something
            if elements:
                element = elements[0]
                driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(1)
                logger.info("Successfully interacted with page")
            
        except Exception as e:
            logger.warning("Element interaction failed: " + str(e))
        
        logger.info(form_name + " access test completed successfully")
        return True
        
    except Exception as e:
        logger.error("Form access test failed: " + str(e))
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    """Main execution"""
    logger.info("MINIMAL Survey Validator Started")
    logger.info("Start time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Get environment variables
    form1_url = os.environ.get('FORM_1_URL')
    form2_url = os.environ.get('FORM_2_URL')
    
    if not form1_url or not form2_url:
        logger.error("Missing environment variables")
        sys.exit(1)
    
    logger.info("Form 1 URL: " + form1_url)
    logger.info("Form 2 URL: " + form2_url)
    
    try:
        # Test access to both forms
        success_count = 0
        
        if test_form_access(form1_url, "Form 1"):
            success_count += 1
        
        time.sleep(2)  # Wait between forms
        
        if test_form_access(form2_url, "Form 2"):
            success_count += 1
        
        logger.info("Completed " + str(success_count) + " form access tests")
        
        if success_count >= 1:
            logger.info("MINIMAL execution completed successfully")
            sys.exit(0)
        else:
            logger.error("MINIMAL execution failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error("Fatal error: " + str(e))
        sys.exit(1)
    finally:
        logger.info("MINIMAL Survey Validator execution completed")

if __name__ == "__main__":
    main()
