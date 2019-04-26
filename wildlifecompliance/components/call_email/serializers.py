import traceback

from rest_framework_gis.serializers import GeoFeatureModelSerializer

from wildlifecompliance.components.call_email.models import (
    CallEmail,
    Classification,
    ReportType,
    ComplianceFormDataRecord,
    ComplianceLogEntry,
    Location,
    ComplianceUserAction,
)
from wildlifecompliance.components.main.serializers import CommunicationLogEntrySerializer
from rest_framework import serializers
from django.core.exceptions import ValidationError


class ComplianceFormDataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceFormDataRecord
        fields = (
            'field_name',
            'schema_name',
            'component_type',
            'instance_name',
            'comment',
            'deficiency',
            'value',
        )
        read_only_fields = (
            'field_name',
            'schema_name',
            'component_type',
            'instance_name',
            'comment',
            'deficiency',
            'value',
        )


class ClassificationSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(source='get_name_display')

    class Meta:
        model = Classification
        fields = (
            'id',
            'name',
        )
        read_only_fields = ('id', 'name', )


class CreateCallEmailSerializer(serializers.ModelSerializer):
    data = ComplianceFormDataRecordSerializer(many=True)

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'classification',
            'number',
            'caller',
            'assigned_to',
            'data',
        )
        read_only_fields = ('id', )


class ReportTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportType
        fields = (
            'report_type',
            'schema',
        )
        read_only_fields = ('report_type', 'schema')


class LocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Location
        geo_field = 'wkb_geometry'
        fields = (
            'id',
            'wkb_geometry',
            'street',
            'town_suburb',
            'state',
            'postcode',
            'country',
        )


class CallEmailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    classification = ClassificationSerializer()
    lodgement_date = serializers.CharField(
        source='lodged_on')
    report_type = ReportTypeSerializer()
    location = LocationSerializer()
    data = ComplianceFormDataRecordSerializer(many=True)

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'location',
            'classification',
            'schema',
            'lodgement_date',
            'number',
            'caller',
            'assigned_to',
            'report_type',
            'data',
        )
        read_only_fields = ('id', )


class UpdateCallEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'classification',
            'number',
            'caller',
            'assigned_to',
        )
        read_only_fields = ('id', )


class UpdateRendererDataSerializer(CallEmailSerializer):
    data = ComplianceFormDataRecordSerializer(many=True)

    class Meta:
        model = CallEmail
        fields = (
            'schema',
            'data',
        )


class ComplianceUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')

    class Meta:
        model = ComplianceUserAction
        fields = '__all__'


class ComplianceLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceLogEntry
        fields = '__all__'
        read_only_fields = (
            'customer',
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]
