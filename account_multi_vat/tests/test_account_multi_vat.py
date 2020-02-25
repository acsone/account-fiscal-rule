# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestAccountMultiVat(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountMultiVat, cls).setUpClass()

        # MODELS
        cls.partner_model = cls.env["res.partner"]
        cls.partner_id_category_model = cls.env["res.partner.id_category"]
        cls.partner_id_number_model = cls.env["res.partner.id_number"]

        # INSTANCES
        cls.partner_01 = cls.partner_model.search([("vat", "=", False)], limit=1)
        cls.valid_vat = "LU11180925"
        cls.invalid_vat = "LU11180924"
        cls.valid_vat_be = "BE0477472701"
        cls.country_lu = cls.env.ref("base.lu")
        cls.country_be = cls.env.ref("base.be")
        cls.vat_partner_lu = cls.partner_model.create(
            {
                "name": "LU Tax Administration",
                "is_tax_administration": True,
                "country_id": cls.country_lu.id,
            }
        )
        cls.vat_partner_be = cls.partner_model.create(
            {
                "name": "BE Tax Administration",
                "is_tax_administration": True,
                "country_id": cls.country_be.id,
            }
        )
        cls.partner_id_category_vat = cls.env.ref(
            "account_multi_vat.partner_id_category_vat"
        )
        cls.partner_id_category_dummy = cls.partner_id_category_model.create(
            {
                "name": "Dummy ID category",
                "code": "TEST",
                "validation_code": "failed = False",
            }
        )

    def test_01(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set an invalid VAT number on the partner, via partner identification
            - partner_issued_id is set and is a tax administration
        Expected result:
            - ValidationError is raised
        """
        self.assertFalse(self.partner_01.has_vat)
        with self.assertRaises(ValidationError):
            self.partner_01.id_numbers = [
                (
                    0,
                    0,
                    {
                        "name": self.invalid_vat,
                        "category_id": self.partner_id_category_vat.id,
                        "partner_issued_id": self.vat_partner_lu.id,
                    },
                )
            ]

    def test_02(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set an valid VAT number on the partner, via partner identification
            - partner_issued_id is set and is a tax administration
        Expected result:
            - The VAT number is correctly set
            - has_vat is True on the partner
        """
        self.partner_01.id_numbers = [
            (
                0,
                0,
                {
                    "name": self.valid_vat,
                    "category_id": self.partner_id_category_vat.id,
                    "partner_issued_id": self.vat_partner_lu.id,
                },
            )
        ]
        self.assertEqual(self.partner_01.id_numbers.name, self.valid_vat)
        self.assertTrue(self.partner_01.has_vat)

    def test_03(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set an valid VAT number on the partner, via partner identification
            - partner_issued_id is set and is not a tax administration
        Expected result:
            - ValidationError is raised
        """
        self.vat_partner_lu.is_tax_administration = False
        with self.assertRaises(ValidationError):
            self.partner_01.id_numbers = [
                (
                    0,
                    0,
                    {
                        "name": self.valid_vat,
                        "category_id": self.partner_id_category_vat.id,
                        "partner_issued_id": self.vat_partner_lu.id,
                    },
                )
            ]

    def test_04(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set an valid VAT number on the partner, via partner identification
            - no partner_issued_id is set
        Expected result:
            - ValidationError is raised
        """
        with self.assertRaises(ValidationError):
            self.partner_01.id_numbers = [
                (
                    0,
                    0,
                    {
                        "name": self.valid_vat,
                        "category_id": self.partner_id_category_vat.id,
                        "partner_issued_id": False,
                    },
                )
            ]

    def test_05(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set a dummy identification category
            - Set a dummy identification value, via partner identification
            - no partner_issued_id is set
        Expected result:
            - The value is correctly set
            - has_vat is False on the partner
        """
        self.partner_01.id_numbers = [
            (
                0,
                0,
                {
                    "name": self.invalid_vat,
                    "category_id": self.partner_id_category_dummy.id,
                    "partner_issued_id": False,
                },
            )
        ]
        self.assertEqual(self.partner_01.id_numbers.name, self.invalid_vat)
        self.assertFalse(self.partner_01.has_vat)

    def test_06(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Create a new partner identification number with VAT category
        Expected result:
            - The domain on the partner_issued_id must show only tax administrations
        """
        new_vat_partner_identification = self.partner_id_number_model.new(
            {"category_id": self.partner_id_category_vat.id}
        )
        onchange_res = new_vat_partner_identification._onchange_category_id_multi_vat()
        onchange_domain = onchange_res.get("domain", {}).get("partner_issued_id", [])
        domain_res = self.partner_model.search(onchange_domain)
        self.assertEqual(len(domain_res), 2)
        self.assertIn(self.vat_partner_be, domain_res)
        self.assertIn(self.vat_partner_lu, domain_res)

    def test_07(self):
        """
        Data:
            - A partner with a two VAT numbers set via partner identification
              (LU and BE)
        Test case:
            1. Search the VAT number for BE
            2. Search the VAT number for LU
            3. Search the VAT number for another country
        Expected result:
            1. BE VAT number is returned
            1. LU VAT number is returned
            1. No VAT number is returned
        """
        self.partner_01.id_numbers = [
            (
                0,
                0,
                {
                    "name": self.valid_vat,
                    "category_id": self.partner_id_category_vat.id,
                    "partner_issued_id": self.vat_partner_lu.id,
                },
            ),
            (
                0,
                0,
                {
                    "name": self.valid_vat_be,
                    "category_id": self.partner_id_category_vat.id,
                    "partner_issued_id": self.vat_partner_be.id,
                },
            ),
        ]
        lu_vat_number = self.partner_01._get_vat_number_for_administration(
            self.vat_partner_lu
        )
        be_vat_number = self.partner_01._get_vat_number_for_administration(
            self.vat_partner_be
        )
        no_vat_number = self.partner_01._get_vat_number_for_administration()
        self.assertEqual(lu_vat_number, self.valid_vat)
        self.assertEqual(be_vat_number, self.valid_vat_be)
        self.assertFalse(no_vat_number)

    def test_08(self):
        """
        Data:
            - A tax administration partner for BE
        Test case:
            - Try to create a tax administration partner for the same country
        Expected result:
            - ValidationError is raised
        """
        with self.assertRaises(ValidationError):
            self.partner_model.create(
                {
                    "name": "LU Tax Administration duplicate",
                    "is_tax_administration": True,
                    "country_id": self.country_lu.id,
                }
            )
