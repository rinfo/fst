# -*- coding: utf-8 -*-
import hashlib
import os
import shutil
from xml.dom.minidom import parseString
from datetime import datetime
from django.test import TestCase
from django.test.client import Client
from rdflib import Graph, Literal, URIRef, RDF
from django.core.urlresolvers import reverse
from fst_web.fs_doc import models
from fst_web.fs_doc.models import generate_atom_entry_for, generate_rdf_post_for
from fst_web.fs_doc.rdfviews import DCT, DCES, RPUBL, RINFO_BASE


NS_ATOM = "http://www.w3.org/2005/Atom"
NS_ATOM_FH = "http://purl.org/syndication/history/1.0"
NS_ATOMLE = "http://purl.org/atompub/link-extensions/1.0"
NS_AT = "http://purl.org/atompub/tombstones/1.0"

class SimpleTest(TestCase):
    """Verify that FST requries login"""

    def setUp(self):
        self.client = Client()

    def test_initial_redirect(self):
        """Verify that accessing the site redirects to '/admin'"""
        response = self.client.get('/',follow=False)
        # Check that there is a redirect for '/'
        self.assertEqual(response.status_code, 302)

    def test_admin_is_accesible(self):
        """Verify that admin is accessible"""
        response = self.client.get('/admin/',follow=True)
        # Check that HTTP response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_admin_is_accesible(self):
        """Verify that admin is accessible"""
        response = self.client.get('/admin/',follow=True)
        # Check that HTTP response is 200 OK.
        self.assertEqual(response.status_code, 200)



class AdminSuperUserTestCase(TestCase):
    #"""Test admin functionality for logged in superuser """

    fixtures = ['exempeldata.json']

    def setUp(self):
        self.username = 'admin'  # This user already exists in fixture
        self.pw = 'admin'        # and is a superuser
        self.assertTrue(self.client.login(
            username=self.username,
            password=self.pw),
                        "Logging in user %s, pw %s failed." %
                        (self.username, self.pw))

    def tearDown(self):
        self.client.logout()

    def test_superuser_access(self):
        #"""Verify that superuser has access to system tables"""

        post_data = {}
        response = self.client.post(reverse('admin:index'), post_data)
        self.assertContains(response, "auth")
        self.assertContains(response, "fs_doc")


class EditorUserTestCase(TestCase):
    """Test admin functionality for logged in ordinary user """

    fixtures = ['exempeldata.json']

    def setUp(self):
        self.username = 'editor'  # This user already exists in fixture
        self.pw = 'editor'        # and is not a superuser
        self.assertTrue(self.client.login(
            username=self.username,
            password=self.pw),
                        "Logging in user %s, pw %s failed." %
                        (self.username, self.pw))

    def tearDown(self):
        self.client.logout()

    def test_editor_access(self):
        """Verify that editor does NOT have access to system tables"""

        post_data = {}
        response = self.client.post(reverse('admin:index'), post_data)
        self.assertNotContains(response, "auth")
        self.assertContains(response, "fs_doc")

    def test_report_beslutsdatum(self):
        """Verify that editor can access report"""
        # Find named report
        response = self.client.get('/admin/beslutsdatum')
        # Find expected documents from sample data
        self.assertContains(response, "EXFS 2009:1")
        self.assertContains(response, "EXFS 2009:2")
        # Obviously bogus document isn't there
        self.assertNotContains(response, "NonExisting 1066:1")

    def test_report_ikrafttradande(self):
        """Verify that editor can access report"""
        # Find named report
        response = self.client.get('/admin/ikrafttradande')
        # Find expected documents from sample data
        self.assertContains(response, "EXFS 2009:1")
        self.assertContains(response, "EXFS 2009:2")
        # Obviously bogus document isn't there
        self.assertNotContains(response, "NonExisting 1066:1")

    def test_report_not_published(self):
        """Verify that editor can access report"""
        # Find named report
        response = self.client.get('/admin/not_published')
        # Find expected documents from sample data
        self.assertContains(response, "EXFS 2009:2")
        self.assertContains(response, "EXFS 2009:3")
        # NOT expected document from sample data isn't there
        self.assertNotContains(response, "EXFS 2011:2")
        # Obviously bogus document isn't there
        self.assertNotContains(response, "NonExisting 1066:1")


