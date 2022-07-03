# Aplikace a script podle zadání
- Python 3.10.4
- psql (14.4 (Ubuntu 14.4-1.pgdg22.04+1))

## Obsah (struktura repozitáře)
- python
    - app
        - __init__.py
        - ArgParser.py - obsahuje třídu parsující argumenty (modul)
        - file-client.py - klientská aplikace
        - grpc_server.py - jednoduchý server pro základní testování
        - rest_server.py - jednoduchý server pro základní testování
        - service_file_pb2_grpc.py - specifikace pro grpc server
        - service_file_pb2.py - specifikace pro grpc server
        - test_file-client.py - unit testy
        - test.txt - soubor jehož obsah je vracen rest serverem (pro testování)
    - README.rts - popis zadané aplikace
    - rest_file.rts - popis rest api
    - service_file.proto - popis grpc
 - sql
    - script
        - script.sql
    - postgresql_task.rts

## Python knihovny
- re
- sys
- requests
- json
- grpc
- unittest
- importlib
- threading
- time
- io
- os

## Příklad spuštění scriptů
python3 file-client.py --base-url=http://127.0.0.1:5000/ --backend=rest read 9c465aa7-05fd-46eb-b759-344c48abc85f
python3 test_file-client.py

## Aplikace
Implementován jak rest, tak grpc. Lze rozšířit, například u restu by šlo implementovat více HTTP metod a také reakce na víc různých status kódů.
Vyvíjeno a testováno na linuxu (Ubuntu 22.04 LTS). Grpc také otestováno na windows.

## Testy
Jednoduché unit testy. Je dobré podotknout, že unit testy pro ArgParser by se ideálně měli rozdělit pro test jednotlivých metod. 
Nechtěl jsem se ale tolik zaměřovat na parsovaní argumentů, tak je to zjednodušené. Grpc a rest jsou testovány pouze na lokálu, cež není ideální.
Testovací grpc server se při spuštění testů spustí paralelně, ale rest je nutné předem spustit pomocí flasku, jinak test selže.

## Postgresql script
Jednoduchý script pro vytvoření požadovaných tabulek. Další možná omezení jsou například, že by nešlo mít čas ukončení před začátkem (jak u domény, tak u flagů).
Dalším omezením je samozřejmě, že by začátek flagu nemohl být před začátkem registrace domény a to samé pro ukončení. Také omezení překrývání flagů.
Dále by se mohla třeba kontrolovat validita názvů a podobně.

## Autor
Jaromír Franěk (xfrane16)