from tests.mockform import MockForm

def run_tests():
    test_cases = [
        {
            "name": "✅ Valid input (int, float, string)",
            "entity": "Parts",
            "test_inputs": {"PartID": "123", "PartName": "Bolt", "PartWeight": "2.5"},
            "expected": {"PartID": 123, "PartName": "Bolt", "PartWeight": 2.5}
        },
        {
            "name": "❌ Invalid integer (text instead of number)",
            "entity": "Parts",
            "test_inputs": {"PartID": "abc", "PartName": "Nut", "PartWeight": "1.5"},
            "expected": None
        },
        {
            "name": "❌ Missing required field (PartName)",
            "entity": "Parts",
            "test_inputs": {"PartID": "200", "PartName": "", "PartWeight": "1.0"},
            "expected": None  # Should fail because PartName is required
        },
        {
            "name": "✅ Uses default value for foreign key",
            "entity": "Parts",
            "test_inputs": {"PartID": "201", "PartName": "Screw", "DrawingID": ""},
            "expected": {"PartID": 201, "PartName": "Screw", "DrawingID": 266}  # Uses default from config_data
        },
        {
            "name": "❌ Invalid float (text instead of number)",
            "entity": "Parts",
            "test_inputs": {"PartID": "300", "PartName": "Washer", "PartWeight": "xyz"},
            "expected": None
        },
        {
            "name": "✅ Empty non-required field (Notes)",
            "entity": "Parts",
            "test_inputs": {"PartID": "400", "PartName": "Pin", "Notes": ""},
            "expected": {"PartID": 400, "PartName": "Pin", "Notes": ""}
        }
    ]

    for test in test_cases:
        form = MockForm(test["entity"], test["test_inputs"])
        result = form.get_form_data()

        print(f"\n🔹 {test['name']}")
        print(f"   ➡ Expected: {test['expected']}")
        print(f"   ➡ Got: {result}")

        if result == test["expected"]:
            print("✅ Test Passed!")
        else:
            print("❌ Test Failed!")

# Run Tests
run_tests()