class WebTestCase(TestCase):
    """Simplistic functional test of public URL:s  """

    fixtures = ['exempeldata.json']

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__))
        testdocs = os.path.join(base, "../dokument_test")

        # Create temporary folder for testing documents
        if not os.path.exists(testdocs):
            os.mkdir(testdocs)

        # Move documents from fixtures to temporary test folder
        shutil.copy(os.path.join(base, "fixtures/foreskrift/EXFS_2009-1_Grund.pdf"),
                    testdocs)
        shutil.copy(os.path.join(base,
                                 "fixtures/bilaga/EXFS_2009-1-bilaga.pdf"),
                    testdocs)
        shutil.copy(os.path.join(base,
                                 "fixtures/foreskrift/EXFS_2009-2_Andring_omtryck.pdf"),
                    testdocs)
        shutil.copy(os.path.join(base,
                                 "fixtures/foreskrift/EXFS_2009-3_Grund.pdf"),
                    testdocs)
        shutil.copy(os.path.join(base,
                                 "fixtures/allmanna_rad/EXFS_2011-1_Allmant_rad.pdf"),
                    testdocs)

    def tearDown(self):
        base = os.path.join(os.path.dirname(__file__))
        testdocs = os.path.join(base, "../dokument_test")

        # Delete temporary testfolder
        shutil.rmtree(testdocs)

    def test_startsida(self):
        """Verify redirect (since we don't have a public start page """

        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 302)

        
    def test_foreskrift(self):
        """Verify that detail page for documents load
        with correct sample data for all document types"""

        response = self.client.get('/publ/exfs/2009:1/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h2>EXFS 2009:1 Föreskrifter om administration hos statliga myndigheter")

        response = self.client.get('/publ/exfs/2011:1/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h2>EXFS 2011:1 Exempelmyndighetens allmänna råd om adminstration")

    def test_feed(self):
        """Verify that Atom feed is created and can be read """

        response = self.client.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'],
                         'application/atom+xml; charset=utf-8')
        dom = parseString(response.content)
        # Feed has exactly one root element
        self.assertEquals(len(dom.getElementsByTagNameNS(NS_ATOM, 'feed')), 1)
        # No entries yet
        self.assertFalse(dom.getElementsByTagNameNS(NS_ATOM, 'entry'))

    def test_get_rdf(self):
        """Verify that we can load RDF data for a published document"""

        # Get document to publish
        foreskrift = models.Myndighetsforeskrift.objects.get(
            forfattningssamling__slug="exfs", arsutgava="2009", lopnummer="1")
        # Publish document. TODO - use explicit publish method here!
        generate_atom_entry_for(foreskrift)

        # Feed now should have exactly one entry element
        response = self.client.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'],
                         'application/atom+xml; charset=utf-8')
        dom = parseString(response.content)
        self.assertEquals(len(dom.getElementsByTagNameNS(NS_ATOM, 'entry')), 1)

        # Check that RDF representation exists
        response = self.client.get('/publ/exfs/2009:1/rdf')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'],
                         'application/rdf+xml;charset=utf-8')


