# ZenPacks.jstanley.AuditLog

AuditLog ZenPack adds a new button to the device page to pull audit logs from Kibana for that device.

## Releases
Version 1.0.3
> Released: 2022/2/15
> * Updated to use internal/bsearch API to work with newer version
> Compatible with Zenoss 6.6.0
> Tested in Zenoss
> * 6.6.0

Version 1.0.0
> Released: 2018/6/18
>
> Compatible with Zenoss 6.1.2+
> Tested in Zenoss
> * 6.1.0
> * 6.1.1
> * 6.1.2
> * 6.2.0
>
> Requires: ZenPackLib ZenPack (https://www.zenoss.com/product/zenpacks/zenpacklib)

## Features
Additional button to the device page to pull audit logs from Kibana for that device.

## Usage
After installing the ZenPack, navigate to Infrastructure and at root device class level (/Devices) set the following zProperties based on your Control Center setup.
* zCCHost
* zCCPort
* zCCUser
* zCCPass
 > These settings will usually be the same you have used on your ControlCenter device under /ControlCenter

For a user to see the button, they must have the "Change Device" permission.

## Installed Items
### zProperties
* zCCHost
* zCCPort
* zCCUser
* zCCPass

## Changes
### 1.0.3
* Updated to use new URL for Zenoss 6.6.0

### 1.0.0
* Initial release.
