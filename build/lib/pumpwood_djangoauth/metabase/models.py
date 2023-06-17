"""Manage Kong routes for Pumpwood."""
import jwt
import os
import time
import pandas as pd
from django.db import models
from django.conf import settings
from pumpwood_djangoviews.action import action
from pumpwood_communication.serializers import PumpWoodJSONEncoder
from pumpwood_communication.exceptions import PumpWoodActionArgsException
from pumpwood_djangoauth.config import microservice_no_login


class MetabaseDashboard(models.Model):
    """Metabase dashboard to serve using Pumpwood."""

    STATUS = (
        ("inactive", "Archived"),
        ("homolog", "Homologation"),
        ("production", "Production"),
    )

    THEME = (
        ("light", "light"),
        ("night", "dark"),
        ("transparent", "transparent"),
    )

    status = models.CharField(
        choices=STATUS, max_length=15, verbose_name="Status",
        help_text="Status")
    description = models.CharField(
        null=False, max_length=100, unique=True,
        help_text="service url to redirect the http calls.")
    notes = models.TextField(
        null=False, default="", blank=True,
        help_text="a long description of the dashboard.")
    metabase_id = models.IntegerField(
        null=False, help_text="Metabase Dashboard Id.")
    expire_in_min = models.IntegerField(
        null=False, default=10, help_text="Minutes to expire url.")
    default_theme = models.CharField(
        choices=THEME, max_length=15, default="light",
        verbose_name="Theme", help_text="Theme")
    default_is_bordered = models.BooleanField(
        default=False, verbose_name="Is bordered?", help_text="Is Bordered?")
    default_is_titled = models.BooleanField(
        default=False, verbose_name="Is titled?", help_text="Is titled?")
    dimensions = models.JSONField(
        encoder=PumpWoodJSONEncoder, null=False, default=dict,
        blank=True, verbose_name="Dimentions",
        help_text="Key/Value Dimentions")
    extra_info = models.JSONField(
        encoder=PumpWoodJSONEncoder, null=False, default=dict,
        blank=True, verbose_name="Extra information",
        help_text="Extra information")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True, related_name='metabase_dash_set',
        verbose_name="Created By", help_text="Created By")
    updated_at = models.DateTimeField(
        null=False, blank=True, verbose_name="Created At",
        help_text="Created At", auto_now=True)

    def __str__(self):
        return '[%s] %s' % (self.id, self.description)

    class Meta:
        db_table = 'metabase__dashboard'

    @action(info='Generate url to embed with iframe.',
            auth_header="auth_header")
    def generate_url(self, auth_header: dict, dashboard_parameters: dict = {},
                     theme: str = None, bordered: bool = None,
                     titled: bool = None) -> str:
        """
        Generate url to embed graph and dash with iframe.

        Create a url to embedded dashboard or graph on front end using
        iframe. Ex.:
            <iframe
                src="{% metabase_dash_url 1 %}"
                frameborder="0"
                width="800"
                height="600"
                allowtransparency
            ></iframe>
        Args
            No Args.
        Kwargs:
            list_service_id [list]: List of ids to reload routes on Kong.
        Return [bool]:
            Return true.
        """
        # Read env Metabase variables.
        METABASE_SITE_URL = os.getenv("METABASE_SITE_URL")
        METABASE_SECRET_KEY = os.getenv("METABASE_SECRET_KEY")

        # List parameters associated with dashboard
        parameter_dict = {}
        parameter_dict_error = {}
        for o in self.parameter_set.all():
            paramenter_value = dashboard_parameters.get(
                o.name, o.default_value)
            if paramenter_value is None:
                if o.type == 'user_id':
                    user_info = microservice_no_login.get_user_info(
                        auth_header=auth_header)
                    parameter_dict[o.name] = user_info["pk"]
                else:
                    parameter_dict_error[o.name] = (
                        "Missing and without default value")
            else:
                try:
                    if o.type == 'int':
                        parameter_dict[o.name] = str(int(paramenter_value))
                    elif o.type == 'str':
                        parameter_dict[o.name] = str(paramenter_value)
                    elif o.type == 'datetime':
                        parameter_dict[o.name] = pd.to_datetime(
                            paramenter_value).isoformat()
                    elif o.type == 'float':
                        parameter_dict[o.name] = str(float(paramenter_value))
                    else:
                        msg = (
                            "It was not possible to convert type [{}]"
                        ).format(o.type)
                        raise Exception(msg)
                except Exception as e:
                    msg = (
                        "Error parsing to [{type}] value [{value}]:\n"
                        "{error}").format(
                            type=o.type, value=paramenter_value,
                            error=str(e))
                    parameter_dict_error[o.name] = msg

        if len(parameter_dict_error.keys()) != 0:
            raise PumpWoodActionArgsException(
                message="Error parsing dashboard parameters",
                payload=parameter_dict_error)

        ##########################################
        # Covert bordered and titled paramenters #
        bordered = bordered or self.default_is_bordered
        titled = titled or self.default_is_titled
        str_bordered = "true" if bordered else "false"
        str_titled = "true" if titled else "false"

        # Covert theme
        str_theme = None
        theme = theme or self.default_theme
        if self.default_theme == 'light':
            str_theme = ""
        elif self.default_theme == 'night':
            str_theme = "theme=night&"
        elif self.default_theme == 'transparent':
            str_theme = "theme=transparent&"
        else:
            raise PumpWoodActionArgsException(
                message=(
                    "Theme not implemented, must be in [light, night, "
                    "transparent]"),
                payload=parameter_dict_error)

        #####################################
        # Crate payload to define dashboard #
        payload = {
          "resource": {"dashboard": self.metabase_id},
          "params": parameter_dict,
          "exp": round(time.time()) + (60 * self.expire_in_min)
        }
        token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
        iframe_url = (
            "{site}/embed/dashboard/{token}#{theme}"
            "bordered={bordered}&titled={titled}").format(
                site=METABASE_SITE_URL, token=token,
                theme=str_theme, bordered=str_bordered,
                titled=str_titled)
        return iframe_url


class MetabaseDashboardParameter(models.Model):
    """Routes registred on Kong API Gateway."""

    PARAMETER_TYPE = [
        ('str', 'String'),
        ('datetime', 'Data/Time'),
        ('int', 'Integer'),
        ('float', 'Float'),
        ('user_id', 'Request User Id'),
    ]

    dashboard = models.ForeignKey(
        MetabaseDashboard, on_delete=models.CASCADE,
        related_name="parameter_set",
        help_text="Dashboard associated with paramenters.")
    type = models.CharField(
        choices=PARAMETER_TYPE, max_length=15, verbose_name="Type",
        help_text="Type")
    name = models.CharField(
        max_length=50, verbose_name="Parameter name",
        help_text="Parameter name")
    notes = models.TextField(
        null=False, default="", blank=True,
        help_text="a long description of the parameter.")
    default_value = models.CharField(
        null=True, max_length=100, unique=False, blank=True,
        verbose_name="Default value", help_text="Default value")

    class Meta:
        db_table = 'metabase__dashboard_parameter'
        unique_together = [['dashboard', 'name']]

    def __str__(self):
        return '%s: %s' % (self.dashboard, self.name)
