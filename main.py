#!/usr/bin/env python3
"""Render Survey Validator - Stateless Burst Execution"""
import os
import sys
import time
import random
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# Configure logging to stdout for Render Dashboard
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# User-Agent rotator
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
]

class ProxyManager:
    """Proxy management for Render deployment"""
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        
    def fetch_proxies(self):
        """Fetch fresh proxies for burst execution"""
        logger.info("Fetching fresh proxies for burst...")
        try:
            # Multiple proxy sources for resilience
            sources = [
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt'
            ]
            
            all_proxies = []
            for source in sources:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        proxies = [line.strip() for line in response.text.split('\n') if ':' in line.strip()]
                        all_proxies.extend(proxies)
                        logger.info("Found " + str(len(proxies)) + " proxies from " + source)
                except Exception as e:
                    logger.warning("Failed to fetch from " + source + ": " + str(e))
            
            # Test and filter working proxies
            working_proxies = []
            for proxy in all_proxies[:50]:  # Limit to first 50 for testing
                if self.test_proxy(proxy):
                    working_proxies.append(proxy)
                    if len(working_proxies) >= 10:  # Need only 10 working proxies
                        break
            
            self.proxies = working_proxies
            logger.info("Found " + str(len(self.proxies)) + " working proxies")
            return len(self.proxies) > 0
            
        except Exception as e:
            logger.error("Proxy fetch failed: " + str(e))
            return False
    
    def test_proxy(self, proxy):
        """Test proxy connectivity"""
        try:
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_proxy(self):
        """Get next available proxy"""
        if self.proxies:
            self.current_proxy = self.proxies.pop(0)
            return self.current_proxy
        return None

