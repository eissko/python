import unittest
import activedirectory


class TestActiveDirectory(unittest.TestCase):
    def test_is_valid_dn_negative_test(self):
        dn = 'CN=i-*,OU=ou,DC=local,DC=test'
        with self.assertRaises(NameError, msg= f'DN \'{dn}\' is in wrong format'):
            activedirectory.is_valid_dn(dn)

    def test_is_valid_dn_positive_test(self):
        dn = 'CN=computer1,OU=ou,DC=local,DC=test'
        self.assertTrue(activedirectory.is_valid_dn(dn))
            

if __name__ == '__main__':
    unittest.main()