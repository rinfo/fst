# -*- coding: utf-8 -*-
"""Django definitions of documents and related classes used by FST"""

import errno
import hashlib
import os
import tempfile
from datetime import datetime
from django.conf import settings
from django.core import urlresolvers
from django.core.files import locks
from django.core.files.move import file_move_safe
from django.utils.text import get_valid_filename
from django.core.files.storage import FileSystemStorage, Storage
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models.signals import post_delete
from django.template import loader, Context
from django.utils.feedgenerator import rfc3339_date
from fst_web.fs_doc import rdfviews

RINFO_PUBL_BASE = "http://rinfo.lagrummet.se/publ/"


class OverwritingStorage(FileSystemStorage):
    """ File storage that allows overwriting of stored files.

    See: http://haineault.com/blog/147/ (describes problem)
         http://djangosnippets.org/snippets/2173/ (implements fix)
         http://djangosnippets.org/comments/cr/15/976/#c1670 (installation)
    """

    def get_available_name(self, name, max_length=None):
        return name

    def _save(self, name, content):
        """
        Lifted partially from django/core/files/storage.py
        """
        full_path = self.path(name)
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        elif not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        # This file has a file path that we can move.
        if hasattr(content, 'temporary_file_path'):
            temp_data_location = content.temporary_file_path()
        else:
            tmp_prefix = "tmp_%s" % (get_valid_filename(name), )
            temp_data_location = tempfile.mktemp(
                prefix = tmp_prefix, dir = self.location)
            try:
                # This is a normal uploadedfile that we can stream.
                # This fun binary flag incantation makes os.open throw an
                # OSError if the file already exists before we open it.
                fd = os.open(temp_data_location,
                             os.O_WRONLY | os.O_CREAT |
                             os.O_EXCL | getattr(os, 'O_BINARY', 0))
                locks.lock(fd, locks.LOCK_EX)
                for chunk in content.chunks():
                    os.write(fd, chunk)
                locks.unlock(fd)
                os.close(fd)
            except Exception as e:
                if os.path.exists(temp_data_location):
                    os.remove(temp_data_location)
                raise
        file_move_safe(temp_data_location, full_path, allow_overwrite=True)
        content.close()
        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)
        return name


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


def current_year():
    return datetime.now().year


def next_lopnummer():
    docs = FSDokument.objects.filter(arsutgava = current_year())
    numbers = []
    for doc in docs:
        numbers.append(int(doc.lopnummer))
    if numbers:
        next_nr = max(numbers) + 1
    else:
        next_nr = 1
    return next_nr


