#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,re,shutil,hashlib
from pprint import pprint

from rdflib import Graph, Literal, URIRef, Namespace, RDF

DCT = Namespace('http://purl.org/dc/terms/')
RPUBL = Namespace('http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#')

# Normal dicts aren't hashable, and can thus not be keys in dicts
# themselves. These dicts can (but modifying it will change the hash,
# so don't do that)
class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

# Global dict. key: bemyndigande (hashable)dict, value: id (seems
# backwards but is practical)
bemyndiganden = {}

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


def doc_resource_to_identifier(resource):
    (saml,fsnr) = str(resource).split("/")[-2:]
    return saml.upper() + " " + fsnr

def org_resource_to_namn(resource):
    return str(resource).split("/")[-1].capitalize().replace("_"," ")


# Assignment functions: Each of these functions get dynamically called
# when a corresponding predicate is found in the RDF data. They do the
# appropriate data mangling and assigns the result to the correct
# place in data
def rdf_type(obj,doctype,data): pass
def dct_issn(obj,doctype,data): pass
def dct_identifier(obj,doctype,data): pass

def dct_title(obj, doctype, data):
    data['fs_doc_fsdokument'][-1]['titel'] = unicode(obj)

def rpubl_arsutgava(obj, doctype, data):
    data['fs_doc_fsdokument'][-1]['arsutgava'] = str(obj)
    
def rpubl_lopnummer(obj, doctype, data):
    data['fs_doc_fsdokument'][-1]['lopnummer'] = str(obj)

def rpubl_utkomFranTrycket(obj, doctype, data):
    data['fs_doc_fsdokument'][-1]['utkom_fran_tryck'] = str(obj)

def rpubl_beslutandedatum(obj, doctype, data):
    data['fs_doc_fsdokument'][-1]['beslutsdatum'] = str(obj)

def rpubl_ikrafttradandedatum(obj, doctype, data):
    data['fs_doc_fsdokument'][-1]['ikrafttradandedatum'] = str(obj)

def rpubl_beslutadAv(obj, doctype, data):
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
    data[doctype][-1]['beslutad_av_id'] = str(myndighet_id)
    # FIXME: This isn't right, but the RDF data lacks dct:publisher for now
    data[doctype][-1]['utgivare_id'] = str(myndighet_id)

def rpubl_forfattningssamling(obj, doctype, data):
    # 1. calculate kortnamn
    slug = obj.split("/")[-1]
    kortnamn = slug.upper()
    # 2. find id of forfattningssamling
    forfattningssamling_id = None
    for d in data['fs_doc_forfattningssamling']:
        if d['kortnamn'] == kortnamn:
            forfattningssamling_id = d['id']
            break
    # 3. add forfattningssamling if not found
    if not forfattningssamling_id:
        forfattningssamling_id = len(data['fs_doc_forfattningssamling'])+1
        data['fs_doc_forfattningssamling'].append({'id':str(forfattningssamling_id),
                                                   # FIXME: Find out real name
                                                   'titel':u'%s författningssamling'%kortnamn,
                                                   'kortnamn':kortnamn,
                                                   'slug':slug})
    # 4. set id value
    data['fs_doc_fsdokument'][-1]['forfattningssamling_id'] = str(forfattningssamling_id)

    
def rpubl_bemyndigande(obj, doctype, data):
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
        data['fs_doc_bemyndigandereferens'].append(parse_bemyndigande(obj))
        data['fs_doc_bemyndigandereferens'][-1]['id'] = str(bemyndigande_id)
    
    # 4. add entry to connection table
    docid = data['fs_doc_fsdokument'][-1]['id'] # could use len(data['fs_doc_fsdokument'])
    conn_id = len(data['fs_doc_myndighetsforeskrift_bemyndiganden'])+1
    data['fs_doc_myndighetsforeskrift_bemyndiganden'].append({'id':str(conn_id),
                                                              'myndighetsforeskrift_id':docid,
                                                              'bemyndigandereferens_id':str(bemyndigande_id)})
    

def loaddata(directory):
    res = {'fs_doc_fsdokument':[],
           'fs_doc_myndighetsforeskrift':[],
           'fs_doc_konsolideradforeskrift':[],
           'fs_doc_allmannarad':[],
           'fs_doc_myndighet':[],
           'fs_doc_forfattningssamling':[],
           'fs_doc_bemyndigandereferens':[],
           'fs_doc_myndighetsforeskrift_bemyndiganden':[],
           }
    for arsutgava in sorted([x for x in os.listdir(directory+"/distilled") if x.isdigit()], reverse=True):
        for rdffile in [x for x in os.listdir(directory+"/distilled/"+arsutgava) if x.endswith(".rdf")]:
            sys.stderr.write("loading %s/%s\n" % (arsutgava,rdffile))
            g = Graph()
            g.bind('dct','http://purl.org/dc/terms/')
            g.bind('rpubl','http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#')
            g.parse(directory+"/distilled/"+arsutgava+"/"+rdffile)

            # first get type
            for (s,p,o) in g:
                if p == RDF.type:
                    if o == RPUBL['MyndighetsForeskrift']:
                        doctype = 'fs_doc_myndighetsforeskrift'
                        dokid = len(res['fs_doc_fsdokument']) + 1
                        res['fs_doc_fsdokument'].append({'id':str(dokid),
                                                         'is_published':'0'})
                        res['fs_doc_myndighetsforeskrift'].append({'fsdokument_ptr_id':str(dokid)})
                    elif o == RPUBL['AllmannaRad']:
                        doctype = 'fs_doc_allmannarad'
                        dokid = len(res['fs_doc_fsdokument']) + 1
                        res['fs_doc_fsdokument'].append({'id':str(dokid),
                                                         'is_published':'0'})
                        res['fs_doc_allmannarad'].append({'fsdokument_ptr_id':dokid})
                    elif o == RPUBL['KonsolideradGrundforfattning']:
                        doctype = 'fs_doc_konsolideradforeskrift'
                        dokid = len(res['fs_doc_konsolideradforeskrift']) + 1
                        res['fs_doc_konsolideradforeskrift'].append({'id':str(dokid),
                                                                     'is_published':'0'})
                    else:
                        sys.stderr.write("Can't handle type %s\n" % o)

            # then iterate through other properties, dynamically
            # calling appropriate functions to massage data and put it
            # where it belongs.
            for (s,p,o) in g:
                funcname = g.qname(p).replace(":","_")
                if funcname in globals():
                    sys.stderr.write("    Calling %s\n" % funcname)
                    globals()[funcname](o,doctype,res)
                else:
                    sys.stderr.write("  Cant handle predicate %s\n" % funcname.replace("_",":"))

            pdffile = directory + "/downloaded/" +arsutgava + "/"+ rdffile.replace(".rdf",".pdf")
            # Create filename base, eg "FFFS-2011-42"
            d = res['fs_doc_fsdokument'][-1]
            sub_d = res[doctype][-1]
            fs = res['fs_doc_forfattningssamling'][int(d['forfattningssamling_id'])-1]
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
            
    return res

if __name__ == "__main__":
    directory = sys.argv[1]
    pprint(loaddata(directory))
