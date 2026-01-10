from flask import Flask, render_template, request, redirect, url_for, g
from datetime import datetime

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    priority = db.Column(db.Integer)
    active = db.Column(db.Boolean)
#DATA_FILE = "dane.txt"

@app.route('/test_alchemy')
def test_alchemy():
    db.create_all()
    return '''Hello Flask-SQLAlchemy'''

PLIK_TXT = Path("moj_plik.txt")
PLIK_DB = Path("baza.db")
SEP = ";"




def get_db():
    """Zwraca połączenie SQLite przypięte do aktualnego requestu (wątku)."""
    if "db" not in g:
        g.db = sqlite3.connect(PLIK_DB)
        # opcjonalnie: wyniki jako dict-like
        g.db.row_factory = sqlite3.Row
        # upewniamy się, że tabela istnieje
        g.db.execute("""
            CREATE TABLE IF NOT EXISTS DANE (
                id TEXT PRIMARY KEY,
                name TEXT,
                surname TEXT,
                age INTEGER
            )
        """)
        g.db.commit()
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    """Zamyka połączenie po zakończeniu requestu."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

@dataclass
class MojeDane:
    """Rekord danych (odpowiednik klasy mojeDane z oryginału)."""
    id: str
    imie: str
    nazwisko: str
    wiek: int

    def wypisz(self) -> None:
        print(f"Moje dane to: id={self.id}, imie={self.imie}, nazwisko={self.nazwisko}, wiek={self.wiek}")

    def daj_linie_pliku(self) -> str:
        """Zwraca linię do zapisu w pliku tekstowym."""
        return f"{self.id}{SEP}{self.imie}{SEP}{self.nazwisko}{SEP}{self.wiek}"



class MojaBazaDB:
    """DAO/Repozytorium: nie trzyma stałego self.conn, tylko bierze conn z get_db()."""

    def INSERT(self, dane: MojeDane) -> None:
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO DANE (id, name, surname, age) VALUES (?, ?, ?, ?)",
                (dane.id, dane.imie, dane.nazwisko, dane.wiek),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"Nie można dodać. Jest już takie ID: {dane.id}")

    def DELETE(self, id: str) -> None:
        conn = get_db()
        conn.execute("DELETE FROM DANE WHERE id = ?", (id,))
        conn.commit()

    def UPDATE(self, dane: MojeDane) -> None:
        conn = get_db()
        conn.execute(
            "UPDATE DANE SET name = ?, surname = ?, age = ? WHERE id = ?",
            (dane.imie, dane.nazwisko, dane.wiek, dane.id),
        )
        conn.commit()

    def SELECT(self):
        conn = get_db()
        cur = conn.execute("SELECT id, name, surname, age FROM DANE")
        return cur.fetchall()


repo = MojaBazaDB()


@app.route("/", methods=["GET", "POST"])
def form():


    if request.method == "POST":
        id = request.form.get("id", "")
        name = request.form.get("name", "")
        surname = request.form.get("surname", "")
        age = request.form.get("age", "")
        
        wybor = request.form.get("wybor", "")

        if wybor == "INSERT":
            dana = MojeDane(id, name, surname, age)
            repo.INSERT(dana)
        elif wybor == "UPDATE":
            dana = MojeDane(id, name, surname, age)
            repo.UPDATE(dana)
        elif wybor == "DELETE":
            repo.DELETE(id)
        elif wybor == "SELECT":
            print("TEST wersja kolejna - 2.1 na innym komputerze")
            print("Dodaje do master")
        else:
    
            pass

        #return redirect(url_for("form"))

    rows = repo.SELECT()
    dane = [dict(r) for r in rows]

    return render_template("form.html", dane = dane)


if __name__ == "__main__":
    app.run(debug=True)