class FSDokument(Document):
    """Superclass of 'Myndighetsforeskrift' and 'AllmannaRad'.

    Defined by the Django model for practical reasons.
    """

    arsutgava = models.CharField("Årsutgåva",
                                 max_length=13,
                                 unique=False,
                                 default= current_year(),
                                 validators=[RegexValidator(
                                     regex="^(19|20)\d\d",
                                     message=u"Ange år som 19YY eller 20YY")])

    lopnummer = models.CharField(
        "Löpnummer",
        max_length=3,
        unique=False,
        default= next_lopnummer,
        validators=[RegexValidator(
            regex="^\d+$",
            message=u"Löpnummer får bara innehålla siffror")])

    is_published = models.BooleanField(u"Publicerad via FST",
                                       default=False,
                                       help_text="""Grön bock = publicerad. \
                                       Rött kryss = ej publicerad. \
                                       Kom ihåg att publicera dina ändringar!
                                     """)

    titel = models.CharField(
        max_length=512,
        unique=False)

    sammanfattning = models.TextField(
        max_length=8192,
        unique=False,
        default="Sammanfattning saknas",
        help_text=
        """<em>Ange valfri sammanfattning av dokuments syfte.</em>""")

    # NOTE: The FST webservice currently only supports document collections
    # of type 'forfattningssamling'.
    forfattningssamling = models.ForeignKey('Forfattningssamling',
        verbose_name=u"författningssamling")

    beslutsdatum = models.DateField("Beslutsdatum")

    ikrafttradandedatum = models.DateField("Ikraftträdandedatum")

    utkom_fran_tryck = models.DateField("Utkom från tryck")

    omtryck = models.BooleanField(u"Är omtryck",
                                  default=False,
                                  blank=True)

    amnesord = models.ManyToManyField('Amnesord',
                                      blank=True,
                                      verbose_name=u"ämnesord")

    # Store checksum of uploaded file
    content_md5 = models.CharField(max_length=32,
                                   blank=True)

    def __str__(self):
        """Display value for user interface."""
        return u'%s %s' % (self.identifierare, self.titel)

    @property
    def identifierare(self):
        return "%s %s:%s" % (self.forfattningssamling.kortnamn,
                             self.arsutgava, self.lopnummer)

    @models.permalink
    def get_absolute_url(self):
        """"Construct Django URL path from document attributes"""

        return ('fs_dokument', [self.get_fs_dokument_slug()])

    def get_admin_url(self):
        """Return URL for editing this document in Django admin."""

        content_type = ContentType.objects.get_for_model(self)
        edit_url = urlresolvers.reverse(
            "admin:fs_doc_" + content_type.model + "_change",
            args=(self.id,))
        return edit_url

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
                               storage=OverwritingStorage(),
                               help_text=
                               """Se till att dokumentet är i PDF-format.""")

    beslutad_av = models.ForeignKey('Myndighet',
                                    related_name='ar_beslutad_av',
                                    null=True,
                                    blank=False)

    utgivare = models.ForeignKey('Myndighet',
                                 related_name='ar_utgivare',
                                 null=True,
                                 blank=False)

    andringar = models.ManyToManyField('self',
                                       blank=True,
                                       symmetrical=False,
                                       related_name='andringar_allmannarad',
                                       verbose_name=u"Dokument som ändras")

    upphavningar = models.ManyToManyField('self',
                                          blank=True,
                                          symmetrical=False,
                                          related_name=
                                          'upphavningar_allmannarad',
                                          verbose_name=u"Dokument som upphävs")

    konsolideringar = models.ManyToManyField('self',
                                             blank=True,
                                             symmetrical=False,
                                             related_name=
                                             'konsolideringar_allmannarad',
                                             verbose_name=\
                                             u"Konsolideringsunderlag")

    class Meta(FSDokument.Meta):
        verbose_name = u"allmänna råd"
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
                               storage=OverwritingStorage(),
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
                                             dessa EU-direktiv")

    beslutad_av = models.ForeignKey('Myndighet',
                                    related_name='doc_beslutad_av',
                                    null=True,
                                    blank=False)

    utgivare = models.ForeignKey('Myndighet',
                                 related_name='doc_utgivare',
                                 null=True,
                                 blank=False)

    andringar = models.ManyToManyField('self',
                                       blank=True,
                                       symmetrical=False,
                                       related_name='andringar_foreskrift',
                                       verbose_name=u"Dokument som ändras")

    upphavningar = models.ManyToManyField('self',
                                          blank=True,
                                          symmetrical=False,
                                          related_name=
                                          'upphavningar_foreskrift',
                                          verbose_name=u"Dokument som upphävs")

    konsolideringar = models.ManyToManyField('self',
                                             blank=True,
                                             symmetrical=False,
                                             related_name=
                                             'konsolideringar_foreskrift',
                                             verbose_name=\
                                             u"Konsolideringsunderlag")

    class Meta(FSDokument.Meta):
        verbose_name = u"myndighetsföreskrift"
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
        help_text="""Myndighetens fullständiga namn""")

    class Meta:
        verbose_name = u"myndighet"
        verbose_name_plural = u"Myndigheter"

    def __str__(self):
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
        help_text="""Fullständigt namn, t.ex.
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
        verbose_name = u"författningssamling"
        verbose_name_plural = u"Författningssamlingar"

    def __str__(self):
        return u'%s %s' % (self.titel, self.kortnamn)

    def get_rinfo_uri(self):
        """"Create URI for this document collection

        As specified by:
        http://dev.lagrummet.se/dokumentation/system/uri-principer.pdf
        """
        slug = to_slug(self.kortnamn)
        uri = "http://rinfo.lagrummet.se/serie/fs/" + slug
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

    def __str__(self):
        return u'%s' % (self.titel)


class Bilaga(HasFile):
    foreskrift = models.ForeignKey('FSDokument',
                                   related_name='bilagor')

    titel = models.CharField("Titel",
                             max_length = 512,
                             blank = True,
                             help_text = """T.ex. <em>Bilaga 1</em>""")

    file = models.FileField(u"Fil",
                            upload_to="bilaga",
                            storage=OverwritingStorage(),
                            blank=True,
                            help_text=
                            """Om ingen fil anges förutsätts bilagan \
                            vara en del av föreskriftsdokumentet.""")

    class Meta:
        verbose_name = u"bilaga"
        verbose_name_plural = u"Bilagor"

    def get_rinfo_uri(self):
        ordinal = 1  # FIXME: compute ordinal
        return self.foreskrift.get_rinfo_uri() + "#bilaga_%s" % ordinal


class OvrigtDokument(HasFile):
    foreskrift = models.ForeignKey('FSDokument',
                                   related_name='ovriga_dokument')

    titel = models.CharField("Titel", max_length=512,
                             help_text="""T.ex. <em>Besluts-PM för ...</em>""")

    file = models.FileField(u"Fil",
                            upload_to="ovrigt",
                            storage=OverwritingStorage())

    class Meta:
        verbose_name = u"övrigt dokument"
        verbose_name_plural = u"Övriga dokument"

    def __str__(self):
        return u'%s' % (self.titel)


class CelexReferens(models.Model):
    titel = models.TextField(help_text="Titel", blank=True)

    celexnummer = models.CharField(
        max_length=255,
        unique=True,
        help_text="Celexnummer, t.ex. <em>31979L0409</em>")

    class Meta:
        verbose_name = u"EU-rättsreferens"
        verbose_name_plural = u"EU-rättsreferenser"

    def __str__(self):
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
        verbose_name = u"ämnesord"
        verbose_name_plural = u"Ämnesord"

    def __str__(self):
        return self.titel


# NOTE: Classes below implement concrete relations to avoid known
# problems using self-referential M2M models with Django admin

class Andringar_fsdokument(models.Model):
    from_doc = models.ForeignKey('FSDokument', related_name='changing')
    to_doc = models.ForeignKey('FSDokument', related_name='changed')


class Upphavningar_fsdokument(models.Model):
    from_doc = models.ForeignKey('FSDokument', related_name='cancelling')
    to_doc = models.ForeignKey('FSDokument', related_name='cancelled')


class Konsolideringar_foreskrift(models.Model):
    # NOTE: if AllmannaRad can be "konsoliderade", generalize this to
    # FSDokument instead of Myndighetsforeskrift
    from_doc = models.ForeignKey('Myndighetsforeskrift',
                                 related_name = 'consolidating')
    to_doc = models.ForeignKey('Myndighetsforeskrift',
                               related_name ='consolidated')


class KonsolideradForeskrift(Document):

    titel = models.CharField(
        max_length=512,
        unique=True)

    konsolideringsdatum = models.DateField("Konsolideringsdatum")

    content = models.FileField(u"PDF-version",
                               upload_to="konsoliderad_foreskrift",
                               help_text=
                               """Se till att dokumentet är i PDF-format.""")

        # Store checksum of uploaded file
    content_md5 = models.CharField(max_length=32,
                                   blank=True)

    grundforfattning = models.ForeignKey(
        'Myndighetsforeskrift',
        related_name='grundforfattning')

    senaste_andringsforfattning = models.ForeignKey(
        'Myndighetsforeskrift',
        related_name='senaste_andringsforfattning')

    class Meta:
        verbose_name = u"konsoliderad föreskrift"
        verbose_name_plural = u"Konsoliderade föreskrifter"

    @property
    def identifierare(self):
        return "%s i lydelse enligt %s" % (
            self.grundforfattning.identifierare, self.konsolideringsdatum)

    #@models.permalink
    #def get_absolute_url(self):
        #""""Construct Django URL path from document attributes"""

        #return ('fst_web.fs_doc.views.fs_dokument',
                #[self.get_fs_dokument_slug()])

    def __str__(self):
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
            id__in=base.andringar_foreskrift.all(),
            arsutgava__gte=base.arsutgava,
            lopnummer__gt=base.lopnummer,
            arsutgava__lte=latest.arsutgava,
            lopnummer__lte=latest.lopnummer):
            yield doc

    def role_label(self):
        """Display role of document in Django GUI

        This is a usability enhancement and not defined by the RDF model.
        """

        label = u"Konsoliderad författning"

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
        verbose_name = u"bemyndigandereferens"
        verbose_name_plural = u"Bemyndigandereferenser"

    def __str__(self):
        if self.kapitelnummer:
            kap_text = " kap."
        else:
            kap_text = ""
        return u"%s %s %s § %s %s " % (self.kapitelnummer,
                                        kap_text,
                                        self.paragrafnummer,
                                        self.sfsnummer,
                                        self.titel)


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
    content_object = GenericForeignKey('content_type', 'object_id')

    slug = models.CharField(max_length=64)
    data = models.TextField()
    md5 = models.CharField(max_length=32)

    class Meta:
        unique_together = ('content_type', 'object_id')
        verbose_name = u"RDF-representation"
        verbose_name_plural = u"Metadata"

    def save(self, *args, **kwargs):
        self.md5 = hashlib.md5(self.data).hexdigest()
        super(RDFPost, self).save(*args, **kwargs)

    @property
    def length(self):
        """Returns length in octets (not characters)"""
        return len(self.data.encode('utf-8'))


