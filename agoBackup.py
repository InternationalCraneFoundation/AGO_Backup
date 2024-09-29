"""
AGOBackup Script
Orignal Author: Dorn Moore, International Crane Foundation 2024-09-16
Modified by: Dorn Moore, International Crane Foundation 2024-09-17

Based on the script by: Esri, Inc. 20213-09-12 - https://support.esri.com/en-us/knowledge-base/back-up-hosted-content-by-looping-through-and-downloadi-000022524

Description:

This script provides functionality to back up feature layers and tables from ArcGIS Online (AGO) to a specified local directory. It includes methods to query items in AGO, retrieve the most recent edit dates, and filter out items that already have backups.

Classes:
    AGOBackup:
        A class to handle the backup process for AGO feature layers and tables.

        Methods:
            __init__(self, gis, backup_location):
                Initializes the AGOBackup instance with a GIS connection and a backup location.

            get_feature_layers(self, query, max_items=2000):
                Searches for feature layers in AGO based on a query and returns the items.

            get_most_recent_edit_date(self, item):
                Retrieves the most recent edit date of the given item, considering both layers and tables.

            filter_existing_backups(self, items):
                Filters out items from the provided list that already have a backup in the specified location.

            backup_item(self, item):
                Backs up the given item to the specified backup location.

            run_backup(self, query):
                Executes the backup process for items matching the query.

Usage:
    1. Initialize the AGOBackup class with a GIS connection and a backup location.
    2. Use the run_backup method with a query to back up the relevant items.

Example Usage:

    gis = gis = GIS('home') or GIS("https://www.arcgis.com", "username", "password")
    
    backup = AGOBackup(gis, "/path/to/backup/location")
    
    newItems = backup.filterExistingBackups(items, backupLocation)

    backup.download_as_fgdb(newItems, backupLocation)

TODO:
* Add single backup method to handle the entire backup process.
* Add support for other item types (e.g., Web Maps, Web Apps, etc.).
* Store a log file with the backup details.
* Add error handling and logging.
* Add command-line arguments for the script.
* option to backup the files to a blob storage instead of a local directory (e.g. Azure Blob Storage or B2/AWS Bucket ).

"""


# from datetime import datetime
import csv
# from time import strftime
import datetime as dt
from arcgis.gis import GIS
import os


