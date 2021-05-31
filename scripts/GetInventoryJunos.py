from django.utils.text import slugify
from dcim.choices import DeviceStatusChoices, SiteStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from extras.scripts import *
from jnpr.junos import Device as Node
from lxml import etree
import jxmlease, os, re

class GetInventoryScript(Script):

    name = "Collect inventory items information from Juniper devices --- TEST"

    class Meta:
        description = "Getting inventory information (via netconf)"
        field_order = ['site_name', 'device_type', 'device_name']
        commit_default = False

    site_name = ObjectVar(
            description="Specify site name - all, if not selected (<i>Optional</i>)",
            model=Site,
            display_field='site',
            required=False
    )
    device_type = ObjectVar(
            description="Specify device type - all, if not selected (<i>Optional</i>)",
            model=DeviceType,
            display_field='model',
            required=False
    )
    device_name = ObjectVar(
            description="Specify device name (<i>Optional</i>)",
            model=Device,
            display_field='device',
            required=False
    )

    def run(self, data, commit):
        inv=[]
        for device in Device.objects.filter(status='active'):
            if device.primary_ip4_id is not None and str(device.device_type.manufacturer) == 'Juniper Networks':
                host=str(device.primary_ip.address).split('/')[0]
                if data['device_name'] is None:
                    if data['device_type'] is None:
                       #no site name was selected - check all sites
                        if data['site_name'] is None:
                            inv=self.sys_hardware(host,inv)
                        #if site name was selected and match
                        elif data['site_name'] == device.site:
                            inv=self.sys_hardware(host,inv)
                    # device_type was selected
                    elif data['device_type'] == device.device_type:
                        if data['site_name'] is None:
                            inv=self.sys_hardware(host,inv)
                        elif data['site_name'] == device.site:
                            inv=self.sys_hardware(host,inv)
                        else:
                            continue
                # device_name selected
                elif data['device_name'] == device:
                    inv=self.sys_hardware(host,inv)
                else:
                    continue
            else:
                continue
        if inv:
            self.log_success("All done, go to Output tab")
            # add a header to the top of the list 
            inv.insert(0,str("device,name,manufacturer,part_id,serial"))
            return '\n\n'.join(inv)

        else:
            self.log_failure('Nothing found')

    def sys_hardware(self,host,inv):
        dev = Node(host=host, user='username', password='password', normalize=True, hostkey_verify=False)
        dev.open()
        hostname=str(dev.facts['hostname'])
        self.log_info('Connected to {}'.format(hostname))
        rpc = dev.rpc.get_chassis_inventory()
        rpc_xml = etree.tostring(rpc, pretty_print=True, encoding='unicode')
        dev.close()

        xmlparser = jxmlease.Parser()
        result = jxmlease.parse(rpc_xml)
        chassis_type=str(result['chassis-inventory']['chassis']['description'])

        if any('chassis-sub-module' in modules for modules in result['chassis-inventory']['chassis']['chassis-module']):
            for modules in result['chassis-inventory']['chassis']['chassis-module']:
                if re.match(r'Routing Engine \d', str(modules.get('name'))) is None:
                    inv.append(hostname+','+str(modules['model-number']+',Juniper Networks,'+str(modules['part-number'])+','+str(modules['serial-number'])))
                if modules.get('chassis-sub-module'):
                    for submodules in modules.get('chassis-sub-module'):
                        if submodules.get('chassis-sub-sub-module'):
                            for items in submodules.get('chassis-sub-sub-module'):
                                inv.append(hostname+','+str(items['description'])+',Juniper Networks,'+str(items['part-number'])+','+str(items['serial-number']))

                        elif submodules.get('serial-number') and str(submodules.get('serial-number')) != 'BUILTIN':
                            if any(str(submodules.get('serial-number')) in invent for invent in inv):
                                continue
                            else:
                                inv.append(hostname+','+str(submodules['model-number'])+',Juniper Networks,'+str(submodules['part-name'])+','+str(submodules['serial-number']))

        else:
            inv.append(hostname+','+chassis_type+','+str(result['chassis-inventory']['chassis'].get('description'))+','
                    +str(result['chassis-inventory']['chassis'].get('description'))+','
                    +str(result['chassis-inventory']['chassis'].get('serial-number')))
        return(inv)
