# VITMMB11 - Házi Feladat

## Bevezető

A jelen dokumentum a Felhők hálózati szolgáltatásai laboratórium (VITMMB11) tantárgy házi feladatának fejlesztői dokumentációja.

## Feladatkiírás

Egy olyan web szolgáltatás létrehozása, ami az alábbi funkciókat látja el:

- Kép és hozzá tartozó rövid leírás feltöltése és tárolása (kép-leírás páros tárolása);
- A feltöltött képen automatikus karakterfelismerés futtatása és a detektált szövegrészletek (szavak vagy karakterek) bekeretezésével a kép megjelenítése a weboldalon;
- A weboldal „üzemeltetői” számára feliratkozás megvalósítása, ami által értesítést tudnak kapni az összes eddigi és az oldalra újonnan feltöltött képekről úgy, hogy kiküldésre kerül számukra a képhez tartozó rövid leírás, és a képen detektált szöveges tartalom is.

##  Webszolgáltatás architektúra

Az alkalmazás általam lefejlesztett komponensei Python nyelven íródnak.

Az alkalmazás három elkülöníthető részből áll, ezek HTTP API-val kommunikálnak egymással:

| Komponens  | Funkció |
| ---------- | ------- |
| frontend   | A felhasználó felé elérhető weboldal megjelenítése, a feltöltött kép és leírás elküldése az adatbázis kezelőnek, illetve a backend értesítése. |
| backend    | Az OCR generálás végrehajtása, a generálás végén az adatbázis kezelő értesítése a kigenerált fájlról és a rajta található szövegekről |
| db_handler | Az eredeti, illetve a generált kép tárolása, a felhasználó által megadott leírás, illetve az OCR által felismert leírás tárolása. |

Az alkalmazás megvalósításához microservice ökoszisztémát használtam, mivel így a komponensek könnyedén kiterjeszthetők vertikálisan és horizontálisan, illetve az architektúra könnyedén módosítható, amennyiben az adott felhasználási mód azt kívánja.

A különböző microservice-k a service nevüknek megfelelő könyvtárban helyezkednek el az alkalmazás gyökérkönyvtárán belül.

### Frontend

A frontend konténerben egy `Flask` alapú webalkalmazás fut. A `Flask` `Blueprint` keretrendszerével történik a weboldalak és tartalmuk kigenerálása. A HTTP kéréseket a `requests` függvénykönyvtár segítségével szolgálom ki.

A Flask alkalmazás a `frontend` könyvtáron belüli `frontend` könyvtárban egy `__init__.py` nevű fájlban van definiálva, az endpointok pedig a `gallery.py` nevű fájlban.

A konténert definiáló `Dockerfile`, illetve a python alkalmazás dependenciáit tartalmazó `requirements.txt` a `frontend` könyvtárban található.

A frontend konténer az alábbi web endpointokat szolgálja ki a felhasználónak:

#### /

- Metódus: GET
- Funkció: Letölti és megjeleníti a generált képeket az adatbázisból, amennyiben léteznek. Ha nem létezik egy kép, amit az alkalmazás egy `processed` nevű flag értékével ellenőriz, akkor egy frissítés gombot tesz elérhetővé, amivel a backend újra késztethető a kép generálására.

#### /refresh/\<image_id\>

- Metódus: GET
- Funkció: Az endpoint, ahol a backend újra késztethető a kép generálására.

#### /upload

- Metódus: GET
- Funkció: Megjeleníti a képfeltöltési mezőt és a felirat megadási mezőt, illetve lehetővé teszi a felhasználónak, hogy ezeket feltöltse.

#### /upload-image

- Metódus: POST
- Funkció: A kép feltöltését végzi. Biztonsági ellenőrzések után (fájl jelen, PNG kiterjesztés) a kép base64-be lesz konvertálva, majd elküldésre kerül a felirattal együtt az adatbázisnak JSON formátumban. Ez egy szinkron kérés, megvárja, amíg az adatbázis visszatér egy azonosítóval, vagy pedig kiírja a felhasználónak, hogy az adatbázis nem elérhető. Az azonosítóval ezután meghívja a backend-et, hogy az meg tudja kezdeni a karakterfelismerést a képen. A backend aszinkron módon hajtja végre a feladatot, a frontend a sikeres kiküldés után sikeres üzenettel tér vissza.

### Backend

A backend konténerben szintén egy `Flask` alapú webalkalmazás fut. A HTTP kéréseket a `requests` függvénykönyvtár segítségével szolgálom ki. Az OCR megoldáshoz a Tesseract szoftvert használom, ehhez a `Dockerfile` segítségével felraktam a `tesseract-ocr` csomagot a konténerbe, illetve a `tesseract-data-eng` és `tesseract-data-deu` csomagokat a leggyakoribb angol, illetve német nyelvek támogatására. Mivel az alkalmazást Python-ban írtam meg, ezért szükségem volt még a `pytesseract` modulra is. A dobozok felrajzolásához a `Pillow` könyvtárat használom.

