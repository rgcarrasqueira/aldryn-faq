from adminsortable.fields import SortableForeignKey
from adminsortable.models import Sortable
from cms.models.fields import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from cms.utils.i18n import get_current_language, force_language
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.utils.translation import get_language, ugettext_lazy as _
from hvad.manager import TranslationManager
from hvad.models import TranslatableModel, TranslatedFields
from hvad.utils import get_translation


def get_slug_in_language(record, language):
    if not record:
        return None
    if language == record.language_code:
        return record.lazy_translation_getter('slug')
    else:  # hit db
        try:
            translation = get_translation(record, language_code=language)
        except models.ObjectDoesNotExist:
            return None
        else:
            return translation.slug


def get_page_url(name, language):
    try:
        url = reverse(name)
    except NoReverseMatch:
        error = _("There is no page translation for the language: %(lang)s"
                  % {'lang': language})
        raise ImproperlyConfigured(error)
    return url


class RelatedManager(models.Manager):

    def filter_by_language(self, language):
        qs = self.get_query_set()
        return qs.filter(language=language)

    def filter_by_current_language(self):
        return self.filter_by_language(get_language())


class CategoryManager(TranslationManager):

    def get_categories(self, language):
        categories = self.language(language).prefetch_related('questions')

        for category in categories:
            category.count = (category.questions
                              .filter_by_language(language).count())
        return sorted(categories, key=lambda x: -x.count)


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255, blank=True,
                              help_text=_('Auto-generated. Clean it to have it re-created. '
                                          'WARNING! Used in the URL. If changed, the URL will change. ')),
    )

    objects = CategoryManager()

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __unicode__(self):
        return self.lazy_translation_getter('name', str(self.pk))

    def get_absolute_url(self, language=None):
        language = language or get_current_language()
        slug = get_slug_in_language(self, language)
        with force_language(language):
            if not slug:  # category not translated in given language
                return get_page_url('faq', language)
            kwargs = {'category_slug': slug}
            return reverse('aldryn_faq:faq-category', kwargs=kwargs)


class Question(Sortable):
    title = models.CharField(_('Title'), max_length=255)
    language = models.CharField(_('language'), max_length=5, choices=settings.LANGUAGES)
    category = SortableForeignKey(Category, related_name='questions')
    answer = PlaceholderField('faq_question_answer', related_name='faq_questions')
    is_top = models.BooleanField(default=False)

    objects = RelatedManager()

    class Meta(Sortable.Meta):
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        ordering = ('title',)

    def __unicode__(self):
        return self.title


class QuestionsPlugin(models.Model):

    questions = models.IntegerField(default=5, help_text=_('The number of questions to be displayed.'))

    def get_queryset(self):
        return Question.objects.filter_by_language(self.language)

    def get_questions(self):
        questions = self.get_queryset()
        return questions[:self.questions]

    class Meta:
        abstract = True


class LatestQuestionsPlugin(CMSPlugin, QuestionsPlugin):

    def get_queryset(self):
        qs = super(LatestQuestionsPlugin, self).get_queryset()
        return qs.order_by('-id')


class TopQuestionsPlugin(CMSPlugin, QuestionsPlugin):

    def get_queryset(self):
        qs = super(TopQuestionsPlugin, self).get_queryset()
        return qs.filter(is_top=True)