import traceback
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ValidationError
#from wildlifecompliance.components.offence.models import Offender
from wildlifecompliance.components.organisations.models import Organisation

from wildlifecompliance.components.main.models import (
    ComplianceManagementSystemGroupPermission
)

from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from django.db import models
from rest_framework import serializers
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import logging
from django.db.models import Q

logger = logging.getLogger(__name__)


class WeakLinks(models.Model):

    first_content_type = models.ForeignKey(
            ContentType, 
            related_name='first_content_type',
            on_delete=models.CASCADE)
    first_object_id = models.PositiveIntegerField()
    first_content_object = GenericForeignKey('first_content_type', 'first_object_id')

    second_content_type = models.ForeignKey(
            ContentType, 
            related_name='second_content_type',
            on_delete=models.CASCADE)
    second_object_id = models.PositiveIntegerField()
    second_content_object = GenericForeignKey('second_content_type', 'second_object_id')
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = 'wildlifecompliance'

    def save(self, *args, **kwargs):
        # test for existing object with first and second fields reversed.  If exists, don't create duplicate.
        duplicate = WeakLinks.objects.filter(
                first_content_type = self.second_content_type,
                second_content_type = self.first_content_type,
                first_object_id = self.second_object_id,
                second_object_id = self.first_object_id
                )
        related_items = get_related_items(self.first_content_object)
        second_object_identifier = self.second_content_object.get_related_items_identifier
        second_object_formatted_model_name = format_model_name(self.second_content_object._meta.model_name)
        duplicate_related_item_exists = False
        if related_items:
            for item in related_items:
                if (second_object_identifier == item.get('identifier') and 
                        second_object_formatted_model_name == item.get('model_name')):
                    duplicate_related_item_exists = True
                    log_message =  'Duplicate RelatedItem/WeakLink - no record created for {} with pk {}'.format(
                                self.first_content_type.model,
                                self.first_object_id)
                    logger.debug(log_message)
        if duplicate_related_item_exists:
            log_message =  'Duplicate RelatedItem/WeakLink - no record created for {} with pk {}'.format(
                        self.first_content_type.model,
                        self.first_object_id)
            logger.debug(log_message)
        elif self.second_content_type and self.second_content_type.model not in [i.lower() for i in approved_related_item_models]:
            log_message =  'Incorrect model type - no record created for {} with pk {}'.format(
                        self.first_content_type.model,
                        self.first_object_id)
            logger.debug(log_message)
        elif duplicate:
            log_message =  'Duplicate WeakLink - no record created for {} with pk {}'.format(
                        self.first_content_type.model,
                        self.first_object_id)
            logger.debug(log_message)
        else:
            super(WeakLinks, self).save(*args,**kwargs)


class RelatedItemsSerializer(serializers.Serializer):
    descriptor = serializers.CharField()
    identifier = serializers.CharField()
    model_name = serializers.CharField()
    second_object_id = serializers.IntegerField(allow_null=True)
    second_content_type = serializers.CharField(allow_blank=True)
    weak_link = serializers.BooleanField()
    action_url = serializers.CharField(allow_blank=True)
    comment = serializers.CharField()


class RelatedItem:

    def __init__(self, model_name, identifier, descriptor, 
            action_url, weak_link=False, second_object_id=None, second_content_type=None, comment=None):
        self.model_name = model_name
        self.identifier = identifier
        self.descriptor = descriptor
        self.action_url = action_url
        self.weak_link = weak_link
        self.second_object_id = second_object_id
        self.second_content_type = second_content_type
        self.comment = comment


