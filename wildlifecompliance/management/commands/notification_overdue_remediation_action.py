from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.core.management.base import BaseCommand
from django.db.models import Q, Max
from django.utils import timezone
import logging
from wildlifecompliance.components.sanction_outcome.email import send_notification_overdue_remediation_action
from wildlifecompliance.components.sanction_outcome.models import RemediationAction, RemediationActionNotification, \
    SanctionOutcomeUserAction
from wildlifecompliance.components.sanction_outcome.serializers import SanctionOutcomeCommsLogEntrySerializer, \
    RemediationActionNotificationCreateSerializer, RemediationActionUpdateStatusSerializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send the overdue mail to the external user of the a remediation action'

    def handle(self, *args, **options):
        try:
            logger.info('Running command {}'.format(__name__))
            today = timezone.localtime(timezone.now()).date()
            # today = today + relativedelta(days=70)

            # Pick up all the remediation actions which are close to due and no notifications sent yet
            ras = RemediationAction.objects.filter(Q(due_date__lt=today) & Q(status=RemediationAction.STATUS_OPEN)). \
                exclude(notifications__in=RemediationActionNotification.objects.filter(type=RemediationActionNotification.TYPE_OVERDUE))

            for ra in ras:
                print(ra)

            # Send email (to: offender, bcc: officers)
            for ra in ras:
                try:
                    with transaction.atomic():
                        # Create new comms log entry
                        data = {'sanction_outcome': ra.sanction_outcome.id}
                        serializer = SanctionOutcomeCommsLogEntrySerializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        workflow_entry = serializer.save()

                        to_address = [ra.sanction_outcome.get_offender()[0].email,]
                        cc = None
                        bcc = [ra.sanction_outcome.responsible_officer.email] if ra.sanction_outcome.responsible_officer else [member.email for member in ra.sanction_outcome.allocated_group.get_members()]
                        attachments = []
                        email_data = send_notification_overdue_remediation_action(to_address, ra.sanction_outcome, cc, bcc, attachments)

                        # Record in the RemediationActionNotification
                        data = {
                            'remediation_action_id': ra.id,
                            'sanction_outcome_comms_log_entry_id': workflow_entry.id,
                            'type': RemediationActionNotification.TYPE_OVERDUE,
                        }
                        serializer = RemediationActionNotificationCreateSerializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        ran = serializer.save()

                        # Set remediation action status to the 'overdue'
                        serializer = RemediationActionUpdateStatusSerializer(ra, data={'status': RemediationAction.STATUS_OVERDUE}, )
                        serializer.is_valid(raise_exception=True)
                        serializer.save()

                        # Comms log
                        if email_data:
                            serializer = SanctionOutcomeCommsLogEntrySerializer(workflow_entry, data=email_data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()

                        # Action log, status has been changed to the 'overdue', record it as an action
                        ra.sanction_outcome.log_user_action(SanctionOutcomeUserAction.ACTION_REMEDIATION_ACTION_OVERDUE.format(ra.remediation_action_id))
                except Exception as e:
                    logger.error('Error command {}'.format(__name__))

            logger.info('Command {} completed'.format(__name__))

        except Exception as e:
            logger.error('Error command {}'.format(__name__))
