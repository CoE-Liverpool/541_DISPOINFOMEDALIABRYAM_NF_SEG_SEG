import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


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
# ELIMINAR PROTECCIONES ANTERIORES CON LA MISMA DESCRIPCIÓN
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
# PROTEGER HOJA COMPLETA RESTRINGIENDO A USUARIOS ESPECÍFICOS
# ============================================================

def proteger_hoja_completa(
    service,
    spreadsheet_id,
    sheet_id,
    descripcion_proteccion,
    lista_correos
):
    # Definimos la protección de toda la hoja sin "unprotectedRanges"
    protected_range = {
        "range": {
            "sheetId": sheet_id
        },
        "description": descripcion_proteccion,
        "warningOnly": False,
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

def ProtegerHojaCompleta(
    SpreadsheetId,
    NombreHoja,
    ServiceAccountPath,
    DescripcionProteccion,
    MailConPermiso  # Puedes enviar 1 correo o varios separados por comas: "correo1@ejemplo.com,correo2@ejemplo.com"
):
    try:
        # Convertir a lista de correos
        lista_correos = [m.strip() for m in MailConPermiso.split(",") if m.strip()]

        # OBTENER EL EMAIL DE LA SERVICE ACCOUNT
        with open(ServiceAccountPath, 'r') as f:
            sa_data = json.load(f)
            sa_email = sa_data.get("client_email")

        # Se incluye la Service Account para evitar el error "You can't remove yourself as an editor"
        if sa_email and sa_email not in lista_correos:
            lista_correos.append(sa_email)

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

        # ELIMINAR PROTECCIÓN PREVIA SI EXISTE
        eliminar_proteccion_anterior(
            service,
            SpreadsheetId,
            sheet_id,
            DescripcionProteccion
        )

        # APLICAR PROTECCIÓN A TODA LA HOJA
        proteger_hoja_completa(
            service,
            SpreadsheetId,
            sheet_id,
            DescripcionProteccion,
            lista_correos
        )

        return "exito"

    except Exception as e:
        return "error: " + str(e)