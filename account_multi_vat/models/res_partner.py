# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_tax_administration = fields.Boolean(string="Tax administration", default=False)
    is_multi_vat = fields.Boolean(
        compute="_compute_is_multi_vat", readonly=True, store=False
    )

    def _compute_is_multi_vat(self):
        partner_id_vat_category = self.env.ref(
            "account_multi_vat.partner_id_category_vat"
        )
        for rec in self:
            if not self.id_numbers:
                rec.is_multi_vat = False
                continue
            rec.is_multi_vat = any(
                n.category_id == partner_id_vat_category for n in self.id_numbers
            )

    def _get_vat_number_for_administration(self, administration_partner=None):
        self.ensure_one()
        if not administration_partner:
            administration_partner = self.env.company.partner_id
        partner_id_vat_category = self.env.ref(
            "account_multi_vat.partner_id_category_vat"
        )
        id_number = self.id_numbers.filtered(
            lambda n: n.category_id == partner_id_vat_category
            and n.partner_issued_id == administration_partner
        )
        res = id_number and id_number.name
        return res or self.vat
