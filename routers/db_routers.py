class AuthRouter:
    route_app_labels = { "auth", "contenttypes", "sessions", "admin", "accounts" }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "accounts"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "accounts"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if ( obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "accounts"
        return None
    

class Logistics:
    route_app_labels = { "logistics" }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "logistics"
        return None


    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "logistics"
        return None


    def allow_relation(self, obj1, obj2, *hints):
        if(obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels   
        ):
            return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "logistics"
        return None




class Payments:
    route_app_labels = { "payments" }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "payments"
        return None


    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "payments"
        return None


    def allow_relation(self, obj1, obj2, *hints):
        if(obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels   
        ):
            return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "payments"
        return None





class Messaging:
    route_app_labels = { "messaging" }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "messaging"
        return None


    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "messaging"
        return None


    def allow_relation(self, obj1, obj2, *hints):
        if(obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels   
        ):
            return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "messaging"
        return None




