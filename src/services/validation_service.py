class ValidationService:
    def __init__(self, column_definitions):
        """Initialize with column definitions for dynamic validation."""
        self.column_definitions = column_definitions

    def validate_field(self, field_name, value, field_type, valid_values=None, default=None, required=False):
        """Validates a single field based on type and constraints."""

        if required and (value is None or value == ""):
            if default is not None:
                print(f"⚠️ WARNING: {field_name} is required but missing. Defaulting to {default}.")
                return default
            raise ValueError(f"{field_name} is required.")

        if valid_values and value not in valid_values:
            if default is not None:
                print(f"⚠️ WARNING: Invalid value for {field_name}: {value}. Defaulting to {default}.")
                return default
            raise ValueError(f"Invalid value for {field_name}. Expected one of {valid_values}.")

        try:
            if field_type == "int":
                return int(value) if value is not None else None  # ✅ Allow None
            elif field_type == "float":
                return float(value) if value is not None else None  # ✅ Allow None
        except ValueError:
            raise ValueError(f"{field_name} must be a {field_type}.")

        return value

    def validate_form_data(self, context, form_data):
        """Validates form data before inserting or updating the database."""
        if context not in self.column_definitions:
            raise ValueError(f"❌ No column definitions found for context: {context}")

        all_columns = self.column_definitions[context]["columns"]
        missing_fields = [col for col, details in all_columns.items()
                        if details.get("required", False) and not form_data.get(col)]

        if missing_fields:
            raise ValueError(f"❌ Validation failed: Missing required fields - {missing_fields}")

        for col_name, col_details in all_columns.items():
            if col_name in form_data:
                form_data[col_name] = self.validate_field(
                    field_name=col_name,
                    value=form_data[col_name],
                    field_type=col_details.get("type", "text"),
                    valid_values=col_details.get("valid_values"),
                    default=col_details.get("default"),
                    required=col_details.get("required", False),  # ✅ Pass required flag
                )

        return True

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