def search_weak_links(request_data):
    from wildlifecompliance.components.call_email.models import CallEmail
    from wildlifecompliance.components.artifact.models import DocumentArtifact,PhysicalArtifact
    from wildlifecompliance.components.inspection.models import Inspection
    from wildlifecompliance.components.offence.models import Offence
    from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome
    from wildlifecompliance.components.legal_case.models import LegalCase

    qs = []
    related_items = []
    entity = None

    entity_id = request_data.get('displayedEntityId')
    entity_id_int = int(entity_id.strip())
    entity_type = request_data.get('displayedEntityType')

    if entity_type == 'callemail':
        entity, created = CallEmail.objects.get_or_create(id=entity_id_int)
    elif entity_type == 'inspection':
        entity, created = Inspection.objects.get_or_create(id=entity_id_int)
    elif entity_type == 'offence':
        entity, created = Offence.objects.get_or_create(id=entity_id_int)
    elif entity_type == 'sanctionoutcome':
        entity, created = SanctionOutcome.objects.get_or_create(id=entity_id_int)
    elif entity_type == 'legalcase':
        entity, created = LegalCase.objects.get_or_create(id=entity_id_int)
    elif entity_type == 'documentartifact':
        entity, created = DocumentArtifact.objects.get_or_create(id=entity_id_int)
    elif entity_type == 'physicalartifact':
        entity, created = PhysicalArtifact.objects.get_or_create(id=entity_id_int)

    related_items = get_related_items(entity)
    
    components_selected = request_data.get('selectedEntity')
    search_text = request_data.get('searchText')
    if 'call_email' in components_selected:
        qs = CallEmail.objects.filter(
                Q(number__icontains=search_text) |
                Q(caller__icontains=search_text) |
                Q(caller_phone_number__icontains=search_text) |
                Q(location__street__icontains=search_text) |
                Q(location__town_suburb__icontains=search_text) 
                )
    elif 'inspection' in components_selected:
        qs = Inspection.objects.filter(
                Q(number__icontains=search_text) |
                Q(title__icontains=search_text) |
                Q(details__icontains=search_text) |
                Q(inspection_type__inspection_type__icontains=search_text) |
                #Q(individual_inspected__first_name__icontains=search_text) | TODO replace if needed or remove
                #Q(individual_inspected__last_name__icontains=search_text) |
                Q(call_email__number__icontains=search_text)
                )
    elif 'offence' in components_selected:
        qs = Offence.objects.filter(
                Q(lodgement_number__icontains=search_text) |
                Q(identifier__icontains=search_text) |
                Q(details__icontains=search_text) |
                Q(alleged_offences__act__name__icontains=search_text) |
                Q(alleged_offences__name__icontains=search_text) |
                Q(offender__person__first_name__icontains=search_text) |
                Q(offender__person__last_name__icontains=search_text)
                )
    elif 'sanction_outcome' in components_selected:
        qs = SanctionOutcome.objects.filter(
                Q(lodgement_number__icontains=search_text) |
                Q(identifier__icontains=search_text) |
                Q(description__icontains=search_text) |
                Q(offence__alleged_offences__act__name__icontains=search_text) |
                Q(offence__alleged_offences__name__icontains=search_text) |
                Q(offender__person__first_name__icontains=search_text) |
                Q(offender__person__last_name__icontains=search_text)
                )
    elif 'legal_case' in components_selected:
        qs = LegalCase.objects.filter(
                Q(number__icontains=search_text) |
                #Q(identifier__icontains=search_text) |
                Q(details__icontains=search_text) 
                )
    elif 'document_artifact' in components_selected:
        qs = DocumentArtifact.objects.filter(
                Q(number__icontains=search_text) |
                Q(identifier__icontains=search_text) |
                Q(description__icontains=search_text) 
                )
    elif 'physical_artifact' in components_selected:
        qs = PhysicalArtifact.objects.filter(
                Q(number__icontains=search_text) |
                Q(identifier__icontains=search_text) |
                Q(description__icontains=search_text) 
                )
    return_qs = []

    # First 10 records only
    for item in qs[:10]:
        duplicate = False
        if related_items:
            for related_item in related_items:
                related_item_model_name = related_item.get('model_name')
                related_item_identifier = related_item.get('identifier')
                print(related_item_model_name)
                print(related_item_identifier)
                print(item._meta.model_name)
                print(item.get_related_items_identifier)
                if related_item_model_name == format_model_name(item._meta.model_name) \
                    and related_item_identifier == item.get_related_items_identifier:
                    duplicate = True
        if not duplicate:
            return_qs.append({
                'id': item.id,
                'model_name': item._meta.model_name,
                'item_identifier': item.get_related_items_identifier,
                'item_description': item.get_related_items_descriptor,
                })
    return return_qs

