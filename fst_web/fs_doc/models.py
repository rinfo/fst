# -*- coding: utf-8 -*-
"""Django definitions of documents and related classes used by FST"""

from datetime import datetime
import hashlib
from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template import loader, Context
from django.utils.feedgenerator import rfc3339_date
from fst_web.fs_doc import rdfviews

RINFO_PUBL_BASE = "http://rinfo.lagrummet.se/publ/"


class Document(models.Model):

    class Meta:
        abstract = True

    def get_rinfo_uri(self):
        """Return canonical document URI"""

        return RINFO_PUBL_BASE + self.get_fs_dokument_slug()

    def get_publisher_uri(self):
        """Return URI for publishing organization

        NOTE: Subclasses that want to explicitly set 'utgivare' on \
        documents should use 'to_slug(self.utgivare.namn)' instead.
        """

        return "http://rinfo.lagrummet.se/org/" + \
               to_slug(settings.FST_ORG_NAME)


class FSDokument(Document):
    """Superclass of 'Myndighetsforeskrift' and 'AllmannaRad'.

    Defined by the Django model for practical reasons.
    """

    arsutgava = models.CharField("Årsutgåva",
                                 max_length=13,
                                 unique=False,
                                 default=2011,
                                 help_text="T.ex. <em>2010</em>")
    lopnummer = models.CharField("Löpnummer",
                                 max_length=3,
                                 unique=False,
                                 help_text="T.ex. <em>1</em>")

    is_published = models.BooleanField(u"Publicerad via FST",
                                       default=False,
                                       help_text="""Grön bock = publicerad. \
                                       Rött streck = ej publicerad. \
                                       Glöm inte att publicera dina ändringar!
                                     """)

    titel = models.CharField(
        max_length=512,
        unique=True,
        help_text="""T.ex. <em>Exempelmyndighetens föreskrifter och
            allmänna råd om arkiv hos statliga myndigheter;</em>""")

    sammanfattning = models.TextField(
        max_length=512,
        blank=True,
        unique=False,
        help_text=
        """T.ex. <em>Denna föreskrift beskriver allmänna råd om arkiv hos
        statliga myndigheter</em>""")

    # NOTE: The FST webservice currently only supports document collections
    # of type 'forfattningssamling'.
    forfattningssamling = models.ForeignKey('Forfattningssamling',
                                            verbose_name=
                                            u"författningssamling")

    beslutsdatum = models.DateField("Beslutsdatum")

    ikrafttradandedatum = models.DateField("Ikraftträdandedatum")

    utkom_fran_tryck = models.DateField("Utkom från tryck")

    omtryck = models.BooleanField(u"Är omtryck",
                                  default=False,
                                  blank=True,
                                  help_text =
                                  """Anger om denna föreskrift \
                                  är ett omtryck.""")

    amnesord = models.ManyToManyField('Amnesord',
                                      blank=True,
                                      verbose_name=u"ämnesord")

    # Store checksum of uploaded file
    content_md5 = models.CharField(max_length=32,
                                   blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        """Display value for user interface."""
        return u'%s %s' % (self.identifierare, self.titel)

    @property
    def identifierare(self):
        return "%s %s:%s" % (self.forfattningssamling.kortnamn,
                             self.arsutgava, self.lopnummer)

    @models.permalink
    def get_absolute_url(self):
        """"Construct Django URL path from document attributes"""

        return ('fst_web.fs_doc.views.fs_dokument',
                [self.get_fs_dokument_slug()])

    def get_fs_dokument_slug(self):
        return "%s/%s:%s" % (self.forfattningssamling.slug,
                             self.arsutgava,
                             self.lopnummer)

    def ikrafttradandear(self):
        """Support additional sorting: by year only"""
        return self.ikrafttradandedatum.year


class AllmannaRad(FSDokument):
    """Common document type in documentcollection of type 'författningsamling'.

    See also the domain model RDF definition at:
    http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#AllmannaRad
    """

    content = models.FileField(u"PDF-version",
                               upload_to="allmanna_rad",
                               help_text=
                               """Se till att dokumentet är i PDF-format.""")

    beslutad_av = models.ForeignKey('Myndighet',
                                    related_name='ar_beslutad_av',
                                    null=True,  # TODO: add GUI to set this!
                                    blank=True)

    utgivare = models.ForeignKey('Myndighet',
                                 related_name='ar_utgivare',
                                 null=True,  # TODO: add GUI to set this!
                                 blank=True)

    andringar = models.ManyToManyField('self',
                                       blank=True,
                                       symmetrical=False,
                                       related_name='andringar_allmannarad',
                                       verbose_name=u"Ändrar")

    upphavningar = models.ManyToManyField('self',
                                          blank=True,
                                          symmetrical=False,
                                          related_name=
                                          'upphavningar_allmannarad',
                                          verbose_name=u"Upphäver")

    konsolideringar = models.ManyToManyField('self',
                                             blank=True,
                                             symmetrical=False,
                                             related_name=
                                             'konsolideringar_allmannarad',
                                             verbose_name=u"Konsoliderar")

    class Meta(FSDokument.Meta):
        verbose_name = u"Allmänna råd"
        verbose_name_plural = u"Allmänna råd"

    def role_label(self):
        """Display role of document in Django GUI

        This is a usability enhancement and not defined by the RDF model.
        """

        label = u"Grundförfattning"
        if (self.andringar.select_related().count() > 0):
            label = u"Ändringsförfattning"
        if self.omtryck:
            label += " (omtryck)"
        return label
    role_label.short_description = u"Roll"

    def to_rdfxml(self):
        """Return metadata as RDF/XML for this document."""
        return rdfviews.AllmanaRadDescription(self).to_rdfxml()


class Myndighetsforeskrift(FSDokument):
    """Main document type in document collections of type 'författningsamling'.

    See also the domain model RDF definition at:
    http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#Myndighetsforeskrift
    """

    content = models.FileField(u"PDF-version",
                               upload_to="foreskrift",
                               help_text=
                               """Se till att dokumentet är i PDF-format.""")

    bemyndiganden = models.ManyToManyField('Bemyndigandereferens',
                                           verbose_name =
                                           u"referenser till bemyndiganden")

    celexreferenser = models.ManyToManyField('CelexReferens',
                                             blank = True,
                                             related_name = "foreskrifter",
                                             verbose_name =
                                             u"Bidrar till att genomföra \
                                             EG-direktiv")

    beslutad_av = models.ForeignKey('Myndighet',
                                    related_name='doc_beslutad_av',
                                    null=True,  # TODO: add GUI to set this!
                                    blank=True)

    utgivare = models.ForeignKey('Myndighet',
                                 related_name='doc_utgivare',
                                 null=True,  # TODO: add GUI to set this!
                                 blank=True)

    andringar = models.ManyToManyField('self',
                                       blank=True,
                                       symmetrical=False,
                                       related_name='andringar_foreskrift',
                                       verbose_name=u"Ändrar")

    upphavningar = models.ManyToManyField('self',
                                          blank=True,
                                          symmetrical=False,
                                          related_name=
                                          'upphavningar_foreskrift',
                                          verbose_name=u"Upphäver")

    konsolideringar = models.ManyToManyField('self',
                                             blank=True,
                                             symmetrical=False,
                                             related_name=
                                             'konsolideringar_foreskrift',
                                             verbose_name=u"Konsoliderar")

    class Meta(FSDokument.Meta):
        verbose_name = u"Myndighetsföreskrift"
        verbose_name_plural = u"Myndighetsföreskrifter"

    def role_label(self):
        """Display role of document in Django GUI

        This is a usability enhancement and not defined by the RDF model.
        """

        label = u"Grundförfattning"
        if (self.andringar.select_related().count() > 0):
            label = u"Ändringsförfattning"
        if self.omtryck:
            label += " (omtryck)"
        return label

    role_label.short_description = u"Roll"

    def to_rdfxml(self):
        """Return metadata as RDF/XML for this document."""
        return rdfviews.MyndighetsforeskriftDescription(self).to_rdfxml()


class Myndighet(models.Model):
    """Organization publishing and/or authorizing documents."""

    namn = models.CharField(
        max_length=255,
        unique=True,
        help_text="""Namn på myndighet, t ex Exempelmyndigheten""")

    class Meta:
        verbose_name = u"Myndighet"
        verbose_name_plural = u"Myndigheter"

    def __unicode__(self):
        """Display value for user interface."""
        return u'%s' % (self.namn)

    def get_rinfo_uri(self):
        """Get URI from service provided by rinfo system """
        slug = to_slug(self.namn)
        uri = "http://rinfo.lagrummet.se/org/" + slug
        return uri


class Forfattningssamling(models.Model):
    """Document collection of type 'författningsamling'.

    See also the domain model RDF definition at:
    http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#forfattningssamling
    """

    titel = models.CharField(
        max_length=255,
        unique=True,
        help_text="""Namn på författningssamling, t.ex.
            <em>Exempelmyndighetens författningssamling</em>""")

    kortnamn = models.CharField(
        max_length=10,
        unique=True,
        help_text="""T.ex. <em>EXFS</em>""")

    slug = models.CharField(
        max_length=20,
        unique=True,
        help_text="""T.ex. <em>exfs</em>""")

    class Meta:
        verbose_name = u"Författningssamling"
        verbose_name_plural = u"Författningssamlingar"

    def __unicode__(self):
        return u'%s %s' % (self.titel, self.kortnamn)

    def get_rinfo_uri(self):
        """"Create URI for this document collection

        As specified by:
        http://dev.lagrummet.se/dokumentation/system/uri-principer.pdf
        """
        slug = to_slug(self.kortnamn)
        uri = "http://rinfo.lagrummet.se/serier/fs/" + slug
        return uri

    def identifierare(self):
        return self.get_rinfo_uri()


class HasFile(models.Model):
    """Superclass of 'Bilaga' and 'OvrigtDokument' used for uploading files.

    This class is defined by the Django model for practical reasons.
    """

    titel = None
    file = None

    file_md5 = models.CharField(max_length=32, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s' % (self.titel)


class Bilaga(HasFile):
    foreskrift = models.ForeignKey('Myndighetsforeskrift',
                                   related_name='bilagor')

    titel = models.CharField("Titel",
                             max_length = 512,
                             blank = True,
                             help_text = """T.ex. <em>Bilaga 1</em>""")

    file = models.FileField(u"Fil", upload_to="bilaga", blank=True, help_text=
                             """Om ingen fil anges förutsätts bilagan \
                            vara en del av föreskriftsdokumentet.""")

    class Meta:
        verbose_name = u"Bilaga"
        verbose_name_plural = u"Bilagor"

    def get_rinfo_uri(self):
        ordinal = 1  # FIXME: compute ordinal
        return self.foreskrift.get_rinfo_uri() + "#bilaga_%s" % ordinal


class OvrigtDokument(HasFile):
    foreskrift = models.ForeignKey('Myndighetsforeskrift',
                                   related_name='ovriga_dokument')

    titel = models.CharField("Titel", max_length=512,
                             help_text="""T.ex. <em>Besluts-PM för ...</em>""")

    file = models.FileField(u"Fil",
                            upload_to="ovrigt",
                            help_text="""T.ex. en PDF-fil.""")

    class Meta:
        verbose_name = u"Övrigt dokument"
        verbose_name_plural = u"Övriga dokument"

    def __unicode__(self):
        return u'%s' % (self.titel)


class CelexReferens(models.Model):
    titel = models.TextField(help_text="Titel", blank=True)

    celexnummer = models.CharField(
        max_length=255,
        unique=True,
        help_text="Celexnummer, t.ex. <em>31979L0409</em>")

    class Meta:
        verbose_name = u"EG-rättsreferens"
        verbose_name_plural = u"EG-rättsreferenser"

    def __unicode__(self):
        if len(self.titel.strip()) > 0:
            return self.titel
        else:
            return self.celexnummer


class Amnesord(models.Model):
    titel = models.CharField(
        max_length=255,
        unique=True,
        help_text="Ämnesordet")

    beskrivning = models.TextField(blank=True)

    class Meta:
        verbose_name = u"Ämnesord"
        verbose_name_plural = u"Ämnesord"

    def __unicode__(self):
        return self.titel


# NOTE: Classes below implement concrete relations to avoid known
# problems using self-referential M2M models with Django admin

class Andringar_foreskrift(models.Model):
    from_doc = models.ForeignKey(
        'Myndighetsforeskrift', related_name='changing')
    to_doc = models.ForeignKey(
        'Myndighetsforeskrift', related_name='changed')


class Andringar_allmannarad(models.Model):
    from_doc = models.ForeignKey('AllmannaRad',
                               related_name='changing')
    to_doc = models.ForeignKey('AllmannaRad',
                             related_name='changed')


class Upphavningar_foreskrift(models.Model):
    from_doc = models.ForeignKey('Myndighetsforeskrift',
                               related_name='cancelling')
    to_doc = models.ForeignKey('Myndighetsforeskrift',
                             related_name='cancelled')


class Upphavningar_allmannarad(models.Model):
    from_doc = models.ForeignKey('AllmannaRad',
                               related_name='cancelling')
    to_doc = models.ForeignKey('AllmannaRad',
                             related_name='cancelled')


class Konsolideringar_foreskrift(models.Model):
    from_doc = models.ForeignKey('Myndighetsforeskrift',
                               related_name = 'consolidating')
    to_doc = models.ForeignKey('Myndighetsforeskrift',
                             related_name ='consolidated')


class Konsolideringar_allmannarad(models.Model):
    from_doc = models.ForeignKey('AllmannaRad',
                               related_name = 'consolidating')
    to_doc = models.ForeignKey('AllmannaRad',
                             related_name = 'consolidated')


class KonsolideradForeskrift(Document):

    titel = models.CharField(
        max_length=512,
        unique=True,
        help_text="""T.ex. <em>Exempelmyndighetens föreskrifter och
            allmänna råd om arkiv hos statliga myndigheter;</em>""")

    konsolideringsdatum = models.DateField("Konsolideringsdatum")

    content = models.FileField(u"PDF-version",
                               upload_to="konsoliderad_foreskrift",
                               help_text=
                               """Se till att dokumentet är i PDF-format.""")

     # Store checksum of uploaded file
    content_md5 = models.CharField(max_length=32,
                                   blank=True)

    grundforfattning = models.ForeignKey('Myndighetsforeskrift',
                                 related_name='grundforfattning')

    senaste_andringsforfattning = models.ForeignKey('Myndighetsforeskrift',
                                 related_name='senaste_andringsforfattning')

    class Meta:
        verbose_name = u"Konsoliderad föreskrift"
        verbose_name_plural = u"Konsoliderade föreskrifter"

    @property
    def identifierare(self):
        return "%s i lydelse enligt %s" % (
            self.grundforfattning.identifierare, self.konsolideringsdatum)

    @models.permalink
    def get_absolute_url(self):
        """"Construct Django URL path from document attributes"""

        return ('fst_web.fs_doc.views.fs_dokument',
                [self.get_fs_dokument_slug()])

    def __unicode__(self):
        """Display value for user interface."""
        return u'%s %s' % (self.identifierare, self.titel)

    def get_fs_dokument_slug(self):
        return "%s/konsolidering/%s" % (
            self.grundforfattning.get_fs_dokument_slug(),
                                        self.konsolideringsdatum)

    def get_konsolideringsunderlag(self):
        base = self.grundforfattning
        latest = self.senaste_andringsforfattning
        yield base
        for doc in Myndighetsforeskrift.objects.filter(
                forfattningssamling=base.forfattningssamling,
                arsutgava__gte=base.arsutgava, lopnummer__gt=base.lopnummer,
                arsutgava__lte=latest.arsutgava,
                lopnummer__lte=latest.lopnummer):
            if False:  # FIXME: if "base in doc.andrar"...
                yield doc

    def to_rdfxml(self):
        """Return metadata as RDF/XML for this document."""
        return rdfviews.KonsolideradForeskriftDescription(self).to_rdfxml()


class Bemyndigandereferens(models.Model):
    titel = models.CharField(max_length=255,
                             help_text="""T.ex. <em>Arkivförordningen</em>""")

    sfsnummer = models.CharField("SFS-nummer",
                                 max_length=10,
                                 help_text="T.ex. <em>1991:446</em>")

    kapitelnummer = models.CharField(max_length=10,
                                     blank=True,
                                     help_text="T.ex. <em>12</em>")

    # Paragrafnummer, t.ex. "11"
    paragrafnummer = models.CharField(max_length =10,
                                      blank=True,
                                      help_text="T.ex. <em>12</em>")

    kommentar = models.CharField(max_length=255,
                                 blank=True,
                                 help_text=
                                 """T.ex. <em>rätt att meddela föreskrifter om\
                                 notarietjänstgöring och \
                                 notariemeritering</em>""")

    class Meta:
        verbose_name = u"Bemyndigandereferens"
        verbose_name_plural = u"Bemyndigandereferenser"

    def __unicode__(self):
        if self.kapitelnummer:
            kap_text = " kap. "
        else:
            kap_text = " "
        return u"%s (%s) %s %s %s §" % (self.titel, self.sfsnummer,
                                         self.kapitelnummer, kap_text,
                                         self.paragrafnummer)


class GenericUniqueMixin(object):

    @classmethod
    def get_for(cls, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        for instance in cls.objects.filter(content_type__pk=obj_type.id,
                                           object_id=obj.id):
            return instance

    @classmethod
    def get_or_create(cls, obj):
        return cls.get_for(obj) or cls(content_object=obj)


class RDFPost(models.Model, GenericUniqueMixin):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField('object_id', db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    slug = models.CharField(max_length=64)
    data = models.TextField()
    md5 = models.CharField(max_length=32)

    class Meta:
        unique_together = ('content_type', 'object_id')

    def save(self, *args, **kwargs):
        self.md5 = hashlib.md5(self.data).hexdigest()
        super(RDFPost, self).save(*args, **kwargs)

    @property
    def length(self):
        return len(self.data)


class AtomEntry(models.Model, GenericUniqueMixin):
    """Class to create entry for Atom feed.

    Automatically created when a document is saved, updated or deleted.
    For deletion, see the 'create_delete_entry'-signal defined below.
    For create/update, see 'ModelAdmin.save_model()' in 'rinfo/admin.py'.
    """

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField('object_id', db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    entry_id = models.CharField(max_length=512)

    updated = models.DateTimeField()
    published = models.DateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)

    rdf_post = models.OneToOneField(RDFPost, null=True, blank=True)

    def to_entryxml(self):
        """XML representation of entry according to Atom standard.

        Uses template in templates/foreskrift_entry.xml
        """

        template = loader.get_template('foreskrift_entry.xml')
        context = Context({
            'entry_id': self.entry_id,
            'updated': rfc3339_date(self.updated),
            'published': rfc3339_date(self.published),
            'deleted': rfc3339_date(self.deleted) if self.deleted else None,

            'doc': self.content_object,
            'rdf_post': self.rdf_post,
            'rdf_url': \
            None if self.deleted \
            else self.content_object.get_absolute_url() + "rdf", \
            'fst_site_url': settings.FST_SITE_URL
        })
        return template.render(context)


def create_delete_entry(sender, instance, **kwargs):
    """Create a special entry when a 'Myndighetsforeskrift' is deleted.

    This entry will be picked up by Rättsinformationssystemet (and others),
    allowing for quick corrections of already collected information."""

    existing_entry = AtomEntry.get_for(instance)
    if existing_entry:
        existing_entry.rdf_post.delete()
        existing_entry.delete()

    deleted_entry = AtomEntry(
        content_object=instance,
        updated=datetime.now(),
        published=datetime.now(),
        deleted=datetime.now(),
        entry_id=instance.get_rinfo_uri())

    deleted_entry.save()

    class Meta:
        unique_together = ('content_type', 'object_id')


post_delete.connect(create_delete_entry, sender=Myndighetsforeskrift,
                    dispatch_uid="fst_web.fs_doc.create_delete_signal")

post_delete.connect(create_delete_entry, sender=AllmannaRad,
                    dispatch_uid="fst_web.fs_doc.create_delete_signal")


def get_file_md5(opened_file):
    md5sum = hashlib.md5()
    block_size = 128 * md5sum.block_size
    while True:
        data = opened_file.read(block_size)
        if not data:
            break
        md5sum.update(data)
    return md5sum.hexdigest()


def to_slug(tag):
    """"Transform identifiers with Swedish characters for URI use.

    As specified by:
    http://dev.lagrummet.se/dokumentation/system/uri-principer.pdf
    """
    tag = tag.lower().encode("utf-8")
    slug = tag.replace('å', 'aa').replace('ä', 'ae').\
         replace('ö', 'oe').replace(' ', '_')
    return slug
