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
kommersiella sammanhang, men att den inte kommer med några garantier för
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

Applikationen är baserad på webbramverket Django
(http://www.djangoproject.com/) och är skirven i programspråket Python.

Rader som börjar med "$" avser kommandon som skall utföras från ett
terminalfönster).

1. Installera programspråket Python 2.6 (Se http://www.python.org/download/).

2. Installera easy_install/setuptools (Se
http://pypi.python.org/pypi/setuptools och
http://peak.telecommunity.com/DevCenter/EasyInstall)

3. Installera Django
    $ easy_install django

4. Installera Sqllite 3 (Se http://www.sqlite.org/)

6. Öppna filen settings.py och modifiera vid behov de inställningar som börjar
med RINFO.

7. Installera databasschemat:
    $ python manage.py syncdb   

Om det inträffade ett fel behöver du eventuellt justera miljövariablen
PYTHONPATH så att den inkluderar katalogen i vilken rinfo-foreksriftshantering
ligger i. Om filerna till applikationen ligger i
c:\projekt\rinfo-foreksriftshantering behöver du lägga till c:\projekt i
PYTHONPATH.

Efter information att tabeller skapas skall du få en fråga om du vill skapa
en 'superuser'. Svara ja på frågan och ange information om användaren.

8. Starta den inbyggda webbservern:
    $ python manage.py runserver

9. Öppna webbläsaren med följande adress: http://127.0.0.1:8000/
Exempelwebbplatsen visas. För att redigera innehåll navigera till
http://127.0.0.1:8000/admin/ och logga in som den användare du skapade i steg 7.

10. Verifiera att applikationen är installerad korrekt genom att köra de
automatiska testerna med:
    $ python manage.py test

Får du problem med isntallationen se följande källor:

http://docs.djangoproject.com/en/dev/intro/install/



Nästa steg
----------

Applikationen illustrerar hur föreskrifter relateras till varandra och hur
metadata av olika slag kan fångas upp och presenteras på ett standardiserat
sätt. 

Om du vill kan du installera medföljande testdata genom att köra följande
kommande inifrånprojektkatalogen:

    $ python manage.py loaddata --settings=rinfo-foreskriftshantering.settings 
        rinfo\fixtures\exempeldata.json

...och sedan kopiera över PDF-dokumenten från mappen rinfo/fixtures till mappen
dokument.

Alternativt börjar du med att logga in i administrationsgränssnittet och skapa
lite grunddata (Författningssamling, några ämnesord och bemyndigandeparagrafer).



Applikationens delar
--------------------

Några saker att utgå från:

1. Filen urls.py visar vilka olika typer av länkar som webbplatsen hanterar.
Varje länkformat är kopplat till en metod i rinfo/views.py. 

2. I rinfo/models.py hittar du klasserna för de olika informationsobjekten.
Klassen Myndighetsforeskrift visar några olika typer av metadata och relationer
till andra objekt. 

3. Mallen templates/foreskrift_rdf.xml visar hur en grundläggande metadatapost
är uppbyggd.

4. Atomfeeden berättar om förändringar som skett med poster i samlingen. Feeden
finns på adressen http://127.0.0.1:8000/feed/. Nya poster, uppdateringar av
poster (skall inte ske om man inte gjort fel tidigare) och radering av poster
(i händelse av en grov felpublicering) gör att ett AtomEntry-objekt skapas.
Dessa sammanställs i en feed i templates/atomfeed.xml.

Eftersom applikationen är baserad på ramverket Django kan det vara bra att
känna till grunderna om detta. Mer information om Django hittar du här:
http://docs.djangoproject.com/en/dev/intro/overview/
