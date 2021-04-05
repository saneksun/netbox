#
# This report looks for a custom field named "" and then acts from there
#

from dcim.choices import DeviceStatusChoices
from dcim.models import Device
from extras.reports import Report

class Check_License_for_Device(Report):
    description = "Check if device has license information"

    def test_license_field(self):
        for device in Device.objects.filter(status=DeviceStatusChoices.STATUS_ACTIVE):
            license = device.cf.get("License")
            if license:
                self.log_success(device, license)
            else:
                continue
