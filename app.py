import pyodbc, time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response

app = Flask(__name__)
app.secret_key = 'Configuraciones-AppCambioSKU'  # Asegúrate de cambiar esto por una clave secreta segura en un entorno real

# Conexión a la base de datos SQL Server
server = 'pxe\\SQLEXPRESS'
database = 'app'
username = 'sa'
password = 'holahola0'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

@app.route('/', methods=['GET', 'POST'])
def index():
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT_BIG(*) AS TotalRegistros FROM [app].[db].[ordenes]")
    total_registros_row = cursor.fetchone()
    total_registros = total_registros_row[0] if total_registros_row else 0

    cursor.execute("SELECT COUNT_BIG(*) AS TotalRegistros1 FROM [app].[app].[app]")
    total_registros1_row = cursor.fetchone()
    total_registros1 = total_registros1_row[0] if total_registros1_row else 0

    cursor.execute("SELECT COUNT_BIG(*) AS TotalRegistros2 FROM [app].[db].[box]")
    total_registros2_row = cursor.fetchone()
    total_registros2 = total_registros2_row[0] if total_registros2_row else 0

    if request.method == 'POST':
        ordre = request.form['ordre']
        session['ord'] = request.form['ordre']
        csku = request.form['csku']
        session['csku'] = request.form['csku']
        unit = request.form['unit']
        session['uni'] = request.form['unit']
        datei = request.form['datei']
        session['fechai'] = request.form['datei']
        formlabel = request.form['formlabel']
        session['formlabel'] = request.form['formlabel']
        label = request.form['label']
        session['label'] = request.form['label']
        ean = request.form['ean']
        session['ean'] = request.form['ean']
        ean = request.form['mascara1']
        session['mascara1'] = request.form['mascara1']
        ean = request.form['mascara2']
        session['mascara2'] = request.form['mascara2']

        cursor = conn.cursor()
        # Preparar la consulta SQL para insertar en la tabla 'ordenes'
        insert_query = "INSERT INTO [app].[db].[ordenes] (ordre, csku, unit, datei, formlabel, label, ean) VALUES (?, ?, ?, ?, ?, ?, ?)"
        # Ejecutar la consulta con los valores proporcionados por el formulario
        cursor.execute(insert_query, (ordre, csku, unit, datei, formlabel, label, ean))
        # Confirmar los cambios en la base de datos
        conn.commit()
        
        return redirect('/ordercreate')

    # Consulta para obtener los últimos 10 registros de la tabla 'ordenes'
    cursor.execute("SELECT TOP 10 * FROM [app].[db].[ordenes] ORDER BY id DESC")
    ordenes = cursor.fetchall()

    return render_template('index.html', total_registros=total_registros, total_registros1=total_registros1, total_registros2=total_registros2, ordenes=ordenes)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        ordre = request.form['ordre']
        print(f'Orden recibida para enviar correo: {ordre}')

        # Consulta la base de datos para obtener los detalles de la orden
        conn = connect_to_database()
        cursor = conn.cursor()
        sql = f"SELECT ORDRE, BOX, BOX_UNITS, SN, CSKU, TOTAL_UNITS, EAN, SERIAL FROM [app].[app].[app] WHERE ordre='{ordre}'"
        cursor.execute(sql)
        libros = cursor.fetchall()
        conn.close()

        if "export_data" in request.form:
            if libros:
                # Crear el mensaje de correo electrónico
                msg = MIMEMultipart()
                msg['From'] = 'imes.config@gmail.com'
                msg['To'] = 'imes.config@gmail.com'
                msg['Subject'] = f'Exportación de datos - Orden {ordre}'

                # Adjuntar los datos al mensaje de correo electrónico
                filename = f"{ordre}.xls"
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload("\t".join([str(column[0]) for column in cursor.description]) + "\n" + "\n".join(["\t".join([str(value) for value in libro]) for libro in libros]))
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', f'attachment; filename={filename}')
                msg.attach(attachment)

                # Enviar el correo electrónico
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                smtp_username = 'imes.config@gmail.com'
                smtp_password = 'Config12342023'
                
                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.sendmail(msg['From'], msg['To'], msg.as_string())
                    server.quit()
                    print ('Correo electrónico enviado correctamente')
                except Exception as e:
                    print(f'Ocurrió un error al enviar el correo electrónico: {str(e)}')
                    return f'Ocurrió un error al enviar el correo electrónico: {str(e)}'
            else:
                return 'No hay datos a exportar'
    
        print("Solicitud POST recibida pero no se procesó correctamente")
        return 'Error en la solicitud'   
    return redirect('/')




