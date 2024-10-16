<!-- markdownlint-disable MD024 -->

# Installation

Before installing blender-mqo add-on, check if
[the add-on version](#support-version) supports on the your Blender version.

There are 3 ways to blender-mqo add-on.

<!-- markdownlint-disable-next-line MD013 -->
* [Blender's Installation Tool (from extensions.blender.org)](#blenders-installation-tool-from-extensionsblenderorg) *(Recommended)*
* [Blender's Installation Tool (from Disk)](#blenders-installation-tool-from-disk)
* [Manual Install](#manual-install)

## Support Version

|Version|Supported Blender Version|
|---|---|
|Unstable|2.79 -|
|2.0|2.79 -|
|1.4|2.79 - 4.1|
|1.3|2.79 - 3.6|
|1.2|2.79 - 3.0|
|1.1|2.79 - 2.91|
|1.0|2.79 - 2.83|

## Blender's Installation Tool (from extensions.blender.org)

*This method works for the stable version on Blender 4.2 or later.*  
*If you want to install the older version, follow other processes*

<!-- markdownlint-disable-next-line MD013 -->
blender-mqo is published at [extensions.blender.org](https://extensions.blender.org/add-ons/blender-mqo/).  
You can install this add-on from there.

1. Launch Blender and open the preference window by clicking *Edit* >
   *Preferences ...*.
2. Click *Get Extensions* in the preference window.
3. Search **MQO (Metasequoia) Format File Importer/Exporter** and click
   *Install* button.

## Blender's Installation Tool (from Disk)

*This method works for the stable version only.*  
*You can't install the unstable version by this method.*  
*If you want to install the unstable version, follow
*[Manual Install](#manual-install) process*

<!-- markdownlint-disable-next-line MD001 -->
#### 1. Download zip archive from below links

|Version|Download URL|
|---|---|
|*unstable*|[Download](https://github.com/nutti/blender-mqo/archive/master.zip)|
|2.0|[Download](https://github.com/nutti/blender-mqo/releases/tag/v2.0.0)|
|1.4|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.4.0)|
|1.3|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.3)|
|1.2|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.2)|
|1.1|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.1)|
|1.0|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.0)|

#### 2. Install the add-on from Blender

Follow below process.

##### Blender 4.2 or later

1. Launch Blender and open the preference window by clicking *Edit* >
   *Preferences ...*.
2. Click *Add-ons* in the preference window
3. Click down arrow button on the upper-right of window, and click
   *Install from Disk...* and select the downloaded .zip file.

or,

1. Launch Blender.
2. Drag and drop the downloaded .zip file to Blender.

##### Blender 4.1 or before

1. Launch Blender and open the preference window by clicking *Edit* >
   *Preferences ...*.
2. Click *Add-ons* in the preference window
3. Click *Install...* and select the downloaded .zip file.

#### 3. Enable add-on

Enable add-on, then you can use add-on blender-mqo.  
The name of add-on displayed in Blender is **MQO (Metasequoia) Format File Importer/Exporter**.

## Manual Install

<!-- markdownlint-disable-next-line MD001 -->
#### 1. Download zip archive from below links

|Version|Download URL|
|---|---|
|*unstable*|[Download](https://github.com/nutti/blender-mqo/archive/master.zip)|
|2.0|[Download](https://github.com/nutti/blender-mqo/releases/tag/v2.0.0)|
|1.4|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.4.0)|
|1.3|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.3)|
|1.2|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.2)|
|1.1|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.1)|
|1.0|[Download](https://github.com/nutti/blender-mqo/releases/tag/v1.0)|

#### 2. Unzip it, and check the add-on sources

Unzip the .zip file you downloaded.  
Then, check if there are add-on sources.

Add-on sources are located on the different places depending on the add-on version.

|Version|Sources|
|---|---|
|unstable|src/blender_mqo|
|1.0 - 2.0|blender_mqo|

#### 3. Copy add-on sources into your add-on folder

Location of add-on folder depends on your operating system.

##### Blender 4.2 or later

|OS|Location|
|---|---|
|Windows|`C:\Users\<username>\AppData\Roaming\Blender Foundation\Blender\<blender_version>\extensions\user_default`|
|Mac|`/Users/<username>/Library/Application Support/Blender/<blender_version>/extensions/user_default`|
|Linux|`/home/<username>/.config/blender/<blender_version>/extensions/user_default`|

##### Blender 4.1 or before

|OS|Location|
|---|---|
|Windows|`C:\Users\<username>\AppData\Roaming\Blender Foundation\Blender\<blender_version>\scripts\addons`|
|Mac|`/Users/<username>/Library/Application Support/Blender/<blender_version>/scripts/addons`|
|Linux|`/home/<username>/.config/blender/<blender_version>/scripts/addons`|

#### 4. Enable add-on

Enable add-on, then you can use add-on blender-mqo.  
The name of add-on displayed in Blender is **MQO (Metasequoia) Format File Importer/Exporter**.
