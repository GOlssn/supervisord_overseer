from django.conf import settings
from process_management.tools import helpers

def nodes(request):
    nodes_list = [name for name, _ in settings.NODES.items()]

    return {
        'nodes_list': nodes_list
    }


def unique_groups(request):
    servers = {name: {'server': helpers._connect_server(node_settings)} for name, node_settings in
               settings.NODES.items()}

    nodes_groups = helpers._get_unique_groups(servers)

    return {
        'unique_groups': nodes_groups
    }