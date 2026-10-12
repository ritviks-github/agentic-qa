import pandas as pd


def read_excel_data(file_path):
    """
    Read all data from an Excel file.

    Returns:
        dict:
            {
                "Sheet1": [
                    {...},
                    {...}
                ],
                "Sheet2": [
                    {...},
                    {...}
                ]
            }
    """

    excel_file = pd.ExcelFile(file_path)

    data = {}

    for sheet_name in excel_file.sheet_names:

        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name
        )

        # Convert NaN to None
        df = df.where(
            pd.notna(df),
            None
        )

        # Convert rows to dictionaries
        data[sheet_name] = df.to_dict(
            orient="records"
        )

    return data