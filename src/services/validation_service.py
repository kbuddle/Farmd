class ValidationService:
    def __init__(self, column_definitions):
        """Initialize with column definitions for dynamic validation."""
        self.column_definitions = column_definitions

    def validate_field(self, field_name, value, field_type, valid_values=None, default=None, required=False):
        """Validates a single field based on type and constraints."""
        print(f"Debug: Validating field {field_name} with value {value}, type {field_type}, valid_values {valid_values}, default {default}, required {required}")
        
        if required and (value is None or value == ""):
            if default is not None:
                return default
            print(f"⚠️ Debug: Raising missing field error for {field_name}")
            raise ValueError(f"❌ {field_name} is required.")

        if valid_values and value not in valid_values:
            if default is not None:
                return default
            print(f"⚠️ Debug: Raising invalid value error for {field_name}")
            raise ValueError(f"❌ Invalid value for {field_name}. Expected one of {valid_values}.")

        try:
            if field_type == "int":
                return int(value)
            elif field_type == "float":
                return float(value)
        except ValueError as e:
            print(f"⚠️ Debug: Type conversion error for {field_name} -> {value} ({field_type}): {str(e)}")
            raise ValueError(f"❌ {field_name} must be a valid {field_type}.")  # ✅ Now replaces Python's default error

        return value


    def extract_form_data(self, form_data, context):
        """Extracts and preprocesses form data (applies defaults, type conversion)."""
        if context not in self.column_definitions:
            raise ValueError(f"❌ No column definitions found for context: {context}")

        all_columns = self.column_definitions[context]["columns"]
        cleaned_data = {}

        for field_name, col_details in all_columns.items():
            value = form_data.get(field_name, col_details.get("default"))

            # ✅ Ensure `None` values are replaced with defaults
            if value in [None, "None",""]:
                value = col_details.get("default", None)# Convert to correct type

            expected_type = col_details.get("type", "text")
            if expected_type == "int":
                value = int(value) if value is not None else None
            elif expected_type == "float":
                value = float(value) if value is not None else None

            cleaned_data[field_name] = value

        return cleaned_data  # ✅ Now returns a processed dictionary

    def validate_form_data(self, context, form_data):
        """Validates form data before inserting or updating the database and returns cleaned data."""
        # ✅ Preprocess data first
        cleaned_data = self.extract_form_data(form_data, context)

        # ✅ Ensure no "None" strings are left in the cleaned data
        for key, value in cleaned_data.items():
            if isinstance(value, str) and value.strip().lower() == "none":
                cleaned_data[key] = None  # Convert to actual None

        all_columns = self.column_definitions[context]["columns"]

        # ✅ Check for missing required fields (after applying defaults)
        missing_fields = [
            col for col, details in all_columns.items()
            if details.get("required", False) and col not in cleaned_data
        ]

        if missing_fields:
            raise ValueError(f"❌ Missing required fields: {', '.join(missing_fields)}")


        # ✅ Perform additional validation (e.g., valid values)
        for col_name, col_details in all_columns.items():
            if col_name in cleaned_data:
                cleaned_data[col_name] = self.validate_field(
                    field_name=col_name,
                    value=cleaned_data[col_name],  # ✅ Now using preprocessed data
                    field_type=col_details.get("type", "text"),
                    valid_values=col_details.get("valid_values"),
                    default=col_details.get("default"),
                    required=col_details.get("required", False),
                )

        return cleaned_data  # ✅ Returns validated data instead of just True

    def validate_table_selection(self, table, context):
        """Ensures a selection has been made in a table."""
        selected_item = table.selection()
        if not selected_item:
            raise ValueError(f"❌ Please select a {context} to proceed.")
        return table.item(selected_item, "values")

    def validate_foreign_keys(self, data, filtered_columns, db_manager, debug=False):
        """Ensures foreign key constraints are met."""
        for col_name, col_details in filtered_columns.items():
            if col_details.get("type") == "foreign_key":
                fk_table = col_details.get("references")
                fk_column = col_details.get("to", col_name)
                fk_value = data.get(col_name)

                if not fk_value:
                    continue

                if debug:
                    print(f"🔍 Validating FK: {col_name} -> {fk_table}({fk_column}) with value {fk_value}")

                fk_query = f"SELECT 1 FROM {fk_table} WHERE {fk_column} = ?"
                result = db_manager.execute_query(fk_query, (fk_value,))

                if not result:
                    raise ValueError(
                        f"❌ The value '{fk_value}' for '{col_name}' does not exist in table '{fk_table}'."
                    )

    def validate_context_structure(self, contexts):
        """Ensures contexts object is a dictionary."""
        if not isinstance(contexts, dict):
            raise TypeError(f"❌ 'contexts' must be a dictionary, got {type(contexts)}")

