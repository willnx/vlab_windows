# -*- coding: UTF-8 -*-
"""
A suite of tests for the windows object
"""
import unittest
from unittest.mock import patch, MagicMock

import ujson
from flask import Flask
from vlab_api_common import flask_common
from vlab_api_common.http_auth import generate_v2_test_token


from vlab_windows_api.lib.views import windows


class TestWindowsView(unittest.TestCase):
    """A set of test cases for the WindowsView object"""
    @classmethod
    def setUpClass(cls):
        """Runs once for the whole test suite"""
        cls.token = generate_v2_test_token(username='bob')

    @classmethod
    def setUp(cls):
        """Runs before every test case"""
        app = Flask(__name__)
        windows.WindowsView.register(app)
        app.config['TESTING'] = True
        cls.app = app.test_client()
        # Mock Celery
        app.celery_app = MagicMock()
        cls.fake_task = MagicMock()
        cls.fake_task.id = 'asdf-asdf-asdf'
        app.celery_app.send_task.return_value = cls.fake_task

    def test_v1_deprecated(self):
        """WindowsView - GET on /api/1/inf/windows returns an HTTP 404"""
        resp = self.app.get('/api/1/inf/windows',
                            headers={'X-Auth': self.token})

        status = resp.status_code
        expected = 404

        self.assertEqual(status, expected)

    def test_get_task(self):
        """WindowsView - GET on /api/2/inf/windows returns a task-id"""
        resp = self.app.get('/api/2/inf/windows',
                            headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_get_task_link(self):
        """WindowsView - GET on /api/2/inf/windows sets the Link header"""
        resp = self.app.get('/api/2/inf/windows',
                            headers={'X-Auth': self.token})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/windows/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_post_task(self):
        """WindowsView - POST on /api/2/inf/windows returns a task-id"""
        resp = self.app.post('/api/2/inf/windows',
                             headers={'X-Auth': self.token},
                             json={'network': "someLAN",
                                   'name': "myWindowsClient",
                                   'image': '10'})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_post_task_link(self):
        """WindowsView - POST on /api/2/inf/windows sets the Link header"""
        resp = self.app.post('/api/2/inf/windows',
                             headers={'X-Auth': self.token},
                             json={'network': "someLAN",
                                   'name': "myWindowsClient",
                                   'image': '10'})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/windows/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_delete_task(self):
        """WindowsView - DELETE on /api/2/inf/windows returns a task-id"""
        resp = self.app.delete('/api/2/inf/windows',
                               headers={'X-Auth': self.token},
                               json={'name': 'myWindowsClient'})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_delete_task_link(self):
        """WindowsView - DELETE on /api/2/inf/windows sets the Link header"""
        resp = self.app.delete('/api/2/inf/windows',
                               headers={'X-Auth': self.token},
                               json={'name': 'myWindowsClient'})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/windows/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_image(self):
        """WindowsView - GET on the ./image end point returns the a task-id"""
        resp = self.app.get('/api/2/inf/windows/image',
                            headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_image_link(self):
        """WindowsView - GET on the ./image end point sets the Link header"""
        resp = self.app.get('/api/2/inf/windows/image',
                            headers={'X-Auth': self.token})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/windows/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)


if __name__ == '__main__':
    unittest.main()
