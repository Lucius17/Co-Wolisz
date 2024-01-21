from flask import Flask, render_template, request, jsonify
import requests
import sqlite3

app = Flask(__name__)

# Inicjalizacja bazy danych
conn = sqlite3.connect('pytania.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pytania (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opcja_1 TEXT NOT NULL,
        opcja_2 TEXT NOT NULL,
        glosy_opcja_1 INTEGER DEFAULT 0,
        glosy_opcja_2 INTEGER DEFAULT 0
    )
''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wybor', methods=['POST'])
def wybor():
    wybor = request.form.get('wybor')
    
    # Aktualizacja głosów w bazie danych
    conn = sqlite3.connect('pytania.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE pytania SET glosy_{wybor.lower().replace(" ", "_")} = glosy_{wybor.lower().replace(" ", "_")} + 1 WHERE id = 1')
    conn.commit()
    conn.close()
    
    return f'Wybrałeś: {wybor}'

@app.route('/pytanie', methods=['GET'])
def pytanie():
    # Przykładowe zapytanie do bazy danych na temat losowego pytania
    conn = sqlite3.connect('pytania.db')
    cursor = conn.cursor()

    # Pobierz losowe pytanie
    cursor.execute('SELECT id, opcja_1, opcja_2 FROM pytania ORDER BY RANDOM() LIMIT 1')
    pytanie = cursor.fetchone()

    if pytanie:
        # Pobierz wyniki dla tego pytania
        cursor.execute('SELECT glosy_opcja_1, glosy_opcja_2 FROM pytania WHERE id = ?', (pytanie[0],))
        wyniki = cursor.fetchone()

        conn.close()

        # Przygotuj odpowiedź JSON
        response = {
            'id_pytania': pytanie[0],
            'opcje': [pytanie[1], pytanie[2]],
            'wyniki': {'opcja_1': wyniki[0], 'opcja_2': wyniki[1]}
        }

        return jsonify(response)
    else:
        conn.close()
        return jsonify({'status': 'Błąd', 'komunikat': 'Brak dostępnych pytań'}), 400

@app.route('/odpowiedz', methods=['POST'])
def odpowiedz():
    dane_odpowiedzi = request.json
    id_pytania = dane_odpowiedzi.get('id')
    odpowiedz = dane_odpowiedzi.get('odpowiedz')

    # Tutaj możesz obsłużyć odpowiedź, np. zapisać w bazie danych
    if id_pytania is not None and odpowiedz in ['true', 'false']:
        # Przykładowa logika obsługi odpowiedzi
        conn = sqlite3.connect('pytania.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pytania WHERE id = ?', (id_pytania,))

        pytanie = cursor.fetchone()

        if pytanie:
            # Tutaj możesz dodać logikę zapisu odpowiedzi do bazy danych
            # Przykład:
            if odpowiedz == 'true':
                cursor.execute('UPDATE pytania SET glosy_opcja_1 = glosy_opcja_1 + 1 WHERE id = ?', (id_pytania,))
            else:
                cursor.execute('UPDATE pytania SET glosy_opcja_2 = glosy_opcja_2 + 1 WHERE id = ?', (id_pytania,))
            
            conn.commit()
            conn.close()

            return jsonify({'status': 'OK'})
        else:
            return jsonify({'status': 'Błąd', 'komunikat': 'Pytanie o podanym ID nie istnieje'}), 400
    else:
        return jsonify({'status': 'Błąd', 'komunikat': 'Nieprawidłowe dane wejściowe'}), 400


@app.route('/dodaj_pytanie', methods=['POST'])
def dodaj_pytania():
    dane_pytania = request.json

    if not isinstance(dane_pytania, list):
        return jsonify({'status': 'Błąd', 'komunikat': 'Dane muszą być przesłane jako lista'}), 400

    conn = sqlite3.connect('pytania.db')
    cursor = conn.cursor()

    for pytanie in dane_pytania:
        opcja_1 = pytanie.get('opcja_1')
        opcja_2 = pytanie.get('opcja_2')

        if not opcja_1 or not opcja_2:
            conn.rollback()
            conn.close()
            return jsonify({'status': 'Błąd', 'komunikat': 'Wszystkie pola muszą być wypełnione'}), 400

        cursor.execute('INSERT INTO pytania (opcja_1, opcja_2) VALUES (?, ?)', (opcja_1, opcja_2))

    conn.commit()
    conn.close()

    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
