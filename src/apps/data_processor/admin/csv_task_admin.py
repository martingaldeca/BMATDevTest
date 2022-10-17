from django.contrib import admin

from data_processor.models import CSVTask, CSVTaskFileRelation, CSVTaskFile


class CSVTaskFileInline(admin.TabularInline):
    model = CSVTaskFileRelation
    extra = 10  # how many rows to show


@admin.register(CSVTask)
class CSVTaskAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'input_file', 'initial_input_file_name', 'error_processing', 'error_message']
    readonly_fields = ['created', 'modified', 'uuid', 'initial_input_file_name']
    inlines = [CSVTaskFileInline, ]
    search_fields = ['uuid', ]
    ordering = ['-created', ]


@admin.register(CSVTaskFile)
class CSVTaskFileAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'output_file', ]
    readonly_fields = ['created', 'modified', 'uuid', ]
    search_fields = ['uuid', ]
    ordering = ['-created', ]