A Flask alkalmazás és az endpointok is a `backend` könyvtárban egy `app.py` nevű fájlban van definiálva.

A konténert definiáló `Dockerfile`, illetve a python alkalmazás dependenciáit tartalmazó `requirements.txt` a `backend` könyvtárban található.

A backend konténer az alábbi API endpointokkal rendelkezik:

#### /image/\<image_id\>

- Metódus: GET
- Funkció: A feldolgozás aszinkron módon történik. Az azonosító segítségével a backend lekérdezi az adatbázistól az eredeti képet. Ezt a tesseract segítségével feldolgozza, majd az elkészült képet és a felismert szöveget visszaküldi az adatbázisnak.

### DB_handler

A db_handler konténerben szintén egy `Flask` alapú webalkalmazás fut. Az adatbázishoz egy `sqlite` adatbázist használok, amihez a Python `sqlite` modulját használom. Az adatbázis vagy az eredeti kép és leírás párost fogadja, vagy a generált képet és az értelmezett szöveget.

A Flask alkalmazás és az endpointok is a `db_handler` könyvtárban egy `app.py` nevű fájlban van definiálva.

A konténert definiáló `Dockerfile`, illetve a python alkalmazás dependenciáit tartalmazó `requirements.txt` a `db_handler` könyvtárban található.

A db_handler konténer az alábbi API endpointokkal rendelkezik:

#### /

- Metódus: GET
- Funkció: Az összes képhez visszaadja az azonosítót, a generált képet, illetve az eredeti és az értelmezett leírást. Amennyiben a generált kép még nem elérhető, akkor az azonosítót, illetve az eredeti leírást adja meg.

#### /image/\<image_id\>

- Metódus: GET
- Funkció: Egy bizonyos képhez visszaadja az azonosítót, a generált képet, illetve az eredeti és az értelmezett leírást. Amennyiben a generált kép még nem elérhető, akkor az azonosítót, illetve az eredeti leírást adja meg.

#### /upload

- Metódus: POST
- Funkció: Fogadja az eredeti képet és a leírást, illetve a generált képet és az értelmezett szöveget. Amennyiben azonosító van megadva, akkor a paramétereket generált képként és értelmezett szövegként értelmezi, különben eredeti képnek és leírásnak. Azonosító megadásakor ellenőrzi, hogy a kép létezik-e.

## Adatszerkezetek

Az adatbázisban egyetlen tábla van `images` néven, ami az alábbi mezőket tartalmazza:

| Név | Típus |
| --- | ----- |
| id           | Szám. Automatikusan növekszik minden új bejegyzésnél. |
| image_normal | A felhasználó által feltöltött kép base64 formátumban. |
| image_proc   | Az OCR által feldolgozott kép base64 formátumban. |
| caption_user | A felhasználó által megadott képleírás. |
| caption_gen  | Az OCR által felismert karakterek sorozata. |
| processed    | Egy flag arra, hogy létezik-e a feldolgozott kép. |

A tábla szerkezete egy `schema.sql` fájlban van letárolva, amely az adatbázis inicializációja közben betöltésre kerül.

Az adatbázis konténer `sqlite` adatbázis fájlja perzisztensen mentve van egy mountolt könyvtárba. Az adatbázis minden commit-nál külön meg van nyitva, illetve be van zárva, hogy a lehető legtöbbször legyen konzisztens.

A `frontend` HTML oldalai a `Blueprint` konfigurációjának megfelelően egy `templates` könyvtárban helyezkednek el, ahol van egy `base.html` ami az oldalak kinézetsablonjait és a menüt tartalmazza, illetve az `image` alkönyvtárban a különböző oldalak template fájljai.

A képek a `frontend`-ben a `static/images/` könyvtárba töltődnek le gyorsítótárazás miatt. Ez a könyvtár nincs perzisztensen mentve.

A `static` könyvtárban ezentúl található még egy `style.css` fájl, ami a HTML oldal stíluslapját tartalmazza.

Mivel a felhasználónak a `Flask` `flash` nevű alrendszerével üzeni meg az alkalmazás, hogy sikeres volt-e egy művelet, amely session cookiekat használ, ezért az alkalmazás tartalmaz egy konfigurációs fájlt `frontend-config.ini` néven, ahol a `Flask` alkalmazás session secretje állítható be, amit környezeti változóként kap meg a `Flask` alkalmazás, hogy az inicializációnál be tudja állítani.