# list of approved related item models
approved_related_item_models = [
        'Offence',
        'CallEmail',
        'Inspection',
        'SanctionOutcome',
        'LegalCase',
        'EmailUser',
        'Organisation',
        'Offender',
        'DocumentArtifact',
        'PhysicalArtifact',
        ]

pending_closure_related_item_models = [
        'Offence',
        'CallEmail',
        'Inspection',
        'SanctionOutcome',
        'LegalCase',
        'DocumentArtifact',
        'PhysicalArtifact',
        ]

approved_email_user_related_items = [
        #'volunteer',
        'individual_inspected',
        'email_user',
        'person_providing_statement',
        'officer_interviewer',
        ## Physical Artifact - not currently required
        #'officer',
        #'custodian',
        ]

def format_model_name(model_name):
    if model_name:
        lower_model_name = model_name.lower()
        switcher = {
                'callemail': 'Call / Email',
                'inspection': 'Inspection',
                'offence': 'Offence',
                'sanctionoutcome': 'Sanction Outcome',
                'case': 'Case',
                'emailuser': 'Person',
                'organisation': 'Organisation',
                'legalcase': 'Case',
                'documentartifact': 'Document Artifact',
                'physicalartifact': 'Physical Artifact',
                'offender': 'Offender',
                'offenderperson': 'Offender'
                }
        return switcher.get(lower_model_name, '')

def format_url(model_name, obj_id):
    if model_name:
        lower_model_name = model_name.lower()
        obj_id_str = str(obj_id)
        #switcher = {
        #        'callemail': '<a href=/internal/call_email/' + obj_id_str + ' target="_blank">View</a>',
        #        'inspection': '<a href=/internal/inspection/' + obj_id_str + ' target="_blank">View</a>',
        #        'offence': '<a href=/internal/offence/' + obj_id_str + ' target="_blank">View</a>',
        #        'sanctionoutcome': '<a href=/internal/sanction_outcome/' + obj_id_str + ' target="_blank">View</a>',
        #        'legalcase': '<a href=/internal/legal_case/' + obj_id_str + ' target="_blank">View</a>',
        #        'emailuser': '<a href=/internal/users/' + obj_id_str + ' target="_blank">View</a>',
        #        'organisation': '<a href=/internal/organisations/' + obj_id_str + ' target="_blank">View</a>',
        #        'documentartifact': '<a href=/internal/object/' + obj_id_str + ' target="_blank">View</a>',
        #        'physicalartifact': '<a href=/internal/object/' + obj_id_str + ' target="_blank">View</a>',
        #        }
        switcher = {
                'callemail': '<a href=/internal/call_email/' + obj_id_str + ' target="_blank">Open</a>',
                'inspection': '<a href=/internal/inspection/' + obj_id_str + ' target="_blank">Open</a>',
                'offence': '<a href=/internal/offence/' + obj_id_str + ' target="_blank">Open</a>',
                'sanctionoutcome': '<a href=/internal/sanction_outcome/' + obj_id_str + ' target="_blank">Open</a>',
                'legalcase': '<a href=/internal/legal_case/' + obj_id_str + ' target="_blank">Open</a>',
                'emailuser': '<a href=/internal/users/' + obj_id_str + ' target="_blank">Open</a>',
                'organisation': '<a href=/internal/organisations/' + obj_id_str + ' target="_blank">Open</a>',
                'documentartifact': '<a href=/internal/object/' + obj_id_str + ' target="_blank">Open</a>',
                'physicalartifact': '<a href=/internal/object/' + obj_id_str + ' target="_blank">Open</a>',
                }

        return switcher.get(lower_model_name, '')

def get_related_offenders(entity, **kwargs):
    from wildlifecompliance.components.offence.models import Offender
    offenders = []
    if entity._meta.model_name == 'sanctionoutcome':
        offenders.append(entity.offender)
    if entity._meta.model_name == 'offence':
        offenders_qs = Offender.objects.filter(offence_id=entity.id).exclude(removed=True).exclude(person=None) #TODO check if org needed
        for offender in offenders_qs:
            offenders.append(offender.person)
    return offenders

