#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,re,shutil,hashlib
from pprint import pprint
from collections import defaultdict

from rdflib import Graph, Literal, URIRef, Namespace, RDF

DCT = Namespace('http://purl.org/dc/terms/')
RPUBL = Namespace('http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#')

# Normal dicts aren't hashable, and can thus not be keys in dicts
# themselves. These dicts can (but modifying it will change the hash,
# so don't do that)
class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

# a dict of list of dicts, representing tables and their rows and the fields of those
data = {}
    
# Global dict. key: bemyndigande (hashable)dict, value: id (seems
# backwards but is practical)
bemyndiganden = {}

current_document = {}
current_subdocument = {}

# various convenience functions for the assignment functions below
def parse_bemyndigande(resource):
    resource = str(resource).split("/")[-1]
    m = re.search(r'(\d+:\d+)#K?([\da-z]*)P([\da-z]*)',resource)
    d = hashabledict()
    if m:
        d['titel'] = "TODO: lagtitel"
        d['sfsnummer'] = m.group(1)
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


def get_or_create_forfattningssamling(kortnamn):
    forfattningssamling_id = None
    for d in data['fs_doc_forfattningssamling']:
        if d['kortnamn'] == kortnamn:
            forfattningssamling_id = d['id']
            break

    if not forfattningssamling_id:
        forfattningssamling_id = len(data['fs_doc_forfattningssamling'])+1
        data['fs_doc_forfattningssamling'].append({'id':str(forfattningssamling_id),
                                                   # FIXME: Find out real name
                                                   'titel':u'%s författningssamling'%kortnamn,
                                                   'kortnamn':kortnamn,
                                                   'slug':kortnamn.lower()})
    return forfattningssamling_id

def get_or_create_fsdokument(fs_id,arsutgava,lopnummer):
    fsdokument_id = None

    for d in data['fs_doc_fsdokument']:
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
        fsdokument_id = len(data['fs_doc_fsdokument'])+2
        placeholder_fsdokument = {'id':str(fsdokument_id),
                                  'is_published':'0',
                                  'forfattningssamling_id':fs_id, # assume same FS
                                  'arsutgava':arsutgava,
                                  'lopnummer':lopnummer,
                                  'titel':'%s:%s' % (arsutgava,lopnummer),
                                  'content_md5': 'd41d8cd98f00b204e9800998ecf8427e',
                                  'beslutsdatum':'%s-01-01' % arsutgava,
                                  'ikrafttradandedatum':'%s-01-01' % arsutgava,
                                  'utkom_fran_tryck':'%s-01-01' % arsutgava,
                                  'omtryck':'0',
                                  'sammanfattning':''}
        data['fs_doc_fsdokument'].append(placeholder_fsdokument)

        # We can't really be sure this is a
        # fs_doc_myndighetsforeskrift (could be fs_doc_allmantrad),
        # but this is the best guess
        placeholder_myndighetsforeskrift = {'beslutad_av_id': '1', #FIXME!
                                            'utgivare_id': '1',     #FIXME!
                                            'fsdokument_ptr_id':str(fsdokument_id),
                                            'content':''
                                            }
        data['fs_doc_myndighetsforeskrift'].append(placeholder_myndighetsforeskrift)

    return fsdokument_id

def doc_resource_to_identifier(resource):
    (saml,fsnr) = str(resource).split("/")[-2:]
    return saml.upper() + " " + fsnr

def org_resource_to_namn(resource):
    return str(resource).split("/")[-1].capitalize().replace("_"," ")

def upphaver_or_andrar(resource,key):
    (slug,fsnr) = str(resource).split("/")[-2:]
    (arsutgava,lopnummer) = fsnr.split(":")
    fs_id = get_or_create_forfattningssamling(slug.upper())
    from_doc_id = current_document['id']
    fsdokument_id = get_or_create_fsdokument(fs_id,arsutgava,lopnummer)
    conn_id = len(data[key])+1
    data[key].append({'id':str(conn_id),
                      'from_myndighetsforeskrift_id':str(from_doc_id),
                      'to_myndighetsforeskrift_id':str(fsdokument_id)})

# Assignment functions: Each of these functions get dynamically called
# when a corresponding predicate is found in the RDF data. They do the
# appropriate data mangling and assigns the result to the correct
# place in data
def rdf_type(obj,doctype): pass
def dct_issn(obj,doctype): pass
def dct_identifier(obj,doctype): pass

def dct_title(obj, doctype):
    current_document['titel'] = unicode(obj)

def rpubl_arsutgava(obj, doctype):
    current_document['arsutgava'] = str(obj)
    
def rpubl_lopnummer(obj, doctype):
    current_document['lopnummer'] = str(obj)

def rpubl_utkomFranTrycket(obj, doctype):
    current_document['utkom_fran_tryck'] = str(obj)

def rpubl_beslutandedatum(obj, doctype):
    current_document['beslutsdatum'] = str(obj)

def rpubl_ikrafttradandedatum(obj, doctype):
    current_document['ikrafttradandedatum'] = str(obj)

def rpubl_beslutadAv(obj, doctype):
    # 1. calculate myndighetsnamn
    namn = org_resource_to_namn(obj)
    # 2. find id of myndighet
    myndighet_id = None
    for d in data['fs_doc_myndighet']:
        if d['namn'] == namn:
            myndighet_id = d['id']
    # 3. add myndighet if not found
    if not myndighet_id:
        myndighet_id = len(data['fs_doc_myndighet'])+1
        data['fs_doc_myndighet'].append({'id':str(myndighet_id),'namn':namn})
    # 4. set id value
    current_subdocument['beslutad_av_id'] = str(myndighet_id)

