from django.utils.text import slugify
import re
from dcim.choices import DeviceStatusChoices, SiteStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from extras.scripts import *

class AllLicensesScript(Script):
    name = "Show licenses values (search by site name, device type, vendor)"
    class Meta:
        description = "Getting license information"
        field_order = ['site_name', 'device_type', 'manufacturer_name', 'comments_field']
        commit_default = False
    site_name = ObjectVar(
            description="Specify site - all, if not selected (<i>Optional</i>)",
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
    manufacturer_name = ObjectVar(
            description="Specify device manufactureir - all, if not selected (<i>Optional</i>)",
            model=Manufacturer,
            display_field='Manufacturer',
            required=False
    )
    comments_field = BooleanVar(
            description="Show information from Comments field?"
    )

    def run(self, data, commit):
        dev=[]
        for device in Device.objects.filter(status='active'):
            if device.custom_field_data.get('License'):
                #if site name selected and match
                if data['site_name'] == device.site:
                    dev=self.get_device_info(data, device, dev)
                #no site name selected - check all sites
                elif data['site_name'] is None:
                    dev=self.get_device_info(data, device, dev)
                else:
                    continue
            else:
                continue
        if dev:
            self.log_success("All done, go to Output tab")
            return '\n\n'.join(dev)
        else:
            self.log_failure('Nothing found')

    def get_device_info (self, data, device, dev):
        if data['device_type']:
            if device.device_type == data['device_type']:
                dev.append(str(device))
                dev.append(str(device.device_type.display_name))
                dev.append(re.sub('\s{2,}', ' \n', str(device.cf.get("License"))))
                if data['comments_field'] is True:
                    dev.append(device.comments)
            else:
                pass
        elif data['manufacturer_name']:
            if device.device_type.manufacturer == data['manufacturer_name']:
                dev.append(str(device))
                dev.append(str(device.device_type.display_name))
                dev.append(re.sub('\s{2,}', ' \n', str(device.cf.get("License"))))
                if data['comments_field'] is True:
                    dev.append(device.comments)
            else:
                pass
        else:
              dev.append(str(device))
              dev.append(str(device.device_type.display_name))
              dev.append(re.sub('\s{2,}', ' \n', str(device.cf.get("License"))))
              if data['comments_field'] is True:
                  dev.append(device.comments)
        return dev
