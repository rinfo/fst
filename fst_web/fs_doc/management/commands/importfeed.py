#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,re,shutil,hashlib,stat
import xml.etree.ElementTree as ET
from pprint import pprint
from collections import defaultdict
from urllib import urlopen, urlretrieve

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from rdflib import Graph, Literal, URIRef, Namespace, RDF
import sqlite3

from fst_web.fs_doc.models import Myndighetsforeskrift, AllmannaRad, \
    KonsolideradForeskrift, generate_rdf_post_for

DCT = Namespace('http://purl.org/dc/terms/')
RPUBL = Namespace('http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#')

# Normal dicts aren't hashable, and can thus not be keys in dicts
# themselves. These dicts can (but modifying it will change the hash,
# so don't do that)
class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

class Command(BaseCommand):
    args = '<feedurl>'
    help = 'Imports all entries (RDF+PDF) from a Atom feed'

    # a dict of list of dicts, representing tables and their rows and the fields of those
    data = {'fs_doc_fsdokument':[],
            'fs_doc_myndighetsforeskrift':[],
            'fs_doc_konsolideradforeskrift':[],
            'fs_doc_allmannarad':[],
            'fs_doc_myndighet':[],
            'fs_doc_forfattningssamling':[],
            'fs_doc_bemyndigandereferens':[],
            'fs_doc_celexreferens':[],
            'fs_doc_myndighetsforeskrift_bemyndiganden':[],
            'fs_doc_myndighetsforeskrift_upphavningar':[],
            'fs_doc_myndighetsforeskrift_andringar':[],
            }
    
    # key: bemyndigande (hashable)dict, value: id (seems backwards but
    # is practical)
    bemyndiganden = {}
    celex = {}
    titlar = {}
    titlegraph = None
    
    current_document = {}
    current_subdocument = {}
    
    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        for url in args:
            self.stdout.write('Loading data from %s\n' % url)
            self.importfeed(url)
            self.load_db(db_path)
            self.generate_rdf_posts()

    def importfeed(self,url):
        stream = urlopen(url)
        tree = ET.parse(stream)
        ns = 'http://www.w3.org/2005/Atom'
        for entry in list(reversed(tree.findall('.//{%s}entry'%ns))):
            pdf_url = None
            rdf_url = None
            for node in entry:
                if (node.tag == "{%s}link"%ns and 
                    node.get('type') == 'application/rdf+xml'):
                    rdf_url = node.get("href")
                elif (node.tag == "{%s}content"%ns and 
                      node.get('type') == 'application/pdf'):
                    pdf_url = node.get("src")
            sys.stderr.write("RDF: %s\nPDF: %s\n" % (rdf_url,pdf_url))
            self.add_entry(rdf_url,pdf_url)
        #pprint(self.data)

    def add_entry(self,rdf_url,pdf_url):
        g = Graph()
        g.bind('dct','http://purl.org/dc/terms/')
        g.bind('rpubl','http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#')
        g.parse(urlopen(rdf_url))

        # first get type
        for (s,p,o) in g:
            if p == RDF.type:
                if o == RPUBL['Myndighetsforeskrift']:
                    doctype = 'fs_doc_myndighetsforeskrift'
                    table =  'fs_doc_fsdokument'
                    targetdir = 'foreskrift'
                elif o == RPUBL['AllmannaRad']:
                    doctype = 'fs_doc_allmannarad'
                    table =  'fs_doc_fsdokument'
                    targetdir = 'allmanna_rad'
                elif o == RPUBL['KonsolideradGrundforfattning']:
                    doctype = 'fs_doc_konsolideradforeskrift'
                    table =  'fs_doc_konsolideradforeskrift'
                    targetdir = 'konsoliderad_foreskrift'
                else:
                    sys.stderr.write("Can't handle type %s\n" % o)

                docid = len(self.data[table]) + 1
                self.current_document['id'] = str(docid)
                self.current_document['is_published'] = '0'
                if table == 'fs_doc_fsdokument':
                    self.current_subdocument['fsdokument_ptr_id'] = str(docid)

        # then iterate through other properties, dynamically
        # calling appropriate functions to massage data and put it
        # where it belongs.
        for (s,p,o) in g:
            funcname = g.qname(p).replace(":","_")
            #if funcname in globals():
            if hasattr(self,funcname):
                #sys.stderr.write("    Calling self.%s\n" % funcname)
                f = getattr(self,funcname)
                #globals()[funcname](o,doctype)
                f(o,doctype)
            else:
                sys.stderr.write("  Cant handle predicate %s\n" % funcname.replace("_",":"))

        # check for required fields:
        d = self.current_document
        sub_d = self.current_subdocument

        for fld in ('arsutgava','lopnummer','forfattningssamling_id'):
            assert fld in d

        # Create filename base, eg "FFFS-2011-42"
        fs = self.data['fs_doc_forfattningssamling'][int(d['forfattningssamling_id'])-1]
        basefile = "%s-%s-%s" % (fs['kortnamn'],d['arsutgava'], d['lopnummer'])

        if not os.path.exists(targetdir):
            os.makedirs(targetdir)
        outfile = "%s/%s.pdf" % (targetdir,basefile)
        urlretrieve(pdf_url,outfile)
        sub_d['content'] = outfile

        md5 = hashlib.md5()
        with open(outfile,'rb') as f: 
            for chunk in iter(lambda: f.read(8192), ''): 
                md5.update(chunk)
        d['content_md5'] = md5.hexdigest()

        # Make sure all other fields have some sort of data
        if not 'sammanfattning' in d:
            d['sammanfattning'] = ""
        if not 'omtryck' in d:
            d['omtryck'] = '0'
        if not 'beslutsdatum' in d:
            d['beslutsdatum'] = "%s-12-31"%d['arsutgava']
            sys.stderr.write("  WARNING: No beslutsdatum found, setting to %s\n"%d['beslutsdatum'])

        if not 'utkom_fran_tryck' in d:
            d['utkom_fran_tryck'] = "%s-12-31"%d['arsutgava']
            sys.stderr.write("  WARNING: No utkom_fran_tryck found, setting to %s\n" % d['utkom_fran_tryck'])

        if not 'ikrafttradandedatum' in d:
            sys.stderr.write("  WARNING: No ikrafttradandedatum found, setting to beslutsdatum\n")
            d['ikrafttradandedatum'] = d['beslutsdatum']
        if not 'titel' in d:
            d['titel'] = "%s %s:%s" % (fs['kortnamn'], d['arsutgava'], d['lopnummer'])
            sys.stderr.write("  WARNING: No titel found, setting to %s\n" % d['titel'])

        if not 'beslutad_av_id' in sub_d:
            sys.stderr.write("  WARNING: no beslutad_av found, setting to 1\n")
            sub_d['beslutad_av_id'] = '1'
        if not 'utgivare_id' in sub_d:
            sys.stderr.write("  WARNING: no utgivare found, setting to beslutad_av\n")
            sub_d['utgivare_id'] = sub_d['beslutad_av_id']

        # Finally, add clones of the global dicts to the
        # appropriate place in data, and then clear them for
        # recycling
        self.data[table].append(d.copy())
        d.clear()
        if table=='fs_doc_fsdokument':

            self.data[doctype].append(sub_d.copy())
        sub_d.clear()


