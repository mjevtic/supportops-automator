import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def execute_action(action_data):
    """
    Execute a Google Sheets action to append a row to a spreadsheet.
    
    Expected action_data format:
    {
        "platform": "google_sheets",
        "action": "append_row",
        "spreadsheet_id": "your-spreadsheet-id",
        "sheet_name": "Sheet1",
        "values": ["value1", "value2", "value3"]
    }
    """
    try:
        # Validate action data
        if action_data.get("action") != "append_row":
            return {"status": "error", "message": "Unsupported action for Google Sheets"}
        
        spreadsheet_id = action_data.get("spreadsheet_id")
        sheet_name = action_data.get("sheet_name", "Sheet1")
        values = action_data.get("values", [])
        
        if not spreadsheet_id:
            return {"status": "error", "message": "Missing spreadsheet_id in action data"}
        
        if not values or not isinstance(values, list):
            return {"status": "error", "message": "Invalid values in action data"}
        
        # Get credentials from service account JSON
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path:
            return {"status": "error", "message": "Google credentials not configured"}
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                creds_path, 
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Build the Sheets API client
            service = build('sheets', 'v4', credentials=credentials)
            sheets = service.spreadsheets()
            
            # Prepare the values to append
            value_range_body = {
                "values": [values]  # Wrap values in a list to create a single row
            }
            
            # Append the values to the sheet
            result = sheets.values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:Z",  # Append to the first available row
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=value_range_body
            ).execute()
            
            return {
                "status": "success", 
                "message": f"Row appended to Google Sheet",
                "details": {
                    "spreadsheet_id": spreadsheet_id,
                    "sheet_name": sheet_name,
                    "updated_range": result.get("updates", {}).get("updatedRange", "")
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Google Sheets API error: {str(e)}"}
            
    except Exception as e:
        return {"status": "error", "message": f"Failed to execute Google Sheets action: {str(e)}"}