def rpubl_forfattningssamling(obj, doctype):
    # 1. calculate kortnamn
    slug = obj.split("/")[-1]
    kortnamn = slug.upper()
    forfattningssamling_id = get_or_create_forfattningssamling(kortnamn)
    # 4. set id value
    current_document['forfattningssamling_id'] = str(forfattningssamling_id)

    
def rpubl_bemyndigande(obj, doctype):
    # 1. Calculate the bemyndigande dict
    bemyndigande = parse_bemyndigande(obj)
    if not bemyndigande:
        return
    # 2. Have we defined this before (does it have a id)?
    bemyndigande_id = None
    if bemyndigande in bemyndiganden:
        bemyndigande_id = bemyndiganden[bemyndigande]
        
    # 3. If not, allocate an id and define it (once in our convenience
    # lookup dict w/o id, and once, with a new copy, in the real list w/ id)
    if not bemyndigande_id:
        bemyndigande_id = len(bemyndiganden) + 1
        bemyndiganden[bemyndigande] = bemyndigande_id

        bemyndigande_copy = bemyndigande.copy()
        bemyndigande_copy['id'] = str(bemyndigande_id)
        data['fs_doc_bemyndigandereferens'].append(bemyndigande_copy)

    
    # 4. add entry to connection table
    docid = current_document['id'] # could use len(data['fs_doc_fsdokument'])
    conn_id = len(data['fs_doc_myndighetsforeskrift_bemyndiganden'])+1
    data['fs_doc_myndighetsforeskrift_bemyndiganden'].append({'id':str(conn_id),
                                                              'myndighetsforeskrift_id':docid,
                                                              'bemyndigandereferens_id':str(bemyndigande_id)})


    # note that this assumes that we iterate through documents from
    # old to new, not the other way round.

def rpubl_upphaver(obj,doctype):
    # FIXME: Sometimes this should be fs_doc_allmannarad_upphavningar
    upphaver_or_andrar(obj,'fs_doc_myndighetsforeskrift_upphavningar')

def rpubl_andrar(obj,doctype):
    upphaver_or_andrar(obj,'fs_doc_myndighetsforeskrift_andringar')


def loaddata(directory):
    data['fs_doc_fsdokument'] = []
    data['fs_doc_myndighetsforeskrift'] = []
    data['fs_doc_konsolideradforeskrift'] = []
    data['fs_doc_allmannarad'] = []
    data['fs_doc_myndighet'] = []
    data['fs_doc_forfattningssamling'] = []
    data['fs_doc_bemyndigandereferens'] = []
    data['fs_doc_myndighetsforeskrift_bemyndiganden'] = []
    data['fs_doc_myndighetsforeskrift_upphavningar'] = []
    data['fs_doc_myndighetsforeskrift_andringar'] = []
    
           
    years = [x for x in os.listdir(directory+"/distilled") if x.isdigit()]
    for year in sorted(years):
        rdffiles = [x for x in os.listdir(directory+"/distilled/"+year) if x.endswith(".rdf")]
        for rdffile in sorted(rdffiles,key=lambda x:int(x.split(".")[0])):
            sys.stderr.write("loading %s/%s\n" % (year,rdffile))
            g = Graph()
            g.bind('dct','http://purl.org/dc/terms/')
            g.bind('rpubl','http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#')
            g.parse(directory+"/distilled/"+year+"/"+rdffile)

            # first get type
            for (s,p,o) in g:
                if p == RDF.type:
                    if o == RPUBL['MyndighetsForeskrift']:
                        doctype = 'fs_doc_myndighetsforeskrift'
                        table =  'fs_doc_fsdokument'
                    elif o == RPUBL['AllmannaRad']:
                        doctype = 'fs_doc_allmannarad'
                        table =  'fs_doc_fsdokument'
                    elif o == RPUBL['KonsolideradGrundforfattning']:
                        doctype = 'fs_doc_konsolideradforeskrift'
                        table =  'fs_doc_konsolideradforeskrift'
                    else:
                        sys.stderr.write("Can't handle type %s\n" % o)

                    docid = len(data[table]) + 1
                    current_document['id'] = str(docid)
                    current_document['is_published'] = '0'
                    if table == 'fs_doc_fsdokument':
                        current_subdocument['fsdokument_ptr_id'] = str(docid)

            # then iterate through other properties, dynamically
            # calling appropriate functions to massage data and put it
            # where it belongs.
            for (s,p,o) in g:
                funcname = g.qname(p).replace(":","_")
                if funcname in globals():
                    sys.stderr.write("    Calling %s\n" % funcname)
                    globals()[funcname](o,doctype)
                else:
                    sys.stderr.write("  Cant handle predicate %s\n" % funcname.replace("_",":"))

            # check for required fields:
            d = current_document
            sub_d = current_subdocument

            for fld in ('arsutgava','lopnummer','forfattningssamling_id'):
                assert fld in d

            # Move PDF files to their correct place and complement metadata
            pdffile = directory + "/downloaded/" +year + "/"+ rdffile.replace(".rdf",".pdf")
            # Create filename base, eg "FFFS-2011-42"
            fs = data['fs_doc_forfattningssamling'][int(d['forfattningssamling_id'])-1]
            basefile = "%s-%s-%s" % (fs['kortnamn'],d['arsutgava'], d['lopnummer'])
            
            if not os.path.exists("uploads/foreskrift"):
                os.makedirs("uploads/foreskrift")
            outfile = "uploads/foreskrift/%s.pdf" % basefile
            shutil.copy2(pdffile,outfile)
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
            data[table].append(d.copy())
            d.clear()
            if table=='fs_doc_fsdokument':
                
                data[doctype].append(sub_d.copy())
            sub_d.clear()
                
    return data

if __name__ == "__main__":
    directory = sys.argv[1]
    pprint(loaddata(directory))
