# daft-code-recruitment-task-1
Zadanie rekrutacyjne do daftcode notif.ai

# Technologie
- Django
- Django Rest Framework
- PostgreSQL
- Heroku

# Opis API
Aby uzyskać dostęp do widoków wymagających uwierzytelnienia, należy wyspecyfikować nagłówek zapytania o polu `Authorization` i wartości: `Token <your-token>` gdzie za `<your-token>` należy wstawić otrzymany token.  

API składa się z następujących endpointów:

## Widok stworzenia użytkownika
- opis: Aby móc korzystać z endpointów, które wymagają uwierzytelniania, potrzebny jest token. Aby uzyskać token, trzeba najpierw stworzyć użytkownika. 
- url: `api/v1/auth/register/`
- LIVE url: http://short-messages.herokuapp.com/api/v1/auth/register/
- metoda: `POST`
- pola zapytania:
    - `username` (nazwa nowego użytkownika)
    - `password` (hasło nowego użytkownika, nie może być za krótkie ani zbyt słabe np. składające się z samych cyfr)
- pola odpowiedzi:
    - `username` (nazwa stworzonego użytkownika)

Przykład odpowiedzi na zapytanie na url `api/v1/auth/register/` z wyspecyfikowanymi polami `username` na `new_user` i `password` na `very_complicated_password123`:
```
{
    "username": "new_user"
}
```
Kod odpowiedzi to `201`.  
W przypadku niepowodzenia walidacji nazwy użytkownika lub hasła zostanie zwrócona odpowiedź z kodem `400` i z polami odpowiedzi, gdzie jedno pole odpowiada błędnemu polu a jego wartością jest lista błędów, np. w przypadku, gdy pole `password` jest puste a użytkownik o takiej nazwie już istnieje:
```
{
    "password": [
        "This field is required."
    ],
    "username": [
        "A user with that username already exists."
    ]
}

```

## Widok uzyskania tokena
- opis: Endpoint zwracający token po prawidłowym uwierzytelnieniu użytkownika.
- url: `api/v1/auth/acquire_token/`
- LIVE url: http://short-messages.herokuapp.com/api/v1/auth/acquire_token/
- metoda: `POST`
- pola zapytania:
    - takie same jak w przypadku widoku stworzenia użytkownika.
- pola odpowiedzi
    - `token` (token, którego należy użyć do uwierzytelniania)

Przykład odpowiedzi na zapytanie na url `api/v1/auth/acquire_token/` z poprawnie wyspecyfikowanymi polami `username` i `password`:
```
{
    "token": "123abc456abc123cde123bgf567123jjjasd098e"
}
```
Kod odpowiedzi to `200`.  
W przypadku niepoprawnych danych użytkownika zostaje wysłana odpowiedź z kodem `400` i z polem `non_field_errors`, którego wartością jest lista z błędami:
```
{
    "non_field_errors": [
        "Unable to log in with provided credentials."
    ]
}
```
Jeśli widoku nie da się uwierzytelnić (nieprawidłowy token) to zostaje zwrócona odpowiedź z kodem `401` i z polem odpowiedzi `detail`, którego wartość to "`Invalid token.`" :
```
{
    "detail": "Invalid token."
}
```
## Widok wiadomości
- opis: Endpoint w odpowiedzi zwraca szczegóły wiadomości o podanym `id` w formacie `json`. Przy 
  wysłaniu zapytania do tego endpointu, licznik wyświetleń tej wiadomości jest zwiększany o 1.
- url: `api/v1/short_messages/<id>/` (gdzie `<id>` to id wiadomości)
- LIVE url: np. http://short-messages.herokuapp.com/api/v1/short_messages/1/
- metoda: `GET`  
- pola zapytania: brak
- pola odpowiedzi:
    - `id` (id wiadomości, liczba całkowita)
    - `body` (treść wiadomości, napis o długości w zakresie [1, 160])
    - `views_counter` (licznik wiadomości, liczba całkowita)  

Przykład odpowiedzi na zapytanie na url `api/v1/short_messages/1/`:
```
{
    "body": "tresc-wiadomosci",
    "id": 1,
    "views_counter": 42
}
```
Kod odpowiedzi to 200.  
W przypadku braku wiadomości o podanym `id` zostaje wysłana odpowiedź o kodzie `404` z
treścią w formacie `json` z polem `detail`:
```
{
    "detail": "Not found."
}  
```
    
