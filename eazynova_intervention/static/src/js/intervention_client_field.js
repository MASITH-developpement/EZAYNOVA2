/** @odoo-module **/

import { registry } from "@web/core/registry"
import { Many2OneField } from "@web/views/fields/many2one/many2one_field"
import { useService } from "@web/core/utils/hooks"

/**
 * Widget Many2One personnalisé pour remplir automatiquement l'adresse d'intervention
 */
export class InterventionClientField extends Many2OneField {
    setup() {
        super.setup()
        this.orm = useService("orm")
    }

    /**
     * Surcharge de la méthode de sélection pour déclencher l'action
     */
    async _onSelectionChanged(value) {
        const result = await super._onSelectionChanged(value)

        // Si c'est le champ client_final_id et qu'une valeur est sélectionnée
        if (this.props.name === "client_final_id" && value) {
            await this._updateAdresseIntervention(value[0])
        }

        return result
    }

    /**
     * Met à jour l'adresse d'intervention avec l'adresse du client sélectionné
     */
    async _updateAdresseIntervention(partnerId) {
        try {
            console.log("Mise à jour adresse pour partenaire ID:", partnerId)

            // Récupérer les données du partenaire
            const partnerData = await this.orm.read(
                "res.partner",
                [partnerId],
                ["street", "street2", "city", "zip", "state_id", "country_id"]
            )

            if (partnerData && partnerData.length > 0) {
                const partner = partnerData[0]
                console.log("Données partenaire:", partner)

                // Construire l'adresse complète
                let adresse = ""
                if (partner.street) adresse += partner.street
                if (partner.street2)
                    adresse += (adresse ? ", " : "") + partner.street2
                if (partner.zip) adresse += (adresse ? ", " : "") + partner.zip
                if (partner.city) adresse += (adresse ? " " : "") + partner.city
                if (partner.state_id && partner.state_id[1]) {
                    adresse += (adresse ? ", " : "") + partner.state_id[1]
                }
                if (partner.country_id && partner.country_id[1]) {
                    adresse += (adresse ? ", " : "") + partner.country_id[1]
                }

                console.log("Adresse construite:", adresse)

                // Mettre à jour le champ adresse_intervention
                if (adresse && this.props.record) {
                    await this.props.record.update({
                        adresse_intervention: adresse,
                    })
                    console.log("Adresse mise à jour dans le record")
                }
            }
        } catch (error) {
            console.error(
                "Erreur lors de la récupération de l'adresse du client:",
                error
            )
        }
    }
}

// Enregistrer le widget avec un nom différent pour éviter les conflits
InterventionClientField.template = "web.Many2OneField"
registry
    .category("fields")
    .add("intervention_client_auto", InterventionClientField)
