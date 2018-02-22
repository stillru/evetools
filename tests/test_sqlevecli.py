import unittest
import mock
import sqlite3
import sqlevecli

class TestCreateConnection(unittest.TestCase):
	
	@mock.patch('sqlite3.connect')
	def test_create_connection(self, mock_sqlite3_connect):
		sqlite_execute_mock = mock.Mock()
		mock_sqlite3_connect.return_value = sqlite_execute_mock
		sqlevecli.create_connection('test.db')
		call = 'drop table if exists some_table;'
		sqlite_execute_mock.execute.assert_called_with(call)

class TestSelectAllTasks(unittest.TestCase):
	def test_select_all_tasks(self):
		# self.assertEqual(expected, select_all_tasks(conn))
		assert False # TODO: implement your test here

class TestSelectTaskByPriority(unittest.TestCase):
	def test_select_task_by_priority(self):
		# self.assertEqual(expected, select_task_by_priority(conn, priority))
		assert False # TODO: implement your test here

class TestMain(unittest.TestCase):
	def test_main(self):
		# self.assertEqual(expected, main())
		assert False # TODO: implement your test here

if __name__ == '__main__':
	unittest.main()