## Widok wylistowania wiadomości  
- opis: Endpoint w odpowiedzi zwraca listę wszystkich wiadomości w formacie `json`.
- url: `api/v1/short_messages/`
- LIVE url: http://short-messages.herokuapp.com/api/v1/short_messages/
- metoda: `GET`  
- pola zapytania: brak
- pola odpowiedzi:
    - Odpowiedzią jest lista, gdzie każdy element jest postaci takiej jak w widoku wiadomości.

Przykład odpowiedzi na zapytanie na url `api/v1/short_messages/`:
```
[
    {
        "body": "tresc-wiadomosci1",
        "id": 1,
        "views_counter": 1
    },
    {
        "body": "tresc-wiadomosci2",
        "id": 2,
        "views_counter": 42
    }
]
```
Kod odpowiedzi to 200.

## Widok edycji wiadomości
- opis: Endpoint odpowiedzialny za edycje wiadomości o podanym `id`. W odpowiedzi zwraca 
  szczegóły wiadomości po edycji w formacie `json`. Po udanym edytowaniu wiadomości, licznik
  wyświetleń zostaje wyzerowany.
- url: `api/v1/short_messages/<id>/` (gdzie `<id>` to id edytowanej wiadomości)
- LIVE url: np. http://short-messages.herokuapp.com/api/v1/short_messages/1/
- metoda: `PUT`  
- **wymaga uwierzytelnienia**
- pola zapytania:
    - `body`
        - nowa treść wiadomości, napis o długości w zakresie [1, 160]
- pola odpowiedzi:
    - Odpowiedzią są szczegóły edytowanej wiadomości w postaci takiej jak w widoku wiadomości.

Przykład odpowiedzi na zapytanie na url `api/v1/short_messages/1/` z wyspecyfikowanym
polem zapytania `body` równym `nowa-tresc-wiadomosci`:
```
{
    "body": "nowa-tresc-wiadomosci",
    "id": 1,
    "views_counter": 0
}
```
Kod odpowiedzi to `200`.  
W przypadku braku wiadomości o podanym `id` zostaje wysłana odpowiedź o kodzie `404` z
treścią w formacie `json` z polem `detail`:
```
{
    "detail": "Not found."
}  
```

## Widok stworzenia wiadomości
- opis: Endpoint odpowiedzialny za stworzenie wiadomości. W odpowiedzi zwraca 
  szczegóły stworzonej wiadomości w formacie `json`.
- url: `api/v1/short_messages/`
- LIVE url: http://short-messages.herokuapp.com/api/v1/short_messages/
- metoda: `POST`  
- **wymaga uwierzytelnienia**
- pola zapytania:
    - `body`
        - treść wiadomości, napis o długości w zakresie [1, 160]
- pola odpowiedzi:
    - Odpowiedzią są szczegóły stworzonej wiadomości w postaci takiej jak w widoku wiadomości.

Przykład odpowiedzi na zapytanie na url `api/v1/short_messages/` z wyspecyfikowanym
polem zapytania `body` równym `tresc-wiadomosci`:
```
{
    "body": "tresc-wiadomosci",
    "id": 50,
    "views_counter": 0
}
```
Kod odpowiedzi to `201`.  

## Widok usunięcia wiadomości
- opis: Endpoint odpowiedzialny za usunięcie wiadomości o podanym `id`.
- url: `api/v1/short_messages/<id>/` (gdzie `<id>` to id usuwanej wiadomości)
- LIVE url: np. http://short-messages.herokuapp.com/api/v1/short_messages/1/
- metoda: `DELETE`  
- **wymaga uwierzytelnienia**
- pola zapytania: brak
- pola odpowiedzi: brak

Przykład odpowiedzi na  poprawne zapytanie na url `api/v1/short_messages/1/` to pusta odpowiedź z
kodem odpowiedzi równym `204`. 

W przypadku braku wiadomości o podanym `id` zostaje wysłana odpowiedź o kodzie `404` z
treścią w formacie `json` z polem `detail`:
```
{
    "detail": "Not found."
}  
```
