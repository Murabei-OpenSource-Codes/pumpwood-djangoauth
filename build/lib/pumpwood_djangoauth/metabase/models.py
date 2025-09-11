"""Manage Kong routes for Pumpwood."""
import jwt
import os
import time
import pandas as pd
from typing import List
from django.db import models
from django.conf import settings
from pumpwood_djangoviews.action import action
from pumpwood_communication.serializers import PumpWoodJSONEncoder
from pumpwood_communication.exceptions import (
    PumpWoodActionArgsException, PumpWoodObjectDoesNotExist,
    PumpWoodException)
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
        verbose_name="Status",
        help_text="Status")
    alias = models.CharField(
        null=False, max_length=100, unique=True,
        verbose_name="Alias",
        help_text="Alias to identify dashboard")
    description = models.CharField(
        null=False, max_length=100, unique=True,
        verbose_name="Description",
        help_text="Dashboard description")
    notes = models.TextField(
        null=False, default="", blank=True,
        verbose_name="Notes",
        help_text="A long description of the dashboard")
    auto_embedding = models.BooleanField(
        default=False,
        verbose_name="Auto embedding",
        help_text="Auto embedd dashboard at front-end")
    object_model_class = models.CharField(
        null=True, max_length=50, unique=False, blank=True,
        verbose_name="Model class",
        help_text="Model class associated with dashboard")
    object_pk = models.IntegerField(
        null=True, unique=False, blank=True,
        verbose_name="Object PK",
        help_text="Object PK associated with dashboard")
    metabase_id = models.IntegerField(
        null=False,
        verbose_name="Metabase ID",
        help_text="Metabase Dashboard Id")
    expire_in_min = models.IntegerField(
        null=False, default=10,
        verbose_name="Expiration period",
        help_text="Minutes to expire url")
    default_theme = models.CharField(
        choices=THEME, max_length=15, default="light",
        verbose_name="Theme",
        help_text="Dashboard Theme")
    default_is_bordered = models.BooleanField(
        default=False,
        verbose_name="Is bordered?",
        help_text="Is bordered?")
    default_is_titled = models.BooleanField(
        default=False,
        verbose_name="Is titled?",
        help_text="Is titled?")
    dimensions = models.JSONField(
        encoder=PumpWoodJSONEncoder, null=False, default=dict,
        blank=True,
        verbose_name="Dimentions",
        help_text="Key/Value Dimentions")
    extra_info = models.JSONField(
        encoder=PumpWoodJSONEncoder, null=False, default=dict,
        blank=True,
        verbose_name="Extra information",
        help_text="Extra information")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True, related_name='metabase_dash_set',
        verbose_name="Updated By",
        help_text="Updated By")
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")

    def __str__(self):
        """__str__."""
        return '[%s] %s' % (self.id, self.description)

    class Meta:
        """Meta Class."""
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
    @action(info='Dump dashboards and parameters')
    def dump_dashboards(cls, filter_alias: List[str] = None,
                        exclude_alias: List[str] = None) -> List[str]:
        """Dump dashboard and parameters to load on another server.

        Args:
            filter_alias (List[str]):
                Filter dashboard that will be dumped.
            exclude_alias (List[str]):
                Exclude dashboard that will be dumped.
        Return List[dict]:
            List of serialized dashboards and its parameters without pks
            associated with them.
        """
        from pumpwood_djangoauth.metabase.serializers import (
            MetabaseDashboardSerializer, MetabaseDashboardParameterSerializer)

        # Django query parameters
        filter_kwargs = {}
        if filter_alias is not None:
            filter_kwargs["alias__in"] = filter_alias

        exclude_kwargs = {}
        if exclude_alias is not None:
            exclude_kwargs["alias__in"] = exclude_alias

        dashboards = cls.objects\
            .filter(**filter_kwargs)\
            .exclude(**exclude_kwargs)

        response_list = []
        for dash in dashboards:
            # Remove pks, they will not match other server pk
            temp_data = MetabaseDashboardSerializer(dash).data
            del temp_data["pk"]
            temp_parameters = MetabaseDashboardParameterSerializer(
                dash.parameter_set.all(), many=True).data
            for x in temp_parameters:
                del x["pk"]
                del x["dashboard_id"]
            temp_data["parameter_set"] = temp_parameters
            response_list.append(temp_data)
        return response_list

    @classmethod
    @action(info='Load dashboards and parameters')
    def load_dashboards(cls, dashboard_dump: List[dict]) -> bool:
        """Load dashboard and parameters to load on another server.

        Args:
            dashboard_dump (list[dict]):
                List of dumped dashboards and its parameters.

        Return:
            Return true..
        """
        # Create or update MetabaseDashboard if there is a corresponding
        # Dashboard with same alias
        for d in dashboard_dump:
            dashboard_obj = MetabaseDashboard.objects.filter(
                alias=d["alias"]).first()
            if dashboard_obj is None:
                dashboard_obj = MetabaseDashboard()

            not_update_keys = ["pk", "model_class", "parameter_set"]
            for key, item in d.items():
                if key in not_update_keys:
                    continue
                try:
                    setattr(dashboard_obj, key, item)
                except Exception as e:
                    msg = (
                        "It was not possible to set attribute [{attribute}] "
                        "value [{value}] to and MetabaseDashboard instance."
                        "Check if data was correctly dumped and not edited "
                        "latter.\nError: {error}")
                    raise PumpWoodActionArgsException(
                        message=msg, payload={
                            'attribute': key, 'value': item,
                            'error': str(e)})

            # Save updated dashboard
            try:
                dashboard_obj.save()
            except Exception as e:
                msg = (
                    "Error saving MetabaseDashboard object to database."
                    "Error: {error}")
                raise PumpWoodException(
                    message=msg, payload={
                        'attribute': key, 'value': item,
                        'error': str(e)})

            for param in d["parameter_set"]:
                parameter_obj = MetabaseDashboardParameter.objects\
                    .filter(
                        dashboard_id=dashboard_obj.id,
                        name=param["name"]).first()
                if parameter_obj is None:
                    parameter_obj = MetabaseDashboardParameter()

                parameter_obj.dashboard_id = dashboard_obj.id
                not_update_keys = [
                    "pk", "model_class", "dashboard_id"]
                for key, item in param.items():
                    if key in not_update_keys:
                        continue

                    try:
                        setattr(parameter_obj, key, item)
                    except Exception as e:
                        msg = (
                            "It was not possible to set attribute "
                            "[{attribute}] value [{value}] to and "
                            "MetabaseDashboardParameter instance. "
                            "Check if data was correctly dumped and "
                            "not edited latter.\nError: {error}")
                        raise PumpWoodActionArgsException(
                            message=msg, payload={
                                'attribute': key, 'value': item,
                                'error': str(e)})
                # Save parameter
                try:
                    parameter_obj.save()
                except Exception as e:
                    msg = (
                        "Error saving MetabaseDashboardParameter "
                        "object to database. Error: {error}")
                    raise PumpWoodException(
                        message=msg, payload={
                            'attribute': key, 'value': item,
                            'error': str(e)})
        return True

    @classmethod
    @action(info='Generate url to embed with iframe using dashboard alias.',
            auth_header="auth_header")
    def generate_url_from_alias(cls, alias: str, auth_header: dict,
                                dashboard_parameters: dict = {},
                                theme: str = None, bordered: bool = None,
                                titled: bool = None) -> str:
        """Generate url to embed graph and dash with iframe using alias.

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
        """Generate url to embed graph and dash with iframe.

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
        METABASE_SITE_URL = os.getenv("METABASE_SITE_URL") # NOQA
        METABASE_SECRET_KEY = os.getenv("METABASE_SECRET_KEY") # NOQA

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
        verbose_name='Pumpwood Metabase Dashbord',
        help_text="Dashboard associated with paramenters")
    type = models.CharField(
        choices=PARAMETER_TYPE, max_length=15,
        verbose_name="Type",
        help_text="Type")
    name = models.CharField(
        max_length=50,
        verbose_name="Parameter name",
        help_text="Parameter name")
    notes = models.TextField(
        null=False, default="", blank=True,
        verbose_name="a long description of the parameter",
        help_text="a long description of the parameter")
    default_value = models.CharField(
        null=True, max_length=100, unique=False, blank=True,
        verbose_name="Default value",
        help_text="Default value")

    class Meta:
        """Meta Class."""
        db_table = 'metabase__dashboard_parameter'
        unique_together = [['dashboard', 'name'], ]
        verbose_name = 'Metabase Dashboard Parameter'
        verbose_name_plural = 'Metabase Dashboard Parameters'

    def __str__(self):
        """__str__."""
        return '%s: %s' % (self.dashboard, self.name)
