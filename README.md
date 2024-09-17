# agoBackup.py

## Overview

[`agoBackup.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FC%3A%2Fcode%2FAGO_Backup%2FagoBackup.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%226e1583df-acfa-4473-be89-32cbafdd3e56%22%5D "c:\code\AGO_Backup\agoBackup.py") is a Python script designed to back up items from an ArcGIS Online organizational portal. The script gathers all of the Feature Service layers accessible by the user and exports a Gile GeoDatabase to a Zip file to download to a local storage location. It also creates a catalog of backed-up items to help identify which items are backed up. Further, the script searches the backup location and checks to see if the online version has been edited since the last backup, creating a new backup for edited versions. The script filters out items that already have existing backups without edits. 

Importantly, a feature service that is regularly edited will create multiple copies to be able to roll back to a previous version if needed. This would be helpful if rows were deleted between backups. Without this, the deleted features or rows would not be recoverable. 

## Features

- **Filter Existing Backups**: The script checks for existing backups and filters out items that have already been backed up.
- **Backup Naming**: Generates a unique backup name for each item based on its ID and last modified date.
- **Error Handling**: Captures and logs errors encountered during the processing of items.

## Requirements

- Python 3.x
- Required Python libraries:
  - `os`
  - `datetime`
  - `csv`
  - `arcgis.gis`

## Usage

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/agoBackup.git
    cd agoBackup
    ```

2. **Modify the script**:
   - Add your ArcGIS Online Credentials
   - Specify the location where the backup files will be stored.
   - Specify the name of the inventory CSV
  
 
4. **Run the script**:
    ```sh
    python agoBackup.py
    ```

## Functions

### `filterExistingBackups(self, items, backupLocation)`

Filters out items that already have existing backups in the specified backup location.

- **Parameters**:
  - `items`: List of items to be backed up.
  - `backupLocation`: Directory where backups are stored.

- **Returns**:
  - `filteredItems`: List of items that do not have existing backups.

### `download_as_fgdb(self, item_list, backupLocation)`

Downloads the items to the specified backuplocation and adds them to the inventory csv


## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
