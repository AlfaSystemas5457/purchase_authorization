from odoo import models, fields
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    authorization_state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("requested", "Autorización Solicitada"),
            ("authorized", "Autorizado"),
            ("rejected", "Rechazado"),
        ],
        string="Estado de Autorización",
        default="draft",
        tracking=True,
        copy=False,
    )

    authorization_requested_by = fields.Many2one(
        "res.users", string="Solicitado Por", readonly=True, copy=False
    )
    authorization_date = fields.Datetime(
        string="Fecha de Autorización", readonly=True, copy=False
    )
    authorized_by = fields.Many2one(
        "res.users", string="Autorizado Por", readonly=True, copy=False
    )
    rejection_reason = fields.Html(
        string="Motivo de Rechazo", readonly=True, copy=False
    )

    def button_request_authorization(self):
        self.ensure_one()
        if self.authorization_state != "draft":
            raise UserError("La autorización ya ha sido solicitada para esta orden.")

        authorizers = self.env["res.users"].search(
            [("can_authorize_purchase", "=", True)]
        )
        if not authorizers:
            raise UserError(
                "No hay usuarios configurados para autorizar compras. Contacte a un administrador."
            )

        self.write(
            {
                "authorization_state": "requested",
                "authorization_requested_by": self.env.user.id,
            }
        )

        for user in authorizers:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=user.id,
                summary=f"Autorizar Orden de Compra {self.name}",
                note=f"La orden de compra {self.name} de {self.partner_id.display_name} requiere autorización.\nTotal: {self.amount_total}",
            )

        self.message_post(
            body=f"Autorización solicitada para {self.name}. Notificación enviada a los autorizadores.",
            partner_ids=authorizers.mapped("partner_id").ids,
            message_type="notification",
            subtype_xmlid="mail.mt_comment",
        )

    def button_authorize(self):
        self.ensure_one()
        if self.authorization_state != "requested":
            raise UserError("No se ha solicitado autorización para esta orden.")

        self.write(
            {
                "authorization_state": "authorized",
                "authorization_date": fields.Datetime.now(),
                "authorized_by": self.env.user.id,
            }
        )

        activities = self.activity_ids
        if activities:
            activities.action_done()

        if self.state in ("draft", "sent"):
            self.button_confirm()

        self.message_post(
            body=f"Orden de compra {self.name} ha sido autorizada por {self.env.user.display_name}.",
            message_type="notification",
            subtype_xmlid="mail.mt_comment",
        )

    def button_reject(self):
        self.ensure_one()
        if self.authorization_state != "requested":
            raise UserError("No se ha solicitado autorización para esta orden.")

        return {
            "type": "ir.actions.act_window",
            "name": "Rechazar Autorización",
            "res_model": "purchase.authorization.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_id": self.id},
        }
