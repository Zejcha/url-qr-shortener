# 🚀 URL Shortener & QR Generator

W pełni funkcjonalna aplikacja webowa do skracania linków i generowania kodów QR. Projekt został zrealizowany w architekturze wielokontenerowej, z obsługą użytkowników, trwałą bazą danych i bezpiecznym serwerem proxy.

## 📸 Demo

<img width="660" height="758" alt="Zrzut ekranu 2025-07-26 160852" src="https://github.com/user-attachments/assets/2755026a-f554-4901-8726-5363aea42fac" />
<img width="617" height="455" alt="2" src="https://github.com/user-attachments/assets/ca1662e0-a9d4-4efe-8fbd-41adafb73063" />
<img width="193" height="294" alt="3" src="https://github.com/user-attachments/assets/2662b78e-eb5a-4c89-8c36-4b286a58111e" />


## ✨ Funkcje

*   **System Kont Użytkowników:** Pełna obsługa rejestracji i logowania.
*   **Trwała Historia:** Każdy użytkownik ma dostęp do swojej własnej, trwałej historii skróconych linków, zapisywanej w bazie danych PostgreSQL.
*   **Bezpieczna Sesja:** Sesja użytkownika jest utrzymywana po odświeżeniu strony za pomocą zaszyfrowanych ciasteczek (cookies) i wygasa automatycznie po 20 minutach.
*   **Customizacja Kodów QR:** Możliwość personalizacji kolorów kodu QR oraz tła.

## 🏛️ Architektura Projektu

Aplikacja działa w oparciu o wielokontenerową architekturę zarządzaną przez Docker Compose.

1.  **Nginx**,
2.  **Streamlit App**,
3.  **PostgreSQL**.

## 🛠️ Użyte Technologie

| Kategoria | Technologia |
| :--- | :--- |
| **Aplikacja** | Python, Streamlit |
| **Baza Danych** | PostgreSQL |
| **Web Server / Proxy** | Nginx |
| **Konteneryzacja** | Docker, Docker Compose |

## ⚙️ Instrukcja Uruchomienia

Projekt jest w pełni skonteneryzowany i jego uruchomienie jest bardzo proste.

### Wymagania Wstępne
*   Zainstalowany `Docker`
*   Zainstalowany `Docker Compose`
*   Zainstalowany `Git`

### Kroki Uruchomienia
1.  **Sklonuj repozytorium na swój komputer:**
    ```
    git clone https://github.com/Zejcha/url-qr-shortener.git
    ```
2.  **Przejdź do folderu projektu:**
    ```
    cd url-qr-shortener
    ```
3.  **Zbuduj i uruchom całą architekturę za pomocą jednej komendy:**
    ```
    docker compose up --build -d
    ```

4.  **Gotowe!** Poczekaj chwilę, aż wszystkie kontenery się uruchomią. Aplikacja będzie dostępna w Twojej przeglądarce pod adresem:
    [http://localhost lub `http://<adres-IP-serwera>`], jeśli uruchamiasz na zdalnej maszynie).

### Jak używać aplikacji?
1.  Otwórz aplikację w przeglądarce.
2.  Zarejestruj nowe konto w zakładce "Rejestracja".
3.  Zaloguj się na swoje konto.
4.  Wpisz link, który chcesz skrócić, wybierz kolory dla kodu QR w panelu bocznym i kliknij "Generuj!".
5.  Przeglądaj swoją historię i generuj ponownie kody QR dla starych linków za pomocą przycisków "Pokaż QR".


---
*Autor: Dominik*

