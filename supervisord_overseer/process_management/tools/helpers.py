from typing import List, Dict
from xmlrpc import client as xmlrpc


def _connect_server(settings: Dict[str, str]):
    try:
        server = xmlrpc.ServerProxy('http://{}:{}@{}:{}/RPC2'.format(
            settings['username'],
            settings['password'],
            settings['hostname'],
            settings['port']
        ))
    except Exception as e:
        return None

    return server


def _get_unique_groups(servers: Dict[str, dict]):
    group_names = []

    for node, _dict in servers.items():
        processes = _dict['server'].supervisor.getAllProcessInfo()

        group_names = [process['group'] for process in processes
                       if process['group'] is not process['name']]

    group_names = list(set(group_names))
    return group_names

def _groups_nodes_processes_map(servers: Dict[str, dict]):
    group_names = []

    for node, _dict in servers.items():
        processes = _dict['server'].supervisor.getAllProcessInfo()

        group_names = [process['group'] for process in processes
                       if process['group'] is not process['name']]

    group_names = list(set(group_names))
    groups = {key: {'nodes': {}} for key in group_names}

    for node, _dict in servers.items():
        processes = _dict['server'].supervisor.getAllProcessInfo()

        for process in processes:
            if node not in groups[process['group']]['nodes'].keys():
                groups[process['group']]['nodes'][node] = {'processes': []}

            if process not in groups[process['group']]['nodes'][node]['processes']:
                groups[process['group']]['nodes'][node]['processes'].append(process)

    return groups


def _stop_process(server: xmlrpc.ServerProxy, name: str):
    stopped = True

    process_state = server.supervisor.getProcessInfo(name)['statename']

    if process_state == 'RUNNING':
        stopped = server.supervisor.stopProcess(name)

    return stopped

def _get_process_state(server: xmlrpc.ServerProxy, name: str):
    process_info = server.supervisor.getProcessInfo(name)

    return process_info['statename']