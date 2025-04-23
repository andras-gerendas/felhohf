# VITMMB11 - Házi Feladat

## Bevezető

A jelen dokumentum a Felhők hálózati szolgáltatásai laboratórium (VITMMB11) tantárgy házi feladatának fejlesztői dokumentációja.

## Feladatkiírás

Egy olyan web szolgáltatás létrehozása, ami az alábbi funkciókat látja el:

- Kép és hozzá tartozó leírás feltöltése (kép és leírás páros tárolás)
- A feltöltött képen automatikus ember detektálás és a megtalált emberek (vagy azok arcainak) bekeretezésével a kép megjelenítése a weboldalon
- A weboldal felhasználói képesek legyenek feliratkozni az oldalra, azaz kapjanak értesítést az összes eddigi és az új feltöltött képekről úgy, hogy kiküldésre kerül számukra a képhez tartozó leírás és a rendszer által detektált emberek száma a feltöltött képen

## CI/CD környezet

Github actions-t használok a CI/CD lépések végrehajtására a széleskörű használata miatt, docker compose-t az elkészült alkalmazás tesztelésére, mivel a github actions környezetben is [elérhető](https://github.com/marketplace/actions/docker-compose-action).

A komponensek docker file-jai tartalmaznak referenciát egy requirements.txt-re, hogy könnyedén lehessen telepíteni a dependenciákat.

Az akció minden commit esetén, ami a main-en történik lefut. A komponensekből (backend, db_handler, frontend) egyesével docker image-eket hoz létre, majd ezeket a Github Container Registry-be [felpusholja](https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions).

A Docker compose file-ban a jelenlegi image-re mutató linkek vannak, így a futást követően a github actions is a legújabb image-ekhez fér hozzá, illetve lokálisan futtatva is a legújabb image-eket indítja el a docker compose.

A docker compose fájlban a konténerek egy hálózaton belül vannak és csak a frontend-nek van a külvilág felé nyitott portja.

[//]: # (## Webszolgáltatás architektúra)

[//]: # (## Futási környezet)

[//]: # (## Fejlesztett kód)

[//]: # (## Adatszerkezetek)
