/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class AIAssistantWidget extends Component {
    static template = "ai_assistant.Widget";

    async generateContent(prompt) {
        // Appeler le service IA via RPC
        const result = await this.env.services.rpc({
            model: 'ai.service',
            method: 'generate_text',
            args: [prompt],
        });
        return result;
    }

    async generateImage(prompt) {
        const result = await this.env.services.rpc({
            model: 'ai.service',
            method: 'generate_image',
            args: [prompt],
        });
        return result;
    }
}

registry.category("fields").add("ai_assistant", AIAssistantWidget);
