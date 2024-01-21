from flask import Flask, render_template, request, jsonify
import requests
import sqlite3
import os

app = Flask(__name__)

# Inicjalizacja bazy danych
if not os.path.exists('pytania.db'):
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

def obsluz_glosowanie(id_pytania, glos):
    conn = sqlite3.connect('pytania.db')
    cursor = conn.cursor()

    # Sprawdź, czy pytanie o podanym ID istnieje
    cursor.execute('SELECT * FROM pytania WHERE id = ?', (id_pytania,))
    pytanie = cursor.fetchone()

    if pytanie:
        # Zwiększ ilość głosów dla odpowiedniej opcji
        if glos == 1:
            cursor.execute('UPDATE pytania SET glosy_opcja_1 = glosy_opcja_1 + 1 WHERE id = ?', (id_pytania,))
        elif glos == 2:
            cursor.execute('UPDATE pytania SET glosy_opcja_2 = glosy_opcja_2 + 1 WHERE id = ?', (id_pytania,))
        else:
            conn.close()
            return {'status': 'Błąd', 'komunikat': 'Nieprawidłowa wartość dla parametru glos'}, 400

        conn.commit()
        conn.close()
        return {'status': 'OK'}
    else:
        conn.close()
        return {'status': 'Błąd', 'komunikat': 'Pytanie o podanym ID nie istnieje'}, 400

@app.route('/wybor', methods=['POST'])
def wybor():
    id_pytania = request.json.get('id')
    glos = request.json.get('glos')

    try:
        id_pytania = int(id_pytania)
        glos = int(glos)
    except ValueError:
        return jsonify({'status': 'Błąd', 'komunikat': 'Nieprawidłowe wartości dla parametrów id i glos'}), 400

    if id_pytania >= 1 and glos in [1, 2]:
        return jsonify(obsluz_glosowanie(id_pytania, glos))
    else:
        return jsonify({'status': 'Błąd', 'komunikat': 'Nieprawidłowe dane wejściowe'}), 400

    
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
