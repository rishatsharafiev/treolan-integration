def exception(logger):

    def decorator(func):
 
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exp:
                logger.exception(exp)
        return wrapper
    return decorator
