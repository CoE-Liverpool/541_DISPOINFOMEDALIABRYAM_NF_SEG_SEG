# Carlos Ricardo Vertiz
# 13/05/2026
# Descripción: Se extrae el GID de un archivo Sheet de Google.
# Nota: Se complementa script a partir de Script De Martin Tolentino


from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

def Obtener_GID(ruta_json, SpreadsheetId, NombreHoja):
    # Usamos la variable ruta_json directamente como el path
    creds = ServiceAccountCredentials.from_json_keyfile_name(ruta_json, scopes=['https://www.googleapis.com/auth/drive'])
    service = build('sheets', 'v4', credentials=creds)
    
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SpreadsheetId).execute()
    sheets = sheet_metadata.get('sheets', '')
    
    for sheet in sheets:
        if sheet['properties']['title'] == NombreHoja:
            return str(sheet['properties']['sheetId']) 