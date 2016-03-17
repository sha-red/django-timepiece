from django.contrib import admin

from timepiece.entries.models import (
    Activity, ActivityGroup, Entry, Location, ProjectHours)

from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ungettext, ugettext_lazy as _


class ActivityAdmin(admin.ModelAdmin):
    model = Activity
    list_display = ('code', 'name', 'billable')
    list_filter = ('billable',)


class ActivityGroupAdmin(admin.ModelAdmin):
    model = ActivityGroup
    list_display = ('name',)
    list_filter = ('activities',)
    filter_horizontal = ('activities',)


def change_status_action(modeladmin, request, queryset):
    class ChangeStatusForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        status = forms.ChoiceField(modeladmin.model.STATUSES.items())

    form = None
    if 'apply' in request.POST:
        form = ChangeStatusForm(request.POST)
        if form.is_valid():
            chosen_status = form.cleaned_data['status']
            # Doesn't work, query is to complex:
            # count = queryset.update(status=chosen_status)
            count = 0
            for obj in queryset.all():
                obj.status = chosen_status
                obj.save()
                count += 1
            message = ungettext(
                'Successfully set %(count)d entry to %(chosen_status)s.',
                'Successfully set %(count)d entries to %(chosen_status)s.',
                count) % {'count': count, 'chosen_status': dict(form.fields['status'].choices)[chosen_status]}
            modeladmin.message_user(request, message)
            return HttpResponseRedirect(request.get_full_path())
    if 'cancel' in request.POST:
        return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = ChangeStatusForm(initial={
            '_selected_action': request.POST.getlist(
                admin.ACTION_CHECKBOX_NAME),
        })

    return render_to_response('admin/timepiece/entries/action_forms/change_status.html', {
        'entries': queryset,
        'action_form': form,
        'opts': modeladmin.model._meta,
        'queryset': queryset,
    }, context_instance=RequestContext(request))
change_status_action.short_description = _("Change status for selected entries")


class EntryAdmin(admin.ModelAdmin):
    model = Entry
    list_display = ('user', '_project', 'location', 'project_type',
                    'activity', 'start_time', 'end_time', 'hours',
                    'status', 'is_closed', 'is_paused')
    list_filter = ['activity', 'status', 'project__type', 'user', 'project']
    search_fields = ['user__first_name', 'user__last_name', 'project__name',
                     'activity__name', 'comments']
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)
    actions = [change_status_action]

    def project_type(self, entry):
        return entry.project.type

    def _project(self, obj):
        """Use a proxy to avoid an infinite loop from ordering."""
        return obj.__str__()
    _project.admin_order_field = 'project__name'
    _project.short_description = 'Project'


class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ProjectHoursAdmin(admin.ModelAdmin):
    list_display = ('_user', '_project', 'week_start', 'hours', 'published')

    def _user(self, obj):
        return obj.user.get_name_or_username()
    _user.short_description = 'User'
    _user.admin_order_field = 'user__last_name'

    def _project(self, obj):
        """Use a proxy to avoid an infinite loop from ordering."""
        return obj.project.__str__()
    _project.admin_order_field = 'project__name'
    _project.short_description = 'Project'


admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityGroup, ActivityGroupAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(ProjectHours, ProjectHoursAdmin)
