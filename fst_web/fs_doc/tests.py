# -*- coding: utf-8 -*-
import hashlib
import os
import shutil
from xml.dom.minidom import parse, parseString
from django.test import TestCase
from rdflib import Graph, Literal, URIRef, RDF
from fst_web.fs_doc import models
from fst_web.fs_doc.admin import generate_atom_entry_for
from fst_web.fs_doc.rdfviews import DCT, DCES, FOAF, RPUBL, RINFO_BASE


NS_ATOM = "http://www.w3.org/2005/Atom"
NS_ATOMLE = "http://purl.org/atompub/link-extensions/1.0"


class WebTestCase(TestCase):
    # Sample data loaded from ./fixtures/
    fixtures = ['exempeldata.json']

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__))
        testdocs = os.path.join(base, "../dokument_test")

        # Create temporary folder for testing documents
        if not os.path.exists(testdocs):
            os.mkdir(testdocs)

        # Move documents from fixtures to temporary test folder
        shutil.copy(os.path.join(base, "fixtures/foreskrift/EXFS-2009-1.pdf"),
                    testdocs)
        shutil.copy(os.path.join(base, "fixtures/bilaga/EXFS-2009-1-bilaga.pdf"),
                    testdocs)
        shutil.copy(os.path.join(base, "fixtures/foreskrift/EXFS-2009-2.pdf"),
                    testdocs)
        shutil.copy(os.path.join(base, "fixtures/foreskrift/EXFS-2009-3.pdf"),
                    testdocs)

    def tearDown(self):
        base = os.path.join(os.path.dirname(__file__))
        testdocs = os.path.join(base, "../dokument_test")

        # Delete temporary testfolder
        shutil.rmtree(testdocs)

    def test_startsida(self):
        """Verify that start page loads and displays correct sample documents"""

        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response,
                "EXFS 2009:1 Föreskrift om administration hos statliga myndigheter")
        self.assertContains(response,
                "EXFS 2009:2 Föreskrift om ändring i föreskrift 2009:1 om "
                "administration hos statliga myndigheter")
        self.assertContains(response,
                "EXFS 2009:3 Föreskrift om budgetering hos statliga myndigheter")

    def test_foreskrift(self):
        """Verify that detail page for document 'Myndighetsforeskrift' loads
        with correct sample data"""

        response = self.client.get('/publ/exfs/2009:1/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response,
                "<h1>EXFS 2009:1 Föreskrift om administration hos statliga myndigheter")

    def test_get_rdf(self):
        """Verify that published 'Myndighetsforeskrift' document has RDF
        metadata"""
        # Generate an RDFPost since it's not included in the fixture
        foreskrift = models.Myndighetsforeskrift.objects.get(
                forfattningssamling__slug="exfs", arsutgava="2009", lopnummer="1")
        # TODO: this will change to "on publish"
        generate_atom_entry_for(foreskrift)

        response = self.client.get('/publ/exfs/2009:1/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'],
                         'application/rdf+xml; charset=utf-8')


class FeedTestCase(TestCase):
    # Sample data loaded from ./fixtures/
    fixtures = ['exempeldata.json']

    def test_empty_feed(self):
        """Verify that an empty Atom feed is created and can be read NOTE -
        Atom feed is empty until entries are explicitly published"""

        response = self.client.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'],
                         'application/atom+xml; charset=utf-8')
        dom = parseString(response.content)
        # One feed element
        self.assertEquals(len(dom.getElementsByTagNameNS(NS_ATOM, 'feed')), 1)
        # No entries yet
        self.assertFalse(dom.getElementsByTagNameNS(NS_ATOM, 'entry'))

    def test_entry_link_md5(self):
        """Verify that checksum of document in Atom feed is correct NOTE - Atom
        feed is empty until entries are explicitly published"""

        # Get Atom feed
        response = self.client.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)

        # TODO: publish a document to produce an entry, then run this
        ## Get links to documents in Atom feed
        #dom = parseString(response.content)
        #links = dom.getElementsByTagNameNS(NS_ATOM, 'link')
        #avlast_md5 = ""
        #for link in links:
        #    # Look for specific sample document in feed
        #    if link.getAttribute("href").endswith("/publ/exfs/2009:1/rdf"):
        #        # Read document checksum from feed
        #        avlast_md5 = link.getAttributeNS(NS_ATOMLE, "md5")
        #        # Compare checksum from feed with checksum of current document
        #        response = self.client.get('/publ/exfs/2009:1/rdf')
        #        md5=hashlib.md5()
        #        md5.update(response.content)
        #        beraknad_rdfmd5=md5.hexdigest()
        #        self.assertEqual(beraknad_rdfmd5, avlast_md5)


