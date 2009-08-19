# coding=utf-8
from django.test import TestCase
import rinfo.models
from xml.dom.minidom import parse, parseString
import hashlib
import os
import shutil

class RinfoTestCase(TestCase):
    # Ladda exempeldata från rinfo/fixtures/exempeldata.json innan test startar
    fixtures = ['exempeldata.json']

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__))
        testdocs = os.path.join(base, "../dokument_test")

        # Skapa mapp för testdokument
        if not os.path.exists(testdocs):
            os.mkdir(testdocs)

        # Kopiera filer från fixtures till dokument_test
        shutil.copy(os.path.join(base, "fixtures/EXFS-2009-1.pdf"), testdocs)
        shutil.copy(os.path.join(base, "fixtures/EXFS-2009-1-bilaga.pdf"), testdocs)
        shutil.copy(os.path.join(base, "fixtures/EXFS-2009-2.pdf"), testdocs)
        shutil.copy(os.path.join(base, "fixtures/EXFS-2009-3.pdf"), testdocs)

    def tearDown(self):
        base = os.path.join(os.path.dirname(__file__))
        testdocs = os.path.join(base, "../dokument_test")

        # Släng testfiler
        shutil.rmtree(testdocs)

    # Verifiera att startsidan kan läsas och att den visar de tre
    # exempelföreskrifterna
    def test_startsida(self):
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, "2009:1 Föreskrift om administration hos statliga myndigheter")
        self.assertContains(response, "2009:2 Föreskrift om ändring i föreskrift 2009:1 om administration hos statliga myndigheter")
        self.assertContains(response, "2009:3 Föreskrift om budgetering hos statliga myndigheter")


    # Verifiera att sidan för en enskild föreskrift visas
    def test_foreskrift(self):
        response = self.client.get('/publ/EXFS/2009:1/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, "<h1>2009:1 Föreskrift om administration hos statliga myndigheter")


    # Verifiera att publicerad föreskrift har metadata i RDF-format
    def test_rdfdata(self):
        response = self.client.get('/publ/EXFS/2009:1/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/rdf+xml; charset=utf-8')
        self.assertContains(response, "Föreskrift om administration hos statliga myndigheter")
        self.assertContains(response, "<dces:subject xml:lang=\"sv\">Administration</dces:subject>")


    # Verifiera att publicerad föreskrift har information om relation till EG-direktiv
    def test_egdirektiv(self):
        response = self.client.get('/publ/EXFS/2009:1/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/rdf+xml; charset=utf-8')
        self.assertContains(response, "<genomforDirektiv rdf:resource=\"http://rinfo.lagrummet.se/ext/eur-lex/31979L0409\"/>")

    # Verifiera att publicerad föreskrift 2009:2 har information om omtryck
    def test_omtryck(self):
        response = self.client.get('/publ/EXFS/2009:2/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/rdf+xml; charset=utf-8')
        self.assertContains(response, "<omtryckAv rdf:resource=\"http://rinfo.lagrummet.se/publ/exfs/2009:1\"/>")

        # och att omtrycksinformation saknas om det inte är ett omtryck
        response = self.client.get('/publ/EXFS/2009:3/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/rdf+xml; charset=utf-8')
        self.assertNotContains(response, "<omtryckAv")


    # Verifiera att feed kan läsas och att den innehåller tre <entry>-poster
    def test_atomfeed(self):
        response = self.client.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/atom+xml; charset=utf-8')
        self.assertContains(response, "<entry>", 3)


    # Verifiera att checksumma för rdf-metadata angiven i atomfeed är korrekt
    def test_rdfmd5_from_feed(self):
        NS_ATOM="http://www.w3.org/2005/Atom"
        NS_ATOMLE="http://purl.org/atompub/link-extensions/1.0"

        response = self.client.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)

        # Hämta md5-summa för entry för föreskrift 2009:1
        dom=parseString(response.content)
        avlast_md5=""
        for link in dom.getElementsByTagNameNS(NS_ATOM, 'link'):
            if link.getAttribute("href")=="/publ/EXFS/2009:1/rdf":
                avlast_md5=link.getAttributeNS(NS_ATOMLE, "md5")

        # Jämför avläst md5summa med egenberäknad
        response = self.client.get('/publ/EXFS/2009:1/rdf')
        md5=hashlib.md5()
        md5.update(response.content)
        beraknad_rdfmd5=md5.hexdigest()
        self.assertEqual(beraknad_rdfmd5, avlast_md5)