def checkWeakLinkAuth(request,content_type_str,object_id):
    from wildlifecompliance.components.inspection.models import Inspection
    from wildlifecompliance.components.offence.models import Offence
    from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome
    from wildlifecompliance.components.legal_case.models import LegalCase

    user_id = request.user
    all_groups_allowed = ['physicalartifact','documentartifact','callemail']

    if (content_type_str in all_groups_allowed):
        return True
    else:
        user_groups = list(ComplianceManagementSystemGroupPermission.objects.filter(emailuser=user_id).values_list("group__id",flat=True))
        if (content_type_str == "inspection"):
            qs = Inspection.objects.filter(id=object_id)#.filter(assigned_to=user_id)
            if qs.exists():
                if user_id in qs[0].inspection_team.all().values_list("id",flat=True):
                    return True
                elif bool(set(qs[0].allowed_groups) & set(user_groups)):
                    return True
        else:
            qs = None
            if (content_type_str == "offence"):
                qs = Offence.objects.filter(id=object_id).filter(assigned_to=user_id)
                if bool(set(qs[0].allowed_groups) & set(user_groups)):
                    return True
            elif (content_type_str == "sanctionoutcome"):
                qs = SanctionOutcome.objects.filter(id=object_id).filter(assigned_to=user_id)
                if bool(set(qs[0].allowed_groups) & set(user_groups)):
                    return True
            elif (content_type_str == "legalcase"):
                qs = LegalCase.objects.filter(id=object_id).filter(assigned_to=user_id)
                if bool(set(qs[0].allowed_groups) & set(user_groups)):
                    return True
            else:
                return False
        return False

