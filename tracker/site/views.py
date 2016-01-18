from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.generic import (TemplateView, CreateView, UpdateView,
                                  ListView, DeleteView)

from .forms import ProjectForm, TicketForm, DeleteTicketForm
from .models import Project, Ticket


class ProjectContextMixin(object):
    project = None

    def get_project(self):
        if not self.project:
            self.project = get_object_or_404(Project,
                                             pk=self.kwargs['project_id'])
        return self.project

    def get_context_data(self, **kwargs):
        context = super(ProjectContextMixin, self).get_context_data(**kwargs)
        context['current_project'] = self.get_project()
        return context


class MyTicketsView(TemplateView):
    template_name = "site/my_tickets.html"

    def get_context_data(self):
        if self.request.user.is_authenticated():
            tickets = (
                Ticket.objects
                .filter(assignees=self.request.user.pk)
                .order_by('-modified')
            )
        else:
            tickets = []

        return {
            'tickets': tickets
        }


my_tickets_view = MyTicketsView.as_view()


class ProjectListView(ListView):
    model = Project
    template_name = "site/project_list.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['project_details'] = [{
            'project': project,
            'assigned': self.request.user in project.assignees,
        } for project in self.object_list]
        return context


project_list_view = ProjectListView.as_view()


class CreateProjectView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "site/project_form.html"

    def get_success_url(self):
        return reverse("project-list")

    def get_form_kwargs(self):
        kwargs = super(CreateProjectView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['title'] = 'Create project'
        return kwargs


create_project_view = login_required(CreateProjectView.as_view())


class UpdateProjectView(ProjectContextMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    pk_url_kwarg = 'project_id'
    template_name = "site/project_form.html"

    def get_success_url(self):
        return reverse("project-list")

    def get_form_kwargs(self):
        kwargs = super(UpdateProjectView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['title'] = "Edit {0}".format(self.object.title)
        return kwargs


update_project_view = login_required(UpdateProjectView.as_view())


class ProjectView(ProjectContextMixin, TemplateView):
    template_name = "site/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        project = self.get_project()
        context.update({
            "project": project,
            "tickets": project.tickets.all()
        })
        return context


project_view = ProjectView.as_view()


class CreateTicketView(ProjectContextMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "site/ticket_form.html"

    def get_success_url(self):
        return reverse("project-detail",
                       kwargs={"project_id": self.kwargs['project_id']})

    def get_form_kwargs(self):
        kwargs = super(CreateTicketView, self).get_form_kwargs()
        kwargs['project'] = self.get_project()
        kwargs['user'] = self.request.user
        kwargs['title'] = 'Create ticket'
        return kwargs


create_ticket_view = login_required(CreateTicketView.as_view())


class UpdateTicketView(ProjectContextMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    pk_url_kwarg = 'ticket_id'
    template_name = "site/ticket_form.html"

    def get_success_url(self):
        return reverse("project-detail",
                       kwargs={"project_id": self.kwargs['project_id']})

    def get_object(self, *args, **kwargs):
        obj = super(UpdateTicketView, self).get_object(*args, **kwargs)
        # If the project in the URL does not match the project of the ticket
        if self.get_project() != obj.project:
            raise Http404
        return obj

    def get_form_kwargs(self):
        kwargs = super(UpdateTicketView, self).get_form_kwargs()
        kwargs['project'] = self.object.project
        kwargs['user'] = self.request.user
        kwargs['title'] = "Edit {0}".format(self.object.title)
        return kwargs


update_ticket_view = login_required(UpdateTicketView.as_view())


class DeleteTicketView(ProjectContextMixin, DeleteView):
    model = Ticket
    form_class = DeleteTicketForm
    pk_url_kwarg = 'ticket_id'
    template_name = "site/ticket_form.html"

    def get_success_url(self):
        return reverse("project-detail",
                       kwargs={"project_id": self.kwargs['project_id']})

    def get_form_kwargs(self):
        kwargs = {}
        kwargs['user'] = self.request.user
        kwargs['title'] = "Delete {0}?".format(self.object.title)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DeleteTicketView, self).get_context_data(**kwargs)
        context['form'] = self.form_class(**self.get_form_kwargs())
        return context

delete_ticket_view = login_required(DeleteTicketView.as_view())
