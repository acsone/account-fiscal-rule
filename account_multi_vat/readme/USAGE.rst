When printing the invoice report, the VAT number will be seeked in the following way:

#. **If there is a fiscal position which has a tax administration:** try to find a VAT number
   matching the tax administration.
#. **If there is no fiscal position on the invoice or no tax administration on
   the fiscal position:** try to find a VAT number matching the country of the company.
#. **If nothing found:** the standard VAT number on the partner is used.
