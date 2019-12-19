# ===============================================================================
# Copyright 2019 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
import random
from datetime import datetime
import platform
import time
import pyvisa
import serial


class Device:
    _handle = None

    def open(self):
        raise NotImplementedError


class SignalDevice(Device):
    period = 0.01

    def __init__(self):
        if platform.system == 'Windows':
            self.device_id = 'UC-232A'
        else:
            self.device_id = '/dev/tty.UC-232A'

    def open(self):
        try:
            self._handle = serial.Serial(self.device_id)
            return True
        except serial.SerialException:
            pass

    def waitfor(self):
        if self._handle:
            while 1:
                if self._handle.dsr:
                    return True

                time.sleep(self.period)


class MeasurementDevice(Device):
    counter = 0
    starttime = 0
    device_id = 'GPIB0::22::INSTR'

    def reset(self):
        self.counter = 0
        self.starttime = time.time()

    def open(self):
        rm = pyvisa.ResourceManager()
        res = rm.list_resources()
        if self.device_id not in res:
            print('DeviceID={}'.format(self.device_id))
            print('Available Resources={}'.format(res))
        else:
            inst = rm.open_resource(self.device_id)
            return inst

        self._handle = rm.open_resource()

    def configure(self):
        self._handle.write('')
        self._handle.write('')

    def get_measurement(self):
        self.counter += 1

        t = time.time() - self.starttime
        r = self.counter / t
        value = self._read()
        row = [self.counter, t, r, datetime.now().isoformat(), value, self._convert_to_temp(value)]

        return row

    # private
    def _convert_to_temp(self, v):
        return v

    def _read(self):
        try:
            return float(self._handle.query('READ?'))
        except BaseException as e:
            print('failed reading from device, Error:{}'.format(e))
            return random.random()
# ============= EOF =============================================
