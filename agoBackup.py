from datetime import datetime
import csv
from time import strftime
import datetime as dt
from arcgis.gis import GIS
import os


class AGOLBackup:
    def __init__(self, gis, backup_location):
        self.gis = gis
        self.backup_location = backup_location

    def get_feature_layers(self, query, max_items=2000):
        items = self.gis.content.search(
            query=query, max_items=max_items, sort_field='modified', sort_order='desc')
        return items

    def download_as_fgdb(self, item_list):
        for item in item_list:
            # for key in item print key and value
            # for key in item:
            #     print(key + ": " + str(item[key]))
            last_edited = None

            try:
                if 'View Service' in item.typeKeywords:
                    pass
                else:
                    layers = item.layers
                    last_edited = None
                    modified_date = None
                    for layer in layers:

                        layer_info = layer.properties
                        last_edited_date = layer_info.editingInfo.lastEditDate / \
                            1000  # Convert from milliseconds to seconds
                        if last_edited is None or last_edited_date > last_edited:
                            last_edited = last_edited_date
                            try:
                                # print("Last edited: " + str(last_edited))

                                modified_date = dt.datetime.fromtimestamp(
                                    last_edited).strftime("%Y-%m-%d_%H-%M-%S")
                                # print(modified_date)
                            except:
                                # print("Modified: " + modified_date)
                                modified_date = ''
                # get the item's id
                item_id = item.id
                # check to see if the backup_location has a file with the same name as item.title + "_" + modified_date
                # if it does, then skip downloading the item
                # if not, then download the item
                backup_name = str(item_id) + "_" + str(modified_date)
                # replace any spaces with underscores
                backup_name = backup_name.replace(" ", "_")
                # replace any colons with underscores
                backup_name = backup_name.replace(":", "_")
                # print("Backup name: " + backup_name)
                if os.path.exists(self.backup_location + "\\" + backup_name + ".zip"):
                    print("A backup already exists for " + item.title)

                else:
                    result = item.export(
                        backup_name, "File Geodatabase", parameters=None, wait=True)
                    # print(result)
                    result.download(self.backup_location)
                    result.delete()
                    print("Successfully downloaded " + item.title)
                    self.write_to_csv(
                        [item], os.path.join(self.backup_location, 'backup_info.csv'), backup_name, modified_date)

            except Exception as e:
                print("An error occurred downloading " +
                      item.title + ": " + str(e))

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
    gis = GIS('home')  # Using the local profile for the AGO Credentails will need to change if the computer running the backup script does not have ArcGIS Pro setup on teh workstation and the AGO credentials are not stored

    # Change this to the location you want to save the backups to
    myBackupLocationPath = r"C:\Users\username\Documents\ArcGIS\AGO_Backup"
    folder_path = myBackupLocationPath
    csv_file_path = os.path.join(folder_path, 'agoBackupDetails.csv')

    backup = AGOLBackup(gis, folder_path)

    query_string = "type:Feature Service AND NOT typekeywords:View Service"
    items = backup.get_feature_layers(query_string)

    # backup.print_item_details(items)
    backup.download_as_fgdb(items)
    # backup.write_to_csv(items, csv_file_path)
