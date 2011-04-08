# -*- coding: utf-8 -*-
from datetime import datetime
import hashlib
from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_delete, post_save
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template import loader, Context
from django.contrib.sites.models import Site
from django.core.files import File
from django.forms import TextInput, Textarea
from django.utils.feedgenerator import rfc3339_date


class Forfattningssamling(models.Model):
    """Modell för författningssamlingar."""

    # Namn på författningssamling
    titel = models.CharField(
            max_length=255,
            unique=True,
            help_text="""Namn på författningssamling, t.ex.
            <em>Exempelmyndighetens författningssamling</em>""")

    # Kortnamn på författningssamling, t.ex. "EXFS"
    kortnamn = models.CharField(
            max_length=10,
            unique=True,
            help_text="""T.ex. <em>EXFS</em>""")

    # Författningssamlingens unika identifierare, t.ex.
    # "http://rinfo.lagrummet.se/serie/fs/ra-fs". Denna erhålls från
    # projektet.
    identifierare = models.URLField(
            verify_exists=False,
            max_length=255,
            unique=True,
            help_text="Erhålls från Domstolsverket")

    def __unicode__(self):
        return u'%s %s' % (self.titel, self.kortnamn)

    # Inställningar för etiketter i administrationsgränssnittet.
    class Meta:
        verbose_name = u"Författningssamling"
        verbose_name_plural = u"Författningssamlingar"


class CelexReferens(models.Model):
    """Modell för referenser till t.ex. EG-direktiv"""

    # Dokumentetes officiella titel. Möjlighet att lämna blank i detta exempel.
    titel = models.TextField(help_text="Titel", blank=True)

    celexnummer = models.CharField(
            max_length=255,
            unique=True,
            help_text="Celexnummer, t.ex. <em>31979L0409</em>")

    def __unicode__(self):
        if len(self.titel.strip()) > 0:
            return self.titel
        else:
            return self.celexnummer

    # Inställningar för etiketter i administrationsgränssnittet.
    class Meta:
        verbose_name = u"EG-rättsreferens"
        verbose_name_plural = u"EG-rättsreferenser"


class Amnesord(models.Model):
    """Modell för ämnesord."""

    # Namn, t.ex. "Arkivgallring"
    titel = models.CharField(
            max_length=255,
            unique=True,
            help_text="Ämnesordet")

    # Beskrivning/definition av ämnesordet
    beskrivning = models.TextField(blank=True)

    def __unicode__(self):
        return self.titel

    # Inställningar för etiketter i administrationsgränssnittet.
    class Meta:
        verbose_name = u"Ämnesord"
        verbose_name_plural = u"Ämnesord"


class Bemyndigandereferens(models.Model):
    """Modell för att hantera bemyndigandereferenser."""

    # Namn, t.ex. "Arkivförordningen"
    titel = models.CharField(max_length=255,
            help_text="""T.ex. <em>Arkivförordningen</em>""")

    # SFS-nummer, t.ex. "1991:446"
    sfsnummer = models.CharField("SFS-nummer", max_length=10, blank=False,
            help_text="T.ex. <em>1991:446</em>")
 
    # Kapitelnummer, t.ex. "2"
    kapitelnummer = models.CharField(max_length=10, blank=True,
            help_text="T.ex. <em>12</em>")

    # Paragrafnummer, t.ex. "11"
    paragrafnummer = models.CharField(max_length=10, blank=True,
            help_text="T.ex. <em>12</em>")

    kommentar = models.CharField(max_length=255, blank=True,
                               help_text="""T.ex. <em>rätt att meddela föreskrifter om notarietjänstgöring och notariemeritering</em>""")

    def __unicode__(self):
		if self.kapitelnummer:
			kap_text = " kap. "
		else:
			kap_text = " "
		return u"%s (%s) %s %s %s §" % (self.titel, self.sfsnummer, self.kapitelnummer, kap_text, self.paragrafnummer)

    # Inställningar för etiketter i administrationsgränssnittet.
    class Meta:
        verbose_name=u"Bemyndigandereferens"
        verbose_name_plural=u"Bemyndigandereferenser"


