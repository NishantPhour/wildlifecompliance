import Vue from 'vue';
import {
    api_endpoints,
    helpers, fetch
}
from '@/utils/hooks';

export const sanctionOutcomeStore = {
    namespaced: true,
    state: {
        sanction_outcome: {
            user_is_assignee: false,
            user_in_group: false,
        },
    },
    getters: {
        sanction_outcome: state => state.sanction_outcome,
    },
    mutations: {
        updateRemediationAction(state, remediation_action){
            console.log('updateRemediationAction');
            for (let i=0; i<state.sanction_outcome.remediation_actions.length; i++){
                if (state.sanction_outcome.remediation_actions[i].id == remediation_action.id){
                    state.sanction_outcome.remediation_actions[i] = remediation_action;
                }
            }
        },
        updateSanctionOutcome(state, sanction_outcome) {
            state.sanction_outcome = {
                ...sanction_outcome
            };
            if (state.sanction_outcome.date_of_issue) {
                state.sanction_outcome.date_of_issue = moment(state.sanction_outcome.date_of_issue, 'YYYY-MM-DD').format('YYYY-MM-DD');
            }
            if (state.sanction_outcome.time_of_issue) {
                state.sanction_outcome.time_of_issue = moment(state.sanction_outcome.time_of_issue, 'HH:mm:ss').format('LT');
            }
            let sanctionOutcomeDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.sanction_outcome,
                state.sanction_outcome.id + "/process_default_document/"
                )
            state.sanction_outcome.sanctionOutcomeDocumentUrl = sanctionOutcomeDocumentUrl; 

            let commsLogsDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.sanction_outcome,
                state.sanction_outcome.id + "/process_comms_log_document/"
                )
            state.sanction_outcome.commsLogsDocumentUrl = commsLogsDocumentUrl; 
        },
        updateAssignedToId(state, assigned_to_id) {
            state.sanction_outcome.assigned_to_id = assigned_to_id;
        },
        updateCanUserAction(state, can_user_action) {
            state.sanction_outcome.can_user_action = can_user_action;
        },
        updateRelatedItems(state, related_items) {
            state.sanction_outcome.related_items = related_items;
        },
        updateRegistrationHolder(state, data) {
            if (data.data_type === 'individual') {
                state.sanction_outcome.registration_holder_id = data.id;
            }
        },
        updateDriver(state, data) {
            if (data.data_type === 'individual') {
                state.sanction_outcome.driver_id = data.id;
            }
        },
    },
    actions: {
        async loadRemediationAction({ dispatch, }, { remediation_action_id }){
            const returned = await fetch.fetchUrl(
                helpers.add_endpoint_json(
                    api_endpoints.remediation_action, 
                    remediation_action_id)
                );
            console.log(returned);

            await dispatch("setRemediationAction", returned.body);
        },
        async loadSanctionOutcome({ dispatch, }, { sanction_outcome_id }) {
            try {
                const returnedSanctionOutcome = await fetch.fetchUrl(
                    helpers.add_endpoint_json(
                        api_endpoints.sanction_outcome, 
                        sanction_outcome_id)
                    );
                console.log(returnedSanctionOutcome);

                await dispatch("setSanctionOutcome", returnedSanctionOutcome.body);
            } catch (err) {
                console.log(err);
            }
        },
        setRegistrationHolder({ commit, }, data) {
            commit("updateRegistrationHolder", data);
        },
        setDriver({ commit, }, data) {
            commit("updateDriver", data);
        },
        async saveSanctionOutcome({ dispatch, state }) {
            console.log('saveSanctionOutcome');
            // Construct url endpoint
            let putUrl = helpers.add_endpoint_join(api_endpoints.sanction_outcome, state.sanction_outcome.id + '/');

            // Construct payload to store data to be sent
            let payload = {};
            Object.assign(payload, state.sanction_outcome);

            if(payload.date_of_issue){
                payload.date_of_issue = moment(payload.date_of_issue, "DD/MM/YYYY").format("YYYY-MM-DD");
            }
            if(payload.time_of_issue){
                payload.time_of_issue = moment(payload.time_of_issue, "LT").format("HH:mm");
            }

            // format 'type'
            payload.type = payload.type.id;

            console.log('payload');
            console.log(payload);
            let savedSanctionOutcome = await Vue.http.put(putUrl, payload);

            // Update sanction outcome in the vuex store
            await dispatch("setSanctionOutcome", savedSanctionOutcome.body);

            // Return the saved data just in case needed
            return savedSanctionOutcome;
        },
        setSanctionOutcome({ commit, }, sanction_outcome) {
            commit("updateSanctionOutcome", sanction_outcome);
        },
        setRemediationAction({ commit, }, remediation_action) {
            commit("updateRemediationAction", remediation_action);
        },
        setAssignedToId({ commit, }, assigned_to_id) {
            commit("updateAssignedToId", assigned_to_id);
        },
        setCanUserAction({ commit, }, can_user_action) {
            commit("updateCanUserAction", can_user_action);
        },
        setRelatedItems({ commit }, related_items ) {
            commit("updateRelatedItems", related_items);
        },
    },
}
