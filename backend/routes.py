from flask import render_template, request, redirect, url_for, flash
from database import db_connection

def init_routes(app):

    # Login page 
    @app.route('/', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            parola = request.form['parola']

            conn = db_connection()
            cursor = conn.cursor()
            
            # conectare cu email si parola
            utilizator = None  
            cursor.execute("SELECT * FROM Angajati WHERE email = ? AND parola = ?", (email, parola))
            utilizator = cursor.fetchone()
            if utilizator:
                return redirect(url_for('auth')) 

            if email == "db-admin@gmail.com" and parola == "admin123":
                utilizator = True  
                return redirect(url_for('admin')) 

            flash('Email sau parolă incorectă!')
            conn.close()

        return render_template('login.html')
    
    # Employee auth - pagina principala a aplicatiei 
    @app.route('/auth')
    def auth():
        return render_template('auth.html')


    # Employee page
    @app.route('/angajat')
    def angajat():
        conn = db_connection()
        cursor = conn.cursor()

        #afisare toti angajatii
        cursor.execute("SELECT * FROM Angajati")
        angajati = cursor.fetchall()

        conn.close()
        return render_template('angajat.html', angajati=angajati)

    
    @app.route('/delete_employee/<int:id_angajat>', methods=['POST'])
    def delete_employee(id_angajat):
        conn = db_connection()
        cursor = conn.cursor()

        # executare interogare de stergere
        cursor.execute("DELETE FROM Angajati WHERE id_angajat = ?", (id_angajat,))
        conn.commit()

        # mesaj pentru stergerea reusita
        flash('Angajatul a fost șters cu succes.', 'success')

        return redirect(url_for('angajat'))

    
    # angajati disponibili 
    @app.route('/angajati_disponibili', methods=['GET'])
    def angajati_disponibili():
        conn = db_connection()
        cursor = conn.cursor()
        #interogare simpla 1 - angajati care nu au taskuri asignate in momentul acesta
        cursor.execute("""
            SELECT a.nume, a.prenume
            FROM Angajati a
            LEFT JOIN Taskuri_Angajat ta ON a.id_angajat = ta.id_angajat
            WHERE a.disponibilitate = 'T' AND ta.id_angajat IS NULL
        """)
        result = cursor.fetchall()
    
        return render_template('angajati_disponibili.html', employees=result)

    #taskuri finalizate 
    @app.route('/taskuri_angajat')
    def taskuri_angajat():
        conn = db_connection()
        cursor = conn.cursor()

        # interogare simpla 2 - angajati care au taskuri finalizate 
        query = """
        SELECT a.nume, a.prenume, c.id_comanda, c.data_asignare, c.data_finalizare
        FROM Angajati a
        JOIN Taskuri_Angajat ta ON a.id_angajat = ta.id_angajat
        JOIN Comenzi c ON ta.id_comanda = c.id_comanda
        JOIN Status_taskuri s ON c.status_id = s.status_id
        WHERE s.denumire_status = 'Finalizat' AND c.data_finalizare IS NOT NULL;

        """
        cursor.execute(query)
        taskuri = cursor.fetchall()

        conn.close()
        return render_template('taskuri_angajat.html', taskuri=taskuri)
    
    #adaugare task pentru un angajat
    @app.route('/adauga_task_angajat', methods=['POST'])
    def adauga_task_angajat():
        id_angajat = request.form['id_angajat']
        id_comanda = request.form['id_comanda']

        conn = db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO Taskuri_Angajat (ID_Angajat, ID_Comanda)
        VALUES (?, ?)
        """
        cursor.execute(query, (id_angajat, id_comanda))
        conn.commit()

        conn.close()
        return redirect('/taskuri_angajat')
    
   
    
    #Angajatii lunii - care au lucrat la comenzi cu preturi peste medie 
    @app.route('/angajati_comenzi_peste_media', methods=['GET'])
    def angajati_comenzi_peste_media():
        conn = db_connection()
        cursor = conn.cursor()

        #interogare complexa 1 -Angajatii  care au lucrat la comenzi cu pretul total mai mare decât media preturilor comenzilor
        cursor.execute("""
            SELECT a.nume, a.prenume, c.id_comanda, c.pret_final
            FROM Angajati a
            JOIN Taskuri_Angajat ta ON a.id_angajat = ta.id_angajat
            JOIN Comenzi c ON ta.id_comanda = c.id_comanda
            WHERE c.pret_final > (
            SELECT AVG(pret_final) FROM Comenzi
            );
        """)
        result = cursor.fetchall()
        return render_template('angajati_comenzi_peste_media.html', angajati=result)

    # angajatii noi 
    @app.route('/angajati_fara_comenzi', methods=['GET'])
    def angajati_fara_comenzi():
        conn = db_connection()
        cursor = conn.cursor()

        #interogare complexa 2 - angajati fara comenzi, care nu au avut niciodata comenzi 
        cursor.execute("""
            SELECT a.nume, a.prenume
            FROM Angajati a
            WHERE a.id_angajat NOT IN (
                SELECT ta.id_angajat
                FROM Taskuri_Angajat ta
            );
        """)
        result = cursor.fetchall()
        return render_template('angajati_fara_comenzi.html', angajati=result)

    # Orders page 
    #lista comenzilor 
    @app.route('/comenzi')
    def comenzi():
        conn = db_connection()
        cursor = conn.cursor()
        
        #interogare simpla 3 - afisare lista tuturor comenzilor 
        query = """
       SELECT c.ID_Comanda, cl.Nume + ' ' + cl.Prenume AS Nume_Client, s.Denumire_Status AS Status, 
       c.Data_Asignare, c.Data_Finalizare, c.Pret_Final
       FROM Comenzi c
       JOIN Clienti cl ON c.ID_Client = cl.ID_Client
       JOIN Status_Taskuri s ON c.Status_ID = s.Status_ID
        """
        cursor.execute(query)
        comenzi = cursor.fetchall()
    
        conn.close()
        return render_template('comenzi.html', comenzi=comenzi)
    
    #adaugarea unui comenzi 
    @app.route('/adauga_comanda', methods=['GET', 'POST'])
    def adauga_comanda():
        conn = db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            id_client = request.form['id_client']
            data_asignare = request.form['data_asignare']
            data_finalizare = request.form['data_finalizare']
            status_id = request.form['status_id']

            cursor.execute("""
                INSERT INTO Comenzi (ID_Client, Data_Asignare, Data_Finalizare, Status_ID)
                VALUES (?, ?, ?, ?)
            """, (id_client, data_asignare, data_finalizare, status_id))
        
            conn.commit()
            conn.close()

            return redirect('/comenzi')
        
        cursor.execute("SELECT id_client, nume +' '+ prenume AS Nume FROM Clienti")
        clienti = cursor.fetchall()
        conn.close()

        return render_template('adauga_comanda.html', clienti=clienti)

    #calcul pret total comanda
    @app.route('/calculeaza_pret/<int:id_comanda>')
    def calculeaza_pret(id_comanda):
        conn = db_connection()
        cursor = conn.cursor()
 
        # interogare simpla 4  - calculeaza suma preturilor tuturor serviciilor unei comenzi 
        cursor.execute("""
            SELECT SUM(s.Pret) AS Pret_Final
            FROM Servicii_Comanda sc
            JOIN Servicii s ON sc.ID_Serviciu = s.ID_Serviciu
            WHERE sc.ID_Comanda = ?
        """, (id_comanda,))
    
        pret_final = cursor.fetchone()[0]
    
        cursor.execute("""
            UPDATE Comenzi
            SET Pret_Final = ?
            WHERE ID_Comanda = ?
        """, (pret_final, id_comanda))
    
        conn.commit()
        conn.close()
        return redirect('/comenzi')

    # Services page
    #lista cu toate serviciile 
    @app.route('/servicii')
    def servicii():
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute(" SELECT * FROM Servicii")
        servicii = cursor.fetchall()

        conn.close()
        return render_template('servicii.html', servicii=servicii)
    
    #adaugare serviciu
    @app.route('/add_service', methods=['POST'])
    def add_service():
        denumire = request.form['denumire']
        descriere = request.form['descriere']
        pret = request.form['pret']
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO Servicii (Denumire, Descriere, Pret) 
        VALUES (?, ?, ?)
        """, (denumire, descriere, pret))
        conn.commit()
    
        return redirect(url_for('servicii'))
    
    #editarea unui serviciu
    @app.route('/update_service/<int:service_id>', methods=['GET', 'POST'])
    def update_service(service_id):
        conn = db_connection()
        cursor = conn.cursor()
    
        if request.method == 'GET':
            cursor.execute("SELECT * FROM Servicii WHERE ID_Serviciu = ?", (service_id))
            serviciu = cursor.fetchone()
            return render_template('editare_serviciu.html', serviciu=serviciu)  
        #editare
        if request.method == 'POST':
            denumire = request.form['denumire']
            descriere = request.form['descriere']
            pret = request.form['pret']
            
            cursor.execute("""
                UPDATE Servicii 
                SET Denumire = ?, Descriere = ?, Pret = ?
                WHERE ID_Serviciu = ?
            """, (denumire, descriere, pret, service_id))
            conn.commit()
            return redirect(url_for('servicii'))  

    # cautare comenzi care contin un anumit serviciu
    @app.route('/comenzi_client_serviciu', methods=['GET'])
    def comenzi_client_serviciu():
        conn = db_connection()
        cursor = conn.cursor()

        nume_serviciu = request.args.get('servicii')
        # interogare complexa 4 cu param variabil
        cursor.execute("""
        SELECT c.id_comanda, c.data_asignare, c.data_finalizare, cl.nume, cl.prenume, s.denumire, sc.id_serviciu
        FROM Comenzi c
        JOIN Clienti cl ON c.id_client = cl.id_client
        JOIN Servicii_Comanda sc ON c.id_comanda = sc.id_comanda
        JOIN Servicii s ON sc.id_serviciu = s.id_serviciu
        WHERE sc.id_serviciu = (
        SELECT id_serviciu 
        FROM Servicii 
        WHERE denumire = ?
        )
        AND cl.nume IS NOT NULL;
        """, (nume_serviciu,))

        result = cursor.fetchall()
        return render_template('comenzi_client_serviciu.html', comenzi=result, nume_serviciu=nume_serviciu)



    # Client page
    @app.route('/client')
    def clienti():
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Clienti")
        clienti = cursor.fetchall()

        conn.close()
        return render_template('client.html', clienti=clienti)
    
    # adaugarea unui client nou 
    @app.route('/add_client', methods=['POST'])
    def add_client():
        nume = request.form['nume']
        prenume = request.form['prenume']
        strada = request.form['strada']
        numar = request.form['numar']
        oras = request.form['oras']
        judet = request.form['judet']
        telefon = request.form['telefon']
        email = request.form['email']

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO Clienti (Nume, Prenume, Strada, Numar, Oras, Judet, Telefon, Email) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nume, prenume, strada, numar, oras, judet, telefon, email))
        conn.commit()
        return redirect(url_for('clienti'))
    
    #editarea unui client 
    @app.route('/update_client/<int:client_id>', methods=['GET', 'POST'])
    def update_client(client_id):
        conn = db_connection()
        cursor = conn.cursor()

        if request.method == 'GET':
            cursor.execute("SELECT * FROM Clienti WHERE ID_Client = ?", (client_id,))
            client = cursor.fetchone()
            return render_template('editare_client.html', client=client)

        # editare
        if request.method == 'POST':
            nume = request.form['nume']
            prenume = request.form['prenume']
            strada = request.form['strada']
            numar = request.form['numar']
            oras = request.form['oras']
            judet = request.form['judet']
            telefon = request.form['telefon']
            email = request.form['email']

            cursor.execute("""
                UPDATE Clienti 
                SET Nume = ?, Prenume = ?, Strada = ?, Numar = ?, Oras = ?, Judet = ?, Telefon = ?, Email = ?
                WHERE ID_Client = ?
                """, (nume, prenume, strada, numar, oras, judet, telefon, email, client_id))
            conn.commit()
            return redirect(url_for('clienti')) 
        
    # comenzi client
    @app.route('/comenzi_client', methods=['GET'])
    def comenzi_client():
        conn = db_connection()
        cursor = conn.cursor()

        if request.method == 'GET':
            client_name = request.args.get('client_name')  
            #interogare simpla 5 - cu param variabil 
            cursor.execute("""
                SELECT cl.nume, cl.prenume, c.id_comanda, c.data_asignare, s.denumire_status
                FROM Clienti cl
                JOIN Comenzi c ON cl.id_client = c.id_client
                JOIN Status_taskuri s ON c.status_id = s.status_id
                WHERE cl.nume = ?
            """, (client_name,))
            result = cursor.fetchall()
            return render_template('comenzi_client.html', orders=result)

    # clienti care au avut comenzi cu cel putin doua servicii      
    @app.route('/clienti_comenzi_doua_servicii', methods=['GET'])
    def clienti_comenzi_doua_servicii():
        conn = db_connection()
        cursor = conn.cursor()
        # interogare complexa 3
        cursor.execute("""
            SELECT cl.nume, cl.prenume, c.id_comanda
            FROM Clienti cl
            JOIN Comenzi c ON cl.id_client = c.id_client
            WHERE c.data_finalizare IS NOT NULL
            AND c.id_comanda IN (
                SELECT id_comanda
                FROM Servicii_Comanda
                GROUP BY id_comanda
                HAVING COUNT(id_serviciu) >= 2
            );
        """)
        result = cursor.fetchall()
        return render_template('clienti_comenzi_doua_servicii.html', clienti=result)
    
    # Servicii comanda
    @app.route('/servicii_comanda/<int:id_comanda>', methods=['GET', 'POST'])
    def servicii_comanda(id_comanda):
        conn = db_connection()
        cursor = conn.cursor()

        # Interogare simpla 6 
        query_servicii_comanda = """
        SELECT SC.ID_Comanda, S.Denumire, S.Pret
        FROM Servicii_Comanda SC
        JOIN Servicii S ON SC.ID_Serviciu = S.ID_Serviciu
        WHERE SC.ID_Comanda = ?
        """
        cursor.execute(query_servicii_comanda, (id_comanda,))
        servicii = cursor.fetchall()
        pret_final = sum([serviciu[2] for serviciu in servicii])  
        if request.method == 'POST':
            servicii_selectate = request.form.getlist('servicii')  

            #adaug servicii in comanda
            for serviciu_id in servicii_selectate:
                cursor.execute("""
                    INSERT INTO Servicii_Comanda (ID_Comanda, ID_Serviciu)
                    VALUES (?, ?)
                """, (id_comanda, serviciu_id))
            conn.commit()
            return redirect(f'/servicii_comanda/{id_comanda}') 

        # actualizeaza lista de comenzi dupa ce am mai adaugat servicii
        cursor.execute("SELECT id_serviciu, denumire FROM Servicii")
        lista_servicii = cursor.fetchall()
        cursor.execute("""
            UPDATE Comenzi
            SET Pret_Final = ?
            WHERE ID_Comanda = ?
        """, (pret_final, id_comanda))
    
        conn.commit()

        conn.close()
    
        return render_template('servicii_comanda.html', servicii=servicii, lista_servicii=lista_servicii, id_comanda=id_comanda, pret_final=pret_final)
    
    #stergere serviciu
    @app.route('/delete_service/<int:service_id>', methods=['POST'])
    def delete_service(service_id):
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Servicii WHERE id_serviciu = ?", (service_id,))
        conn.commit()

        return redirect(url_for('servicii')) 

