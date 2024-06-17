# routers.py

class Routes:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'AuthService':
            return 'auth_db'
        if model._meta.app_label == 'logs':
            return 'log_db'
        if model._meta.app_label == 'MecanicaApp':
            return 'default'
        if model._meta.app_label == 'sessions':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'AuthService':
            return 'auth_db'
        if model._meta.app_label == 'logs':
            return 'log_db'
        if model._meta.app_label == 'MecanicaApp':
            return 'default'
        if model._meta.app_label == 'sessions':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in ('AuthService', 'logs', 'MecanicaApp', 'sessions') or \
           obj2._meta.app_label in ('AuthService', 'logs', 'MecanicaApp', 'sessions'):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'AuthService':
            return db == 'auth_db'
        if app_label == 'logs':
            return db == 'log_db'
        if app_label == 'MecanicaApp':
            return db == 'default'
        if app_label == 'sessions':
            return db == 'default'
        return None
