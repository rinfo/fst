# -*- coding: utf-8 -*-
from django.test import TestCase
import fst_web.fs_doc.models
from xml.dom.minidom import parse, parseString
import hashlib
import os
import shutil

class RinfoTestCase(TestCase):
    # Initialize with sample data from fsdoc/fixtures/exempeldata.json
    fixtures = ['exempeldata.json']

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__))
        testdocs = os.path.join(base, "../dokument_test")

        # Create temporary folder for testing documents
        if not os.path.exists(testdocs):
            os.mkdir(testdocs)

        # Move documents from fixtures to temporary test folder
        shutil.copy(os.path.join(base, 
                                 "fixtures/foreskrift/EXFS-2009-1.pdf"), testdocs)
        shutil.copy(os.path.join(base, 
                                 "fixtures/bilaga/EXFS-2009-1-bilaga.pdf"), testdocs)
        shutil.copy(os.path.join(base, 
                                 "fixtures/foreskrift/EXFS-2009-2.pdf"), testdocs)
        shutil.copy(os.path.join(base, 
                                 "fixtures/foreskrift/EXFS-2009-3.pdf"), testdocs)

    def tearDown(self):
        base = os.path.join(os.path.dirname(__file__))
        testdocs = os.path.join(base, "../dokument_test")

        # Delete temporary testfolder
        shutil.rmtree(testdocs)
        
    # Verify that start page loads and displays correct sample documents
    def test_startsida(self):
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, 
                            "EXFS 2009:1 Föreskrift om administration hos statliga myndigheter")
        self.assertContains(response, 
                            "EXFS 2009:2 Föreskrift om ändring i föreskrift 2009:1 om administration hos statliga myndigheter")
        self.assertContains(response, 
                            "EXFS 2009:3 Föreskrift om budgetering hos statliga myndigheter")

    # Verify that detail page for document 'Myndighetsforeskrift' loads
    # with correct sample data
    def test_foreskrift(self):
        response = self.client.get('/publ/exfs/2009:1/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, 
                            "<h1>EXFS 2009:1 Föreskrift om administration hos statliga myndigheter")

    # Verify that published 'Myndighetsforeskrift' document has 
    # correct RDF metadata' for keywords (Django class'Amnesord')
    def test_rdfdata(self):
        response = self.client.get('/publ/exfs/2009:1/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 
                         'application/rdf+xml; charset=utf-8')
        self.assertContains(response, 
                            "Föreskrift om administration hos statliga myndigheter")
        self.assertContains(response, 
                            "<dces:subject xml:lang=\"sv\">Administration</dces:subject>")

    # Verify that published 'Myndighetsforeskrift' document has 
    # correct RDF metadata for legal directives (Django class 'CelexReferens')
    def test_egdirektiv(self):
        response = self.client.get('/publ/exfs/2009:1/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 
                         'application/rdf+xml; charset=utf-8')
        self.assertContains(response, 
                            "<genomforDirektiv rdf:resource=\"http://rinfo.lagrummet.se/ext/eur-lex/31979L0409\"/>")

    # Verify that published 'Myndighetsforeskrift' document has 
    # correct RDF metadata for property 'omtryck'
    def test_omtryck(self):
        response = self.client.get('/publ/exfs/2009:2/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'],
                         'application/rdf+xml; charset=utf-8')
        self.assertContains(response, "<omtryckAv rdf:resource=\"http://rinfo.lagrummet.se/publ/exfs/2009:1\"/>")

        # No metadata should be genereated unless property 'omtryck' is true
        response = self.client.get('/publ/exfs/2009:3/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 
                         'application/rdf+xml; charset=utf-8')
        self.assertNotContains(response, "<omtryckAv")

    # Verify that an empty Atom feed is created and can be read
    # NOTE - Atom feed is empty until entries are explicitly published
    def test_atomfeed(self):
        response = self.client.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 
                         'application/atom+xml; charset=utf-8')
        # No entries yet
        self.assertContains(response, "<entry>", 0)

    # Verify that checksum of document in Atom feed is correct
    # NOTE - Atom feed is empty until entries are explicitly published
    def test_rdfmd5(self):
        NS_ATOM="http://www.w3.org/2005/Atom"
        NS_ATOMLE="http://purl.org/atompub/link-extensions/1.0"
        # Get Atom feed
        response = self.client.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)

        # Get links to documents in Atom feed
        dom = parseString(response.content)
        links = dom.getElementsByTagNameNS(NS_ATOM, 'link')
        avlast_md5 = ""           
        for link in links:
            # Look for specific sample document in feed
            if link.getAttribute("href")=="/publ/exfs/2009:1/rdf":
                # Read document checksum from feed
                avlast_md5 = link.getAttributeNS(NS_ATOMLE, "md5")
                # Compare checksum from feed with checksum of current document
                response = self.client.get('/publ/exfs/2009:1/rdf')
                md5=hashlib.md5()
                md5.update(response.content)
                beraknad_rdfmd5=md5.hexdigest()
                self.assertEqual(beraknad_rdfmd5, avlast_md5)