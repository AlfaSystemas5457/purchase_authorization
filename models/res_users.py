from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    can_authorize_purchase = fields.Boolean(
        string="Puede Autorizar Compras",
        default=False,
        help="Si está activado, este usuario recibirá solicitudes de autorización de órdenes de compra.",
    )

    def write(self, vals):
        res = super().write(vals)
        if "can_authorize_purchase" in vals:
            group = self.env.ref(
                "purchase_authorization.group_purchase_authorization_manager"
            )
            for user in self:
                if user.can_authorize_purchase:
                    user.sudo().write({"group_ids": [(4, group.id)]})
                else:
                    user.sudo().write({"group_ids": [(3, group.id)]})
        return res

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        group = self.env.ref(
            "purchase_authorization.group_purchase_authorization_manager"
        )
        for user in users:
            if user.can_authorize_purchase:
                user.sudo().write({"groups_id": [(4, group.id)]})
        return users
