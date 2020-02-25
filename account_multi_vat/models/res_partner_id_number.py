# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartnerIdNumber(models.Model):
    _inherit = "res.partner.id_number"

    @api.constrains("partner_issued_id")
    def _check_partner_issued_id_multi_vat(self):
        partner_id_category_vat = self.env.ref(
            "account_multi_vat.partner_id_category_vat"
        )
        for rec in self:
            if rec.category_id != partner_id_category_vat:
                continue
            if not rec.partner_issued_id:
                raise ValidationError(
                    _("Please specify a tax administration in the 'Issued by' field.")
                )
            if not rec.partner_issued_id.is_tax_administration:
                raise ValidationError(
                    _("The VAT number must be issued by a tax administration.")
                )

    @api.onchange("category_id")
    def _onchange_category_id_multi_vat(self):
        self.ensure_one()
        partner_issued_domain = []
        partner_id_category_vat = self.env.ref(
            "account_multi_vat.partner_id_category_vat"
        )
        if self.category_id == partner_id_category_vat:
            partner_issued_domain.append(("is_tax_administration", "=", True))
        return {"domain": {"partner_issued_id": partner_issued_domain}}
