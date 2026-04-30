from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

import smtplib
import base64,sys

# Función para obtener el archivo de imagen y devolverlo como MIMEImage
def decifrar_base64(base64_password):
    return base64.b64decode(base64_password).decode("utf-8")

# Función para enviar el correo HTML con imágenes inline (CID)
def EmailHTML(Remitente, Password, Destinatario, Subject,Content_Html, RemitenteNegocio): 
    Subject = Subject.encode('utf-16', 'surrogatepass').decode('utf-16')
    try:
        Password = decifrar_base64(base64_password=Password)

        # Crear contenedor principal (related → necesario para imágenes inline)
        mensaje = MIMEMultipart('related')
        mensaje['From'] = f"Alertas EDS Seguros"
        
        if isinstance(Destinatario, str):
            Destinatario = Destinatario.split(",")
            
        mensaje['To'] = ", ".join(Destinatario)
        mensaje['Subject'] = Header(Subject, 'utf-8')

        # Contenedor para el HTML
        alternative = MIMEMultipart('alternative')
        alternative.attach(MIMEText(Content_Html, 'html', 'utf-8'))

        # Meter alternative dentro de related
        mensaje.attach(alternative)
        
        # Enviar correo
    
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(Remitente, Password)
        smtp.sendmail(RemitenteNegocio, Destinatario, mensaje.as_string())
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
        Content_Html="",
        RemitenteNegocio='cricardov@liverpool.com.mx'
    )
