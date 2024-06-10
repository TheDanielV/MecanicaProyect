# routers.py

class Routes:
    """
    Un enrutador para controlar todas las operaciones de base de datos
    sobre los modelos de autenticación hacia 'auth_db'.
    """

    def db_for_read(self, model, **hints):
        """
        Intenta leer modelos de autenticación desde 'auth_db'.
        """
        if model._meta.app_label == 'AuthService':
            return 'auth_db'
        if model._meta.app_label == 'logs':
            return 'log_db'
        if model._meta.app_label == 'MecanicaApp':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Intenta escribir modelos de autenticación en 'auth_db'.
        """
        if model._meta.app_label == 'AuthService':
            return 'auth_db'
        if model._meta.app_label == 'logs':
            return 'log_db'
        if model._meta.app_label == 'MecanicaApp':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relaciones si un modelo en 'auth_app' está involucrado.
        """
        if obj1._meta.app_label == 'AuthService' or obj2._meta.app_label == 'AuthService':
            return True
        if obj1._meta.app_label == 'logs' or obj2._meta.app_label == 'logs':
            return True
        if obj1._meta.app_label == 'MecanicaApp' or obj2._meta.app_label == 'MecanicaApp':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Asegura que los modelos de autenticación solo se migren en 'auth_db'.
        """
        if app_label == 'AuthService':
            return db == 'auth_db'
        if app_label == 'logs':
            return db == 'log_db'
        if app_label == 'MecanicaApp':
            return db == 'default'
        return None
