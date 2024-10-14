import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import calendar

# Połączenie z bazą danych
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Funkcja zamieniająca numer miesiąca na nazwę miesiąca w języku polskim
def polski_miesiac(miesiac):
    miesiace_polskie = [
        "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
        "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
    ]
    return miesiace_polskie[miesiac - 1]

# Funkcja dodająca nowy wydatek do bazy danych
def add():
    try:
        kwota = float(input("Podaj kwotę: "))
        data = input("Podaj datę transakcji (YYYY-MM-DD): ")
        kategoria = input("Podaj kategorię wydatku: ")
        forma_platnosci = input("Podaj formę płatności: ")

        if kwota and data and kategoria and forma_platnosci:
            # Wstawienie danych do bazy
            cursor.execute('''
                INSERT INTO wydatki (kwota_wydana, data, kategoria, forma_plat)
                VALUES (?, ?, ?, ?)
            ''', (kwota, data, kategoria, forma_platnosci))
            conn.commit()
            print("Wydatek dodany pomyślnie.")
        else:
            print("WSZYSTKIE POLA MUSZĄ BYĆ UZUPEŁNIONE!")
    except ValueError:
        print("Niepoprawny format danych! Kwota musi być liczbą.")

# Funkcja wyświetlająca wydatki według filtru
def filtered_show(filtr, wartosc):
    cursor.execute(f'SELECT * FROM wydatki WHERE {filtr} = ?', (wartosc,))
    rows = cursor.fetchall()

    print("Id_wydatku | Kwota Wydana | Data       | Kategoria | Forma Płatności")
    print("-------------------------------------------------------------")
    for row in rows:
        print(f"{row[0]}          | {row[1]:<12} | {row[2]} | {row[3]:<10} | {row[4]}")

# Funkcja wyświetlająca wydatki na różne sposoby
def show():
    print('''Jak chciałbyś zobaczyć wydatki:
    1. Wszystkie
    2. Po kategorii
    3. Po dacie
    4. Po kwocie
    5. Po sposobie płatności''')

    opcja = input("Wybierz opcję: ")

    try:
        opcja = int(opcja)
        if opcja == 1:
            cursor.execute('SELECT * FROM wydatki')
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        elif opcja == 2:
            kategoria = input("Z jakiej kategorii wydatki chcesz zobaczyć?: ")
            filtered_show("kategoria", kategoria)
        elif opcja == 3:
            data = input("Z jakiej daty wydatki chcesz zobaczyć (YYYY-MM-DD)?: ")
            filtered_show("data", data)
        elif opcja == 4:
            print("Podaj zakres kwot (od-do): ")
            kwota_min = float(input("Minimalna kwota: "))
            kwota_max = float(input("Maksymalna kwota: "))
            cursor.execute('SELECT * FROM wydatki WHERE kwota_wydana BETWEEN ? AND ?', (kwota_min, kwota_max))
            rows = cursor.fetchall()
            print("Id_wydatku | Kwota Wydana | Data       | Kategoria | Forma Płatności")
            print("-------------------------------------------------------------")
            for row in rows:
                print(f"{row[0]}          | {row[1]:<12} | {row[2]} | {row[3]:<10} | {row[4]}")
        elif opcja == 5:
            platnosc = input("Z jakiego sposobu płatności wydatki chcesz zobaczyć?: ")
            filtered_show("forma_plat", platnosc)
        else:
            print("Niepoprawna opcja!")
    except ValueError:
        print("Niepoprawny wybór. Wybierz liczbę od 1 do 5.")

# Funkcja usuwająca wydatek z bazy danych
def delete():
    cursor.execute('SELECT * FROM wydatki')
    rows = cursor.fetchall()

    print("Id_wydatku | Kwota Wydana | Data       | Kategoria | Forma Płatności")
    print("-------------------------------------------------------------")
    for row in rows:
        print(f"{row[0]}          | {row[1]:<12} | {row[2]} | {row[3]:<10} | {row[4]}")

    while True:
        try:
            id_wydatku = int(input("Podaj id wydatku do usunięcia: "))
            cursor.execute('DELETE FROM wydatki WHERE Id_wydatku = ?', (id_wydatku,))
            conn.commit()
            print("Wydatek usunięty pomyślnie.")
            cont = input("Czy chcesz usunąć kolejny wydatek? (tak/nie): ")
            if cont.lower() == "nie":
                break
        except ValueError:
            print("Niepoprawne ID wydatku!")

# Funkcja generująca raport (miesięczny lub roczny)
def raport():
    y = []
    x = []

    print("Chciałbyś wygenerować raport roczny czy miesięczny? ")
    opcja = input('''
    1. Roczny
    2. Miesięczny\n''')

    try:
        opcja = int(opcja)
        if opcja == 1:
            rok = input("Z którego roku raport chcesz wygenerować? ")
            cursor.execute('''SELECT SUM(kwota_wydana), kategoria FROM wydatki 
                              WHERE SUBSTR(data, 1, 4) = ? GROUP BY kategoria''', (rok,))
            rows = cursor.fetchall()
            for row in rows:
                y.append(row[0])
                x.append(row[1])
            plt.title(f"Raport z roku {rok}")
            plt.pie(y, labels=x, autopct=lambda p: f'{p * sum(y) / 100 :.2f} zł')
            plt.show()
        elif opcja == 2:
            miesiac = input("Z którego miesiąca raport chcesz wygenerować? (1-12) ")
            miesiac = int(miesiac)
            cursor.execute('''SELECT SUM(kwota_wydana), kategoria FROM wydatki 
                              WHERE SUBSTR(data, 6, 2) = ? GROUP BY kategoria''', (f'{miesiac:02}',))
            rows = cursor.fetchall()
            for row in rows:
                y.append(row[0])
                x.append(row[1])
            plt.title(f"Raport z {polski_miesiac(miesiac)}")
            plt.pie(y, labels=x, autopct=lambda p: f'{p * sum(y) / 100 :.2f} zł')
            plt.show()
        else:
            print("Niepoprawna opcja!")
    except ValueError:
        print("Niepoprawny wybór!")

# Główna pętla programu
if __name__ == "__main__":
    print("Witam w twoim koszyku wydatkowym!")

    while True:
        print('''\nCo chciałbyś zrobić?
        1. Dodaj wydatek
        2. Zobacz wydatki
        3. Usuń wydatek
        4. Utwórz raport
        5. Wyjdź''')

        opcja = input("Wybierz opcję: ")

        try:
            opcja = int(opcja)
            if opcja == 1:
                add()
            elif opcja == 2:
                show()
            elif opcja == 3:
                delete()
            elif opcja == 4:
                raport()
            elif opcja == 5:
                print("Zamykam program.")
                break
            else:
                print("Niepoprawna opcja!")
        except ValueError:
            print("Niepoprawny wybór. Wybierz liczbę od 1 do 5.")

# Zamknięcie połączenia z bazą danych
conn.close()