@app.route('/ordercreate')
def ordercreate():
    return render_template('ordercreate.html')

@app.route('/box', methods=['GET', 'POST'])
def box():
    cursor = conn.cursor()
    ord1 = session.get('ord')  # Obtener 'ord' de la sesión
    label = session.get('label')  # Obtener 'label' de la sesión

    if request.method == 'POST':
        boxnum = request.form['boxnum']
        session['boxnum1'] = request.form['boxnum']
        unit = request.form['unit']
        session['unitbox'] = request.form['unit']
        
        cursor = conn.cursor()
        # Preparar la consulta SQL para insertar en la tabla 'box'
        insert_query = "INSERT INTO [app].[db].[box] (ordre, boxnum, unit) VALUES (?, ?, ?)"
        # Ejecutar la consulta con los valores proporcionados por el formulario
        cursor.execute(insert_query, (ord1, boxnum, unit))
        # Confirmar los cambios en la base de datos
        conn.commit()
        
        return redirect('/boxcreate')

    # Consulta para obtener los últimos 10 registros de la tabla 'box'
    cursor.execute("SELECT TOP 10 * FROM [app].[db].[box] ORDER BY id DESC")
    box_records = cursor.fetchall()

    return render_template('box.html', ord1=ord1, label=label, box_records=box_records)

@app.route('/boxcreate')
def boxcreate():
    return render_template('boxcreate.html')

@app.route('/unit', methods=['GET', 'POST'])
def unit():
    cursor = conn.cursor()
    ord1 = session.get('ord')
    uni = session.get('uni')
    fechai = session.get('fechai')
    boxnum1 = session.get('boxnum1')
    unitbox = session.get('unitbox')
    formlabel = session.get('formlabel')
    ean = session.get('ean')
    mascara1 = session.get('mascara1')
    mascara2 = session.get('mascara2')
    csku = session.get('csku')
    label = session.get('label', 0)
    qr = "www.mi.com/es/service/userguide/"
    qr2 = "www.mi.com-es-service-userguide-"

    if request.method == 'POST':
        serial = request.form['serial']
        
        # Consulta serials existentes
        cursor.execute("SELECT COUNT_BIG(*) AS count FROM [app].[app].[app] WHERE serial = ?", (serial,))
        row = cursor.fetchone()
        totalserialexist = row[0] if row else 0
        
        if (totalserialexist > 0) or (serial == ean) or (serial == qr) or (serial == qr2) or (serial == mascara1) or (serial == mascara2):
            # Si existe el registro, imprime un mensaje y redirige a /unit
            return redirect('/error1')

        
        # Consulta para obtener el último valor de label
        cursor.execute("SELECT TOP 1 label FROM [app].[app].[app] WHERE ordre=? ORDER BY id DESC", (ord1,))
        last_label_record = cursor.fetchone()
        if last_label_record:
            last_label = last_label_record[0]
        else:
            last_label = '00000'
        # Incrementar el valor de label en 1 para el próximo registro
        label = str(int(last_label) + 1).zfill(5)
        etiqueta = formlabel + label
        
        # Consulta etiqueta creada config existentes
        cursor.execute("SELECT COUNT_BIG(*) AS count FROM [app].[app].[app] WHERE sn=?", (etiqueta,))
        row = cursor.fetchone()
        totallabelexist = row[0] if row else 0
        
        if totallabelexist > 0:
            # Si existe la etiqueta, imprime un mensaje y redirige a /unit
            return redirect('/error2')
        
        # Insertar registro en la base de datos
        insert_query = "INSERT INTO [app].[app].[app] (ordre, total_units, datei, box, box_units, serial, formlabel, ean, csku, label, sn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (ord1, uni, fechai, boxnum1, unitbox, serial, formlabel, ean, csku, label, etiqueta))
        conn.commit()

        # Consulta orden completa
        cursor.execute("SELECT COUNT_BIG(*) AS count FROM [app].[app].[app] WHERE ordre=?", (ord1,))
        total_units_record = cursor.fetchone()
        total_units = total_units_record[0] if total_units_record else 0
        total_units = int(total_units)
        uni = int(uni)  # Convertir a entero

        if total_units == uni:
            # Si la orden está completa, redirige a /export y destruye la sesión
            session.clear()
            
            return redirect('/ordercomplete')

        # Consulta box completa
        cursor.execute("SELECT COUNT_BIG(*) AS count FROM [app].[app].[app] WHERE box=?", (boxnum1,))
        totalbox_record = cursor.fetchone()
        totalbox = totalbox_record[0] if totalbox_record else 0
        totalbox = int(totalbox)
        unitbox = int(unitbox)

        if totalbox == unitbox:
            # Si la caja está completa, redirige a /box
            
            return redirect('/boxcomplete')

        # Si no está completa, redirige a /unit
        
        return redirect('/unit')
    


    # Consulta para obtener los últimos registros de la tabla 'app'
    cursor.execute("SELECT * FROM [app].[app].[app] WHERE ordre=? ORDER BY id DESC", (ord1,))
    unit_records = cursor.fetchmany(10)

  
    return render_template('unit.html', ord1=ord1, uni=uni, fechai=fechai, boxnum1=boxnum1, unitbox=unitbox, formlabel=formlabel, ean=ean, mascara1=mascara1, mascara2=mascara2, csku=csku, label=label, unit_records=unit_records)

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/boxcomplete')
def boxcomplete():
    return render_template('boxcomplete.html')

