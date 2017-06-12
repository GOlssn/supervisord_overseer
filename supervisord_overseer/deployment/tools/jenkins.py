import requests


def trigger_jenkins(jenkins_url, **kwargs):
    if kwargs:
        params = '&'.join(['{}={}'.format(key, value) for key, value in kwargs.items()])
        jenkins_url += '/buildWithParameters?{}'.format(params)
    else:
        jenkins_url += '/build'

    res = requests.get(jenkins_url)