class AGOBackup:
    def __init__(self, gis, backup_location):
        self.gis = gis
        self.backup_location = backup_location

    def get_feature_layers(self, query, max_items=2000):
        items = self.gis.content.search(
            query=query, max_items=max_items, sort_field='modified', sort_order='desc')
        return items

    def get_most_recent_edit_date(self, item):
        last_edited = None

        try:
            # Check layers
            for layer in item.layers:
                # print(layer.properties)
                if layer.properties.editingInfo:
                    last_edited_date = layer.properties.editingInfo['lastEditDate']
                else:
                    continue

                if last_edited is None or last_edited_date > last_edited:
                    last_edited = last_edited_date

            # Check tables
            for table in item.tables:
                if table.properties.editingInfo:
                    last_edited_date = table.properties.editingInfo['lastEditDate']
                else:
                    continue
                if last_edited is None or last_edited_date > last_edited:
                    last_edited = last_edited_date

            if last_edited is not None:
                last_edited = dt.datetime.fromtimestamp(
                    last_edited_date/1000).strftime("%Y-%m-%d_%H-%M-%S")
                return last_edited
            else:
                return None

        except Exception as e:
            print(f"Error processing item {item.title}: {e}")
            return None

    def filterExistingBackups(self, items, backupLocation):
        filteredItems = []

        for item in items:

            last_edited_date = self.get_most_recent_edit_date(item)
            if last_edited_date is None:
                items.remove(item)
                continue
            else:
                if last_edited_date != "None":
                    modified_date = last_edited_date
                else:
                    modified_date = "None"
                # modified_date = last_edited_date

            # get the item's id
            item_id = item.id

            backup_name = str(item_id) + "_" + str(modified_date)
            # replace any spaces with underscores
            backup_name = backup_name.replace(" ", "_")
            # replace any colons with underscores
            backup_name = backup_name.replace(":", "_")
            # print("Backup name: " + backup_name)
            if os.path.exists(backupLocation + "\\" + backup_name + ".zip"):
                # print("A backup already exists for " + item.title)
                items.remove(item)
            else:
                filteredItems.append(item)
        return filteredItems

    def download_as_fgdb(self, item_list, backupLocation, csv_file_path):
        for item in item_list:

            last_edited_date = self.get_most_recent_edit_date(item)
            # print(last_edited_date)
            if last_edited_date is None:
                continue
            else:
                if last_edited_date != "None":
                    modified_date = last_edited_date
                else:
                    modified_date = "None"
                # get the item's id
                item_id = item.id
                backup_name = str(item_id) + "_" + str(modified_date)
                # replace any spaces with underscores
                backup_name = backup_name.replace(" ", "_")
                # replace any colons with underscores
                backup_name = backup_name.replace(":", "_")
                # print("Backup name: " + backup_name)

                if os.path.exists(backupLocation + "\\" + backup_name + ".zip"):
                    print(" * A backup already exists for " + item.title)

                else:
                    try:
                        result = item.export(
                            backup_name, "File Geodatabase", parameters=None, wait=True)
                        # print(result)
                        result.download(backupLocation)
                        result.delete()
                        print(" * Successfully downloaded " + item.title)
                        self.write_to_csv(
                            [item], self.csv_file_path, backup_name, modified_date)
                    except Exception as e:
                        print(f" * ERROR downloading item {item.title}: {e}")
                        continue
        print("Finished downloading backups")

    def write_to_csv(self, item_list, csv_file_path, file_name, last_edited, skip_keys=None):
        if skip_keys is None:
            skip_keys = []

        file_exists = os.path.isfile(csv_file_path)

        with open(csv_file_path, mode='a', newline='') as csv_file:
            fieldnames = ['FileName', 'Title', 'ID', 'Owner', 'typeKeywords', 'Snippet',
                          'ownerFolder', 'groupDesignations', 'layers', 'tables', 'Last Edited']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for item in item_list:
                if last_edited is None:
                    last_edited = ''
                item_dict = {
                    'FileName': file_name,
                    'Title': item.title,
                    'ID': item.id,
                    'Owner': item.owner,
                    'typeKeywords': item.typeKeywords,
                    'Snippet': item.snippet,
                    'ownerFolder': item.ownerFolder,
                    'groupDesignations': item.groupDesignations,
                    'layers': item.layers,
                    'tables': item.tables,
                    'Last Edited': last_edited
                }

                writer.writerow(item_dict)



# Usage
if __name__ == "__main__":
    print("Starting AGO Backup")
    gis = GIS('home')  # Using the local profile for the AGO Credentails will need to change if the computer running the backup script does not have ArcGIS Pro setup on teh workstation and the AGO credentials are not stored

    # Change this to the location you want to save the backups to
<<<<<<< HEAD
    myBackupLocationPath = r"C:\Users\Dorn\INTERNATIONAL CRANE FOUNDATION\GIS Team - Documents\AGOL_Backup"
    backupLocation = myBackupLocationPath
    folder_path = myBackupLocationPath
=======
    backupLocation = r"MY_BACKUP_LOCATION"
    folder_path = backupLocation
>>>>>>> bfc16484ada8b884c8fabb28f2b6fb324d2e3402
    csv_file_path = os.path.join(backupLocation, 'agoBackupDetails.csv')

    backup = AGOBackup(gis, folder_path)

    query_string = "type:Feature Service AND NOT typekeywords:View Service"
    items = backup.get_feature_layers(query_string)
    # return the count of items
    print(" - Number of Feature Services: " + str(len(items)))

    # limit the items based on the existing backups
    print("Filtering existing backups to only download items with update content...")
    newItems = backup.filterExistingBackups(items, backupLocation)
    print(" - Number of items to backup: " + str(len(newItems)))

    print("Downloading items...")
    backup.download_as_fgdb(newItems, backupLocation, csv_file_path)
