#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,re,shutil

from rdflib import Graph, Literal, URIRef, Namespace, RDF

DCT = Namespace('http://purl.org/dc/terms/')
RPUBL = Namespace('http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#')

def fs_kortnamn(resource):
    return ('forfattningssamling',str(resource).split("/")[-1].upper())

def parse_bemyndigande(resource):
    resource = str(resource).split("/")[-1]
    m = re.search(r'(\d+:\d+)#K?([\da-z]*)P([\da-z]*)',resource)
    d = {}
    if m:
        d['titel'] = "TODO: lagtitel"
        d['sfsnummer'] = m.group(1)
        if m.group(2):
            d['kapitelnummer'] = m.group(2)
        d['paragrafnummer'] = m.group(3)
    else:
        print "WARNING: Can't parse %s" % resource
    return ('bemyndiganden',d)

def andringar_identifierare(resource):
    return ('andringar',doc_resource_to_identifier(resource))

def upphavningar_identifierare(resource):
    return ('upphavningar',doc_resource_to_identifier(resource))

def beslutad_av_namn(resource):
    return ('beslutad_av', org_resource_to_name(resource))

def utgivare_namn(resource):
    return ('utgivare', org_resource_to_name(resource))

def doc_resource_to_identifier(resource):
    (saml,fsnr) = str(resource).split("/")[-2:]
    return saml.upper() + " " + fsnr

def org_resource_to_name(resource):
    return str(resource).split("/")[-1].capitalize().replace("_"," ")
    

literalmap = {DCT['identifier']:'identifierare',
              RPUBL['arsutgava']:'arsutgava',
              RPUBL['lopnummer']:'lopnummer',
              DCT['title']:'titel',
              DCT['abstract']:'sammanfattning',
              RPUBL['beslutandedatum']:'beslutsdatum',
              RPUBL['utkomFranTrycket']: 'utkom_fran_tryck',
              RPUBL['ikrafttradandedatum']: 'ikrafttradandedatum',
              }

resourcemap = {RPUBL['forfattningssamling']:fs_kortnamn,
               RPUBL['beslutadAv']:beslutad_av_namn,
               DCT['publisher']:utgivare_namn,
               }

listmap = {RPUBL['bemyndigande']: parse_bemyndigande,
           RPUBL['andrar']: andringar_identifierare,
           RPUBL['upphaver']: upphavningar_identifierare
           }

def loaddata(directory):
    res = {'Myndighetsforeskrift':[],
           'KonsolideradForeskrift':[],
           'AllmannaRad':[]}
    for arsutgava in [x for x in os.listdir(directory+"/distilled") if x.isdigit()]:
        for rdffile in [x for x in os.listdir(directory+"/distilled/"+arsutgava) if x.endswith(".rdf")]:
            print "loading %s/%s" % (arsutgava,rdffile)
            g = Graph()
            d = {}
            g.parse(directory+"/distilled/"+arsutgava+"/"+rdffile)
            for (s,p,o) in g:
                if p == RDF.type:
                    if o == RPUBL['MyndighetsForeskrift']:
                        res['Myndighetsforeskrift'].append(d)
                    else:
                        print "Can't handle type %s" % o
                elif p in literalmap:
                    d[literalmap[p]] = unicode(o)
                elif p in resourcemap:
                    (k,v) = resourcemap[p](o)
                    if v:
                        d[k] = v
                elif p in listmap:
                    (k,v) = listmap[p](o)
                    if k in d:
                        d[k].append(v)
                    else:
                        d[k] = [v]
                else:
                    print "Skipping %s" % p
            pdffile = directory + "/downloaded/" +arsutgava + "/"+ rdffile.replace(".rdf",".pdf")
            fileslug = d['identifierare'].replace(" ","-").replace(":","-")
            if not os.path.exists("uploads/foreskrift"):
                os.makedirs("uploads/foreskrift")
            outfile = "uploads/foreskrift/%s.pdf" % fileslug
            shutil.copy2(pdffile,outfile)
            d['content'] = outfile
    return res

if __name__ == "__main__":
    directory = sys.argv[1]
    from pprint import pprint
    pprint(loaddata(directory))
