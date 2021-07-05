Netbox scripts

### <i>custom_field_search.py</i>
Searching for all devices with information in a 'License' custom field. 
Search can be done by site name, device type, vendor.
Licenses output is in Juniper format

### <i>GetInventoryJunos.py</i>
Getting chassis inventory information from JunOS devices that are registered in Netbox and have primary_ip address, using NETCONF (must be allowded on devices). 
Search can be done by site name, device type, device name.
