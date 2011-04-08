Om FST (Föreskriftshantering som tjänst)
-----------------------

Syftet med denna applikation är att göra det möjligt för myndigheter att publicera sin information till rättsinformationssystemet genom ett lättanvänt webbgränssnitt. Det passar myndigheter som inte har möjlighet att integrera sin befintliga lösning för publicering av författning med rättsinformationssystemet, eller som saknar ett sådant system överhuvudtaget.

Domstolsverket kommer, som samordningsmyndighet för rättsinformationssystemet, att drifta en instans av systemet för varje myndighet som vill använda det. En myndighet behöver alltså inte själv sätta upp systemet, utan kan använda Domstolsverkets befintliga tjänst (därav systemets namn: "..som tjänst").

Applikationen har tre delar;

1) en administrationsdel i vilken man hanterar föreskrifter, ämnesord och   grundläggande metadata, 
2) en exempelwebbplats som visar informationen för potentiella besökare, och
3) publicering av postförteckning, metadata och dokumentinnehåll enligt rättsinformationssystemet angivna standarder.

Applikationen är byggd på webbramverket Django som ges ut under BSD-licensen.
Det betyder att du får använda och vidareutveckla koden om du vill, även i
kommersiella sammanhang, men att den inte kommer med några garantier för
funktion eller lämplighet. Se BSD-licensen för mer information om möjligheter
att använda dig av programkoden. 

Vi är dock tacksamma för feedback och rapporter om eventuella fel. För mer
information om rättsinformationsprojektet kontakta Staffan Malmgren (staffan.malmgren@dom.se) eller besök projektbloggen: 

http://rinfoprojektet.wordpress.com/

Mer information om rättsinformationsprojektet, inklusive specifikationer, finns på:

http://dev.lagrummet.se/dokumentation/


Installationsansvisningar
-------------------------

Applikationen är baserad på webbramverket Django
(http://www.djangoproject.com/) och är skirven i programspråket Python.

Rader som börjar med "$" avser kommandon som skall utföras från ett
terminalfönster).

1. Installera programspråket Python 2.6 eller senare (Se http://www.python.org/download/). Python 3.* stöds i dagsläget inte.

2. Installera easy_install/setuptools (Se
http://pypi.python.org/pypi/setuptools och
http://peak.telecommunity.com/DevCenter/EasyInstall)

3. Installera Django

    $ easy_install django

4. Installera Sqllite 3 (Se http://www.sqlite.org/)

5. Öppna filen settings.py och modifiera vid behov de inställningar som börjar
med RINFO.

6. Installera databasschemat:

    $ python manage.py syncdb 

Om det inträffade ett fel behöver du eventuellt justera miljövariablen
PYTHONPATH så att den inkluderar katalogen i vilken rinfo-foreksriftshantering
ligger i. Om filerna till applikationen ligger i
c:\projekt\fst behöver du lägga till c:\projekt i
PYTHONPATH.

Efter information att tabeller skapas skall du få en fråga om du vill skapa
en 'superuser'. Svara ja på frågan och ange information om användaren.

7. Starta den inbyggda webbservern:

    $ python manage.py runserver

8. Öppna webbläsaren med följande adress: http://127.0.0.1:8000/
Exempelwebbplatsen visas. För att redigera innehåll navigera till
http://127.0.0.1:8000/admin/ och logga in som den användare du skapade i steg 7.

9. Verifiera att applikationen är installerad korrekt genom att köra de
automatiska testerna med:

    $ python manage.py test

Får du problem med installationen se följande källor:

http://docs.djangoproject.com/en/dev/intro/install/



Nästa steg
----------

Applikationen illustrerar hur föreskrifter relateras till varandra och hur
metadata av olika slag kan fångas upp och presenteras på ett standardiserat
sätt. 

Om du vill kan du installera medföljande testdata genom att köra följande
kommando inifrån projektkatalogen:

    $ python manage.py loaddata --settings=fst_web.settings \
                                           fs_doc/fixtures/exempeldata.json

...och sedan kopiera över PDF-dokumenten från mappen fst_web/fs_doc/fixtures till mappen dokument:

    $ cp fs_doc/fixtures/*.pdf uploads/foreskrift

Alternativt börjar du med att logga in i administrationsgränssnittet och skapa
lite grunddata (en författningssamling, några bemyndiganden och eventuellt några ämnesord).

Egna experiment
---------------

Om du senare vill spara din aktuella databas till en fil använder du detta kommando:

    $ python manage.py dumpdata --indent 4 --exclude admin --exclude sessions.session --exclude contenttypes.contenttype  --exclude fs_doc.atomentry --exclude fs_doc.rdfpost > fs_doc/fixtures/egna_data.json

Applikationens delar
--------------------

Några saker att utgå från:

1. Filen urls.py visar vilka olika typer av länkar som webbplatsen hanterar.
Varje länkformat är kopplat till en metod i rinfo/views.py. 

2. I fst_web/models.py hittar du klasserna för de olika informationsobjekten.
Klassen Myndighetsforeskrift visar några olika typer av metadata och relationer
till andra objekt. 

3. Mallen fst_web/templates/foreskrift_rdf.xml visar hur en grundläggande metadatapost är uppbyggd.

4. Atomfeeden berättar om förändringar som skett med poster i samlingen. Feeden
finns på adressen http://127.0.0.1:8000/feed/. Nya poster, uppdateringar av
poster (skall inte ske om man inte gjort fel tidigare) och radering av poster
(i händelse av en grov felpublicering) går att ett AtomEntry-objekt skapas.
Dessa sammanställs i en feed i fst_web/templates/atomfeed.xml.

Eftersom applikationen är baserad på ramverket Django kan det vara bra att
känna till grunderna om detta. Mer information om Django hittar du här:
http://docs.djangoproject.com/en/dev/intro/overview/
