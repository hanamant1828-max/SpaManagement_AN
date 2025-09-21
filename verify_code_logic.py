
"""
Verify the break time logic implementation
"""
import re

def analyze_break_time_logic():
    """Analyze the break time logic in bookings_views.py"""
    print("🔍 Analyzing Break Time Logic Implementation")
    print("=" * 50)
    
    try:
        with open('modules/bookings/bookings_views.py', 'r') as f:
            content = f.read()
        
        print("✅ Successfully loaded bookings_views.py")
        
        # Check for the staff_availability function
        if 'def staff_availability():' in content:
            print("✅ staff_availability function found")
            
            # Extract the function
            func_start = content.find('def staff_availability():')
            # Find the next function definition to get the end
            next_func = content.find('\n@app.route', func_start + 1)
            if next_func == -1:
                next_func = content.find('\ndef ', func_start + 1)
            
            if next_func != -1:
                function_code = content[func_start:next_func]
            else:
                function_code = content[func_start:]
            
            print(f"📊 Function length: {len(function_code)} characters")
            
            # Check for break time logic patterns
            break_checks = {
                "Break time check exists": "break_start and break_end" in function_code,
                "Break time comparison": "break_start <= slot_time < break_end" in function_code,
                "Break status set": '"status": "break"' in function_code,
                "Break Time display": '"Break Time"' in function_code,
                "Continue statement after break": "continue" in function_code,
                "Break logic before booking check": self.check_break_before_booking(function_code)
            }
            
            print("\n🔍 Break Time Logic Checks:")
            for check_name, result in break_checks.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check_name}")
            
            # Show the critical break time section
            break_section_start = function_code.find("# Check if time slot is during break time")
            if break_section_start != -1:
                break_section_end = function_code.find("# Check if this time slot is booked", break_section_start)
                if break_section_end != -1:
                    break_section = function_code[break_section_start:break_section_end]
                    print("\n📋 Break Time Logic Section:")
                    print("-" * 40)
                    print(break_section.strip())
                    print("-" * 40)
            
            return all(break_checks.values())
            
        else:
            print("❌ staff_availability function not found")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing code: {e}")
        return False

def check_break_before_booking(self, code):
    """Check if break time logic comes before booking logic"""
    break_pos = code.find("# Check if time slot is during break time")
    booking_pos = code.find("# Check if this time slot is booked")
    
    if break_pos != -1 and booking_pos != -1:
        return break_pos < booking_pos
    return False

def check_template_logic():
    """Check the template logic for break time display"""
    print("\n🎨 Analyzing Template Logic...")
    
    try:
        with open('templates/staff_availability.html', 'r') as f:
            template_content = f.read()
        
        print("✅ Successfully loaded staff_availability.html")
        
        # Check for break time handling in template
        template_checks = {
            "Break status check": "availability.status == 'break'" in template_content,
            "Break Time display text": "Break Time" in template_content,
            "Warning background": "bg-warning" in template_content,
            "Coffee icon": "fas fa-coffee" in template_content,
            "Break time tooltip": "availability.reason" in template_content
        }
        
        print("\n🔍 Template Break Time Checks:")
        for check_name, result in template_checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
        
        return all(template_checks.values())
        
    except Exception as e:
        print(f"❌ Error analyzing template: {e}")
        return False

def main():
    """Run all code verification checks"""
    print("🧪 Break Time Code Logic Verification")
    print("=" * 50)
    
    logic_ok = analyze_break_time_logic()
    template_ok = check_template_logic()
    
    print("\n📊 Verification Summary:")
    print(f"  Backend Logic: {'✅ PASS' if logic_ok else '❌ FAIL'}")
    print(f"  Template Logic: {'✅ PASS' if template_ok else '❌ FAIL'}")
    
    if logic_ok and template_ok:
        print("\n🎉 Code verification passed! The fix should be working.")
    else:
        print("\n⚠️  Code verification found issues. Manual review needed.")
    
    print("\n🎯 Next Steps:")
    print("1. Run the complete test: python complete_break_test.py")
    print("2. Check the staff availability page manually")
    print("3. Verify break times are displayed correctly")

if __name__ == "__main__":
    main()
