import Vue from 'vue';
import {
    api_endpoints,
    helpers, fetch_util
}
from '@/utils/hooks';

export const remediationActionStore = {
    namespaced: true,
    state: {
        remediation_action: { },
    },
    getters: {
        remediation_action: state => state.remediation_action,
    },
    mutations: {
        updateRemediationAction(state, remediation_action) {
            console.log('updateRemediationAction');
            state.remediation_action = {
                ...remediation_action
            };
            if (state.remediation_action.due_date) {
                state.remediation_action.due_date = moment(state.remediation_action.due_date, 'YYYY-MM-DD').format('YYYY-MM-DD');
            }

            let remediationActionDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.remediation_action,
                state.remediation_action.id + "/process_default_document/"
                )
            console.log(remediationActionDocumentUrl);
            state.remediation_action.remediationActionDocumentUrl = remediationActionDocumentUrl; 

            let commsLogsDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.remediation_action,
                state.remediation_action.id + "/process_comms_log_document/"
                )
            state.remediation_action.commsLogsDocumentUrl = commsLogsDocumentUrl; 
        },
        updateCanUserAction(state, can_user_action) {
            state.remediation_action.can_user_action = can_user_action;
        },
    },
    actions: {
        async loadRemediationAction({ dispatch, }, { remediation_action_id }) {
            const returnedRemediationAction = await fetch_util.fetchUrl(
                    helpers.add_endpoint_json(
                        api_endpoints.remediation_action, 
                        remediation_action_id)
                    );

            await dispatch("setRemediationAction", returnedRemediationAction);
        },
        async saveRemediationAction({ dispatch, state }) {
            // Construct url endpoint
            let putUrl = helpers.add_endpoint_join(api_endpoints.remediation_action, state.remediation_action.id + '/');

            // Construct payload to store data to be sent
            let payload = {};
            Object.assign(payload, state.remediation_action);

            let savedRemediationAction = await Vue.http.put(putUrl, payload);
        },
        async submitRemediationAction({ dispatch, state }) {
            // Construct url endpoint
            let submitUrl = helpers.add_endpoint_join(api_endpoints.remediation_action, state.remediation_action.id + '/submit/');

            // Construct payload to store data to be sent
            let payload = {};
            Object.assign(payload, state.remediation_action);

            let ret = await Vue.http.post(submitUrl, payload);
            return ret.body;
        },
        setRemediationAction({ commit, }, remediation_action) {
            commit("updateRemediationAction", remediation_action);
        },
        setCanUserAction({ commit, }, can_user_action) {
            commit("updateCanUserAction", can_user_action);
        },
    },
}
