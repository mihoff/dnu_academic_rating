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


@register.filter()
def filter_qs_by_report_period(qs, value):
    return qs.filter(report_period=value).first()