# 

    # various convenience functions for the assignment functions below
    def parse_bemyndigande(self, resource):
        """Creates a hash (to be put in a row in the
        fs_doc_bemyndiganden table) from a bemyndigande URI, eg:

        'http://rinfo.lagrummet.se/publ/sfs/1962:700#K4P1' =>
        {'title': 'Brottsbalk',
         'sfsnummer': '1962:700',
         'kapitelnummer': '4',
         'paragrafnummer': '1'}
        """
        resource = str(resource).split("/")[-1]
        m = re.search(r'(\d+:\d+)#K?([\da-z]*)P([\da-z]*)',resource)
        d = hashabledict()
        if m:
            d['sfsnummer'] = m.group(1)
            d['titel'] = self.get_titel_from_sfsnr(d['sfsnummer'])
            if m.group(2):
                d['kapitelnummer'] = m.group(2)
            else:
                d['kapitelnummer'] = ""
            d['paragrafnummer'] = m.group(3)
            d['kommentar'] = ""
            # Sanity check
            if d['sfsnummer'] == '9999:999':
                return None
        else:
            sys.stderr.write("WARNING: Can't parse %s\n" % resource)
            return None

        return d

    def get_titel_from_sfsnr(self, sfsnr):
        if sfsnr in self.titlar:
            return self.titlar[sfsnr]
        titlefile = "titles.n3"
        url = "https://lagen.nu/sfs/parsed/rdf.nt"
        if not os.path.exists(titlefile):
        # TODO: 1: Download big n3 file from lagen.nu
            sys.stderr.write("Downloading N3 file (will take a few minutes...)\n")
            stream = urlopen(url)
            nt = open(titlefile,"w")
            for line in stream:
        #       2: Save dct:title lines
                if '<http://purl.org/dc/terms/title>' in line:
                    nt.write(line)
            nt.close()

        #       3: lookup title
        if not self.titlegraph:
            sys.stderr.write("Loading title graph from %s\n" % titlefile)
            self.titlegraph = Graph()
            self.titlegraph.bind('dct','http://purl.org/dc/terms/')
            self.titlegraph.bind('rpubl','http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#')
            self.titlegraph.parse(titlefile, format="nt")

        subj = URIRef("http://rinfo.lagrummet.se/publ/sfs/%s" % sfsnr)
        pred = DCT['title']
        titles = list(self.titlegraph.objects(subj,pred))
        if titles:
            title = titles[0]
        else:
            # probably old 
            title = "SFS %s" % sfsnr
        
        #       4: save title in self.titlar so we can look for it later.
        self.titlar[sfsnr] = title

        return title
    
    def get_or_create_forfattningssamling(self, kortnamn):
        forfattningssamling_id = None
        for d in self.data['fs_doc_forfattningssamling']:
            if d['kortnamn'] == kortnamn:
                forfattningssamling_id = d['id']
                break

        if not forfattningssamling_id:
            forfattningssamling_id = len(self.data['fs_doc_forfattningssamling'])+1
            self.data['fs_doc_forfattningssamling'].append({'id':str(forfattningssamling_id),
                                                       # FIXME: Find out real name
                                                       'titel':u'%s författningssamling'%kortnamn,
                                                       'kortnamn':kortnamn,
                                                       'slug':kortnamn.lower()})
        return forfattningssamling_id

    def get_or_create_fsdokument(self,fs_id,arsutgava,lopnummer):
        fsdokument_id = None

        for d in self.data['fs_doc_fsdokument']:
            if not (('forfattningssamling_id' in d) and
                    ('arsutgava' in d) and
                    ('lopnummer' in d)):
                # If these properties are missing, it's almost certainly
                # the very doc we're trying to find andringar/upphavningar
                # for
                continue

            if ((d['forfattningssamling_id'] == fs_id) and
                (d['arsutgava'] == arsutgava) and
                (d['lopnummer'] == lopnummer)):
                fsdokument_id = d['id']
                break

        if not fsdokument_id:
            # +2 because the main document we're creating hasn't been added to data yet
            fsdokument_id = len(self.data['fs_doc_fsdokument'])+2
            placeholder_fsdokument = {'id':str(fsdokument_id),
                                      'is_published':'0',
                                      'forfattningssamling_id':fs_id, # assume same FS
                                      'arsutgava':arsutgava,
                                      'lopnummer':lopnummer,
                                      'titel':'%s:%s' % (arsutgava,lopnummer),
                                      'content_md5': 'd41d8cd98f00b204e9800998ecf8427e', # empty string
                                      'beslutsdatum':'%s-01-01' % arsutgava,
                                      'ikrafttradandedatum':'%s-01-01' % arsutgava,
                                      'utkom_fran_tryck':'%s-01-01' % arsutgava,
                                      'omtryck':'0',
                                      'sammanfattning':''}
            self.data['fs_doc_fsdokument'].append(placeholder_fsdokument)

            # We can't really be sure this is a
            # fs_doc_myndighetsforeskrift (could be fs_doc_allmantrad),
            # but this is the best guess
            placeholder_myndighetsforeskrift = {'beslutad_av_id': '1', #FIXME!
                                                'utgivare_id': '1',     #FIXME!
                                                'fsdokument_ptr_id':str(fsdokument_id),
                                                'content':'does-not-exist.pdf'
                                                }
            self.data['fs_doc_myndighetsforeskrift'].append(placeholder_myndighetsforeskrift)

        return fsdokument_id

    def doc_resource_to_identifier(self,resource):
        (saml,fsnr) = str(resource).split("/")[-2:]
        return saml.upper() + " " + fsnr

    def org_resource_to_namn(self,resource):
        return str(resource).split("/")[-1].capitalize().replace("_"," ")

    def upphaver_or_andrar(self,resource,key):
        (slug,fsnr) = str(resource).split("/")[-2:]
        (arsutgava,lopnummer) = fsnr.split(":")
        fs_id = self.get_or_create_forfattningssamling(slug.upper())
        from_doc_id = self.current_document['id']
        fsdokument_id = self.get_or_create_fsdokument(fs_id,arsutgava,lopnummer)
        conn_id = len(self.data[key])+1
        self.data[key].append({'id':str(conn_id),
                          'from_myndighetsforeskrift_id':str(from_doc_id),
                          'to_myndighetsforeskrift_id':str(fsdokument_id)})

    # Assignment functions: Each of these functions get dynamically called
    # when a corresponding predicate is found in the RDF data. They do the
    # appropriate data mangling and assigns the result to the correct
    # place in data
    def rdf_type(self,obj,doctype): pass
    def dct_issn(self,obj,doctype): pass
    def dct_identifier(self,obj,doctype): pass

    def dct_title(self,obj, doctype):
        self.current_document['titel'] = unicode(obj)

    def rpubl_arsutgava(self,obj, doctype):
        self.current_document['arsutgava'] = str(obj)

    def rpubl_lopnummer(self,obj, doctype):
        self.current_document['lopnummer'] = str(obj)

    def rpubl_utkomFranTryck(self,obj, doctype):
        self.current_document['utkom_fran_tryck'] = str(obj)

    def rpubl_beslutsdatum(self,obj, doctype):
        self.current_document['beslutsdatum'] = str(obj)

    def rpubl_ikrafttradandedatum(self,obj, doctype):
        self.current_document['ikrafttradandedatum'] = str(obj)

    def rpubl_beslutadAv(self, obj, doctype):
        # 1. calculate myndighetsnamn
        namn = self.org_resource_to_namn(obj)
        # 2. find id of myndighet
        myndighet_id = None
        for d in self.data['fs_doc_myndighet']:
            if d['namn'] == namn:
                myndighet_id = d['id']
        # 3. add myndighet if not found
        if not myndighet_id:
            myndighet_id = len(self.data['fs_doc_myndighet'])+1
            self.data['fs_doc_myndighet'].append({'id':str(myndighet_id),'namn':namn})
        # 4. set id value
        self.current_subdocument['beslutad_av_id'] = str(myndighet_id)

    def dct_publisher(self, obj, doctype):
        # 1. calculate myndighetsnamn
        namn = self.org_resource_to_namn(obj)
        # 2. find id of myndighet
        myndighet_id = None
        for d in self.data['fs_doc_myndighet']:
            if d['namn'] == namn:
                myndighet_id = d['id']
        # 3. add myndighet if not found
        if not myndighet_id:
            myndighet_id = len(self.data['fs_doc_myndighet'])+1
            self.data['fs_doc_myndighet'].append({'id':str(myndighet_id),'namn':namn})
        # 4. set id value
        self.current_subdocument['utgivare_id'] = str(myndighet_id)

    def rpubl_forfattningssamling(self, obj, doctype):
        # 1. calculate kortnamn
        slug = obj.split("/")[-1]
        kortnamn = slug.upper()
        forfattningssamling_id = self.get_or_create_forfattningssamling(kortnamn)
        # 4. set id value
        self.current_document['forfattningssamling_id'] = str(forfattningssamling_id)

    def rpubl_genomforDirektiv(self, obj, doctype):
        # 1. Create the celex dict
        celexnum = obj.split("/")[-1]
        if len(celexnum) == 8:
            # Pad old-style 392L0049 to new style 31992L0049
            celexnum = celexnum[0] + "19" + celexnum[1:]
        celex = hashabledict()
        celex['titel'] = 'CELEX %s' % celexnum
        celex['celexnummer'] = celexnum
        
        # 2. Have we defined this before (does it have a id)?
        celex_id = None
        if celex in self.celex:
            celex_id = self.celex[celex]

        # 3. If not, allocate an id and define it (once in our convenience
        # lookup dict w/o id, and once, with a new copy, in the real list w/ id)
        if not celex_id:
            celex_id = len(self.celex) + 1
            self.celex[celex] = celex_id

            celex_copy = celex.copy()
            celex_copy['id'] = str(celex_id)
            self.data['fs_doc_celexreferens'].append(celex_copy)
        
    def rpubl_bemyndigande(self, obj, doctype):
        # 1. Calculate the bemyndigande dict
        bemyndigande = self.parse_bemyndigande(obj)
        if not bemyndigande:
            return
        # 2. Have we defined this before (does it have a id)?
        bemyndigande_id = None
        if bemyndigande in self.bemyndiganden:
            bemyndigande_id = self.bemyndiganden[bemyndigande]

        # 3. If not, allocate an id and define it (once in our convenience
        # lookup dict w/o id, and once, with a new copy, in the real list w/ id)
        if not bemyndigande_id:
            bemyndigande_id = len(self.bemyndiganden) + 1
            self.bemyndiganden[bemyndigande] = bemyndigande_id

            bemyndigande_copy = bemyndigande.copy()
            bemyndigande_copy['id'] = str(bemyndigande_id)
            self.data['fs_doc_bemyndigandereferens'].append(bemyndigande_copy)


        # 4. add entry to connection table
        docid = self.current_document['id'] # could use len(self.data['fs_doc_fsdokument'])
        conn_id = len(self.data['fs_doc_myndighetsforeskrift_bemyndiganden'])+1
        self.data['fs_doc_myndighetsforeskrift_bemyndiganden'].append({'id':str(conn_id),
                                                                  'myndighetsforeskrift_id':docid,
                                                                  'bemyndigandereferens_id':str(bemyndigande_id)})


        # note that this assumes that we iterate through documents from
        # old to new, not the other way round.

    def rpubl_upphaver(self, obj,doctype):
        # FIXME: Sometimes this should be fs_doc_allmannarad_upphavningar
        self.upphaver_or_andrar(obj,'fs_doc_myndighetsforeskrift_upphavningar')

    def rpubl_andrar(self, obj,doctype):
        self.upphaver_or_andrar(obj,'fs_doc_myndighetsforeskrift_andringar')
    
    def load_db(self,db_path):
        """Run sample data on empty DB.

        The updated DB displays inserted records when used with FST and
        Django admin. We must verify all necessary related tables are created.
        """
        sys.stderr.write("copying fst_no_docs.db to %s\n" % db_path)
        import shutil
        shutil.copy2("../tools/fst_no_docs.db", db_path)
        # Group and other should have write permission
        mode = os.stat(db_path)[stat.ST_MODE]
        os.chmod(db_path,mode|stat.S_IWGRP|stat.S_IWOTH)
        
        db_connection = sqlite3.connect(db_path)
        db_connection.text_factory = str  # bugger 8-bit bytestrings

        sys.stderr.write("loaded indata, %s top-level keys\n" % len(self.data))
        for table in self.data.keys():
            self.fill_table(table,self.data,db_connection)

    def get_insert_string(self,row):
        """ Build SQL string for fieldnames and values.

        Parameter 'row' is a dictionary, so we must keep key/value combinations
        together when constructing the string.
        """
        fields = "("
        values = " VALUES("
        for key, val in row.items():
            fields = fields + key + ", "
            if type(val) == int:
                val = str(val)
            values = values + "'" + val + "'" + ", "
        fields = fields[:-2] + ")"
        values = values[:-2] + ")"
        return fields + values


    def fill_table(self,table_name, data, db_connection):
        """Insert records in SQlite using a list of dictionaries """
        sys.stderr.write("Filling table %s\n" % table_name)
        for row in data[table_name]:
            # print "   record"
            self.fill_record(table_name, row, db_connection)


    def fill_record(self,table_name, row, db_connection):
        """Insert record in SQlite using a Python dictionary """
        cursor = db_connection.cursor()
        insert_statement = "INSERT INTO %s " % table_name
        insert_data = self.get_insert_string(row)
        sql = insert_statement + insert_data
        # print sql
        cursor.execute(sql)
        db_connection.commit()
        
    def generate_rdf_posts(self):
        for cls in (Myndighetsforeskrift, AllmannaRad, KonsolideradForeskrift):
            for obj in cls.objects.all():
                sys.stderr.write("Generating rdf post for %s\n" % obj.identifierare)
                generate_rdf_post_for(obj)