class SurveyValidator:
    """Stateless Survey Validator for Render deployment"""
    def __init__(self):
        self.form1_url = os.environ.get('FORM_1_URL')
        self.form2_url = os.environ.get('FORM_2_URL')
        self.proxy_manager = ProxyManager()
        
        if not self.form1_url or not self.form2_url:
            logger.error("FORM_1_URL and FORM_2_URL environment variables are required")
            sys.exit(1)
    
    def create_driver(self, proxy=None):
        """Create headless Chrome driver with stealth"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument(f'--user-agent={random.choice(USER_AGENTS)}')
        
        if proxy:
            options.add_argument(f'--proxy-server=http://{proxy}')
        
        # CDP stealth commands
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Try to create Chrome driver
            driver = webdriver.Chrome(options=options)
            
            # Execute CDP stealth commands
            try:
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['en-US', 'en']
                        });
                    '''
                })
            except:
                # CDP commands might not work in all environments
                pass
            
            return driver
        except Exception as e:
            logger.error("Driver creation failed: " + str(e))
            # Try with Firefox as fallback
            try:
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                from selenium.webdriver import Firefox
                
                firefox_options = FirefoxOptions()
                firefox_options.add_argument('--headless')
                firefox_options.add_argument('--no-sandbox')
                firefox_options.add_argument('--disable-dev-shm-usage')
                
                if proxy:
                    firefox_options.add_argument(f'--proxy={proxy}')
                
                driver = Firefox(options=firefox_options)
                logger.info("Firefox driver created as fallback")
                return driver
            except Exception as firefox_e:
                logger.error("Firefox fallback also failed: " + str(firefox_e))
                return None
    
    def full_form_audit(self, driver):
        """Full-Form Audit - verify every question has answer"""
        try:
            questions = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem'], div[data-item-id]")
            unanswered = []
            
            for i, question in enumerate(questions):
                try:
                    # Check if question has any selected option
                    options = question.find_elements(By.CSS_SELECTOR, "div[role='radio'], div[role='checkbox'], input[type='radio'], input[type='checkbox']")
                    has_selection = any(opt.get_attribute('aria-checked') == 'true' for opt in options if opt.get_attribute('aria-checked'))
                    
                    # Check text inputs
                    text_inputs = question.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
                    has_text = any(inp.get_attribute('value') for inp in text_inputs)
                    
                    if not has_selection and not has_text:
                        unanswered.append(f"Question {i+1}")
                        
                except Exception as e:
                    logger.warning("Audit error on question " + str(i+1) + ": " + str(e))
            
            if unanswered:
                logger.error("Full-Form Audit FAILED: Unanswered questions: " + ', '.join(unanswered))
                return False
            else:
                logger.info("Full-Form Audit PASSED: All questions answered")
                return True
                
        except Exception as e:
            logger.error("Full-Form Audit error: " + str(e))
            return False
    
    def process_form(self, driver, form_url, form_name):
        """Process single form with full validation"""
        try:
            logger.info("Processing " + form_name + ": " + form_url)
            driver.get(form_url)
            time.sleep(random.uniform(2, 4))
            
            # Wait for form to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem'], div[data-item-id]"))
            )
            
            # Find and answer questions
            questions = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem'], div[data-item-id]")
            logger.info("Found " + str(len(questions)) + " questions")
            
            for i, question in enumerate(questions):
                try:
                    # Find clickable options
                    options = question.find_elements(By.CSS_SELECTOR, "div[role='radio'], div[role='checkbox']")
                    if options:
                        selected = random.choice(options)
                        driver.execute_script("arguments[0].scrollIntoView();", selected)
                        time.sleep(random.uniform(0.5, 1.0))
                        selected.click()
                        logger.info("Answered question " + str(i+1))
                    
                    # Handle text inputs
                    text_inputs = question.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
                    if text_inputs:
                        text_input = text_inputs[0]
                        text_input.clear()
                        text_input.send_keys(random.choice(["20-24", "Mama wa nyumbani", "Miezi 6", "1"]))
                        logger.info("Filled text input for question " + str(i+1))
                        
                except Exception as e:
                    logger.warning("Error answering question " + str(i+1) + ": " + str(e))
            
            # Full-Form Audit before submission
            if not self.full_form_audit(driver):
                logger.error("Form audit failed for " + form_name)
                return False
            
            # Submit form
            submit_buttons = driver.find_elements(By.XPATH, "//span[contains(text(),'Submit') or contains(text(),'Wasilisha')]")
            if submit_buttons:
                submit_buttons[0].click()
                time.sleep(random.uniform(2, 3))
                
                # Verify submission
                if "formResponse" in driver.current_url:
                    logger.info(form_name + " submitted successfully!")
                    return True
                else:
                    logger.error(form_name + " submission verification failed")
                    return False
            else:
                logger.error("No submit button found for " + form_name)
                return False
                
        except Exception as e:
            logger.error("Error processing " + form_name + ": " + str(e))
            return False
    
    def execute_burst(self):
        """Execute 2:1 burst pattern (2 Form 1, 1 Form 2)"""
        logger.info("Starting 2:1 burst execution...")
        
        # Fetch fresh proxies
        if not self.proxy_manager.fetch_proxies():
            logger.error("Failed to fetch proxies, aborting burst")
            return False
        
        burst_pattern = [
            (self.form1_url, "Form 1"),
            (self.form1_url, "Form 1"),
            (self.form2_url, "Form 2")
        ]
        
        successful_submissions = 0
        
        for i, (form_url, form_name) in enumerate(burst_pattern):
            logger.info("Burst submission " + str(i+1) + "/3: " + form_name)
            
            # Get new proxy for each submission
            proxy = self.proxy_manager.get_proxy()
            logger.info("Using proxy: " + str(proxy))
            
            driver = None
            try:
                driver = self.create_driver(proxy)
                if not driver:
                    logger.error("Failed to create driver for " + form_name)
                    continue
                
                if self.process_form(driver, form_url, form_name):
                    successful_submissions += 1
                
                # Randomized pacing between submissions
                if i < len(burst_pattern) - 1:
                    wait_time = random.uniform(300, 600)  # 5-10 minutes
                    logger.info("Waiting " + str(wait_time/60) + " minutes before next submission...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                logger.error("Burst submission " + str(i+1) + " failed: " + str(e))
            finally:
                if driver:
                    driver.quit()
        
        logger.info("Burst completed: " + str(successful_submissions) + "/3 submissions successful")
        return successful_submissions >= 2  # Success if at least 2/3 submissions work

def main():
    """Main execution function"""
    logger.info("Survey Validator Burst Execution Started")
    logger.info("Environment: Render.com - Stateless Mode")
    logger.info("Start time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    try:
        validator = SurveyValidator()
        success = validator.execute_burst()
        
        if success:
            logger.info("Burst execution completed successfully")
            sys.exit(0)
        else:
            logger.error("Burst execution failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error("Fatal error: " + str(e))
        sys.exit(1)
    finally:
        logger.info("Survey Validator execution completed - Ready for next hourly trigger")

if __name__ == "__main__":
    main()
