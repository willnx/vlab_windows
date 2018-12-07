# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in vmware.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_windows_api.lib.worker import vmware


class TestVMware(unittest.TestCase):
    """A set of test cases for the vmware.py module"""

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_show_windows(self, fake_vCenter, fake_consume_task, fake_get_info):
        """``show_windows`` returns a dictionary when everything works as expected"""
        fake_vm = MagicMock()
        fake_vm.name = 'win10'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'component' : "Windows",
                                      'created': 1234,
                                      'version': "10",
                                      'configured': False,
                                      'generation': 1,
                                     }

        output = vmware.show_windows(username='alice')
        expected = {'win10': {'component' : "Windows",
                              'created': 1234,
                              'version': "10",
                              'configured': False,
                              'generation': 1,
                             }}

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_windows(self, fake_vCenter, fake_consume_task, fake_power, fake_get_info):
        """``delete_windows`` returns None when everything works as expected"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'win10'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'component' : "Windows",
                                      'created': 1234,
                                      'version': "10",
                                      'configured': False,
                                      'generation': 1,
                                     }

        output = vmware.delete_windows(username='bob', machine_name='win10', logger=fake_logger)
        expected = None

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_windows_value_error(self, fake_vCenter, fake_consume_task, fake_power, fake_get_info):
        """``delete_windows`` raises ValueError when unable to find requested vm for deletion"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'win10'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'component' : "Windows",
                                      'created': 1234,
                                      'version': "10",
                                      'configured': False,
                                      'generation': 1,
                                     }

        with self.assertRaises(ValueError):
            vmware.delete_windows(username='bob', machine_name='myOtherWinBox', logger=fake_logger)

    @patch.object(vmware.virtual_machine, 'set_meta')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_windows(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova, fake_get_info, fake_Ova, fake_set_meta):
        """``create_windows`` returns a dictionary upon success"""
        fake_logger = MagicMock()
        fake_deploy_from_ova.return_value.name = 'win10'
        fake_get_info.return_value = {'worked': True}
        fake_Ova.return_value.networks = ['someLAN']
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}

        output = vmware.create_windows(username='alice',
                                       machine_name='win10',
                                       image='10',
                                       network='someLAN',
                                       logger=fake_logger)
        expected = {'win10': {'worked': True}}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_windows_invalid_network(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova, fake_get_info, fake_Ova):
        """``create_windows`` raises ValueError if supplied with a non-existing network"""
        fake_logger = MagicMock()
        fake_get_info.return_value = {'worked': True}
        fake_Ova.return_value.networks = ['someLAN']
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}

        with self.assertRaises(ValueError):
            vmware.create_windows(username='alice',
                                  machine_name='win10',
                                  image='10',
                                  network='someOtherLAN',
                                  logger=fake_logger)

    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_windows_bad_image(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova, fake_get_info, fake_Ova):
        """``create_windows`` raises ValueError if supplied with a non-existing image/version of Windows to deploy"""
        fake_logger = MagicMock()
        fake_get_info.return_value = {'worked': True}
        fake_Ova.side_effect = FileNotFoundError('testing')
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}

        with self.assertRaises(ValueError):
            vmware.create_windows(username='alice',
                                  machine_name='win10',
                                  image='10',
                                  network='someOtherLAN',
                                  logger=fake_logger)

    @patch.object(vmware.os, 'listdir')
    def test_list_images(self, fake_listdir):
        """``list_images`` - Returns a list of available Windows versions that can be deployed"""
        fake_listdir.return_value = ['Windows-10.ova', 'Windows-8.ova', 'Windows-7.ova']

        output = vmware.list_images()
        expected = ['10', '8', '7']

        # set() avoids ordering issue in test
        self.assertEqual(set(output), set(expected))

    def test_convert_name(self):
        """``convert_name`` - defaults to converting to the OVA file name"""
        output = vmware.convert_name(name='10')
        expected = 'Windows-10.ova'

        self.assertEqual(output, expected)

    def test_convert_name_to_version(self):
        """``convert_name`` - can take a OVA file name, and extract the version from it"""
        output = vmware.convert_name('Windows-10.ova', to_version=True)
        expected = '10'

        self.assertEqual(output, expected)


if __name__ == '__main__':
    unittest.main()
