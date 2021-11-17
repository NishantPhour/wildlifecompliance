import logging
import abc

from django.contrib import admin
from wildlifecompliance.components.main import models, forms
from wildlifecompliance.components.main.models import SanctionOutcomeWordTemplate
from wildlifecompliance.components.main.utils import to_local_tz
#from reversion.admin import VersionAdmin

logger = logging.getLogger(__name__)


class AdministrationAction(object):
    '''
    An abstract class for Adminstration Actions allowing for actions to be
    applied to a single object which can be accessed from either the change
    list view or the change form view.

    '''
    logger_title = 'AdministrationAction()'    # logger.
    request = None                              # property for client request.

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def do_action(self, row_ids=None) -> bool:
        '''
        Method to execute an Action from Administration on selected rows.
        '''
        pass

    @abc.abstractmethod
    def log_action(self) -> bool:
        '''
        Method to log this command action.
        '''
        pass


@admin.register(models.GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    ordering = ('key',)


@admin.register(models.SystemMaintenance)
class SystemMaintenanceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'description', 'start_date', 'end_date', 'duration'
    ]
    ordering = ('start_date',)
    readonly_fields = ('duration',)
    form = forms.SystemMaintenanceAdminForm


@admin.register(SanctionOutcomeWordTemplate)
class SanctionOutcomeWordTemplateAdmin(admin.ModelAdmin):
    list_display = ('Version', '_file', 'sanction_outcome_type', 'act', 'description', 'Date', 'Time')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['_file', 'description', 'Date', 'Time']
        else:
            return []

    def Version(self, obj):
        return obj.id

    def Date(self, obj):
        local_date = to_local_tz(obj.uploaded_date)
        return local_date.strftime('%d/%m/%Y')

    def Time(self, obj):
        local_date = to_local_tz(obj.uploaded_date)
        return local_date.strftime('%H:%M')
