import os
from pprint import pprint, pformat
from django.core.urlresolvers import reverse

from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import loader
from django.utils.safestring import mark_safe
from guardian.decorators import permission_required_or_403
from django.template.context import RequestContext
from django.views.generic import View
import guardian.shortcuts

from archer.core.decorators import class_view_decorator
from archer.projects.forms import UploadFileForm
from archer.projects.models import Project
from archer.packages.models import Package

NUMBER_OF_PACKAGES = 5


def unauthenticated(request):
    return render(request, 'unauthenticated.html')


def get_objects_for_user(user, perms, klass=None, use_groups=True, any_perm=False):
    if user.is_authenticated():
        return guardian.shortcuts.get_objects_for_user(user, perms, klass, use_groups, any_perm)
    return []


def index(request):
    debug_info = {'user': pformat(request.user.__dict__),
                  'environ': pformat(dict(os.environ.items())),
                  'meta': pformat(dict(request.META))}
    projects = get_objects_for_user(request.user, 'projects.view_project')
    package_sets = [(project,
                     request.user.has_perm('projects.upload_package', project),
                     [package for package in project.package_set.order_by('-id')],
                    ) for project in projects]
    context = {'package_sets': package_sets, 'debug_info': debug_info}
    return render(request, 'projects/index.html', context)


@class_view_decorator(permission_required_or_403('projects.upload_package', (Project, 'pk', 'project_id')))
class UploadView(View):
    def get(self, request, project_id):
        form = UploadFileForm()
        return render_to_response('projects/upload.html',
                                  {'form': form, 'project_id': project_id},
                                  context_instance=RequestContext(request))

    def post(self, request, project_id):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            from guardian.shortcuts import assign_perm
            # handle files
            pprint(form)
            package = form.save(commit=False)
            package.status = Package.Status.uploaded
            package.project_id = project_id
            package.save()
            assign_perm('packages.deploy_package', request.user, package)
            assign_perm('packages.remove_package', request.user, package)
            return HttpResponseRedirect(reverse('projects:show', args=[project_id]))
        return render_to_response('projects/upload.html',
                                  {'form': form, 'project_id': project_id},
                                  context_instance=RequestContext(request))


# @permission_required_or_403('projects.view_project', (Project, 'pk', 'project_id'))
def rmdir(request, project_id, path):
    pass


def mkdir(request, project_id):
    pass


@permission_required_or_403('projects.view_project', (Project, 'pk', 'project_id'))
def show(request, project_id):
    project = Project.objects.get(pk=project_id)
    can_upload = request.user.has_perm('projects.upload_package', project)
    path = project.full_path()

    def index_maker():
        def _index(root):
            # rfiles = []
            files = os.listdir(root)
            files_only = []
            for mfile in files:
                t = os.path.join(root, mfile)
                if os.path.isdir(t):
                    yield loader.render_to_string('tree/_folder.html',
                                                  {'file': mfile + '/',
                                                   'subfiles': _index(os.path.join(root, t)),
                                                   'can_upload': can_upload,
                                                   'project_id': project_id,
                                                   'path': root + '/' + mfile,
                                                  })
                    continue
                files_only += [mfile]
            if len(files_only) > 0:
                pre = len(files_only) > 50
                if pre:
                    files_only = "\n".join(files_only)
                yield loader.render_to_string('tree/_files.html',
                                              {'files': files_only,
                                               'project_id': project_id,
                                               'path': root + '/' + mfile,
                                               'pre': pre,
                                              })
                #         rfiles += ('dir', mfile + '/', index(os.path.join(root, t)))
                #     else:
                #         rfiles += ('file', mfile)
                # return rfiles

        if not os.path.isdir(path):
            return None
        return _index(path)

    return render_to_response('projects/show.html',
                              {'project': project,
                               'can_upload': can_upload,
                               'packages': [package for package in project.package_set.order_by('-id')],
                               'files': index_maker(),
                              },
                              context_instance=RequestContext(request))