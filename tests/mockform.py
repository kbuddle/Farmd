class MockForm:
    def __init__(self, entity_name, test_inputs):
        self.entity_name = entity_name  # Simulated entity name
        self.fields = {field: MockEntry(value) for field, value in test_inputs.items()}
        self.entity_tree = MockTreeView()  # Simulated tree view (for PK selection)

    def get_form_data(self):
        """ Retrieves form data from input fields, ensuring correct types, required values, and default values while handling errors properly. """
        form_data = {}
        form_errors = {}

        for field, entry in self.fields.items():
            value = entry.get().strip()  # ✅ Remove whitespace
            column_def = COLUMN_DEFINITIONS.get(self.entity_name, {}).get("columns", {}).get(field, {})

            # ✅ Skip auto-increment primary keys if no selection exists
            if column_def.get("is_primary_key", False):
                if not self.entity_tree.selection():
                    continue  # ✅ Do not include primary key for new records

            # ✅ Get expected type & default value
            expected_type = column_def.get("type")
            default_value = column_def.get("default", None)
            is_required = not column_def.get("foreign_key", False) and default_value is None

            # ✅ Handle empty values
            if value == "":
                if is_required:
                    form_errors[field] = "This field is required."
                value = default_value  # ✅ Apply default if available

            else:  # ✅ Convert to expected type
                try:
                    if expected_type == "int":
                        value = int(value)
                    elif expected_type == "float":
                        value = float(value)
                    # ✅ Strings require no conversion

                except ValueError:
                    form_errors[field] = f"Expected {expected_type} but got '{value}'."

            form_data[field] = value

        if form_errors:
            print(f"❌ Form validation failed: {form_errors}")
            return None  # ✅ Return `None` if validation errors exist

        return form_data

# Mock Input Classes
class MockEntry:
    """ Simulates an entry field in a form. """
    def __init__(self, value):
        self.value = str(value) if value is not None else ""

    def get(self):
        return self.value  # Simulate retrieving user input

class MockTreeView:
    """ Simulates a tree view selection for primary key handling. """
    def selection(self):
        return None  # Simulate no selection (new record case)
