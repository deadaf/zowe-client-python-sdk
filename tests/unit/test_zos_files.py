"""Unit tests for the Zowe Python SDK z/OS Files package."""
from unittest import TestCase, mock
from zowe.zos_files_for_zowe_sdk import Files, exceptions


class TestFilesClass(TestCase):
    """File class unit tests."""

    def setUp(self):
        """Setup fixtures for File class."""
        self.test_profile = {"host": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Files class."""
        files = Files(self.test_profile)
        self.assertIsInstance(files, Files)

    @mock.patch('requests.Session.send')
    def test_delete_uss(self, mock_send_request):
        """Test deleting a directory recursively sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_uss("filepath_name", recursive=True)
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_create_zFS_file_system(self, mock_send_request):
        """Test creating a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).create_zFS_file_system("file_system_name", {"perms":100, "cylsPri": 16777213, "cylsSec": 16777215})
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_delete_zFS_file_system(self, mock_send_request):
        """Test deleting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_zFS_file_system("file_system_name")
        mock_send_request.assert_called_once()
    
    def test_invalid_permission(self):
        """Test that the correct exception is raised when an invalid permission option is provided"""
        with self.assertRaises(exceptions.InvalidPermsOption) as e_info:
            Files(self.test_profile).create_zFS_file_system("file_system_name", {"perms": -1, "cylsPri": 16777213, "cylsSec": 16777215})
        self.assertEqual(str(e_info.exception), "Invalid zos-files create command 'perms' option: -1")

    def test_invalid_memory_allocation(self):
        """Test that the correct exception is raised when an invalid memory allocation option is provided"""
        with self.assertRaises(exceptions.MaxAllocationQuantityExceeded) as e_info:
            Files(self.test_profile).create_zFS_file_system("file_system_name", {"perms": 775, "cylsPri": 1677755513, "cylsSec": 16777215})
        self.assertEqual(str(e_info.exception), "Maximum allocation quantity of 16777215 exceeded")
    
    @mock.patch('requests.Session.send')
    def test_mount_zFS_file_system(self, mock_send_request):
        """Test mounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).mount_file_system("file_system_name", "mount_point")
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_unmount_zFS_file_system(self, mock_send_request):
        """Test unmounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).unmount_file_system("file_system_name")
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_list_zFS_file_system(self, mock_send_request):
        """Test unmounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).list_unix_file_systems("file_system_name")
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_rename_dataset(self, mock_send_request):
        """Test renaming dataset sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).rename_dataset("MY.OLD.DSN", "MY.NEW.DSN")
        mock_send_request.assert_called_once()

    def test_rename_dataset_parametrized(self):
        "Test renaming a dataset with different values."
        test_values = [
            (('DSN.OLD', "DSN.NEW"), True),
            (('DS.NAME.CURRENT', "DS.NAME.NEW"), True),
            (('MY.OLD.DSN', "MY.NEW.DSN"), True),
        ]

        files_test_profile = Files(self.test_profile)
        
        for test_case in test_values:
            files_test_profile.request_handler.perform_request = mock.Mock()

            data = {
                "request": "rename",
                "from-dataset": {
                    "dsn": test_case[0][0].strip(),
                }
            }

            files_test_profile.rename_dataset(test_case[0][0], test_case[0][1])

            custom_args = files_test_profile._create_custom_request_arguments()
            custom_args["json"] = data
            custom_args["url"] = "https://https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0][1])
            files_test_profile.request_handler.perform_request.assert_called_once_with("PUT", custom_args, expected_code=[200])

    @mock.patch('requests.Session.send')
    def test_rename_dataset_member(self, mock_send_request):
        """Test renaming dataset member sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).rename_dataset_member("MY.DS.NAME", "MEMBEROLD", "MEMBERNEW")
        mock_send_request.assert_called_once()

    def test_rename_dataset_member_raises_exception(self):
        """Test renaming a dataset member raises error when assigning invalid values to enq parameter."""
        with self.assertRaises(ValueError) as e_info:
            Files(self.test_profile).rename_dataset_member("MY.DS.NAME", "MEMBER1", "MEMBER1N", "RANDOM")

        self.assertEqual(str(e_info.exception), "Invalid value for enq.")

    def test_rename_dataset_member_parametrized(self):
        "Test renaming a dataset member with different values."
        test_values = [
            (('DSN', "MBROLD", "MBRNEW", "EXCLU"), True),
            (('DSN', "MBROLD", "MBRNEW", "SHRW"), True),
            (('DSN', "MBROLD", "MBRNEW", "INVALID"), False),
            (('DATA.SET.NAME', 'MEMBEROLD', 'MEMBERNEW'), True),
            (('DS.NAME', "MONAME", "MNNAME"), True),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.request_handler.perform_request = mock.Mock()

            data = {
                "request": "rename",
                "from-dataset": {
                    "dsn": test_case[0][0].strip(),
                    "member": test_case[0][1].strip(),
                }
            }

            if len(test_case[0]) > 3:
                data["from-dataset"]["enq"] = test_case[0][3].strip()
            if test_case[1]:
                files_test_profile.rename_dataset_member(*test_case[0])
                custom_args = files_test_profile._create_custom_request_arguments()
                custom_args["json"] = data
                custom_args["url"] = "https://https://mock-url.com:443/zosmf/restfiles/ds/{}({})".format(test_case[0][0], test_case[0][2])
                files_test_profile.request_handler.perform_request.assert_called_once_with("PUT", custom_args, expected_code=[200])
            else:
                with self.assertRaises(ValueError) as e_info:
                    files_test_profile.rename_dataset_member(*test_case[0])
                self.assertEqual(str(e_info.exception), "Invalid value for enq.")

    def test_create_data_set_raises_error_without_required_arguments(self):
        """Not providing required arguments should raise error."""
        with self.assertRaises(KeyError):
            obj = Files(self.test_profile).create_data_set("DSNAME123", options={
                "alcunit": "CYL",
                "dsorg": "PO",
                "recfm": "FB",
                "blksize": 6160,
                "dirblk": 25
            })

    def test_create_default_data_set_raises_error_for_unsupported_types(self):
        """Attempting to create a data set that is not part of the suggested list should raise error."""
        with self.assertRaises(exceptions.UnsupportedDefaultDataSetRequested) as e_info:
            obj = Files(self.test_profile).create_default_data_set("DSNAME123", "unsuporrted_type")
        
        expected = "Invalid request. The following default options are available: partitioned, sequential, classic, c, binary."
        self.assertEqual(str(e_info.exception), expected)

    @mock.patch('requests.Session.send')
    def test_create_default_dataset_with_partitioned_type(self, mock_send_request):
        """Test creating a partitioned data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).create_default_data_set("dataset_name", "partitioned")
        mock_send_request.assert_called_once()
