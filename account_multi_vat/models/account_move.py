# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    customer_vat = fields.Char(
        string="Customer VAT",
        compute="_compute_customer_vat",
        readonly=False,
        store=True,
    )

    @api.depends("partner_shipping_id")
    def _compute_customer_vat(self):
        for rec in self:
            if not rec.partner_id:
                rec.customer_vat = False
                continue
            country = rec.partner_shipping_id.country_id
            rec.customer_vat = rec.partner_id._get_vat_number_for_country(country)
