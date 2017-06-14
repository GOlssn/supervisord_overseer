# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from _socket import gaierror

from django.conf import settings
from django.contrib.auth import logout
from django.http.response import JsonResponse, Http404, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import RedirectView

from process_management.models import SystemEvent, SystemEventViewTransformer
from process_management.tools import helpers as helpers


class IndexView(View):
    def get(self, request):
        try:
            servers = [helpers._connect_server(node_settings) for name, node_settings in settings.NODES.items()]

            groups = []
            process_count = {
                'running': 0,
                'not_running': 0
            }

            for server in servers:
                processes = server.supervisor.getAllProcessInfo()
                counting = [True if process['statename'] == 'RUNNING' else False for process in processes]
                process_count['running'] += counting.count(True)
                process_count['not_running'] += counting.count(False)

                for process in processes:
                    if process['group'] not in groups and process['name'] not in process['group']:
                        groups.append(process['group'])

            group_count = len(groups)
            node_count = len(servers)
        except gaierror as e:
            return render(request, 'error/node_not_reachable.html', {'message': e})
        except Exception as e:
            raise Http404(e)

        se_qs = SystemEvent.objects.all().order_by('-created')
        sevt = SystemEventViewTransformer(se_qs)

        return render(request, 'components/index.html', {'nodes': node_count, 'groups': group_count, 'processes': process_count, 'title': 'Dashboard', 'system_event_view_transformer': sevt})


class AllNodesView(View):
    def get(self, request):
        try:
            servers = {name: {'server': helpers._connect_server(node_settings)} for name, node_settings in
                       settings.NODES.items()}

            for name, _dict in servers.items():
                processes_info = _dict['server'].supervisor.getAllProcessInfo()
                for process_info in processes_info:
                    start = datetime.datetime.fromtimestamp(process_info['start'])
                    now = datetime.datetime.fromtimestamp(process_info['now'])
                    uptime = now - start
                    process_info['uptime'] = uptime
                servers[name]['processes'] = processes_info
                state = _dict['server'].supervisor.getState()['statename']
                servers[name]['state'] = state

                if state == 'RUNNING':
                    servers[name]['state_class_postfix'] = 'success'
                else:
                    servers[name]['state_class_postfix'] = 'danger'

                _dict.pop('server', None)

        except gaierror as e:
            return render(request, 'error/node_not_reachable.html', {'message': e})
        except Exception as e:
            raise Http404(e)

        return render(request, 'components/all_nodes.html', {'servers': servers, 'title': 'All Nodes'})


class SingleNodeView(View):
    def get(self, request, node):
        try:
            node_settings = settings.NODES[node]
            server = helpers._connect_server(node_settings)

            processes = server.supervisor.getAllProcessInfo()

            counts = {
                'RUNNING': 0,
                'FATAL': 0,
                'STOPPED': 0,
                'OTHERS': 0
            }

            for process in processes:
                start = datetime.datetime.fromtimestamp(process['start'])
                now = datetime.datetime.fromtimestamp(process['now'])
                process['uptime'] = now - start

                # If name == group the process does not belong to a group
                if process['group'] == process['name']:
                    process['group'] = ''

                # Count nr of processes in different states
                if process['statename'] in counts.keys():
                    counts[process['statename']] += 1
                else:
                    counts['OTHERS'] += 1

                # Clean up process dictionary
                keys_to_pop = ['start', 'now', 'description', 'state', 'logfile', 'stdout_logfile', 'stderr_logfile']
                for key in keys_to_pop:
                    process.pop(key)
        except gaierror as e:
            return render(request, 'error/node_not_reachable.html', {'message': e})
        except Exception as e:
                raise Http404(e)

        return render(request, 'components/single_node.html', {'node': node, 'processes': processes, 'state_counts': counts, 'title': node})


class SingleGroupView(View):
    # Displays every process running in a single group, regardless of which node it runs in
    # Shows information about the process, such as PID, node, name, etc.
    def get(self, request, group):
        servers = {name: {'server': helpers._connect_server(node_settings)} for name, node_settings in
                   settings.NODES.items()}

        group_processes = []

        for node, _dict in servers.items():
            processes = _dict['server'].supervisor.getAllProcessInfo()

            for process in processes:
                if process['group'] == group:
                    process['node'] = node
                    start = datetime.datetime.fromtimestamp(process['start'])
                    now = datetime.datetime.fromtimestamp(process['now'])
                    process['uptime'] = now - start
                    group_processes.append(process)

        return render(request, 'components/single_group.html', {'group': group, 'processes': group_processes})


