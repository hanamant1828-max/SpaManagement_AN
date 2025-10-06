
#!/usr/bin/env python3
"""
Test script to diagnose face capture initialization issues
This script will help identify exactly where the face capture flow is breaking
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_result(test_name, passed, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"    └─ {message}")

def test_face_capture_flow():
    """Test the complete face capture flow"""
    
    print_section("Starting Face Capture Flow Test")
    
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--use-fake-ui-for-media-stream')  # Auto-allow camera
    options.add_argument('--use-fake-device-for-media-stream')
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    
    try:
        # Step 1: Login
        print_section("Step 1: Login")
        driver.get("http://127.0.0.1:5000/login")
        time.sleep(2)
        
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        time.sleep(2)
        
        print_result("Login successful", "Dashboard" in driver.title or "dashboard" in driver.current_url)
        
        # Step 2: Navigate to Customers page
        print_section("Step 2: Navigate to Customers Page")
        driver.get("http://127.0.0.1:5000/customers")
        time.sleep(2)
        
        print_result("Customers page loaded", "customers" in driver.current_url.lower())
        
        # Step 3: Check if Face Recognition tab exists
        print_section("Step 3: Check Face Recognition Tab")
        try:
            face_tab = driver.find_element(By.CSS_SELECTOR, 'a[href="#face-capture"]')
            print_result("Face Recognition tab found", True, f"Tab text: {face_tab.text}")
        except NoSuchElementException:
            print_result("Face Recognition tab found", False, "Tab not found in DOM")
            return False
        
        # Step 4: Check elements BEFORE clicking tab
        print_section("Step 4: Elements Status BEFORE Tab Click")
        
        elements_before = {
            'faceVideo': None,
            'faceCanvas': None,
            'startFaceCamera': None,
            'captureFacePhoto': None,
            'saveFaceData': None,
            'faceClientSelect': None
        }
        
        for element_id, _ in elements_before.items():
            try:
                element = driver.find_element(By.ID, element_id)
                is_displayed = element.is_displayed()
                elements_before[element_id] = {
                    'exists': True,
                    'displayed': is_displayed,
                    'style_display': element.get_attribute('style')
                }
                print_result(f"Element '{element_id}'", True, 
                           f"Exists: ✓ | Visible: {'✓' if is_displayed else '✗'} | Style: {element.get_attribute('style')}")
            except NoSuchElementException:
                elements_before[element_id] = {'exists': False, 'displayed': False}
                print_result(f"Element '{element_id}'", False, "Not found in DOM")
        
        # Step 5: Click Face Recognition tab
        print_section("Step 5: Click Face Recognition Tab")
        face_tab.click()
        time.sleep(1)  # Wait for tab content to show
        
        print_result("Tab clicked", True)
        
        # Step 6: Check elements AFTER clicking tab
        print_section("Step 6: Elements Status AFTER Tab Click")
        
        elements_after = {
            'faceVideo': None,
            'faceCanvas': None,
            'startFaceCamera': None,
            'captureFacePhoto': None,
            'saveFaceData': None,
            'faceClientSelect': None
        }
        
        for element_id, _ in elements_after.items():
            try:
                element = driver.find_element(By.ID, element_id)
                is_displayed = element.is_displayed()
                elements_after[element_id] = {
                    'exists': True,
                    'displayed': is_displayed,
                    'style_display': element.get_attribute('style')
                }
                print_result(f"Element '{element_id}'", True, 
                           f"Exists: ✓ | Visible: {'✓' if is_displayed else '✗'} | Style: {element.get_attribute('style')}")
            except NoSuchElementException:
                elements_after[element_id] = {'exists': False, 'displayed': False}
                print_result(f"Element '{element_id}'", False, "Not found in DOM")
        
        # Step 7: Check JavaScript console logs
        print_section("Step 7: JavaScript Console Logs")
        
        logs = driver.get_log('browser')
        relevant_logs = [log for log in logs if 'face' in log['message'].lower() or 'camera' in log['message'].lower()]
        
        if relevant_logs:
            for log in relevant_logs[-10:]:  # Show last 10 relevant logs
                print(f"  📝 {log['level']}: {log['message']}")
        else:
            print("  ℹ️ No face/camera related logs found")
        
        # Step 8: Check if initializeFaceCapture was called
        print_section("Step 8: Check Initialization Status")
        
        init_called = driver.execute_script("""
            return window.faceCaptureInitialized || false;
        """)
        
        print_result("Face capture initialization flag", init_called, 
                    "Check if custom flag was set")
        
        # Step 9: Try to check if event listener is attached
        print_section("Step 9: Check Event Listener Status")
        
        try:
            start_btn = driver.find_element(By.ID, 'startFaceCamera')
            has_onclick = start_btn.get_attribute('onclick')
            print_result("Start button has onclick", has_onclick is not None, 
                        f"onclick: {has_onclick}")
        except NoSuchElementException:
            print_result("Start button check", False, "Button not found")
        
        # Step 10: Check tab activation event
        print_section("Step 10: Check Tab Activation")
        
        active_tab = driver.find_element(By.CSS_SELECTOR, '.nav-link.active')
        active_pane = driver.find_element(By.CSS_SELECTOR, '.tab-pane.active')
        
        print_result("Active tab", True, f"Text: {active_tab.text}")
        print_result("Active pane", True, f"ID: {active_pane.get_attribute('id')}")
        
        # Step 11: Inject debug script
        print_section("Step 11: Debug Script Injection")
        
        debug_info = driver.execute_script("""
            const info = {
                videoElement: !!document.getElementById('faceVideo'),
                canvasElement: !!document.getElementById('faceCanvas'),
                startButton: !!document.getElementById('startFaceCamera'),
                startButtonOnclick: document.getElementById('startFaceCamera')?.onclick?.toString() || 'null',
                tabListeners: 0,
                documentListeners: 0
            };
            
            // Count event listeners (approximate)
            const tabLinks = document.querySelectorAll('a[data-bs-toggle="tab"]');
            info.tabListeners = tabLinks.length;
            
            return info;
        """)
        
        print("  Debug Info:")
        for key, value in debug_info.items():
            print(f"    {key}: {value}")
        
        # Step 12: Try clicking Start Camera button
        print_section("Step 12: Test Start Camera Button Click")
        
        try:
            start_btn = driver.find_element(By.ID, 'startFaceCamera')
            
            # Check if button is clickable
            is_enabled = start_btn.is_enabled()
            is_displayed = start_btn.is_displayed()
            
            print_result("Button is enabled", is_enabled)
            print_result("Button is displayed", is_displayed)
            
            if is_enabled and is_displayed:
                # Click the button
                start_btn.click()
                time.sleep(2)
                
                # Check console for errors
                new_logs = driver.get_log('browser')
                error_logs = [log for log in new_logs if log['level'] == 'SEVERE']
                
                if error_logs:
                    print_result("Button click generated errors", False)
                    for log in error_logs[-5:]:
                        print(f"    ⚠️ {log['message']}")
                else:
                    print_result("Button click successful", True, "No errors in console")
            
        except Exception as e:
            print_result("Button click test", False, str(e))
        
        # Step 13: Summary
        print_section("Test Summary")
        
        print("\n🔍 ANALYSIS:")
        print("─" * 60)
        
        if not elements_before['faceVideo']['exists']:
            print("❌ ISSUE: Video element doesn't exist before tab click")
        elif not elements_after['faceVideo']['displayed']:
            print("⚠️ WARNING: Video element exists but not displayed after tab click")
        else:
            print("✅ Video element exists and visible")
        
        if not elements_after['startFaceCamera']['exists']:
            print("❌ ISSUE: Start button doesn't exist")
        elif not start_btn.is_enabled():
            print("⚠️ WARNING: Start button exists but disabled")
        else:
            print("✅ Start button exists and enabled")
        
        if not debug_info['startButtonOnclick'] or debug_info['startButtonOnclick'] == 'null':
            print("❌ ISSUE: Start button has no onclick handler attached")
        else:
            print("✅ Start button has onclick handler")
        
        print("\n💡 RECOMMENDATION:")
        print("─" * 60)
        
        if not debug_info['startButtonOnclick'] or debug_info['startButtonOnclick'] == 'null':
            print("""
The root cause is that the onclick handler is not being attached to
the Start Camera button when the Face Recognition tab is activated.

The initializeFaceCapture() function is listening for the tab activation
event, but it's not properly setting up the button click handler.

Solution: The code needs to ensure that when the 'shown.bs.tab' event
fires for #face-capture, it properly attaches the onclick handler.
            """)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        print_section("Cleanup")
        driver.quit()
        print("✅ Browser closed")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Face Capture Flow Diagnostic Test                    ║
║         Testing Face Recognition Tab Initialization          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    success = test_face_capture_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed successfully")
        sys.exit(0)
    else:
        print("❌ Test failed - check output above for details")
        sys.exit(1)
