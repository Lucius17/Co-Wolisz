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
        tresc TEXT NOT NULL,
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
    # Przykładowe zapytanie do bazy danych
    conn = sqlite3.connect('pytania.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tresc, opcja_1, opcja_2 FROM pytania WHERE id = 1')
    pytanie = cursor.fetchone()
    conn.close()

    return jsonify({
        'pytanie': pytanie[0],
        'opcje': [pytanie[1], pytanie[2]]
    })

@app.route('/odpowiedz', methods=['POST'])
def odpowiedz():
    odpowiedz = request.json.get('odpowiedz')
    # Tutaj możesz obsłużyć odpowiedź, np. zapisać w bazie danych
    return jsonify({'status': 'OK'})

@app.route('/wyniki', methods=['GET'])
def wyniki():
    # Pobieranie wyników z bazy danych
    conn = sqlite3.connect('pytania.db')
    cursor = conn.cursor()
    cursor.execute('SELECT glosy_opcja_1, glosy_opcja_2 FROM pytania WHERE id = 1')
    wyniki = cursor.fetchone()
    conn.close()

    suma_glosow = wyniki[0] + wyniki[1]
    procent_opcja_1 = (wyniki[0] / suma_glosow) * 100 if suma_glosow > 0 else 0
    procent_opcja_2 = (wyniki[1] / suma_glosow) * 100 if suma_glosow > 0 else 0

    return jsonify({
        'opcja_1': {'glosy': wyniki[0], 'procent': procent_opcja_1},
        'opcja_2': {'glosy': wyniki[1], 'procent': procent_opcja_2}
    })

@app.route('/dodaj_pytanie', methods=['POST'])
def dodaj_pytanie():
    dane_pytania = request.json

    tresc = dane_pytania.get('tresc')
    opcja_1 = dane_pytania.get('opcja_1')
    opcja_2 = dane_pytania.get('opcja_2')

    if not tresc or not opcja_1 or not opcja_2:
        return jsonify({'status': 'Błąd', 'komunikat': 'Wszystkie pola muszą być wypełnione'}), 400

    conn = sqlite3.connect('pytania.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pytania (tresc, opcja_1, opcja_2) VALUES (?, ?, ?)', (tresc, opcja_1, opcja_2))
    conn.commit()
    conn.close()

    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