@app.route('/error1')
def error1():
    return render_template('error1.html')

@app.route('/error2')
def error2():
    return render_template('error2.html')

def connect_to_database():
    return pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar_orden():
    if request.method == 'POST':
        conn = connect_to_database()
        cursor = conn.cursor()
        ordre = request.form['ordre']
        sql = f"SELECT * FROM [app].[app].[app] WHERE ordre='{ordre}' ORDER BY id"
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.close()
        return render_template('buscarorden.html', data=data)
    return render_template('buscarorden.html')

@app.route('/buscarunit', methods=['GET', 'POST'])
def buscar_unit():
    if request.method == 'POST':
        conn = connect_to_database()
        cursor = conn.cursor()
        serial = request.form['serial']
        sql = f"SELECT * FROM [app].[app].[app] WHERE serial='{serial}' OR sn='{serial}' ORDER BY id"
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.close()
        return render_template('buscarunidad.html', data=data)
    return render_template('buscarunidad.html')

@app.route('/actualizar', methods=['POST'])
def actualizar_datos():
    if request.method == 'POST':
        conn = connect_to_database()
        cursor = conn.cursor()
        id = request.form['edit-id']
        serial = request.form['newserial']
        sn = request.form['newsn']
        update_query = f"UPDATE [app].[app].[app] SET serial = ?, sn = ? WHERE id = ?"
        cursor.execute(update_query, (serial, sn, id))
        conn.commit()
        conn.close()
        response = {
            'success': True,
            'message': 'Datos actualizados correctamente',
            'new_serial': serial,
            'new_sn': sn
        }
        return jsonify(response)

@app.route('/export', methods=['GET', 'POST'])
def export_to_excel():
    if request.method == 'POST':
        conn = connect_to_database()
        cursor = conn.cursor()
        ordre = request.form['ordre']
        sql = f"SELECT ORDRE, BOX, BOX_UNITS, SN, CSKU, TOTAL_UNITS, EAN, SERIAL FROM [app].[app].[app] WHERE ordre='{ordre}'"
        cursor.execute(sql)
        libros = cursor.fetchall()
        conn.close()

        if "export_data" in request.form:
            if libros:
                filename = f"{ordre}.xls"
                header = {
                    "Content-Type": "application/vnd.ms-excel",
                    "Content-Disposition": f"attachment; filename={filename}"
                }
                content = ""

                # Obtener los nombres de las columnas a partir de los metadatos de la consulta
                column_names = [column[0] for column in cursor.description]
                content += "\t".join(column_names) + "\n"

                # Agregar los datos
                for libro in libros:
                    content += "\t".join([str(value) for value in libro]) + "\n"
                
                response = make_response(content)
                response.headers = header
                return response
            else:
                return 'No hay datos a exportar'
    
    return render_template('export.html')

if __name__ == '__main__':
    app.run(host='10.24.1.1', port=5000, debug=True)