[![Build Status](https://travis-ci.org/rinfo/fst.svg?branch=develop)](https://travis-ci.org/rinfo/fst) _Källkoden byggs och testas varje natt_

##FST (Föreskriftshantering som tjänst)##

FST är en webbtjänst för att publicera rättsinformationsdokument och dess metadata. Tjänsten har utvecklats för svenska myndigheter som vill publicera föreskrifter och andra dokument som öppna data. 

FST är ett komplement till befintliga IT-lösningar: användare laddar upp befintliga dokument och tillhörande metadata i ett enkelt webbgränssnitt. Den inmatade informationen omvandlas automatiskt till ett strukturerat format och publiceras via ett ATOM/RSS-nyhetsflöde.


###Att komma igång och använda FST###

Här finns en kort guide som beskriver hur du installerar FST på din egen dator för att provköra eller kanske göra en demo:

[Installera FST på en utvecklingsmaskin](https://github.com/rinfo/fst/wiki/Install-on-development-machine) _engelsk text_ 

Användarhandledningen är till för dig som vill använda FST när tjänsten är installerad. 
Texten riktar sig till handläggare och jurister:

[Användarhandledning](https://github.com/rinfo/fst/blob/develop/doc/anvandarhandledning_fst.pdf)

För den som vill installera FST som tjänst på en publik server finns en detaljerad guide:  

[Installera FST som tjänst på en server](https://github.com/rinfo/fst/wiki/Server-installation-FST) _engelsk text_

###Mer information om FST###

FST är implementerat med webbramverket [Django](https://www.djangoproject.com/), som är ett beprövat ramverk med öppen källkod och utmärkt [dokumentation](https://docs.djangoproject.com/en/1.10/).

[Denna guide](https://docs.djangoproject.com/en/1.10/intro/tutorial01/) ger en utmärkt introduktion till hur FST:s kod fungerar i praktiken. Lägg särskilt märke till vad som skrivs om [Django admin](https://docs.djangoproject.com/en/1.10/ref/contrib/admin/), som vi använt för FST:s användargränssnitt.

Den tekniska dokumentationen finns på [FST:s wiki](https://github.com/rinfo/fst/wiki). _For detailed technical documentation, see the [FST Wiki](https://github.com/rinfo/fst/wiki)._

De tekniska specifikationer som FST utgått ifrån finns här: http://dev.lagrummet.se/dokumentation/#specifikationer. 
De centrala delarna är [begreppsmodell för svensk rättsinformation](http://dev.lagrummet.se/dokumentation/model.pdf), [användande av nyhetsflöden för publicering](http://dev.lagrummet.se/dokumentation/system/atom-insamling.pdf) och [principer för att skapa för persistenta identifierare](http://dev.lagrummet.se. Dessa tre är grunden för den tekniska utformningen av FST. 

_Observera att den icke-tekniska projektdokumentationen från Rättsinformationsprojektet inte är uppdaterad i alla delar._

###Licens###
 
FST ges ut under BSD-licensen. Det betyder att du får
använda och vidareutveckla koden om du vill, även i kommersiella
sammanhang, men att den inte kommer med några garantier för funktion
eller lämplighet. Se BSD-licensen för mer information om möjligheter
att använda dig av programkoden.