class AtomEntry(models.Model, GenericUniqueMixin):
    """Class to create entry for Atom feed.

    Automatically created when a document is saved, updated or deleted.
    For deletion, see the 'create_delete_entry'-signal defined below.
    For create/update, see 'ModelAdmin.save_model()' in 'rinfo/admin.py'.
    """

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField('object_id', db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    entry_id = models.CharField(max_length=512)

    updated = models.DateTimeField()
    published = models.DateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)

    rdf_post = models.OneToOneField(RDFPost, null=True, blank=True)

    class Meta:
        verbose_name = u"Flödespost"
        verbose_name_plural = u"Poster i ATOM-flödet"

    def to_entryxml(self):
        """XML representation of entry according to Atom standard.

        Uses template in templates/foreskrift_entry.xml
        """
        if not self.content_object:
            # Can happen with old databases that may have stale
            # AtomEntry-objects with the delete property set.
            return ""
        template = loader.get_template('foreskrift_entry.xml')
        context = {
            'entry_id': self.entry_id,
            'updated': rfc3339_date(self.updated),
            'published': rfc3339_date(self.published),
            'deleted': rfc3339_date(self.deleted) if self.deleted else None,
            'doc': self.content_object,
            'rdf_post': self.rdf_post,
            'rdf_url': \
            None if self.deleted \
            else self.content_object.get_absolute_url() + "rdf", \
            'fst_instance_url': settings.FST_INSTANCE_URL
        }
        return template.render(context)


