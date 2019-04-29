# Blender Add-on: blender-mqo (Metasequoia File Importer/Exporter)

blender-mqo is an importer/exporter between Blender and Metasequoia via .mqo files.


## Download

All releases are available from [Release Page](https://github.com/nutti/blender-mqo/releases).  
If you are an adventurous user, you can download and use [unstable version](https://github.com/nutti/blender-mqo/archive/master.zip) instead.


## Features

blender-mqo supports **English** only.  
The features of this add-on are as follows.

* Import .mqo File
  * Object (includes Mesh)
  * UV map
  * Materials
  * Mirror modifier
* Export .mqo File
  * Object (includes Mesh)
  * UV map
  * Materials
  * Modifiers (All modifiers are applied before exporting)


## Tutorials

### Install

1. [Download add-on](https://github.com/nutti/blender-mqo#download).
2. Unzip the .zip file you downloaded. Then, check if the add-on sources are located on `src/mqo`.
3. Copy add-on sources into your add-on folder.
4. Enable add-on. The add-on name is **MQO (Metasequoia) format**.


### Import .mqo

1. Click *File* > *Import* > *Metasequoia (.mqo)*.
2. Select .mqo file to import.
   * You can choose objects/materials to import.
   * You can add a prefix string to the name of imported objects/materials
3. Click *Import Metasequoia file (.mqo)*.


### Export .mqo

1. Click *File* > *Export* > *Metasequoia (.mqo)*.
2. Select .mqo file to export.
   * You can choose objects/materials to export.
   * You can add a prefix string to the name of exported objects/materials
3. Click *Export Metasequoia file (.mqo)*.


## Change Log

All changes about this add-on can be seen in [CHANGELOG.md](CHANGELOG.md).


## Bug report / Feature request / Disscussions

If you want to report bug, request features or discuss about this add-on, see [ISSUES.md](ISSUES.md).


## Contribution

If you want to contribute to this project, see [CONTRIBUTING.md](CONTRIBUTING.md).