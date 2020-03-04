# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = "account.tax"

    vat_partner_id = fields.Many2one(
        string="Tax administration",
        comodel_name="res.partner",
        ondelete="restrict",
        domain=[("is_tax_administration", "=", True)],
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        related=False,
        compute="_compute_country_id",
        store=False,
        readonly=True,
    )

    @api.constrains("vat_partner_id")
    def _check_vat_partner_tags(self):
        repartition_lines = self.mapped("invoice_repartition_line_ids") | self.mapped(
            "refund_repartition_line_ids"
        )
        if any(repartition_line.tag_ids for repartition_line in repartition_lines):
            raise ValidationError(
                _("The country of the tax doesn't match the one of the tax grids.")
            )

    @api.depends("company_id", "vat_partner_id")
    def _compute_country_id(self):
        """
        Country is now a computed field (not related).
        If a Tax administration is set, take its country. Otherwise, fall back on
        standard behavior by taking the country of the company.
        """
        for rec in self:
            country = rec.vat_partner_id.country_id or rec.company_id.country_id
            rec.country_id = country