class RDFTestCase(TestCase):

    fixtures = ['exempeldata.json']

    def test_foreskrift(self):
        """Verify that published 'Myndighetsforeskrift' document has correct
        RDF metadata """

        graph = self._get_foreskrift_graph("exfs", "2009", "1")
        ref = URIRef("/publ/exfs/2009:1", RINFO_BASE)
        title = Literal(u"Föreskrift om administration hos statliga myndigheter", lang='sv')
        keyword = Literal(u"Administration", lang='sv')
        self.assertIn((ref, RDF.type, RPUBL.Myndighetsforeskrift), graph)
        self.assertIn((ref, DCT.title, title), graph)
        self.assertIn((ref, DCES.subject, keyword), graph)

    def test_allmanna_rad(self):
        """Verify that published 'AllmannaRad' document has correct
        RDF metadata' """

        graph = self._get_allmana_rad_graph("exfs", "2011", "1")
        ref = URIRef("/publ/exfs/2011:1", RINFO_BASE)
        title = Literal(u"Exempelmyndighetens allmänna råd om adminstration", lang='sv')
        keyword = Literal(u"Administration", lang='sv')
        self.assertIn((ref, RDF.type, RPUBL.AllmannaRad), graph)
        self.assertIn((ref, DCT.title, title), graph)
        self.assertIn((ref, DCES.subject, keyword), graph)
        
    def test_egdirektiv(self):
        """Verify that published 'Myndighetsforeskrift' document has correct
        RDF metadata for legal directives (Django class 'CelexReferens')"""

        graph = self._get_foreskrift_graph("exfs", "2009", "1")
        ref = URIRef("/publ/exfs/2009:1", RINFO_BASE)
        dir_ref = URIRef("/ext/eur-lex/31979L0409", RINFO_BASE)
        self.assertIn((ref, RPUBL.genomforDirektiv, dir_ref), graph)

    def test_omtryck(self):
        """Verify that published 'Myndighetsforeskrift' document has correct
        RDF metadata for property 'omtryck'"""

        graph = self._get_foreskrift_graph("exfs", "2009", "2")
        ref = URIRef("/publ/exfs/2009:2", RINFO_BASE)
        omtryck_ref = URIRef("/publ/exfs/2009:1", RINFO_BASE)
        self.assertIn((ref, RPUBL.omtryckAv, omtryck_ref), graph)

    def test_no_omtryck(self):
        """No metadata should be genereated unless property 'omtryck' is true"""

        graph = self._get_foreskrift_graph("exfs", "2009", "3")
        ref = URIRef("/publ/exfs/2009:3", RINFO_BASE)
        self.assertFalse(list(graph.objects(ref, RPUBL.omtryckAv)))

    def _get_foreskrift_graph(self, fs_slug, arsutgava, lopnummer):
        return self._get_graph_for_type(models.Myndighetsforeskrift,
                                        fs_slug, arsutgava, lopnummer)

    def _get_allmana_rad_graph(self, fs_slug, arsutgava, lopnummer):
        return self._get_graph_for_type(models.AllmannaRad, fs_slug,
                                        arsutgava, lopnummer)

    def _get_graph_for_type(self, modeltype, fs_slug, arsutgava, lopnummer):
        foreskrift = modeltype.objects.get(
                forfattningssamling__slug=fs_slug,
                arsutgava=arsutgava, lopnummer=lopnummer)
        return Graph().parse(data=foreskrift.to_rdfxml())
    

    

