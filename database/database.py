#!/usr/local/bin/python3.4

"""
Database model
{
    "<sliceName>": {
        "status": "<status>",
        "sliceSubnetIds": {
            "<sliceSubnetName>": {
                "status": "<status>"
            }
        }
    }
}

"""

from threading import Lock

class slice_database:
    """ Class to store references to all slices """

    def __init__(self):
        self.slice_db = dict()
        self.lock = Lock()

    def add_slice(self, name):
        """ Creates a new slice with the given name """
        self.lock.acquire()
        if name in self.slice_db:
            self.lock.release()
            raise ValueError("Error while adding slice \""+ name + "\": Already exists!")

        slice_entry = dict()
        slice_entry["status"]="CREATING"
        self.slice_db[name] = slice_entry
        self.lock.release()

    def add_slice_subnet(self, name, sliceName):
        """ Creates a new slice subnet with the given name in the given sliceName """
        self.lock.acquire()
        if not sliceName in self.slice_db:
            self.lock.release()
            raise ValueError("Error while adding slice subnet to slice \""+ sliceName + "\": Not exists!")

        if "sliceSubnetIds" in self.slice_db[sliceName]:
            if name in self.slice_db[sliceName]["sliceSubnetIds"]:
                self.lock.release()
                raise ValueError("Error while adding slice subnet \""+ name + "\": Already exists!")

        else: 
            self.slice_db[sliceName].update({"sliceSubnetIds":{}})

        slice_subnet_entry = dict()
        slice_subnet_entry["status"]="CREATING"
        self.slice_db[sliceName]["sliceSubnetIds"][name]=slice_subnet_entry

        self.lock.release()

    def del_slice(self, name):
        """ Deletes the slice with that name """
        self.lock.acquire()
        if not name in self.slice_db:
            self.lock.release()
            raise ValueError("Error while deleting slice \""+ name + "\": Not exists!") 

        #del self.slice_db[name]
        self.slice_db.pop(name)
        self.lock.release()

    def del_slice_subnet(self, name, sliceName):
        """ Deletes the slice subnet with that name in the given sliceName """
        self.lock.acquire()
        if not sliceName in self.slice_db:
            self.lock.release()
            raise ValueError("Error while deleting slice subnet from slice \""+ sliceName + "\": Not exists!")

        if not "sliceSubnetIds" in self.slice_db[sliceName]:
            self.lock.release()
            raise ValueError("Error while deleting slice subnet \""+ name + "\" from slice: Not exists!")

        if not name in self.slice_db[sliceName]["sliceSubnetIds"]:
            self.lock.release()
            raise ValueError("Error while deleting slice subnet \""+ name + "\" from slice: Not exists!")

        self.slice_db[sliceName]["sliceSubnetIds"].pop(name)

        self.lock.release()

    def update_status_slice(self, status, name):
        """ Updates the slice with that status for the given name """
        self.lock.acquire()
        if not name in self.slice_db:
            self.lock.release()
            raise ValueError("Error while updating slice \""+ name + "\": Not exists!") 

        self.slice_db[name]["status"] = status

        self.lock.release()

    def update_status_slice_subnet(self, status, name, sliceName):
        """ Updates the slice subnet with that status for the given name in the given sliceName """
        self.lock.acquire()
        if not sliceName in self.slice_db:
            self.lock.release()
            raise ValueError("Error while updating slice subnet from slice \""+ sliceName + "\": Not exists!")

        if not "sliceSubnetIds" in self.slice_db[sliceName]:
            self.lock.release()
            raise ValueError("Error while updating slice subnet \""+ name + "\" from slice: Not exists!")

        if not name in self.slice_db[sliceName]["sliceSubnetIds"]:
            self.lock.release()
            raise ValueError("Error while updating slice subnet \""+ name + "\" from slice: Not exists!")

        self.slice_db[sliceName]["sliceSubnetIds"][name]["status"] = status

        self.lock.release()

    def get_status_slice(self, name):
        """ Returns the status of slice """

        if not name in self.slice_db:
            raise ValueError("Error while geting status slice \""+ name + "\": Not exists!") 

        return self.slice_db[name]["status"]

    def get_status_slice_subnet(self, name, sliceName):
        """ Returns the status of slice subnet for the given name in the given sliceName """

        if not sliceName in self.slice_db:
            raise ValueError("Error while geting slice subnet from slice \""+ sliceName + "\": Not exists!")

        if not "sliceSubnetIds" in self.slice_db[sliceName]:
            raise ValueError("Error while geting slice subnet \""+ name + "\" from slice: Not exists!")

        if not name in self.slice_db[sliceName]["sliceSubnetIds"]:
            raise ValueError("Error while geting slice subnet \""+ name + "\" from slice: Not exists!") 

        return self.slice_db[sliceName]["sliceSubnetIds"][name]["status"]

    def get_slice(self, name):
        """ Returns the slice (object) to perform operations in that slice """

        if not name in self.slice_db:
            raise ValueError("Error while geting slice \""+ name + "\": Not exists!") 

        return self.slice_db[name]

    def get_all_slices(self):
        """ Returns the slice database (object) to perform operations """

        return self.slice_db