## CI/CD környezet

Github actions-t használok a CI/CD lépések végrehajtására a széleskörű használata miatt, docker compose-t az elkészült alkalmazás tesztelésére, mivel a github actions környezetben is [elérhető](https://github.com/marketplace/actions/docker-compose-action).

A Docker compose file-ban a jelenlegi image-re mutató linkek vannak, így a futást követően a github actions is a legújabb image-ekhez fér hozzá, illetve lokálisan futtatva is a legújabb image-eket indítja el a Docker compose.

A Docker compose fájlban a konténerek egy közös, elszigetelt hálózaton belül vannak és csak a `frontend`-nek van a külvilág felé nyitott portja.

### Lokális tesztelés

A lokális teszteléshez az alábbi komponensek szükségesek:

- make
- docker

A dokumentáció kigenerálásához még az alábbi komponensek megléte feltételezett:

- pandoc
- xelatex

A fejlesztés során Windows 11-ről WSL 2-t használtam Docker Desktop támogatással Ubuntu 24.04 operációs rendszerrel.

Az egyes különálló komponensek teszteléséhez létrehoztam az alkalmazás gyökérkönyvtárában egy `Makefile`-t, amiben komponensenként az alábbi lehetőségek elérhetőek:

| Parancs | Funkció |
| ------- | ------- |
| *-build | A megfelelő komponenst lebuildeli és abból egy teszt konténert hoz létre |
| *-run   | Futtatja alapértelmezett parancsával a konténert és egy konfigurálható porton elérhetővé teszi a külvilág számára (dependál a build-re) |
| *-shell | Futtat egy shellt a konténerben és közben egy konfigurálható porton elérhetővé teszi a külvilág számára (dependál a build-re) |
| *-clean | Törli az image-t |

Ezen kívül elérhetőek még az alábbi globális `make` parancsok:

| Parancs | Funkció |
| ------- | ------- |
| build-doc | Kigenerálja ezt a dokumentációt az alkalmazás gyökérkönyvtárában található `README.md` dokumentációjából a projektnek |
| compose | Egy fejlesztői docker compose-t indít, amiben a teszt konténerek alkotják az élessel identikus hálózatot (dependál minden komponens buildjére) |
| clean   | Törli az összes komponens image-t |

A fejlesztői docker compose hálózat leírása a `dev/docker-compose.yml` fájlban található meg. Az éles docker compose ezzel szemben csak szimplán az alkalmazás gyökérkönyvtárában `docker-compose.yml` néven.

### Validálás github környezetben

A komponensek Docker file-jai tartalmaznak referenciát komponensenként egy-egy `requirements.txt`-re, hogy könnyedén lehessen automatikusan telepíteni a dependenciákat.

Az akció minden commit esetén, ami a `main` branchen történik lefut:

1. A komponensekből (`backend`, `db_handler`, `frontend`) egyesével Docker image-eket hoz létre
2. Ezeket a Github Container Registry-be [felpusholja](https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions)
3. Teszteli az alkalmazás elindulását a compose fájl lefuttatásával

A github actions-ben az alábbi jobokat határoztam meg:

- build-frontend
- build-backend
- build-db-handler
- deploy-test

#### build-frontend job

- Checkout action segítségével letölti a kódbázist
- Futtat egy docker buildet, ahol label-nek az aktuális `GITHUB_RUN_ID`-t adja meg
- Bejelentkezik a `ghcr` docker registry-be a felhasználómmal
- Feltölti a létrejött image-t megtagelve a `github.ref` alapján

#### build-backend job

- Checkout action segítségével letölti a kódbázist
- Futtat egy docker buildet, ahol label-nek az aktuális `GITHUB_RUN_ID`-t adja meg
- Bejelentkezik a `ghcr` docker registry-be a felhasználómmal
- Feltölti a létrejött image-t megtagelve a `github.ref` alapján

#### build-db-handler job

- Checkout action segítségével letölti a kódbázist
- Futtat egy docker buildet, ahol label-nek az aktuális `GITHUB_RUN_ID`-t adja meg
- Bejelentkezik a `ghcr` docker registry-be a felhasználómmal
- Feltölti a létrejött image-t megtagelve a `github.ref` alapján

#### deploy-test

- Checkout action segítségével letölti a kódbázist
- Futtatja a docker compose fájlt

A `deploy-test` job dependál a build jobokra.

Az alkalmazás fejlesztése folyamán a github actions modularitásának köszönhetően további tesztelési lépések is könnyedén hozzáadhatóak.

[//]: # (## Futási környezet)

[//]: # (## Fejlesztett kód)
