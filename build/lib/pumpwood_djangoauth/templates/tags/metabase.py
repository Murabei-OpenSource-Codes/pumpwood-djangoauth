"""Custom tags used on hole site."""
from django import template
from django.utils.html import format_html
from pumpwood_djangoauth.config import microservice


register = template.Library()


@register.simple_tag
def metabase_dash_url(dashboard_id, variable_name=None, variable_value=None):
    if dashboard_id is None:
        return "O objeto ainda não foi criado"
    else:
        microservice.login()
        dashboard_parameters = {
            "dashboard_parameters": {}
        }
        if variable_name and variable_value:
            dashboard_parameters['dashboard_parameters'] = {
                variable_name: variable_value
            }
        actions = microservice.execute_action(
            model_class="MetabaseDashboard",
            pk=dashboard_id,
            action="generate_url",
            parameters=dashboard_parameters)

        iframe_url = actions["result"]
        iframe_html = (
            '<div style="width: 100%; height: 850px;">'
            '<iframe src="{iframe_url}" frameborder="0" '
            'width="100%" '
            'height="800px" '
            'allowtransparency>'
            '</iframe> '
            '</div>'
        ).format(iframe_url=iframe_url)
        html = format_html(iframe_html)
        return html


@register.simple_tag
def metabase_dash_url_alias(dashboard_alias, variable_name=None,
                            variable_value=None):
    if dashboard_alias is None:
        return "O objeto ainda não foi criado"
    else:
        microservice.login()
        dashboard_parameters = {
            "alias": dashboard_alias,
            "dashboard_parameters": {}
        }
        if variable_name and variable_value:
            dashboard_parameters['dashboard_parameters'] = {
                variable_name: variable_value
            }
        actions = microservice.execute_action(
            model_class="MetabaseDashboard",
            action="generate_url_from_alias",
            parameters=dashboard_parameters)

        iframe_url = actions["result"]
        iframe_html = (
            '<div style="width: 100%; height: 850px;">'
            '<iframe src="{iframe_url}" frameborder="0" '
            'width="100%" '
            'height="800px" '
            'allowtransparency>'
            '</iframe> '
            '</div>'
        ).format(iframe_url=iframe_url)
        html = format_html(iframe_html)
        return html