def get_related_items(entity, pending_closure=False, **kwargs):
    try:
        return_list = []
        children = []
        parents = []
        field_objects = None
        related_item_models = pending_closure_related_item_models if pending_closure else approved_related_item_models

        # Strong links
        for f in entity._meta.get_fields():
            if f.is_relation and f.related_model.__name__ in related_item_models:
                # foreign keys from other objects to entity
                if f.is_relation and f.one_to_many:
                    if entity._meta.model_name == 'callemail':
                        field_objects = f.related_model.objects.filter(call_email_id=entity.id)
                    elif entity._meta.model_name == 'inspection':
                        field_objects = f.related_model.objects.filter(inspection_id=entity.id)
                    elif entity._meta.model_name == 'sanctionoutcome':
                        field_objects = f.related_model.objects.filter(sanction_outcome_id=entity.id)
                    elif entity._meta.model_name == 'offence' and f.name == 'offender':
                        field_objects = get_related_offenders(entity)
                    elif entity._meta.model_name == 'offence':
                        field_objects = f.related_model.objects.filter(offence_id=entity.id)
                    elif entity._meta.model_name == 'legalcase':
                        field_objects = f.related_model.objects.filter(legal_case_id=entity.id)

                    if field_objects:
                        for field_object in field_objects:
                            if pending_closure:
                                children.append(field_object)
                            elif isinstance(field_object, EmailUser):
                                related_item = RelatedItem(
                                        model_name = format_model_name(f.related_model.__name__),
                                        identifier = field_object.email,
                                        descriptor = field_object.first_name + " " + field_object.last_name,
                                        action_url = format_url(
                                                model_name=f.related_model.__name__,
                                                obj_id=field_object.id
                                                )
                                        )
                                return_list.append(related_item)
                            else:
                                related_item = RelatedItem(
                                        model_name = format_model_name(f.related_model.__name__),
                                        identifier = field_object.get_related_items_identifier,
                                        descriptor = field_object.get_related_items_descriptor,
                                        action_url = format_url(
                                                model_name=f.related_model.__name__,
                                                obj_id=field_object.id
                                                )
                                        )
                                return_list.append(related_item)

                # legal case artifacts
                elif entity._meta.model_name == 'legalcase' and f.is_relation and f.many_to_many \
                        and f.name in ('legal_case_document_artifacts', 'legal_case_physical_artifacts'):
                    field_objects = f.related_model.objects.filter(legal_cases=entity)
                    children, return_list = process_many_to_many(f, children, return_list, field_objects, pending_closure)

                # artifacts linked to legal case
                # linked legal cases
                elif f.name == 'legal_cases' and f.is_relation and f.many_to_many \
                        and entity._meta.model_name in ('documentartifact', 'physicalartifact'):
                    if entity._meta.model_name == 'documentartifact':
                        field_objects = f.related_model.objects.filter(legal_case_document_artifacts=entity)
                    elif entity._meta.model_name == 'physicalartifact':
                        field_objects = f.related_model.objects.filter(legal_case_physical_artifacts=entity)
                    parents, return_list = process_many_to_many(f, parents, return_list, field_objects, pending_closure)

                ## legal case artifacts - brief of evidence
                #elif entity._meta.model_name == 'legalcase' and f.is_relation and f.many_to_many \
                #        and f.name in ('legal_case_document_artifacts_brief_of_evidence', 'legal_case_physical_artifacts_brief_of_evidence'):
                #    field_objects = f.related_model.objects.filter(brief_of_evidence_legal_cases=entity)
                #    children, return_list = process_many_to_many(f, children, return_list, field_objects, pending_closure)

                ## artifacts linked to legal case - brief of evidence
                #elif f.name == 'brief_of_evidence_legal_cases' and f.is_relation and f.many_to_many \
                #        and entity._meta.model_name in ('documentartifact', 'physicalartifact'):
                #    if entity._meta.model_name == 'documentartifact':
                #        field_objects = f.related_model.objects.filter(legal_case_document_artifacts_brief_of_evidence=entity)
                #    elif entity._meta.model_name == 'physicalartifact':
                #        field_objects = f.related_model.objects.filter(legal_case_physical_artifacts_brief_of_evidence=entity)
                #    children, return_list = process_many_to_many(f, children, return_list, field_objects, pending_closure)

                ## legal case artifacts - prosecution brief
                #elif entity._meta.model_name == 'legalcase' and f.is_relation and f.many_to_many \
                #        and f.name in ('legal_case_document_artifacts_prosecution_brief', 'legal_case_physical_artifacts_prosecution_brief'):
                #    field_objects = f.related_model.objects.filter(prosecution_brief_legal_cases=entity)
                #    children, return_list = process_many_to_many(f, children, return_list, field_objects, pending_closure)

                ## artifacts linked to legal case - prosecution brief
                #elif f.name == 'prosecution_brief_legal_cases' and f.is_relation and f.many_to_many \
                #        and entity._meta.model_name in ('documentartifact', 'physicalartifact'):
                #    if entity._meta.model_name == 'documentartifact':
                #        field_objects = f.related_model.objects.filter(legal_case_document_artifacts_prosecution_brief=entity)
                #    elif entity._meta.model_name == 'physicalartifact':
                #        field_objects = f.related_model.objects.filter(legal_case_physical_artifacts_prosecution_brief=entity)
                #    children, return_list = process_many_to_many(f, children, return_list, field_objects, pending_closure)


                # legal case associated_persons
                elif entity._meta.model_name == 'legalcase' and f.is_relation and f.many_to_many \
                    and f.name == 'associated_persons':
                    field_objects = entity.associated_persons.all()
                    if field_objects:
                        for field_object in field_objects:
                            compliance_management_email_user = EmailUser.objects.get(id=field_object.id)
                            related_item = RelatedItem(
                                    model_name = format_model_name(f.related_model.__name__),
                                    identifier = compliance_management_email_user.get_related_items_identifier,
                                    descriptor = compliance_management_email_user.get_related_items_descriptor,
                                    action_url = format_url(
                                            model_name=f.related_model.__name__,
                                            obj_id=field_object.id
                                            )
                                    )
                            return_list.append(related_item)

                # artifacts linked to legal_case
                # primary legal case for artifact
                elif f.name == 'legal_case' and f.is_relation and f.many_to_many \
                        and entity._meta.model_name in ('documentartifact', 'physicalartifact'):
                    if entity._meta.model_name == 'documentartifact':
                        field_objects = f.related_model.objects.filter(legal_case_document_artifacts=entity)
                    elif entity._meta.model_name == 'physicalartifact':
                        field_objects = f.related_model.objects.filter(legal_case_physical_artifacts=entity)
                    parents, return_list = process_many_to_many(f, parents, return_list, field_objects, pending_closure)
                    ## TODO: Refactor repeated code
                    #if field_objects:
                    #    for field_object in field_objects:
                    #        if pending_closure:
                    #            children.append(field_object)
                    #        else:
                    #            related_item = RelatedItem(
                    #                    model_name = format_model_name(f.related_model.__name__),
                    #                    identifier = field_object.get_related_items_identifier,
                    #                    descriptor = field_object.get_related_items_descriptor,
                    #                    action_url = format_url(
                    #                            model_name=f.related_model.__name__,
                    #                            obj_id=field_object.id
                    #                            )
                    #                    )
                    #            return_list.append(related_item)

                # foreign keys from entity to EmailUser
                #TODO fix this to use EmailUserRO
                elif f.is_relation and f.related_model._meta.model_name == 'emailuser':
                    field_value = f.value_from_object(entity)
                    print("EmailUser")
                    print(field_value)
                    if field_value and f.name in approved_email_user_related_items:
                        base_field_object = f.related_model.objects.get(id=field_value)
                        field_object = EmailUser.objects.get(id=base_field_object.id)
                        related_item = RelatedItem(
                                model_name = format_model_name(f.related_model.__name__),
                                identifier = field_object.get_related_items_identifier,
                                descriptor = field_object.get_related_items_descriptor,
                                action_url = format_url(
                                        model_name=f.related_model.__name__,
                                        obj_id=field_object.id
                                        )
                                )
                        return_list.append(related_item)
                elif f.is_relation and f.get_internal_type() == 'OneToOneField':
                    # Inheritance model such as DocumentArtifact's fk to parent (Artifact)
                    pass
                # remaining entity foreign keys
                elif f.is_relation:
                    field_object = None
                    # Sanction Outcome FK to Offender
                    if f.name == 'offender':
                        field_object_list = get_related_offenders(entity)
                        # There will only ever be one at most
                        if field_object_list:
                            field_object = field_object_list[0]
                    # All other FKs
                    else:
                        print(f)
                        print(f.name)
                        print(f.related_model.__name__)
                        field_value = f.value_from_object(entity)
                        if field_value:
                            field_object = f.related_model.objects.get(id=field_value)
                    if field_object:
                        if pending_closure:
                            parents.append(field_object)
                        elif isinstance(field_object, EmailUser):
                                related_item = RelatedItem(
                                        model_name = format_model_name(f.related_model.__name__),
                                        identifier = field_object.email,
                                        descriptor = field_object.first_name + " " + field_object.last_name,
                                        action_url = format_url(
                                                model_name=f.related_model.__name__,
                                                obj_id=field_object.id
                                                )
                                        )
                                return_list.append(related_item)
                        else:
                            related_item = RelatedItem(
                                    model_name = format_model_name(field_object._meta.model_name),
                                    identifier = field_object.get_related_items_identifier,
                                    descriptor = field_object.get_related_items_descriptor,
                                    action_url = format_url(
                                            model_name=field_object._meta.model_name,
                                            obj_id=field_object.id
                                            )
                                    )
                            return_list.append(related_item)

        # Weak links - first pass with instance as first_content_object
        entity_content_type = ContentType.objects.get_for_model(type(entity))

        weak_links = WeakLinks.objects.filter(
                first_content_type__pk=entity_content_type.id,
                first_object_id=entity.id
                )
        for link in weak_links:
            link_content_type = ContentType.objects.get_for_model(
                    type(
                        link.second_content_object
                        ))
            if link_content_type.model in [i.lower() for i in approved_related_item_models]:
                related_item = RelatedItem(
                        model_name =  format_model_name(link_content_type.model),
                        identifier = link.second_content_object.get_related_items_identifier,
                        descriptor = link.second_content_object.get_related_items_descriptor,
                        second_object_id = link.second_content_object.id,
                        second_content_type = link_content_type.model,
                        weak_link = True,
                        action_url = format_url(
                                model_name=link_content_type.model,
                                obj_id=link.second_content_object.id
                                ),
                        comment = link.comment
                        )
                return_list.append(related_item)

        # Weak links - first pass with instance as second_content_object
        weak_links = WeakLinks.objects.filter(
                second_content_type__pk=entity_content_type.id,
                second_object_id=entity.id
                )
        for link in weak_links:
            link_content_type = ContentType.objects.get_for_model(
                    type(
                        link.first_content_object
                        ))
            if link_content_type.model in [i.lower() for i in approved_related_item_models]:
                related_item = RelatedItem(
                        model_name = format_model_name(link_content_type.model),
                        identifier = link.first_content_object.get_related_items_identifier,
                        descriptor = link.first_content_object.get_related_items_descriptor,
                        second_object_id = link.first_content_object.id,
                        second_content_type = link_content_type.model,
                        weak_link = True,
                        action_url = format_url(
                                model_name=link_content_type.model,
                                obj_id=link.first_content_object.id
                                ),
                        comment = link.comment
                        )
                return_list.append(related_item)
        
        if pending_closure:
            return children, parents
        else:
            serializer = RelatedItemsSerializer(return_list, many=True)
            return serializer.data
    except serializers.ValidationError:
        print(traceback.print_exc())
        raise
    except ValidationError as e:
        print(traceback.print_exc())
        raise serializers.ValidationError(repr(e.error_dict))
    except Exception as e:
        print(traceback.print_exc())
        raise serializers.ValidationError(str(e))

