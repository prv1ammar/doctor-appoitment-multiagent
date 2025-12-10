#!/usr/bin/env python3
"""Test script to verify the updates work correctly."""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_patient_tools():
    """Test patient management tools."""
    print("Testing patient management tools...")
    
    try:
        from toolkit.toolkits import create_patient, get_patient, update_patient, check_patient_id
        
        # Test check_patient_id
        print("1. Testing check_patient_id...")
        result = check_patient_id.func(1)  # Should exist
        print(f"   Result: {result}")
        
        result = check_patient_id.func(999999)  # Should not exist
        print(f"   Result: {result}")
        
        # Test get_patient
        print("\n2. Testing get_patient...")
        result = get_patient.func(1)
        print(f"   Result: {result}")
        
        print("\n✅ Patient tools import and basic execution successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing patient tools: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_availability_tools():
    """Test availability checking tools."""
    print("\nTesting availability tools...")
    
    try:
        from toolkit.toolkits import check_availability_by_doctor, check_availability_by_specialization
        
        # Test with date only (daily availability)
        print("1. Testing check_availability_by_doctor (daily)...")
        result = check_availability_by_doctor.func("04-12-2025", "Dr.Mohamed Tajmouati")
        print(f"   Result: {result[:100]}...")
        
        # Test with specialization
        print("\n2. Testing check_availability_by_specialization...")
        result = check_availability_by_specialization.func("04-12-2025", "Orthodontie")
        print(f"   Result: {result[:100]}...")
        
        print("\n✅ Availability tools import and basic execution successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing availability tools: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_files():
    """Check that data files exist and are readable."""
    print("\nTesting data files...")
    
    data_files = [
        "data/patients.csv",
        "data/doctor_availability.csv",
        "data/doctors.csv",
        "data/rendez_vous.csv"
    ]
    
    all_good = True
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                print(f"✅ {file_path}: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"❌ {file_path}: Error reading - {e}")
                all_good = False
        else:
            print(f"❌ {file_path}: File not found")
            all_good = False
    
    return all_good

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Doctor Appointment System Updates")
    print("=" * 60)
    
    # Test data files first
    if not test_data_files():
        print("\n❌ Data file tests failed. Cannot proceed with tool tests.")
        return False
    
    # Test tools
    patient_ok = test_patient_tools()
    availability_ok = test_availability_tools()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if patient_ok and availability_ok:
        print("✅ All tests passed! The updates are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
