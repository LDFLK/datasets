class Utils:
    @staticmethod
    def format_issue(issue):
        location = ""

        if issue.get("row") is not None:
            location += f"Row {issue['row']}"

        if issue.get("column"):
            # handle list of columns OR single column
            if isinstance(issue["column"], list):
                cols = ", ".join(issue["column"])
                location += f", Columns [{cols}]"
            else:
                location += f", Column '{issue['column']}'"

        return f"[{issue['type'].upper()}] {issue['file']}: {location} {issue['message']}"
    
    @staticmethod
    def fits_in_int32(value: int) -> bool:
        INT32_MIN = -2_147_483_648
        INT32_MAX = 2_147_483_647
        return INT32_MIN <= value <= INT32_MAX