from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import make_msgid
import smtplib
import base64,sys

# Función para obtener el archivo de imagen y devolverlo como MIMEImage
def obtener_imagen_como_mime(ruta_imagen):
    with open(ruta_imagen, 'rb') as f:
        return MIMEImage(f.read())

def decifrar_base64(base64_password):
    return base64.b64decode(base64_password).decode("utf-8")

# Función para enviar el correo HTML con imágenes inline (CID)
def EmailHTML(Remitente, Password, Destinatario, Subject,Content_Html,FolderImages): 
    try:
        Password = decifrar_base64(base64_password=Password)

        # Crear los objetos MIMEImage
        img_banner = obtener_imagen_como_mime(FolderImages+"BANNER.gif")
        img_logo = obtener_imagen_como_mime(FolderImages+"Logo.gif")
        img_header = obtener_imagen_como_mime(FolderImages+"Notificacion.gif")

        # Crear CIDs únicos
        cid_banner = make_msgid(domain="DIP_NF.com")
        cid_logo = make_msgid(domain="DIP_NF.com")
        cid_header = make_msgid(domain="DIP_NF.com")

        # Asignar Content-ID a cada imagen
        img_banner.add_header('Content-ID', cid_banner)
        img_logo.add_header('Content-ID', cid_logo)
        img_header.add_header('Content-ID', cid_header)

        # Reemplazar marcadores en HTML
        Content_Html = Content_Html.replace("BASE64_BANNER", f"cid:{cid_banner[1:-1]}")
        Content_Html = Content_Html.replace("BASE64_LOGO", f"cid:{cid_logo[1:-1]}")
        Content_Html = Content_Html.replace("BASE64_NOTI", f"cid:{cid_header[1:-1]}")

        # Crear contenedor principal (related → necesario para imágenes inline)
        mensaje = MIMEMultipart('related')
        mensaje['From'] = f"CoE DIP NF"
        
        if isinstance(Destinatario, str):
            Destinatario = Destinatario.split(",")
            
        mensaje['To'] = ", ".join(Destinatario)
        mensaje['Subject'] = Subject

        # Contenedor para el HTML
        alternative = MIMEMultipart('alternative')
        alternative.attach(MIMEText(Content_Html, 'html', 'utf-8'))

        # Meter alternative dentro de related
        mensaje.attach(alternative)

        # Adjuntar imágenes inline
        mensaje.attach(img_banner)
        mensaje.attach(img_logo)
        mensaje.attach(img_header)

        # Enviar correo
    
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(Remitente, Password)
        smtp.sendmail(Remitente, Destinatario, mensaje.as_string())
        smtp.quit()
        return "OK"
    except Exception as ErrorPython:
        print('Error on Line '+str(format(sys.exc_info()[-1].tb_lineno))+' <'+str(ErrorPython)+'>')
        return('Error on Line '+str(format(sys.exc_info()[-1].tb_lineno))+' <'+str(ErrorPython)+'>')

if __name__ == "__main__":
    EmailHTML(
        Remitente='dip1-ci-2@liverpool.com.mx', 
        Password='******', 
        Destinatario='gmartint@liverpool.com.mx',  # Ejemplo de múltiples destinatarios
        Subject="PRUEBA DE CORREO 2", 
        Content_Html=""
    )
