import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

# Ustawienia plików
PLIK_TXT = Path("moj_plik.txt")
PLIK_DB = Path("baza.db")
SEP = ";"


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


class MojaBazaTXT:
    """Operacje INSERT/DELETE/UPDATE na pliku tekstowym (tak jak mojaBaza)."""

    def __init__(self, sciezka: Path = PLIK_TXT) -> None:
        self.sciezka = sciezka
        # Tworzymy plik jeśli nie istnieje
        self.sciezka.touch(exist_ok=True)

    def _wczytaj_linie(self) -> list[str]:
        return self.sciezka.read_text(encoding="utf-8").splitlines()

    def INSERT(self, dane: MojeDane) -> None:
        """Dodaje rekord jeśli ID jeszcze nie istnieje."""
        linie = self._wczytaj_linie()

        for linia in linie:
            if not linia.strip():
                continue
            pola = linia.split(SEP)
            if pola[0] == dane.id:
                print(f"Nie można dodać. Jest już takie ID: {dane.id}")
                return

        with self.sciezka.open("a", encoding="utf-8") as f:
            f.write(dane.daj_linie_pliku() + "\n")

    def DELETE(self, id: str) -> None:
        """Usuwa rekord o danym ID."""
        linie = self._wczytaj_linie()
        nowe = []

        for linia in linie:
            if not linia.strip():
                continue
            pola = linia.split(SEP)
            if pola[0] != id:
                nowe.append(linia)

        self.sciezka.write_text("\n".join(nowe) + ("\n" if nowe else ""), encoding="utf-8")

    def UPDATE(self, dane: MojeDane) -> None:
        """Nadpisuje rekord o tym samym ID; jeśli nie ma - nic nie zmienia (jak w oryginale)."""
        linie = self._wczytaj_linie()
        nowe = []

        for linia in linie:
            if not linia.strip():
                continue
            pola = linia.split(SEP)
            if pola[0] == dane.id:
                nowe.append(dane.daj_linie_pliku())
            else:
                nowe.append(linia)

        self.sciezka.write_text("\n".join(nowe) + ("\n" if nowe else ""), encoding="utf-8")


class MojaBazaDB:
    """Operacje INSERT/DELETE/UPDATE/SELECT na SQLite (tak jak mojaBazaDB)."""

    def __init__(self, sciezka_db: Path = PLIK_DB) -> None:
        self.sciezka_db = sciezka_db
        self.conn = sqlite3.connect(self.sciezka_db)
        self._utworz_tabele()

    def _utworz_tabele(self) -> None:
        """Tworzy tabelę jeśli nie istnieje."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS DANE (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    surname TEXT,
                    age INTEGER
                )
            """)

    def close(self) -> None:
        """Zamyka połączenie z bazą."""
        self.conn.close()

    def INSERT(self, dane: MojeDane) -> None:
        """Dodaje rekord (bezpiecznie, parametryzowane SQL)."""
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO DANE (id, name, surname, age) VALUES (?, ?, ?, ?)",
                    (dane.id, dane.imie, dane.nazwisko, dane.wiek),
                )
        except sqlite3.IntegrityError:
            # Jeśli ID już istnieje (PRIMARY KEY), zachowujemy się podobnie do wersji plikowej:
            print(f"Nie można dodać. Jest już takie ID: {dane.id}")

    def DELETE(self, id: str) -> None:
        """Usuwa rekord o danym ID."""
        with self.conn:
            self.conn.execute("DELETE FROM DANE WHERE id = ?", (id,))

    def UPDATE(self, dane: MojeDane) -> None:
        """Aktualizuje rekord o danym ID."""
        with self.conn:
            self.conn.execute(
                "UPDATE DANE SET name = ?, surname = ?, age = ? WHERE id = ?",
                (dane.imie, dane.nazwisko, dane.wiek, dane.id),
            )

    def SELECT(self) -> None:
        """Wypisuje wszystkie rekordy."""
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, surname, age FROM DANE")
        print(cur.fetchall())


def testuj2() -> None:
    """Odpowiednik Twojego testuj2()."""
    print("SQLite version:", sqlite3.sqlite_version)

    a1 = MojeDane("7", "Ala", "Makota", 30)
    a2 = MojeDane("8", "Ala", "Makota", 30)
    a3 = MojeDane("9", "Ala", "Makota", 30)

    db = MojaBazaDB()

    db.INSERT(a1)
    db.INSERT(a2)
    db.INSERT(a3)

    db.DELETE("4")  # jak w oryginale (może nie istnieć)

    a4 = MojeDane("9", "Bela", "Mapsa", 90)
    db.UPDATE(a4)

    db.DELETE("8")
    db.SELECT()

    db.close()


if __name__ == "__main__":
    testuj2()
