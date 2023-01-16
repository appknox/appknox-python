import datetime
import stat
import os
from unittest import TestCase
from unittest import mock
from requests import Response
import tempfile
from appknox.client import Appknox, ApiResource
from appknox.mapper import Organization
from appknox.exceptions import ReportError


class ReportTest(TestCase):
    def setUp(self):
        self.file_id = 100
        self.report_id = 200
        self.report_preferences = {
            "show_api_scan": True,
            "show_manual_scan": True,
            "show_static_scan": True,
            "show_dynamic_scan": True,
            "show_ignored_analyses": True,
            "show_hipaa": {"value": True, "is_inherited": True},
            "show_pcidss": {"value": True, "is_inherited": True},
        }
        with mock.patch.object(Appknox, "get_organizations", self.get_org_list):
            self.ap_client = Appknox(
                access_token="test-access_token", host="https://test.domain.com"
            )

    def get_org_list(self):
        return [Organization(id=1, name="Test Organization")]

    def get_report_list_response(self, *args, **kwargs):
        return {
            "count": 2,
            "next": None,
            "prev": None,
            "results": [
                {
                    "id": self.report_id,
                    "language": "en",
                    "generated_on": "2023-01-04T19:35:34.835213Z",
                    "progress": 100,
                    "rating": "5.50",
                    "preferences": self.report_preferences,
                },
                {
                    "id": self.report_id - 1,
                    "language": "en",
                    "generated_on": "2023-01-03T19:35:34.835213Z",
                    "progress": 100,
                    "rating": "4.50",
                    "preferences": self.report_preferences,
                },
            ],
        }

    def get_report_create_reponse(self, *args, **kwargs):
        return {
            "id": self.report_id + 1,
            "language": "en",
            "generated_on": datetime.datetime.now().isoformat(),
            "progress": 100,
            "rating": "5.50",
            "preferences": self.report_preferences,
        }

    def get_report_summary_csv_url_response(self, *args, **kwargs):
        return {"url": "https:://example.com/api/v2/reports/200?sig=abccba"}

    def get_csv_http_response(self, *args, **kwargs):
        response = Response()
        response._content = b"1,2,3\n1,2,3"
        response._content_consumed = False
        response.status_code = 200
        return response

    def get_report_cannot_be_generated_response(self, *args, **kwargs):
        return {"message": "Report can't be generated"}

    def get_url_expired_response(self, *args, **kwargs):
        response = Response()
        response._content = b'{"detail": "This URL has expired."}'
        response._content_consumed = False
        response.status_code = 403
        return response

    def get_invalid_signature_response(self, *args, **kwargs):
        response = Response()
        response._content = b'{"detail": "Invalid signature."}'
        response._content_consumed = False
        response.status_code = 403
        return response

    def get_empty_list_response(self, *args, **kwargs):
        return {"count": 0, "next": None, "prev": None, "results": []}

    def get_permission_denied_response(self, *args, **kwargs):
        return {"detail": "You do not have permission to perform this action."}

    def get_permission_denied_http_response(self, *args, **kwargs):
        response = Response()
        response._content = (
            b'{"detail": "You do not have permission to perform this action."}'
        )
        response._content_consumed = False
        response.status_code = 403
        return response

    def get_not_found_response(self, *args, **kwargs):
        return {"detail": "Not found."}

    def get_not_found_http_response(self, *args, **kwargs):
        response = Response()
        response._content = b'{"detail": "Not found."}'
        response._content_consumed = False
        response.status_code = 404
        return response

    def test_list_report_returns_all_the_reports(self):
        with mock.patch.object(ApiResource, "get", self.get_report_list_response):
            reports = self.ap_client.list_reports(self.file_id)
            self.assertEqual(reports[0].id, self.report_id)
            self.assertEqual(reports[0].language, "en")
            self.assertEqual(reports[0].generated_on, "2023-01-04T19:35:34.835213Z")
            self.assertEqual(reports[0].progress, 100)
            self.assertEqual(reports[0].rating, "5.50")
            self.assertEqual(reports[1].id, self.report_id - 1)
            self.assertEqual(reports[1].language, "en")
            self.assertEqual(reports[1].generated_on, "2023-01-03T19:35:34.835213Z")
            self.assertEqual(reports[1].progress, 100)
            self.assertEqual(reports[1].rating, "4.50")

    def test_list_report_handles_empty_report_list(self):
        with mock.patch.object(ApiResource, "get", self.get_empty_list_response):
            reports = self.ap_client.list_reports(101)
            self.assertEqual(reports, [])

    def test_list_report_raises_exception_for_permission_denied_response(self):
        with mock.patch.object(ApiResource, "get", self.get_permission_denied_response):
            with self.assertRaises(ReportError, msg="Could not fetch report list"):
                self.ap_client.list_reports(103)

    def test_list_report_raises_exception_for_not_found_response(self):
        with mock.patch.object(ApiResource, "get", self.get_not_found_response):
            with self.assertRaises(ReportError, msg="Could not fetch report list"):
                self.ap_client.list_reports(0)

    def test_create_report_returns_newly_created_report(self):
        with mock.patch.object(ApiResource, "post", self.get_report_create_reponse):
            report = self.ap_client.create_report(self.file_id)
            self.assertEqual(report.id, self.report_id + 1)
            self.assertEqual(report.language, "en")
            self.assertEqual(
                report.generated_on[0:19], datetime.datetime.now().isoformat()[0:19]
            )
            self.assertEqual(report.progress, 100)
            self.assertEqual(report.rating, "5.50")

    def test_create_report_raises_exception_for_report_cannot_be_generated_response(
        self,
    ):
        with mock.patch.object(
            ApiResource, "post", self.get_report_cannot_be_generated_response
        ):
            with self.assertRaises(ReportError, msg="Failed to create a report"):
                self.ap_client.create_report(101)

    def test_create_report_raises_exception_for_permissed_denied_response(self):
        with mock.patch.object(
            ApiResource, "post", self.get_permission_denied_response
        ):
            with self.assertRaises(ReportError, msg="Failed to create a report"):
                self.ap_client.create_report(103)

    def test_create_report_raises_exception_for_not_found_response(self):
        with mock.patch.object(ApiResource, "post", self.get_not_found_response):
            with self.assertRaises(ReportError, msg="Failed to create a report"):
                self.ap_client.create_report(0)

    def test_get_summary_csv_report_url_returns_download_url(self):
        with mock.patch.object(
            ApiResource, "get", self.get_report_summary_csv_url_response
        ):
            csv_url = self.ap_client.get_summary_csv_report_url(self.report_id)
            self.assertEqual(
                csv_url, "https:://example.com/api/v2/reports/200?sig=abccba"
            )

    def test_get_summary_csv_report_url_raises_exception_for_permission_denied_response(
        self,
    ):
        with mock.patch.object(ApiResource, "get", self.get_permission_denied_response):
            with self.assertRaises(ReportError, msg="Failed to get report summary URL"):
                self.ap_client.get_summary_csv_report_url(203)

    def test_get_summary_csv_report_url_raises_exception_for_not_found_response(self):
        with mock.patch.object(ApiResource, "get", self.get_not_found_response):
            with self.assertRaises(ReportError, msg="Failed to get report summary URL"):
                self.ap_client.get_summary_csv_report_url(0)

    def test_download_report_data_returns_bytes_data_with_given_url(self):
        with mock.patch.object(
            ApiResource, "direct_get_http_response", self.get_csv_http_response
        ):
            url = self.get_report_summary_csv_url_response()["url"]
            report_data = self.ap_client.download_report_data(url)
            self.assertEqual(report_data, b"1,2,3\n1,2,3")

    def test_download_report_data_raises_exception_for_url_expired_response(self):
        with mock.patch.object(
            ApiResource, "direct_get_http_response", self.get_url_expired_response
        ):
            with self.assertRaises(ReportError, msg="Could not Download Report Data"):
                url = self.get_report_summary_csv_url_response()["url"]
                self.ap_client.download_report_data(url)

    def test_download_report_data_raises_exception_for_invalid_signature(self):
        with mock.patch.object(
            ApiResource, "direct_get_http_response", self.get_invalid_signature_response
        ):
            with self.assertRaises(ReportError, msg="Could not Download Report Data"):
                url = self.get_report_summary_csv_url_response()["url"] + "123"
                self.ap_client.download_report_data(url)

    def test_download_report_data_raises_exception_for_permission_denied_response(self):
        with mock.patch.object(
            ApiResource,
            "direct_get_http_response",
            self.get_permission_denied_http_response,
        ):
            with self.assertRaises(ReportError, msg="Could not Download Report Data"):
                url = self.get_report_summary_csv_url_response()["url"].replace(
                    "200", "203"
                )
                self.ap_client.download_report_data(url)

    def test_download_report_data_raises_exception_for_not_found_response(self):
        with mock.patch.object(
            ApiResource, "direct_get_http_response", self.get_not_found_http_response
        ):
            with self.assertRaises(ReportError, msg="Could not Download Report Data"):
                url = self.get_report_summary_csv_url_response()["url"].replace(
                    "200", "0"
                )
                self.ap_client.download_report_data(url)

    def test_write_data_to_file_works_if_only_directory_exists(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, "report_summary.csv")
            self.ap_client.write_data_to_file(b"1,2,3", file_path)
            with open(file_path, "rb") as fp:
                bytes = fp.read()
            self.assertEqual(bytes, b"1,2,3")

    def test_write_data_to_file_works_if_both_directory_and_file_exist(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, "report_summary.csv")
            # create the file
            with open(file_path, "wb") as fp:
                pass
            self.ap_client.write_data_to_file(b"1,2,3", file_path)
            with open(file_path, "rb") as fp:
                bytes = fp.read()
            self.assertEqual(bytes, b"1,2,3")

    def test_write_data_to_file_works_if_both_directory_and_file_donot_exist(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, "report_summary", "report_summary.csv")
            self.ap_client.write_data_to_file(b"1,2,3", file_path)
            with open(file_path, "rb") as fp:
                bytes = fp.read()
            self.assertEqual(bytes, b"1,2,3")

    def test_write_data_to_file_works_even_if_the_data_is_empty(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, "report_summary.csv")
            # create the file
            with open(file_path, "wb") as fp:
                pass
            self.ap_client.write_data_to_file(b"", file_path)
            with open(file_path, "rb") as fp:
                bytes = fp.read()
            self.assertEqual(bytes, b"")

    def test_write_data_to_file_raises_exception_if_directory_is_not_writeable(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            report_directory_path = os.path.join(tmpdirname, "report_summary")
            os.makedirs(report_directory_path)
            os.chmod(report_directory_path, stat.S_IREAD)
            file_path = os.path.join(report_directory_path, "report_summary.csv")
            with self.assertRaises(
                ValueError, msg=("Failed to write data to {}".format(file_path))
            ):
                self.ap_client.write_data_to_file(b"1,2,3", file_path)

    def test_write_data_to_file_raises_exception_if_child_dir_creations_not_allowed(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmpdirname:
            report_directory_path = os.path.join(tmpdirname, "report_summary")
            os.makedirs(report_directory_path)
            os.chmod(report_directory_path, stat.S_IREAD)
            file_path = os.path.join(
                report_directory_path, "child_report_dir", "report_summary.csv"
            )
            with self.assertRaises(
                ValueError, msg=("Failed to write data to {}".format(file_path))
            ):
                self.ap_client.write_data_to_file(b"1,2,3", file_path)

    def test_write_data_to_file_raises_exception_if_file_is_not_writeable(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, "report_summary.csv")
            # create the file
            with open(file_path, "wb") as _:
                pass
            os.chmod(file_path, stat.S_IREAD)
            with self.assertRaises(
                ValueError, msg=("Failed to write data to {}".format(file_path))
            ):
                self.ap_client.write_data_to_file(b"1,2,3", file_path)
