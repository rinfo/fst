Om exempelapplikationen
-----------------------

Syftet med denna exempelapplikation är att illustrera i programkod hur man kan
implementera de format som rekommenderas av Rättsinformationsprojektet för den
mest grundläggande nivån av publicering av myndighetsföreskrifter. Tanken är
inte att tillhandahålla ett färdigt system för rättsinformationshantering.

Applikationen har två delar; 1) en administrationsdel i vilken man hanterar
ämnesord, föreskrifter och grunddata och 2) en exempelwebbplats som visar
informationen för potentiella besökare. 

Applikationem är byggd på webbramverket Django som ges ut under BSD-licensen.
Det betyder att du får använda och vidareutveckla koden om du vill, även i
kommersiella sammanhang, men att den inte kommer med n�gra garantier för
funktion eller lämplighet. Se BSD-licensen för mer information om möjligheter
att använda dig av programkoden. 

Vi är dock tacksamma för feedback och rapporter om eventuella fel. För mer
information om rättsinformationsprojektet kontakta Staffan Malmgren, telefon 08-561
66 921 på Domstolsverket eller besök projektbloggen: 

http://rinfoprojektet.wordpress.com/

Mer information om rättsinformationsprojektet, inklusive specifikationer, finns på:

http://dev.lagrummet.se/dokumentation/


Installationsansvisningar
-------------------------

Applikationen �r baserad p� webbramverket Django
(http://www.djangoproject.com/) och �r skirven i programspr�ket Python.

Rader som b�rjar med "$" avser kommandon som skall utf�ras fr�n ett
terminalf�nster).

1. Installera programspr�ket Python 2.6 (Se http://www.python.org/download/).

2. Installera easy_install/setuptools (Se
http://pypi.python.org/pypi/setuptools och
http://peak.telecommunity.com/DevCenter/EasyInstall)

3. Installera Django
    $ easy_install django

4. Installera Sqllite 3 (Se http://www.sqlite.org/)

6. �ppna filen settings.py och modifiera vid behov de inst�llningar som b�rjar
med RINFO.

7. Installera databasschemat:
    $ python manage.py syncdb   

Om det intr�ffade ett fel beh�ver du eventuellt justera milj�variablen
PYTHONPATH s� att den inkluderar katalogen i vilken rinfo-foreksriftshantering
ligger i. Om filerna till applikationen ligger i
c:\projekt\rinfo-foreksriftshantering beh�ver du l�gga till c:\projekt i
PYTHONPATH.

Efter information att tabeller skapas skall du f� en fr�ga om du vill skapa
en 'superuser'. Svara ja p� fr�gan och ange information om anv�ndaren.

8. Starta den inbyggda webbservern:
    $ python manage.py runserver

9. �ppna webbl�saren med f�ljande adress: http://127.0.0.1:8000/
Exempelwebbplatsen visas. F�r att redigera inneh�ll navigera till
http://127.0.0.1:8000/admin/ och logga in som den anv�ndare du skapade i steg 7.

10. Verifiera att applikationen �r installerad korrekt genom att k�ra de
automatiska testerna med:
    $ python manage.py test

F�r du problem med isntallationen se f�ljande k�llor:

http://docs.djangoproject.com/en/dev/intro/install/



N�sta steg
----------

Applikationen illustrerar hur f�reskrifter relateras till varandra och hur
metadata av olika slag kan f�ngas upp och presenteras p� ett standardiserat
s�tt. 

Om du vill kan du installera medf�ljande testdata genom att k�ra f�ljande
kommando inifr�n projektkatalogen:

    $ python manage.py loaddata --settings=rinfo-foreskriftshantering.settings \
                                           rinfo/fixtures/exempeldata.json

...och sedan kopiera �ver PDF-dokumenten fr�n mappen rinfo/fixtures till mappen
dokument:

    $ cp rinfo/fixtures/*.pdf dokument/

Alternativt b�rjar du med att logga in i administrationsgr�nssnittet och skapa
lite grunddata (F�rfattningssamling, n�gra �mnesord och bemyndigandeparagrafer).



Applikationens delar
--------------------

N�gra saker att utg� fr�n:

1. Filen urls.py visar vilka olika typer av l�nkar som webbplatsen hanterar.
Varje l�nkformat �r kopplat till en metod i rinfo/views.py. 

2. I rinfo/models.py hittar du klasserna f�r de olika informationsobjekten.
Klassen Myndighetsforeskrift visar n�gra olika typer av metadata och relationer
till andra objekt. 

3. Mallen templates/foreskrift_rdf.xml visar hur en grundl�ggande metadatapost
�r uppbyggd.

4. Atomfeeden ber�ttar om f�r�ndringar som skett med poster i samlingen. Feeden
finns p� adressen http://127.0.0.1:8000/feed/. Nya poster, uppdateringar av
poster (skall inte ske om man inte gjort fel tidigare) och radering av poster
(i h�ndelse av en grov felpublicering) g�r att ett AtomEntry-objekt skapas.
Dessa sammanst�lls i en feed i templates/atomfeed.xml.

Eftersom applikationen �r baserad p� ramverket Django kan det vara bra att
k�nna till grunderna om detta. Mer information om Django hittar du h�r:
http://docs.djangoproject.com/en/dev/intro/overview/
