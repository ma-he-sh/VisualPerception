import uuid

class MapObj( object ):
    def __init__(self, uuid, file_name, file_date, file_ext ):
        self.uuid = uuid
        self.file_name = file_name
        self.file_date = file_date
        self.file_ext  = file_ext

    def get_file_name(self):
        return self.file_name

    def get_file_ext(self):
        return self.file_ext

    def get_uuid(self):
        return self.uuid

    def get_file_path(self):
        pass

class MapHandler:
    @staticmethod
    def file_exist( uuid ):
        pass

    @staticmethod
    def save_file( uuid, fileObj ):
        pass

    @staticmethod
    def delete_file( uuid ):
        pass

    @staticmethod
    def get_map( uuid ):
        pass
