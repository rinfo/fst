
[![Build Status](https://travis-ci.org/rinfo/fst.svg?branch=develop)](https://travis-ci.org/rinfo/fst) _FST source code is built and tested nightly and on every commit._

For current technical documentation in English, see [FST wiki](https://github.com/rinfo/fst/wiki)._


#FST (Föreskriftshantering som tjänst)#

FST är en webbtjänst för att publicera rättsinformationsdokument och dess metadata. Tjänsten har utvecklats för svenska myndigheter som vill publicera föreskrifter och andra dokument som öppna data. 

FST är ett komplement till befintliga IT-lösningar: användare laddar upp befintliga dokument och tillhörande metadata i ett enkelt webbgränssnitt. Den inmatade informationen omvandlas automatiskt till ett strukturerat format och publiceras via ett ATOM/RSS-nyhetsflöde.


##Att komma igång och använda FST##

Användarhandledningen är till för dig som ska använda FST när tjänsten är installerad.
Texten är på svenska och riktar sig till jurister, webbredaktörer och andra handläggare:

[Användarhandledning](https://github.com/rinfo/fst/blob/develop/doc/anvandarhandledning_fst.pdf)


Här finns en kort guide för den som vill installera och provköra FST på sin egen dator. 
Guiden är på engelska och förutsätter viss vana vid att installera programvara:

[Installera FST på din egen dator](https://github.com/rinfo/fst/wiki/Install-on-development-machine)


För den tekniskt kunnige som vill installera FST på en publik server har vi en detaljerad guide på engelska:  

[Installera FST som tjänst på en server](https://github.com/rinfo/fst/wiki/Server-installation-FST) 

##Dokumentation##

Den aktuella tekniska dokumentationen finns på [FST:s wiki](https://github.com/rinfo/fst/wiki). 

FST är implementerat med webbramverket [Django](https://www.djangoproject.com/), ett beprövat ramverk med öppen källkod och utmärkt [dokumentation](https://docs.djangoproject.com/en/1.10/). Genom att följa [denna guide](https://docs.djangoproject.com/en/1.10/intro/tutorial01/) får du en god överblick av hur FST:s kod fungerar i praktiken. Här finns också en introduktion till [Django admin](https://docs.djangoproject.com/en/1.10/ref/contrib/admin/), som vi har använt för FST:s användargränssnitt.

De grundläggande tekniska specifikationer som FST utgår från finns här: http://dev.lagrummet.se/dokumentation/#specifikationer. 
Centrala delar är [begreppsmodellen för svensk rättsinformation](http://dev.lagrummet.se/dokumentation/model.pdf), [användandet av nyhetsflöden för publicering](http://dev.lagrummet.se/dokumentation/system/atom-insamling.pdf) och [principerna för att skapa persistenta identifierare](http://dev.lagrummet.se/dokumentation/system/uri-principer.pdf). Dessa tre styr på ett grundläggande sätt den tekniska utformningen av FST. 

_Observera att projektdokumentationen från Rättsinformationsprojektet inte är uppdaterad._

##Kontakt##

För mer information kontakta helene.lundgren@dom.se.

##Licens##
 
FST ges ut under BSD-licensen. Det betyder att du får
använda och vidareutveckla koden om du vill, även i kommersiella
sammanhang, men att den inte kommer med några garantier för funktion
eller lämplighet. Se [BSD-licensen](https://github.com/rinfo/fst/blob/master/LICENSE.TXT) för mer information om möjligheter
att använda dig av programkoden.