class Myndighetsforeskrift(models.Model):
    """Modell för myndighetsföreskrifter. Denna hanterar det huvudsakliga
    innehållet i en författningssamling - själva föreskrifterna. Den kan enkelt
    utökas med fler egenskaper."""

    # Denna föreskrift är publicerad via FST
    publicerad = models.BooleanField(u"Är publicerad", default=False, null=False, blank=True,
            help_text="""Denna föreskrift är redan publicerad via FST. Vid eventuella felaktigheter, ändra och publicera sedan om. """)

    # Föreskriftens officiella titel
    titel = models.CharField(
            max_length=512,
            unique=True,
            help_text="""T.ex. <em>Exempelmyndighetens föreskrifter och
            allmänna råd om arkiv hos statliga myndigheter;</em>""")

    # Sammanfattning
    sammanfattning = models.CharField(
           max_length=512,
           blank=True,
           unique=False,
           help_text="""T.ex. <em>Denna föreskrift beskriver allmänna råd om arkiv hos statliga myndigheter</em>""")

    # Författningssamling (referens till post i de upprättade
    # författningssamlingarna)
    forfattningssamling = models.ForeignKey(Forfattningssamling, blank=False,
            verbose_name=u"författnings-samling")

    arsutgava = models.CharField("Årsutgåva", max_length=13,
                               unique=False, blank=False,
                               help_text="T.ex. <em>2010</em>")
    lopnummer = models.CharField("Löpnummer", max_length=3,
                               unique=False, blank=False,
                               help_text="T.ex. <em>1</em>")


    @property
    def identifierare(self):
        return "%s %s:%s" % (self.forfattningssamling.kortnamn,
                self.arsutgava, self.lopnummer)

    # Utfärdandedatum, t.ex. 2007-02-09
    beslutsdatum = models.DateField("Beslutsdatum", blank=False)

    # Ikraftträdandedatum, t.ex. 2007-02-01
    ikrafttradandedatum = models.DateField("Ikraftträdandedatum", blank=False)

    # Utkom från tryck datum, t.ex. 2007-02-09
    utkom_fran_tryck = models.DateField("Utkom från tryck", blank=False)


    # Bemyndiganden (referenser till bemyndigandereferenser)
    bemyndiganden = models.ManyToManyField(Bemyndigandereferens,
            blank=False, verbose_name=u"referenser till bemyndiganden")

    # PDF-version av dokumentet
    content = models.FileField(u"PDF-version av föreskrift",
            upload_to="foreskrift",
            blank=False,
            help_text="""Se till att dokumentet är i PDF-format.""")

    content_md5 = models.CharField(max_length=32, blank=True, null=True)

    # Koppling till ämnesord
    amnesord = models.ManyToManyField(Amnesord, blank=True, verbose_name=u"ämnesord")

    # Eventuell koppling till föreskrift som ändras (limit_choices_to
    # säkerställer att bara grundföreskrifter visas i admingränssnittet (dvs
    # man skall inte kunna ändra en ändringsföreskrift).
    andrar = models.ForeignKey("self", null=True, blank=True,
            related_name="andringar", limit_choices_to={'andrar': None}, verbose_name=u"Ändrar")

    # Anger om föreskriften är ett omtryck
    omtryck = models.BooleanField(u"Är omtryck", default=False, null=False, blank=True,
            help_text="""Anger om denna föreskrift är ett omtryck.""")

    # Referenser till EG-direktiv som denna föreskrift helt eller delvis genomför.
    celexreferenser = models.ManyToManyField(CelexReferens,
            blank=True, verbose_name=u"Bidrar till att genomföra EG-direktiv", related_name="foreskrifter")

    def typ(self):
        """Typ av dokument i klartext; Myndighetsföreskrift, Ändringsförfattning, Ändringsförfattning (omtryck)"""
        typtext = u"Myndighetsföreskrift"
        if self.andrar:
            typtext = u"Ändringsförfattning"
            if self.omtryck:
                typtext = u"Ändringsförfattning (omtryck)"
        return typtext

    def ikrafttradandear(self):
        """Returnera bara årtalet från ikraftträdandedagen."""
        return self.ikrafttradandedatum.year

    @models.permalink
    def get_absolute_url(self):
        """Genererar webbplatsens länk till denna post."""
        return ('fst_web.fs_doc.views.foreskrift',
                [str(self.forfattningssamling.kortnamn), str(self.arsutgava), str(self.lopnummer)])

    def get_rinfo_uri(self):
        """Metod för att skapa rättsinformationssystemets unika identifierare för denna post."""
        return settings.FST_PUBL_BASE_URI + self.arsutgava + ":" + self.lopnummer

    # Metod för att returnera textrepresentation av en föreskrift (används i
    # admin-gränssnittets listor)
    def __unicode__(self):
        return u'%s %s' % (self.identifierare, self.titel)

    def to_rdfxml(self):
        """Metod för att skapa den standardiserade metadataposten om denna
        föreskrift."""

        template = loader.get_template('foreskrift_rdf.xml')
        context = Context({ 'foreskrift': self, 'publisher_uri':
            settings.FST_ORG_URI, 'rinfo_base_uri': settings.FST_PUBL_BASE_URI})

        return template.render(context)

    class Meta:
        verbose_name = u"Myndighetsföreskrift"
        verbose_name_plural = u"Myndighetsföreskrifter"


