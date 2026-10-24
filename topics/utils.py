import uuid

from django.utils.text import slugify

from topics.models import Topic

CYRILLIC_TO_LATIN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z',
    'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh',
    'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def transliterate(text):
    return ''.join(CYRILLIC_TO_LATIN.get(char, char) for char in text.lower())


def slug_generator(instance):
    """Уникальный slug из названия топика.

    slugify() без транслитерации превращает русское название в пустую строку,
    а пустой slug не подходит под маршрут <slug:slug> (NoReverseMatch).
    """
    base = slugify(transliterate(instance.title))[:200] or 'topic'
    slug = base
    while Topic.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f'{base}-{uuid.uuid4().hex[:6]}'
    return slug
