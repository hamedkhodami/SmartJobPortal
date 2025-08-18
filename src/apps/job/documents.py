# jobs/documents.py
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import JobModel

job_index = Index('jobs')
job_index.settings(number_of_shards=1, number_of_replicas=0)


@registry.register_document
class JobDocument(Document):
    employer = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'email': fields.TextField(),
    })

    class Index:
        name = 'jobs'

    class Django:
        model = JobModel
        fields = [
            'title',
            'description',
            'location',
            'employment_type',
            'salary_min',
            'salary_max',
            'is_approved',
            'is_closed',
            'created_at',
        ]
