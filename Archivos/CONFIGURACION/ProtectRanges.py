from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json

# ============================================================
# CONVERTIR LETRA DE COLUMNA A ÍNDICE
# ============================================================

def columna_a_indice(columna):
    columna = columna.strip().upper()
    resultado = 0
    for caracter in columna:
        resultado = resultado * 26 + (ord(caracter) - ord("A") + 1)
    return resultado - 1


# ============================================================
# OBTENER SHEET ID A PARTIR DEL NOMBRE DE LA HOJA
# ============================================================

def obtener_sheet_id(service, spreadsheet_id, nombre_hoja):
    respuesta = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="sheets(properties(sheetId,title))"
    ).execute()

    for hoja in respuesta.get("sheets", []):
        propiedades = hoja["properties"]
        if propiedades["title"] == nombre_hoja:
            return propiedades["sheetId"]

    raise Exception("No se encontró la hoja: " + nombre_hoja)


# ============================================================
# ELIMINAR PROTECCIÓN ANTERIOR
# ============================================================

def eliminar_proteccion_anterior(
    service,
    spreadsheet_id,
    sheet_id,
    descripcion_proteccion
):
    respuesta = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="sheets(properties(sheetId,title),protectedRanges)"
    ).execute()

    requests = []

    for hoja in respuesta.get("sheets", []):
        propiedades = hoja["properties"]
        if propiedades["sheetId"] != sheet_id:
            continue

        for proteccion in hoja.get("protectedRanges", []):
            descripcion = proteccion.get("description", "")
            if descripcion == descripcion_proteccion:
                protected_range_id = proteccion.get("protectedRangeId")
                if protected_range_id is not None:
                    requests.append({
                        "deleteProtectedRange": {
                            "protectedRangeId": protected_range_id
                        }
                    })

    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()


# ============================================================
# PROTEGER TODA LA HOJA EXCEPTO COLUMNAS INDICADAS (CON EDITORES)
# ============================================================

def proteger_hoja_excepto_columnas(
    service,
    spreadsheet_id,
    sheet_id,
    columnas_editables,
    descripcion_proteccion,
    lista_correos,
    sa_email  # <- Recibimos el correo de la Service Account
):
    rangos_no_protegidos = []

    for columna in columnas_editables:
        indice = columna_a_indice(columna)
        rangos_no_protegidos.append({
            "sheetId": sheet_id,
            "startColumnIndex": indice,
            "endColumnIndex": indice + 1
        })

    # Nos aseguramos de que el correo de la Service Account esté en la lista
    if sa_email and sa_email not in lista_correos:
        lista_correos.append(sa_email)

    protected_range = {
        "range": {
            "sheetId": sheet_id
        },
        "description": descripcion_proteccion,
        "warningOnly": False,
        "unprotectedRanges": rangos_no_protegidos,
        "editors": {
            "users": lista_correos
        }
    }

    request = {
        "addProtectedRange": {
            "protectedRange": protected_range
        }
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [request]}
    ).execute()


# ============================================================
# FUNCIÓN PRINCIPAL PARA INVOKE PYTHON
# ============================================================

def AgregarProteccionAlSheet(
    SpreadsheetId,
    NombreHoja,
    ServiceAccountPath,
    ColumnasEditables,
    DescripcionProteccion,
    MailsConPermiso
):
    try:
        lista_columnas = [c.strip() for c in ColumnasEditables.split(",") if c.strip()]
        lista_correos = [m.strip() for m in MailsConPermiso.split(",") if m.strip()]

        # OBTENER EL EMAIL DE LA SERVICE ACCOUNT
        with open(ServiceAccountPath, 'r') as f:
            sa_data = json.load(f)
            sa_email = sa_data.get("client_email")

        # CONEXIÓN
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_file(
            ServiceAccountPath,
            scopes=SCOPES
        )
        service = build("sheets", "v4", credentials=credentials)

        # OBTENER SHEET ID
        sheet_id = obtener_sheet_id(
            service,
            SpreadsheetId,
            NombreHoja
        )

        # ELIMINAR PROTECCIÓN ANTERIOR
        eliminar_proteccion_anterior(
            service,
            SpreadsheetId,
            sheet_id,
            DescripcionProteccion
        )

        # PROTEGER HOJA EXCEPTO COLUMNAS Y ASIGNAR USUARIOS
        proteger_hoja_excepto_columnas(
            service,
            SpreadsheetId,
            sheet_id,
            lista_columnas,
            DescripcionProteccion,
            lista_correos,
            sa_email # <- Pasamos el email aquí
        )

        return "exito"

    except Exception as e:
        return "error: " + str(e)