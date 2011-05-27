# -*- coding: UTF-8 -*-
from rdflib import Graph, BNode, Literal, Namespace, RDF, URIRef


DCT = Namespace("http://purl.org/dc/terms/")
DCES = Namespace("http://purl.org/dc/elements/1.1/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
RPUBL = Namespace("http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#")

RINFO_BASE = "http://rinfo.lagrummet.se"


def eur_lex_ref(celexnum):
    return URIRef("%s/ext/eur-lex/%s" % (RINFO_BASE, celexnum))


def sfs_ref(sfsnum):
    return URIRef("%s/publ/sfs/%s" % (RINFO_BASE, sfsnum))


class Description(object):

    def to_rdfxml(self):
        graph = self.to_rdf()
        graph.namespace_manager.bind('dct', DCT)
        graph.namespace_manager.bind('dces', DCES)
        graph.namespace_manager.bind('foaf', FOAF)
        graph.namespace_manager.bind('', RPUBL)
        return graph.serialize(format='pretty-xml')


class DocumentDescription(Description):

    def __init__(self, obj):
        self.obj = obj
        self.ref = URIRef(obj.get_rinfo_uri())

    def to_rdf(self):
        graph = Graph()
        obj = self.obj
        add = lambda p, o: graph.add((self.ref, p, o))

        add(DCT.title, Literal(obj.titel, lang='sv'))
        add(DCT.identifier, Literal(obj.identifierare))
        add(DCT.publisher, URIRef(obj.get_publisher_uri()))

        return graph


class FSDokumentDescription(DocumentDescription):

    def to_rdf(self):
        graph = super(FSDokumentDescription, self).to_rdf()
        obj = self.obj
        add = lambda p, o: graph.add((self.ref, p, o))

        add(RPUBL.arsutgava, Literal(obj.arsutgava))
        add(RPUBL.lopnummer, Literal(obj.lopnummer))
        add(RPUBL.beslutsdatum, Literal(obj.beslutsdatum))
        add(RPUBL.ikrafttradandedatum, Literal(obj.ikrafttradandedatum))
        add(RPUBL.utkomFranTryck, Literal(obj.utkom_fran_tryck))

        if obj.omtryck:
            for changed_doc in obj.andringar.all():
                add(RPUBL.omtryckAv, URIRef(changed_doc.get_rinfo_uri()))

        for changed_doc in obj.andringar.all():
            add(RPUBL.andrar, URIRef(changed_doc.get_rinfo_uri()))

        for amnesord in obj.amnesord.all():
            add(DCES.subject, Literal(amnesord.titel, lang="sv"))

        return graph


class AllmanaRadDescription(FSDokumentDescription):

    def to_rdf(self):
        graph = super(AllmanaRadDescription, self).to_rdf()
        graph.add((self.ref, RDF.type, RPUBL.AllmannaRad))
        obj = self.obj
        add = lambda p, o: graph.add((self.ref, p, o))

        add(RDF.type, RPUBL.AllmannaRad)

        return graph


class MyndighetsforeskriftDescription(FSDokumentDescription):

    def to_rdf(self):
        graph = super(MyndighetsforeskriftDescription, self).to_rdf()
        obj = self.obj
        add = lambda p, o: graph.add((self.ref, p, o))

        add(RDF.type, RPUBL.Myndighetsforeskrift)

        if obj.celexreferenser.all():
            for referens in obj.celexreferenser.all():
                add(RPUBL.genomforDirektiv, eur_lex_ref(referens.celexnummer))

        for bemyndigande in obj.bemyndiganden.all():
            bemyndigande_ref = BNode()
            add(RPUBL.bemyndigande, bemyndigande_ref)
            bemyndigande_add = lambda p, o: graph.add((bemyndigande_ref, p, o))
            bemyndigande_add(RDF.type, RPUBL.Forfattningsreferens)
            bemyndigande_add(RPUBL.angerGrundforfattning,
                             sfs_ref(bemyndigande.sfsnummer))
            if bemyndigande.kapitelnummer:
                bemyndigande_add(RPUBL.angerKapitelnummer,
                                 Literal(bemyndigande.kapitelnummer))
            bemyndigande_add(RPUBL.angerParagrafnummer,
                             Literal(bemyndigande.paragrafnummer))

        for i, bilaga in enumerate(obj.bilagor.all()):
            if bilaga.titel:
                bilaga_ref = URIRef("%s#bilaga_%s" %
                                    (obj.get_rinfo_uri(), i+1))
                add(RPUBL.bilaga, bilaga_ref)
                graph.add((bilaga_ref, DCT.title,
                           Literal(bilaga.titel)))  # no lang?

        for dok in obj.ovriga_dokument.all():
            dok_ref = URIRef("%s/%s" % (obj.get_rinfo_uri(), dok.file.url))
            dok_add = lambda p, o: graph.add((dok_ref, p, o))
            dok_add(RDF.type, FOAF.Document)
            dok_add(DCT.title, Literal(dok.titel, lang="sv"))
            dok_add(FOAF.primaryTopic, self.ref)

        return graph


class KonsolideradForeskriftDescription(DocumentDescription):

    def to_rdf(self):
        graph = super(KonsolideradForeskriftDescription, self).to_rdf()
        obj = self.obj
        add = lambda p, o: graph.add((self.ref, p, o))

        add(RDF.type, RPUBL.KonsolideradGrundforfattning)
        add(DCT.issued, Literal(obj.konsolideringsdatum))

        add(RPUBL.konsoliderar, URIRef(obj.grundforfattning.get_rinfo_uri()))

        for dok in obj.get_konsolideringsunderlag():
            add(RPUBL.konsolideringsunderlag, URIRef(dok.get_rinfo_uri()))

        return graph

