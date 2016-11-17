[![Build Status](https://travis-ci.org/rinfo/fst.svg?branch=develop)](https://travis-ci.org/rinfo/fst) _Källkoden byggs och testas varje natt_

##FST (Föreskriftshantering som tjänst)##

FST är en webbtjänst för att publicera rättsinformationsdokument och dess metadata. Tjänsten har utvecklats för svenska myndigheter som vill publicera föreskrifter och andra dokument som öppna data. 

FST är ett komplement till befintliga IT-lösningar: användare laddar upp befintliga dokument och tillhörande metadata i ett enkelt webbgränssnitt. Den inmatade informationen omvandlas automatiskt till ett strukturerat format och publiceras via ett ATOM/RSS-nyhetsflöde.


###Att komma igång och använda FST###

Här finns en kort guide som beskriver hur du installerar FST på din egen dator för att provköra eller kanske göra en demo. _Text på engelska_ 

[Installera FST på en utvecklingsmaskin](https://github.com/rinfo/fst/wiki/Install-on-development-machine)

Användarhandledningen är till för dig som vill använda FST när tjänsten är installerad. 
Texten är på svenska och riktar sig till handläggare och jurister. 

[Användarhandledning](https://github.com/rinfo/fst/blob/develop/doc/anvandarhandledning_fst.pdf)

Det finns också en detaljerad guide som beskriver hur du installerar FST som tjänst på en publik server. _Text på engelska_ 

[Installera FST som tjänst på en server](https://github.com/rinfo/fst/wiki/Server-installation-FST)

###Mer information om FST###

Mer teknisk information finns på [FST:s wiki](https://github.com/rinfo/fst/wiki). _For detailed technical information, see the [FST Wiki](https://github.com/rinfo/fst/wiki)._

De tekniska specifikationer som FST utgått ifrån finns här: http://dev.lagrummet.se/dokumentation/#specifikationer. 
Notera särskilt ([begreppsmodellen för svensk rättsinformation](http://dev.lagrummet.se/dokumentation/model.pdf)), [användandet av nyhetsflöden för publicering](http://dev.lagrummet.se/dokumentation/system/atom-insamling.pdf) och [principer för att skapa persistenta identifierare (URI:er)](http://dev.lagrummet.se/dokumentation/system/uri-principer.pdf), som är den tekniska grunden för FST. _Observera att den icke-tekniska projektdokumentationen från Rättsinformationsprojektet inte är uppdaterad i alla delar._

FST är implementerat med webbramverket [Django](https://www.djangoproject.com/), som är ett beprövat ramverk med öppen källkod och utmärkt [dokumentation](https://docs.djangoproject.com/en/1.10/).

[Denna guide](https://docs.djangoproject.com/en/1.10/intro/tutorial01/) ger en utmärkt introduktion till hur FST:s kod fungerar i praktiken. Lägg särskilt märke till vad som skrivs om [Django admin](https://docs.djangoproject.com/en/1.10/ref/contrib/admin/), som vi använt för FST:s användargränssnitt.


###Licens###
 
FST ges ut under BSD-licensen. Det betyder att du får
använda och vidareutveckla koden om du vill, även i kommersiella
sammanhang, men att den inte kommer med några garantier för funktion
eller lämplighet. Se BSD-licensen för mer information om möjligheter
att använda dig av programkoden.

