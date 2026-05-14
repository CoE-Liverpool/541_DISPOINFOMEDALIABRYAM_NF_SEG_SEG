# Carlos Ricardo Vertiz
# 13/05/2026
# Descripción: Se extrae el GID de un archivo Sheet de Google.
# Nota: Se complementa script a partir de Script De Martin Tolentino


from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

def Obtener_GID(in_Config, spreadsheet_id, nombre_hoja):
    creds = ServiceAccountCredentials.from_json_keyfile_name(in_Config['Key_SA'], scopes='https://www.googleapis.com/auth/drive')
    service = build('drive', 'v3', credentials=creds)
    
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    
    for sheet in sheets:
        if sheet['properties']['title'] == nombre_hoja:
            return sheet['properties']['sheetId'] # <--- AQUÍ retornamos el ID real

    return None