def process_many_to_many(f, relatives, return_list, field_objects, pending_closure=False):
    if field_objects:
        for field_object in field_objects:
            if pending_closure:
                relatives.append(field_object)
            elif isinstance(field_object, EmailUser):
                related_item = RelatedItem(
                        model_name = format_model_name(f.related_model.__name__),
                        identifier = field_object.email,
                        descriptor = field_object.first_name + " " + field_object.last_name,
                        action_url = format_url(
                                model_name=f.related_model.__name__,
                                obj_id=field_object.id
                                )
                        )
                return_list.append(related_item)
            else:
                related_item = RelatedItem(
                        model_name = format_model_name(f.related_model.__name__),
                        identifier = field_object.get_related_items_identifier,
                        descriptor = field_object.get_related_items_descriptor,
                        action_url = format_url(
                                model_name=f.related_model.__name__,
                                obj_id=field_object.id
                                )
                        )
                if related_item not in return_list:
                    return_list.append(related_item)
    return relatives, return_list

def can_close_legal_case(entity, request=None):
    print("can close legal case")
    children, parents = get_related_items(entity, pending_closure=True)
    close_record = True
    #artifact_children = []
    if children:
        for child in children:
            if child._meta.model_name in ('documentartifact', 'physicalartifact'):
                close_child_record = True
                sub_children, sub_parents = get_related_items(child, pending_closure=True)
                for sub_parent in sub_parents:
                    # check status of other legal_cases related to artifact
                    ## TODO: should logic check Offence, Offender related to artifact?
                    if (sub_parent._meta.model_name == 'legalcase' and 
                            sub_parent.status not in ('closed', 'pending_closure') and 
                            sub_parent.id != entity.id):
                        close_child_record = False
                if child.status not in ('closed', 'waiting_for_disposal') and close_child_record:
                    # attempt to close artifact
                    child.close(request)
                # Read the updated child status to determine whether legal case can be closed
                #if child.status not in ('closed', 'waiting_for_disposal'):
                 #   close_record = False
            else:
                # All other related child objects
                if child.status not in ('closed', 'discarded', 'declined', 'withdrawn'):  # This tuple should include only very final status of the entity
                    close_record = False
    return close_record, parents

#def can_close_artifact(entity, request=None):
#    print("can close artifact")
#    children, parents = get_related_items(entity, pending_closure=True)
#    close_record = True
#    if parents:
#        for parent in parents:
#            print("parent.status")
#            print(parent.status)
#            if parent.status not in ('closed', 'pending_closure'):  # Final status codes for Legal Case
#                close_record = False
#    return close_record, parents


def can_close_record(entity, request=None):
    children, parents = get_related_items(entity, pending_closure=True)
    close_record = True
    if children:
        for child in children:
            if child.status not in ('closed', 'discarded', 'declined', 'withdrawn'):  # This tuple should include only very final status of the entity
                close_record = False
                break
    return close_record, parents

# Examples of model properties for get_related_items
@property
def get_related_items_identifier(self):
    return self.id

@property
def get_related_items_descriptor(self):
    return '{0}, {1}'.format(self.street, self.wkb_geometry)
# End examples

