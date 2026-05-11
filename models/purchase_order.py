from odoo import models, fields
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(
        selection_add=[
            ("to_approve", "Por aprobar"),
            ("approved", "Aprobado"),
        ]
    )

    authorization_state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("requested", "Solicitado"),
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
        if self.state != "draft":
            raise UserError(
                "La orden debe estar en estado Borrador para solicitar autorización."
            )

        authorizers = self.env["res.users"].search(
            [("can_authorize_purchase", "=", True)]
        )
        if not authorizers:
            raise UserError(
                "No hay usuarios configurados para autorizar compras. Contacte a un administrador."
            )

        self.write(
            {
                "state": "to_approve",
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

    def button_cancel_authorization(self):
        self.ensure_one()
        if self.state != "to_approve":
            raise UserError(
                "No hay una solicitud de autorización activa para cancelar."
            )

        activities = self.activity_ids
        if activities:
            activities.action_done()

        self.write(
            {
                "state": "draft",
                "authorization_state": "draft",
                "authorization_requested_by": False,
            }
        )

        self.message_post(
            body=f"Solicitud de autorización cancelada para {self.name} por {self.env.user.display_name}.",
            message_type="notification",
            subtype_xmlid="mail.mt_comment",
        )

    def button_cancel(self):
        for order in self:
            if order.state == "to_approve":
                activities = order.activity_ids
                if activities:
                    activities.action_done()
                order.write(
                    {
                        "state": "draft",
                        "authorization_state": "draft",
                        "authorization_requested_by": False,
                    }
                )
        return super().button_cancel()

    def button_authorize(self):
        self.ensure_one()
        if self.state != "to_approve":
            raise UserError("No se ha solicitado autorización para esta orden.")

        self.write(
            {
                "state": "approved",
                "authorization_state": "authorized",
                "authorization_date": fields.Datetime.now(),
                "authorized_by": self.env.user.id,
            }
        )

        activities = self.activity_ids
        if activities:
            activities.action_done()

        self.message_post(
            body=f"Orden de compra {self.name} ha sido autorizada por {self.env.user.display_name}.",
            message_type="notification",
            subtype_xmlid="mail.mt_comment",
        )

    def button_reject(self):
        self.ensure_one()
        if self.state != "to_approve":
            raise UserError("No se ha solicitado autorización para esta orden.")

        return {
            "type": "ir.actions.act_window",
            "name": "Rechazar Autorización",
            "res_model": "purchase.authorization.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_id": self.id},
        }

    def button_confirm(self):
        for order in self:
            if order.state == "to_approve":
                raise UserError(
                    "No se puede confirmar una orden pendiente de aprobación."
                )
            if order.state == "approved":
                order.write({"state": "sent"})
        return super().button_confirm()
