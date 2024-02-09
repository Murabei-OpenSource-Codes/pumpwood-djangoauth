"""Manage Kong routes for Pumpwood."""
import jwt
import os
import time
import pandas as pd
from django.db import models
from django.conf import settings
from pumpwood_djangoviews.action import action
from pumpwood_communication.serializers import PumpWoodJSONEncoder
from pumpwood_communication.exceptions import (
    PumpWoodActionArgsException, PumpWoodObjectDoesNotExist)
from pumpwood_djangoauth.config import microservice_no_login
from pumpwood_djangoauth.i8n.translate import t


class MetabaseDashboard(models.Model):
    """Metabase dashboard to serve using Pumpwood."""

    STATUS = (
        ("inactive", "Archived"),
        ("dev", "Development"),
        ("homolog", "Homologation"),
        ("production", "Production"),
    )

    THEME = (
        ("light", "light"),
        ("night", "dark"),
        ("transparent", "transparent"),
    )

    status = models.CharField(
        choices=STATUS, max_length=15,
        verbose_name=t(
            "Status",
            tag="MetabaseDashboard__admin__status"),
        help_text=t(
            "Status",
            tag="MetabaseDashboard__admin__status"))
    alias = models.CharField(
        null=False, max_length=100, unique=True,
        verbose_name=t(
            "Alias",
            tag="MetabaseDashboard__admin__alias"),
        help_text=t(
            "Alias to identify dashboard",
            tag="MetabaseDashboard__admin__alias"))
    description = models.CharField(
        null=False, max_length=100, unique=True,
        verbose_name=t(
            "Description",
            tag="MetabaseDashboard__admin__description"),
        help_text=t(
            "Dashboard description",
            tag="MetabaseDashboard__admin__description"))
    notes = models.TextField(
        null=False, default="", blank=True,
        verbose_name=t(
            "Notes",
            tag="MetabaseDashboard__admin__notes"),
        help_text=t(
            "A long description of the dashboard",
            tag="MetabaseDashboard__admin__notes"))
    auto_embedding = models.BooleanField(
        default=False,
        verbose_name=t(
            "Auto embedding",
            tag="MetabaseDashboard__admin__auto_embedding"),
        help_text=t(
            "Auto embedd dashboard at front-end",
            tag="MetabaseDashboard__admin__auto_embedding"))
    object_model_class = models.CharField(
        null=True, max_length=50, unique=False, blank=True,
        verbose_name=t(
            "Model class",
            tag="MetabaseDashboard__admin__object_model_class"),
        help_text=t(
            "Model class associated with dashboard",
            tag="MetabaseDashboard__admin__object_model_class"))
    object_pk = models.IntegerField(
        null=True, unique=False, blank=True,
        verbose_name=t(
            "Object PK",
            tag="MetabaseDashboard__admin__object_pk"),
        help_text=t(
            "Object PK associated with dashboard",
            tag="MetabaseDashboard__admin__object_pk"))
    metabase_id = models.IntegerField(
        null=False,
        verbose_name=t(
            "Metabase ID",
            tag="MetabaseDashboard__admin__metabase_id"),
        help_text=t(
            "Metabase Dashboard Id",
            tag="MetabaseDashboard__admin__metabase_id"))
    expire_in_min = models.IntegerField(
        null=False, default=10,
        verbose_name=t(
            "Expiration period",
            tag="MetabaseDashboard__admin__expire_in_min"),
        help_text=t(
            "Minutes to expire url",
            tag="MetabaseDashboard__admin__expire_in_min"))
    default_theme = models.CharField(
        choices=THEME, max_length=15, default="light",
        verbose_name=t(
            "Theme",
            tag="MetabaseDashboard__admin__default_theme"),
        help_text=t(
            "Dashboard Theme",
            tag="MetabaseDashboard__admin__default_theme"))
    default_is_bordered = models.BooleanField(
        default=False,
        verbose_name=t(
            "Is bordered?",
            tag="MetabaseDashboard__admin__default_is_bordered"),
        help_text=t(
            "Is bordered?",
            tag="MetabaseDashboard__admin__default_is_bordered"))
    default_is_titled = models.BooleanField(
        default=False,
        verbose_name=t(
            "Is titled?",
            tag="MetabaseDashboard__admin__default_is_titled"),
        help_text=t(
            "Is titled?",
            tag="MetabaseDashboard__admin__default_is_titled"))
    dimensions = models.JSONField(
        encoder=PumpWoodJSONEncoder, null=False, default=dict,
        blank=True,
        verbose_name=t(
            "Dimentions",
            tag="MetabaseDashboard__admin__dimensions"),
        help_text=t(
            "Key/Value Dimentions",
            tag="MetabaseDashboard__admin__dimensions"))
    extra_info = models.JSONField(
        encoder=PumpWoodJSONEncoder, null=False, default=dict,
        blank=True,
        verbose_name=t(
            "Extra information",
            tag="MetabaseDashboard__admin__extra_info"),
        help_text=t(
            "Extra information",
            tag="MetabaseDashboard__admin__extra_info"))
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True, related_name='metabase_dash_set',
        verbose_name=t(
            "Updated By",
            tag="MetabaseDashboard__admin__updated_by"),
        help_text=t(
            "Updated By",
            tag="MetabaseDashboard__admin__updated_by"))
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name=t(
            "Updated At",
            tag="MetabaseDashboard__admin__updated_at"),
        help_text=t(
            "Updated At",
            tag="MetabaseDashboard__admin__updated_at"))

    def __str__(self):
        return '[%s] %s' % (self.id, self.description)

    class Meta:
        db_table = 'metabase__dashboard'
        verbose_name = t(
            'Pumpwood Metabase Dashbord',
            tag="MetabaseDashboard__admin")
        verbose_name_plural = t(
            'Pumpwood Metabase Dashbords',
            tag="MetabaseDashboard__admin", plural=True)

    def save(self, *args, **kwargs):
        """Ovewrite save to add output_modeling_unit_id."""
        super(MetabaseDashboard, self).save(*args, **kwargs)

        ###########################################################
        # Crating parameters necessary to dashboard associated with
        # model_class and specific objects
        if self.object_model_class is not None:
            parameter = self.parameter_set.filter(
                name="model_class").first()
            parameter_id = None if parameter is None else parameter.id
            parameter = MetabaseDashboardParameter(
                id=parameter_id,
                dashboard=self, type="str", name="model_class",
                notes=(
                    "**Dashboard with object_model_class not null, must"
                    "have model_class parameter. Please do not delete!**"),
                default_value=None)
            parameter.save()

        if self.object_pk is not None:
            parameter = self.parameter_set.filter(
                name="pk").first()
            parameter_id = None if parameter is None else parameter.id
            parameter = MetabaseDashboardParameter(
                id=parameter_id,
                dashboard=self, type="int", name="pk",
                notes=(
                    "**Dashboard with object_pk not null, must"
                    "have pk parameter. Please do not delete!**"),
                default_value=None)
            parameter.save()

    @classmethod
    @action(info='Generate url to embed with iframe using dashboard alias.',
            auth_header="auth_header")
    def generate_url_from_alias(cls, alias: str, auth_header: dict,
                                dashboard_parameters: dict = {},
                                theme: str = None, bordered: bool = None,
                                titled: bool = None) -> str:
        """
        Generate url to embed graph and dash with iframe using alias.

        Use dashboard alias to create iframe link. This might help when
        replicating enviroments and dashboards.

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
        try:
            obj = cls.objects.get(alias=alias)
        except Exception:
            msg = "Alias [{}] not found on database".format(alias)
            raise PumpWoodObjectDoesNotExist(msg)
        return obj.generate_url(
            auth_header=auth_header, dashboard_parameters=dashboard_parameters,
            theme=theme, bordered=bordered, titled=titled)

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
        verbose_name=t(
            'Pumpwood Metabase Dashbord',
            tag="MetabaseDashboardParameter__admin__dashboard"),
        help_text=t(
            "Dashboard associated with paramenters",
            tag="MetabaseDashboardParameter__admin__dashboard"))
    type = models.CharField(
        choices=PARAMETER_TYPE, max_length=15,
        verbose_name=t(
            "Type",
            tag="MetabaseDashboardParameter__admin__type"),
        help_text=t(
            "Type",
            tag="MetabaseDashboardParameter__admin__type"))
    name = models.CharField(
        max_length=50,
        verbose_name=t(
            "Parameter name",
            tag="MetabaseDashboardParameter__admin__name"),
        help_text=t(
            "Parameter name",
            tag="MetabaseDashboardParameter__admin__name"))
    notes = models.TextField(
        null=False, default="", blank=True,
        verbose_name=t(
            "a long description of the parameter",
            tag="MetabaseDashboardParameter__admin__notes"),
        help_text=t(
            "a long description of the parameter",
            tag="MetabaseDashboardParameter__admin__notes"))
    default_value = models.CharField(
        null=True, max_length=100, unique=False, blank=True,
        verbose_name=t(
            "Default value",
            tag="MetabaseDashboardParameter__admin__notes"),
        help_text=t(
            "Default value",
            tag="MetabaseDashboardParameter__admin__notes"))

    class Meta:
        db_table = 'metabase__dashboard_parameter'
        unique_together = [['dashboard', 'name']]
        verbose_name = t(
            'Metabase Dashboard Parameter',
            tag="MetabaseDashboardParameter__admin")
        verbose_name_plural = t(
            'Metabase Dashboard Parameters',
            tag="MetabaseDashboardParameter__admin", plural=True)

    def __str__(self):
        return '%s: %s' % (self.dashboard, self.name)
