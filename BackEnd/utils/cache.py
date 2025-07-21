_cache = None

def set_cache_instance(cache_instance):
    global _cache
    _cache = cache_instance

def get_cache():
    return _cache
