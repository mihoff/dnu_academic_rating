from django.template import Library

register = Library()


@register.filter()
def period_url_replace(value: str) -> str:
    """
    Replace slash to dash for correct url path
    :param value:
    :return:
    """
    return value.replace("/", "-")