class HasFile(models.Model):

    class Meta:
        abstract = True

    titel = None
    file = None

    file_md5 = models.CharField(max_length=32, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.titel)


class Bilaga(HasFile):

    foreskrift = models.ForeignKey(Myndighetsforeskrift, blank=False, related_name='bilagor')

    titel = models.CharField("Titel", max_length=512, blank=True, null=True,
        help_text="""T.ex. <em>Bilaga 1</em>""")

    file = models.FileField(u"Fil",
            upload_to="bilaga",
            blank=True, null=True,
            help_text="""Om ingen fil anges förutsätts bilagan vara en del av föreskriftsdokumentet.""")

    def get_rinfo_uri(self):
        ordinal = 1 # FIXME: compute ordinal
        return self.foreskrift.get_rinfo_uri() + "#bilaga_%s" % ordinal

    class Meta:
        verbose_name = u"Bilaga"
        verbose_name_plural = u"Bilagor"


class OvrigtDokument(HasFile):

    foreskrift = models.ForeignKey(Myndighetsforeskrift, blank=False, related_name='ovriga_dokument')

    titel = models.CharField("Titel", max_length=512, blank=False, null=False,
        help_text="""T.ex. <em>Besluts-PM för ...</em>""")

    file = models.FileField(u"Fil",
            upload_to="ovrigt",
            blank=False, null=False,
            help_text="""T.ex. en PDF-fil.""")

    def __unicode__(self):
        return u'%s' % (self.titel)

    class Meta:
        verbose_name = u"Övrigt dokument"
        verbose_name_plural = u"Övriga dokument"


class RDFPost(models.Model):

    data = models.TextField(blank=False)
    md5 = models.CharField(max_length=32, blank=False)

    def save(self, *args, **kwargs):
        self._add_checksum()
        super(RDFPost, self).save(*args, **kwargs)

    def _add_checksum(self):
        checksum = hashlib.md5()
        checksum.update(self.data)
        self.md5 = checksum.hexdigest()

    @property
    def length(self):
        return len(self.data)

    @classmethod
    def create_for(cls, obj):
        data = obj.to_rdfxml().encode("utf-8")
        return cls(data=data)


class AtomEntry(models.Model):
    """En klass för att skapa ett Atom entry för feeden. Dessa objekt skapas
    automatiskt i samband med att en föreskrift sparas, uppdateras eller
    raderas. För radering se create_delete_entry-signalen sist i denna fil. För
    uppdatering/nya poster se ModelAdmin.save_model() i rinfo/admin.py."""

    #class Meta:
    #    unique_together = ('content_type', 'object_id')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField('object_id', db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    entry_id = models.CharField(max_length=512, blank=False)

    updated = models.DateTimeField(blank=False)
    published = models.DateTimeField(blank=False)
    deleted = models.DateTimeField(blank=True, null=True)

    rdf_post = models.OneToOneField(RDFPost, null=True, blank=True)


    def to_entryxml(self):
        """Skapa en XML-representation av ett entry enligt Atom-standarden. Se
        mallen i templates/foreskrift_entry.xml"""

        template = loader.get_template('foreskrift_entry.xml')
        context = Context({
            'entry_id': self.entry_id,
            'updated': rfc3339_date(self.updated),
            'published': rfc3339_date(self.published),
            'deleted': rfc3339_date(self.deleted) if self.deleted else None,

            'doc': self.content_object,
            'rdf_post': self.rdf_post,
            'rdf_url': self.content_object.get_absolute_url() + "rdf",

            'rinfo_base_uri': settings.FST_PUBL_BASE_URI,
            'fst_site_url': settings.FST_SITE_URL
        })
        return template.render(context)


# Signal för att skapa AtomEntry-poster i samband med att föreskrifter raderas.
def create_delete_entry(sender, instance, **kwargs):
    """Skapa en speciell AtomEntry-post i samband med att en
    myndighetsföreskrift raderas. AtomEntry-posten plockas upp av
    rättsinformationssystemet (och andra) och ger möjlighet att snabbt
    korrigera felaktigheter i eventuellt redan hämtad information."""

    # Skapa AtomEntry-posten
    entry = AtomEntry(
            content_object=instance,
            updated=datetime.now(),
            published=datetime.now(),
            deleted=datetime.now(),
            entry_id=instance.get_rinfo_uri())

    # Spara AtomEntry för denna aktivitet
    entry.save()

# Koppla upp signalhanteringen
post_delete.connect(create_delete_entry, sender=Myndighetsforeskrift,
        dispatch_uid="fst_web.fs_doc.create_delete_signal")


def get_file_md5(opened_file):
    md5sum = hashlib.md5()
    block_size = 128 * md5sum.block_size
    while True:
        data = opened_file.read(block_size)
        if not data: break
        md5sum.update(data)
    return md5sum.hexdigest()


