class User:
    def __init__(self, id, guid, name, location=None, description=None):
        self.id = id
        self.guid = guid
        self.name = name
        self.location = location
        self.description = description

    def get_id(self):
        return self.id

    def get_guid(self):
        return self.guid

    def get_name(self):
        return self.name

    def get_location(self):
        return self.location

    def get_description(self):
        return self.description