class AjaxRestartProcessView(View):
    def post(self, request):
        process_name = request.POST.get('process_name', None)
        node = request.POST.get('node', None)
        group = request.POST.get('group', None)

        if not process_name or not node or group is None:
            return JsonResponse({'success': False, 'message': 'Please supply a process and node name'})

        if group == '':
            full_name = process_name
        else:
            full_name = '{}:{}'.format(group, process_name)

        try:
            node_settings = settings.NODES[node]

            server = helpers._connect_server(node_settings)

            started = False

            stopped = helpers._stop_process(server, full_name)

            if stopped:
                started = server.supervisor.startProcess(full_name)
            else:
                return JsonResponse({'success': False, 'message': 'Could not stop process'})

            if not started:
                return JsonResponse({'success': False, 'message': 'Could not start process'})

            new_state = helpers._get_process_state(server, full_name)
        except gaierror as e:
            return JsonResponse({'success': False, 'message': e})
        except Exception as e:
            return JsonResponse({'success': False, 'message': e})

        SystemEvent.restarted_process(request.user, full_name, node)

        return JsonResponse({'success': True, 'message': '{}: Restarted successfully'.format(full_name), 'state': new_state})

class AjaxStopProcessView(View):
    def post(self, request):
        node = request.POST.get('node', None)
        process_name = request.POST.get('process_name', None)
        group = request.POST.get('group', None)

        if not process_name or not node or group is None:
            return JsonResponse({'success': False, 'message': 'Please supply a process and node name'})

        if group == '':
            full_name = process_name
        else:
            full_name = '{}:{}'.format(group, process_name)

        try:
            node_settings = settings.NODES[node]

            server = helpers._connect_server(node_settings)

            stopped = helpers._stop_process(server, full_name)

            if not stopped:
                return JsonResponse({'success': False, 'message': 'Could not stop process'})

            new_state = helpers._get_process_state(server, full_name)
        except gaierror as e:
            return JsonResponse({'success': False, 'message': e})
        except Exception as e:
            return JsonResponse({'success': False, 'message': e})

        SystemEvent.stopped_process(request.user, full_name, node)

        return JsonResponse({'success': True, 'message': '{}: Stopped successfully'.format(full_name), 'state': new_state})

class AjaxRestartAllProcessesView(View):
    def post(self, request):
        node = request.POST.get('node', None)

        if not node:
            return JsonResponse({'success': False, 'message': 'Please supply a node name'})

        try:
            node_settings = settings.NODES[node]
            server = helpers._connect_server(node_settings)
            processes = server.supervisor.getAllProcessInfo()

            for process in processes:
                if process['group'] == '':
                    full_name = process['name']
                else:
                    full_name = '{}:{}'.format(process['group'], process['name'])

                stopped = helpers._stop_process(server, full_name)

                if stopped:
                    started = server.supervisor.startProcess(full_name)
                else:
                    return JsonResponse({'success': False, 'message': 'Could not stop process'})

                if not started:
                    return JsonResponse({'success': False, 'message': 'Could not start process'})

        except gaierror as e:
            return JsonResponse({'success': False, 'message': e})
        except Exception as e:
            return JsonResponse({'success': False, 'message': e})

        SystemEvent.free_text(request.user, 'Restarted all processes on {}'.format(node))

        return JsonResponse({'success': True, 'message': 'Successfully restarted all processes on {}'.format(node)})


class AjaxStopAllProcessesView(View):
    def post(self, request):
        node = request.POST.get('node', None)

        if not node:
            return JsonResponse({'success': False, 'message': 'Please supply a node name'})

        try:
            node_settings = settings.NODES[node]
            server = helpers._connect_server(node_settings)
            processes = server.supervisor.getAllProcessInfo()

            for process in processes:
                if process['group'] == '':
                    full_name = process['name']
                else:
                    full_name = '{}:{}'.format(process['group'], process['name'])

                stopped = helpers._stop_process(server, full_name)

                if not stopped:
                    return JsonResponse({'success': False, 'message': 'Could not stop process'})

        except gaierror as e:
            return JsonResponse({'success': False, 'message': e})
        except Exception as e:
            return JsonResponse({'success': False, 'message': e})

        SystemEvent.free_text(request.user, 'Stopped all processes on {}'.format(node))

        return JsonResponse({'success': True, 'message': 'Successfully stopped all processes on {}'.format(node)})


class LogoutView(RedirectView):
    """
    A view that logout user and redirect to homepage.
    """
    permanent = False
    query_string = True
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        """
        Logout user and redirect to target url.
        """
        if self.request.user.is_authenticated():
            logout(self.request)

        return super(LogoutView, self).get_redirect_url(*args, **kwargs)