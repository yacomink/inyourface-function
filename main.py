import platform
import re
import os, sys
from flask import request, escape
import inyourface.effect
from inyourface import EffectOrchestrator
from google.cloud import storage
import pprint

"""
This is a basic request for an inyourface effect which will return a gif with
the requested effects
request should have:
{
  urls: string [] // list of images, gifs
  effects: string [] // list of effects
}
"""
def hello_http(request):
    if re.search('Linux.*debian', platform.platform()):
        os.environ['PATH'] = "./bin/deb/:" + os.getenv('PATH')
    elif re.search('Darwin', platform.platform()):
        os.environ['PATH'] = "./bin/osx/:" + os.getenv('PATH')

    data = request.get_json()
    urls = data.get("urls")
    # TODO: error handling for no image_url
    effects = data.get("effects")
    effects = list(filter((lambda x: is_effect(x)), effects))

    gif = EffectOrchestrator(urls, "/tmp/", None, effects)
    name = gif.gif()
    client = storage.Client()
    bucket = client.get_bucket('inyourface')
    blob = bucket.blob(re.sub('^/tmp', 'cf', name))
    blob.upload_from_filename(filename=name)

    pprint.pprint(os.stat(name))
    print(len(blob.download_as_string()))
    print(os.system("gifsicle"))

    return blob.public_url


def is_effect(e):
    try:
        effect_module = getattr(inyourface.effect, e[0].upper() + e[1:])
        return True
    except Exception as ex:
        return False
