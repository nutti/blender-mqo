# Tutorial

* [Import .mqo](#import-mqo)
* [Export .mqo](#export-mqo)

## Import .mqo

1. Click *File* > *Import* > *Metasequoia (.mqo)*.
2. Select .mqo file to import. You can change the import behaviour by
   changing the options.
   * *Import Objects* : The add-on will not import objects if enabled.
   * *Import Materials* : The add-on will not import materials if enabled.
   * *Import Vertex Weights* : The add-on will import vertex weights
     if enabled.
   * *Add Import Prefix* : Add a prefix string to the name of imported
     objects/materials
3. Click *Import Metasequoia file (.mqo)*.

### Select Objects/Materials to Import

If the option *Selective Import* in *Preferences* is enabled, you can choose
the objects/materials to import upto the limit specified by
*Importable Objects Limit* option and *Importable Materials Limit* option.

## Export .mqo

1. Click *File* > *Export* > *Metasequoia (.mqo)*.
2. Select .mqo file to export. You can change the export behaviour by
   changing the options.
3. Click *Export Metasequoia file (.mqo)*.

Other options effect will be changed by the *Export Mode* option.

### Export Mode: Selected Objects

Export only selected objects in *3D Viewport*.  
Dependant assets will be exported as well if options are specified.

* *Export Materials* : The add-on will export selected materials if enabled.
* *Export Vertex Weights* : The add-on will export selected vertex weights
  if enabled.
* *Add Export Prefix* : Add a prefix string to the name of exported
  objects/materials

### Export Mode: Manual

Export assets selected manually by name.  
Dependency among assets are not taken into account.

* *Export Objects* : The add-on will export selected objects if enabled.
* *Export Materials* : The add-on will export selected materials if enabled.
* *Export Vertex Weights* : The add-on will export selected vertex weights
  if enabled.
* *Add Export Prefix* : Add a prefix string to the name of exported
  objects/materials

## Note

### About "Export Vertex Weights" option

The vertex weights will be exported after merging the values among
the selected vertex groups.
The weight will be selected randomly from the vertex groups
the vertex belongs.
