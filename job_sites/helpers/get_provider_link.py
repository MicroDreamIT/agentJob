from urllib.parse import urlparse


def get_provider_and_link(url):
    parsed_url = urlparse(url)
    provider = parsed_url.netloc.replace('www.', '')
    return provider, url