class FeedTestCase(TestCase):
    """Test functionality for creating valid ATOM feed """

    fixtures = ['exempeldata.json']

    def setUp(self):
        # Publish some of the documents from fixture
        foreskrift1 = models.Myndighetsforeskrift.objects.get(
            forfattningssamling__slug="exfs", arsutgava="2009", lopnummer="1")
        generate_rdf_post_for(foreskrift1)
        generate_atom_entry_for(foreskrift1)

        foreskrift2 = models.Myndighetsforeskrift.objects.get(
            forfattningssamling__slug="exfs", arsutgava="2009", lopnummer="2")
        generate_rdf_post_for(foreskrift2)
        generate_atom_entry_for(foreskrift2)

    def test_feed_has_entries(self):
        """Verify that an Atom feed with entries is created from sample data"""

        dom = self._get_parsed_feed('/feed/')

        # Feed has exactly one root element
        self.assertEquals(len(dom.getElementsByTagNameNS(NS_ATOM, 'feed')), 1)
        # Feed has two published entries
        self.assertEquals(len(dom.getElementsByTagNameNS(NS_ATOM, 'entry')), 2)

    def test_feed_is_complete(self):
        dom = self._get_parsed_feed('/feed/')
        self.assertEquals(len(dom.getElementsByTagNameNS(NS_ATOM_FH,
                                                         'complete')), 1)

    def test_entry_link_md5(self):
        """Verify that checksum of document in Atom feed is correct"""

        # Get Atom feed
        response = self.client.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)

        # Get links to documents in Atom feed
        dom = parseString(response.content)
        links = dom.getElementsByTagNameNS(NS_ATOM, 'link')
        avlast_md5 = ""
        for link in links:
            # Look for specific sample document in feed
            if link.getAttribute("href").endswith("/publ/exfs/2009:1"):
                # Read document checksum from feed
                avlast_md5 = link.getAttributeNS(NS_ATOMLE, "md5")
                # Compare checksum from feed with checksum of current document
                response = self.client.get('/publ/exfs/2009:1')
                md5 = hashlib.md5()
                md5.update(response.content)
                beraknad_rdfmd5 = md5.hexdigest()
                self.assertEqual(beraknad_rdfmd5, avlast_md5)

    def test_delete_feedentry(self):
        """Verify that entries can be deleted and NOT replaced by special entry"""

        dom = self._get_parsed_feed('/feed/')

        # Check that two document entries exist
        self.assertEquals(len(dom.getElementsByTagNameNS(NS_ATOM, 'entry')), 2)

        # Delete one document
        foreskrift2 = models.Myndighetsforeskrift.objects.get(
            forfattningssamling__slug="exfs", arsutgava="2009", lopnummer="2")
        foreskrift2.delete()

        dom = self._get_parsed_feed('/feed/')

        # Only one document entry exists
        self.assertEquals(len(dom.getElementsByTagNameNS(NS_ATOM, 'entry')), 1)

        # Special entry signaling deletion should NOT exist since this is a fh:complete feed
        self.assertFalse(dom.getElementsByTagNameNS(NS_AT, 'deleted-entry'))

    def _get_parsed_feed(self, path):
        # Get Atom feed
        response = self.client.get(path)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response['content-type'],
                         'application/atom+xml; charset=utf-8')
        return parseString(response.content)


class RDFTestCase(TestCase):
    """Test basic RDF functionality  """

    fixtures = ['exempeldata.json']

    def test_foreskrift(self):
        """Verify that published 'Myndighetsforeskrift' document has correct
        RDF metadata """

        graph = self._get_foreskrift_graph("exfs", "2009", "1")
        ref = URIRef("/publ/exfs/2009:1", RINFO_BASE)
        title = Literal(
            u"Föreskrifter om administration hos statliga myndigheter",
            lang='sv')
        keyword = Literal(u"Administration", lang='sv')
        self.assertIn((ref, RDF.type, RPUBL.Myndighetsforeskrift), graph)
        self.assertIn((ref, DCT.title, title), graph)
        self.assertIn((ref, DCES.subject, keyword), graph)

    def test_allmanna_rad(self):
        """Verify that published 'AllmannaRad' document has correct
        RDF metadata' """

        graph = self._get_allmana_rad_graph("exfs", "2011", "1")
        ref = URIRef("/publ/exfs/2011:1", RINFO_BASE)
        title = Literal(u"Exempelmyndighetens allmänna råd om adminstration",
                        lang='sv')
        keyword = Literal(u"Centralisering", lang='sv')
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
        """No metadata for property 'omtryck' unless true"""

        graph = self._get_foreskrift_graph("exfs", "2009", "3")
        ref = URIRef("/publ/exfs/2009:3", RINFO_BASE)
        self.assertFalse(list(graph.objects(ref, RPUBL.omtryckAv)))

    def test_andrar(self):
        """Verify that property 'andringar' has correct RDF metadata """

        graph = self._get_foreskrift_graph("exfs", "2009", "2")
        ref = URIRef("/publ/exfs/2009:2", RINFO_BASE)
        self.assertTrue(list(graph.objects(ref, RPUBL.andrar)))

    def _get_foreskrift_graph(self, fs_slug, arsutgava, lopnummer):
        return self._get_graph_for_type(models.Myndighetsforeskrift, \
                                        fs_slug, arsutgava, lopnummer)

    def _get_allmana_rad_graph(self, fs_slug, arsutgava, lopnummer):
        return self._get_graph_for_type(models.AllmannaRad, fs_slug,
                                        arsutgava, lopnummer)

    def _get_graph_for_type(self, modeltype, fs_slug, arsutgava, lopnummer):
        foreskrift = modeltype.objects.get(
            forfattningssamling__slug=fs_slug,
            arsutgava=arsutgava, lopnummer=lopnummer)
        return Graph().parse(data=foreskrift.to_rdfxml())
