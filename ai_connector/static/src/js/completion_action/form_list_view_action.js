/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { ActionMenus, ACTIONS_GROUP_NUMBER } from "@web/search/action_menus/action_menus";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";


export class RunCompletion extends Component {
    static template = "ai_connector.RunCompletion";
    static props = ["title", "completion_id", "menu"];

    static components = { DropdownItem };

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
    }

    async runCompletion() {
        await this.orm.call("ai.completion", "run_completion",
            [this.props.completion_id, this.props.menu.props.getActiveIds()]);

        this.action.doAction({
            type: "ir.actions.client",
            tag: "soft_reload"
        });
    }
}

RunCompletion.template = 'ai_connector.RunCompletion';

patch(ActionMenus.prototype, 'ai_connector.ActionMenus', {

    async setActionItems(props) {

        const items = await this._super(...arguments);
        if ('registryItems' in props) {
            return items;
        }
        if (!('getActiveIds' in props)) {
            return items;
        }

        const results = await this.orm.call("ai.completion", "get_model_completions", [this.props.resModel]);
        for (const i in results) {
            const res = results[i];
            items.push({
                RunCompletion,
                Component: RunCompletion,
                groupNumber: ACTIONS_GROUP_NUMBER,
                key: `run-completion-${res['id']}`,
                description: _t(res['name']),
                props: {
                    menu: this,
                    title: _t(res['name']),
                    completion_id: res['id'],
                },
            });
        }
        return items;

    },

})
