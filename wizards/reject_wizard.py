from odoo import models, fields
from odoo.exceptions import UserError


class PurchaseAuthorizationRejectWizard(models.TransientModel):
    _name = "purchase.authorization.reject.wizard"
    _description = "Asistente para rechazar autorización de orden de compra"

    order_id = fields.Many2one(
        "purchase.order", string="Orden de Compra", required=True, readonly=True
    )
    rejection_reason = fields.Html(string="Motivo de Rechazo", required=True)

    def action_reject(self):
        self.ensure_one()
        order = self.order_id

        if order.authorization_state != "requested":
            raise UserError("La autorización ya ha sido procesada para esta orden.")

        order.write(
            {
                "authorization_state": "rejected",
                "rejection_reason": self.rejection_reason,
                "authorized_by": self.env.user.id,
            }
        )

        activities = order.activity_ids
        if activities:
            activities.action_done()

        order.message_post(
            body=f"Orden de compra {order.name} ha sido rechazada por {self.env.user.display_name}.\nMotivo: {self.rejection_reason}",
            partner_ids=(
                [order.authorization_requested_by.partner_id.id]
                if order.authorization_requested_by
                else []
            ),
            message_type="notification",
            subtype_xmlid="mail.mt_comment",
        )

        return {"type": "ir.actions.act_window_close"}