def delete_entry(sender, instance, **kwargs):
    """Delete associated Atom entry when a document is deleted."""
    existing_entry = AtomEntry.get_for(instance)
    if existing_entry:
        existing_entry.rdf_post.delete()
        existing_entry.delete()
     #deleted_entry = AtomEntry(
         #content_object=instance,
         #updated=datetime.now(),
         #published=datetime.now(),
         #deleted=datetime.now(),
         #entry_id=instance.get_rinfo_uri())

     #deleted_entry.save()

     #class Meta:
         #unique_together = ('content_type', 'object_id')


post_delete.connect(
    delete_entry,
    sender=Myndighetsforeskrift,
    dispatch_uid="fs_doc.Myndighetsforeskrift.create_delete_signal")

post_delete.connect(
    delete_entry,
    sender=AllmannaRad,
    dispatch_uid="fs_doc.AllmannaRad.create_delete_signal")

post_delete.connect(
    delete_entry,
    sender=KonsolideradForeskrift,
    dispatch_uid="fs_doc.KonsolideradForeskrift.create_delete_signal")


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
    tag = tag.lower()
    slug = tag.replace('å', 'aa').replace('ä', 'ae').\
         replace('ö', 'oe').replace(' ', '_')
    return slug


def generate_atom_entry_for(obj, update_only=False):
    updated = datetime.utcnow()

    # Check if we already published this document
    obj_type = ContentType.objects.get_for_model(obj)
    entries = AtomEntry.objects.filter(content_type__pk=obj_type.id,
                                       object_id=obj.id)
    # Find entry for object
    for entry in entries.order_by("published"):
        entry_published = entry.published
        break
    else:
        if update_only:
            return
        # For new documents
        entry_published = updated

    # Get RDF representation of object
    rdf_post = RDFPost.get_for(obj)

    entry = AtomEntry.get_or_create(obj)
    entry.entry_id = obj.get_rinfo_uri()
    entry.updated = updated
    entry.published = entry_published
    entry.rdf_post = rdf_post
    entry.save()


def generate_rdf_post_for(obj):
    # Create RDF metadata
    rdf_post = RDFPost.get_or_create(obj)
    rdf_post.slug = obj.get_fs_dokument_slug()
    rdf_post.data = obj.to_rdfxml()
    rdf_post.save()
    return rdf_post
