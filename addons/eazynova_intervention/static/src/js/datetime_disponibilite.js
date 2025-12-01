/** @odoo-module **/

import { registry } from "@web/core/registry"
import { DateTimeField } from "@web/views/fields/datetime/datetime_field"
import { useService } from "@web/core/utils/hooks"
import { _t } from "@web/core/l10n/translation"
import { onMounted, onWillUpdateProps } from "@odoo/owl"

export class DatetimeDisponibiliteField extends DateTimeField {
    setup() {
        super.setup()
        this.orm = useService("orm")
        this.notification = useService("notification")
        this.isUpdating = false

        onMounted(() => {
            this._checkAndProposePremierCreneau()
        })

        onWillUpdateProps(nextProps => {
            if (
                nextProps.record.data.technicien_principal_id !==
                    this.props.record.data.technicien_principal_id ||
                nextProps.record.data.duree_prevue !==
                    this.props.record.data.duree_prevue
            ) {
                this._checkAndProposePremierCreneau(nextProps)
            }
        })
    }

    async onChange(ev) {
        await super.onChange(ev)
        await this._verifierDisponibilite()
    }

    async _checkAndProposePremierCreneau(props = null) {
        const record = props ? props.record : this.props.record
        const technicien = record.data.technicien_principal_id
        const duree = record.data.duree_prevue || 1.0
        const dateActuelle = record.data[this.props.name]

        // Proposer seulement si pas de date et technicien sélectionné
        if (!dateActuelle && technicien && technicien[0]) {
            try {
                const result = await this.orm.call(
                    "intervention.intervention",
                    "get_creneaux_libres_widget",
                    [technicien[0], duree]
                )

                if (result.premier_libre) {
                    this.isUpdating = true
                    await this.props.record.update({
                        [this.props.name]: result.premier_libre,
                    })
                    this.isUpdating = false

                    this.notification.add(
                        _t("Premier créneau libre sélectionné automatiquement"),
                        {
                            type: "info",
                        }
                    )
                }
            } catch (error) {
                console.error(
                    "Erreur lors de la proposition du premier créneau:",
                    error
                )
            }
        }
    }

    async _verifierDisponibilite() {
        if (this.isUpdating) return

        const record = this.props.record
        const technicien = record.data.technicien_principal_id
        const duree = record.data.duree_prevue || 1.0
        const date_prevue = record.data[this.props.name]

        if (!technicien || !technicien[0] || !date_prevue) {
            return
        }

        try {
            const result = await this.orm.call(
                "intervention.intervention",
                "verifier_creneau_disponible",
                [technicien[0], date_prevue, duree]
            )

            if (!result.disponible) {
                this._afficherConflits(result.conflits)

                if (result.creneau_alternatif) {
                    this._proposerCreneauAlternatif(result.creneau_alternatif)
                }
            }
        } catch (error) {
            console.error(
                "Erreur lors de la vérification de disponibilité:",
                error
            )
        }
    }

    _afficherConflits(conflits) {
        let message = _t("⚠️ Conflit détecté sur ce créneau:") + "\n\n"
        conflits.forEach(conflit => {
            message += `• ${conflit.titre}\n  ${conflit.debut} → ${conflit.fin}\n`
        })

        this.notification.add(message, {
            title: _t("Conflit de planning"),
            type: "warning",
            sticky: true,
        })
    }

    _proposerCreneauAlternatif(datetime_str) {
        this.notification.add(_t("Créneau alternatif disponible"), {
            title: _t("Souhaitez-vous utiliser ce créneau libre proche ?"),
            type: "info",
            sticky: true,
            buttons: [
                {
                    name: _t("✓ Utiliser ce créneau"),
                    primary: true,
                    onClick: async () => {
                        this.isUpdating = true
                        await this.props.record.update({
                            [this.props.name]: datetime_str,
                        })
                        this.isUpdating = false
                    },
                },
                {
                    name: _t("✗ Garder ma sélection"),
                    onClick: () => {},
                },
            ],
        })
    }
}

// Enregistrer le widget
registry
    .category("fields")
    .add("datetime_disponibilite", DatetimeDisponibiliteField)
