import unittest


class TestDetector(unittest.TestCase):
    def setUp(self):
        self.urls = [
            ["Computer_A", "https://runtime-00.cargocult.tech:7601"],
            ["Computer_B", "https://runtime-01.cargocult.tech:7601"],
            ["Computer_C", "https://runtime-03.cargocult.tech:7601"],
            ["Computer_D", "https://runtime-04.cargocult.tech:7601"],
            ["Computer_E", "https://runtime-05.cargocult.tech:7601"],
        ]
        self.db_client = DbClient(in_memory=True)

    def test_add_new_runtime_instance(self):
        for url in self.urls:
            # Remove the instance first to verify that adding a new instance works
            instance_id = self.db_client.get_instance_id_by_url(url[1])
            self.db_client.remove_runtime_instance_by_id(instance_id)
            ret = self.db_client.add_new_runtime_instance(friendly_name=url[0], url=url[1])
            self.assertEqual(ret, True)
        self.assertEqual(len(self.urls), len(self.db_client.get_runtime_instances()))


if __name__ == "__main__":
    unittest.main()
