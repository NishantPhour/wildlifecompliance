import Vue from 'vue';
import {
    api_endpoints,
    helpers, fetch_util
}
from '@/utils/hooks';
import moment from 'moment';

export const inspectionStore = {
    namespaced: true,
    state: {
        inspection: {
            user_is_assignee: false,
            user_in_group: false,
        },
        
    },
    getters: {
        inspection: state => state.inspection,
        inspection_latitude(state) {
            if (state.inspection.location) {
                if (state.inspection.location.geometry) {
                    if (state.inspection.location.geometry.coordinates.length > 0) {
                        return state.inspection.location.geometry.coordinates[1];
                    } else {return "";}
                } else {return "";}
            } else {return "";}
        },
        inspection_longitude(state) {
            if (state.inspection.location) {
                if (state.inspection.location.geometry) {
                    if (state.inspection.location.geometry.coordinates.length > 0) {
                        return state.inspection.location.geometry.coordinates[0];
                    } else {return "";}
                } else {return "";}
            } else {return "";}
        },
    },
    mutations: {
        updateInspection(state, inspection) {
            state.inspection = {
                ...inspection
            };
            console.log('updateInspection');
            if (!inspection.location) {
                /* When location is null, set default object */
                state.inspection.location =
                    {
                        "type": "Feature",
                        properties: {
                            town_suburb: null,
                            street: null,
                            state: null,
                            postcode: null,
                            country: null,
                        },
                        id: null,
                        geometry: {
                            "type": "Point",
                            "coordinates": [],
                        },
                    }; 
            }
            if (state.inspection.planned_for_date) {
                state.inspection.planned_for_date = moment(state.inspection.planned_for_date, 'YYYY-MM-DD').format('YYYY-MM-DD');
            }
            // format artifact time from 24 to 12 hour
            if (state.inspection.planned_for_time) {
                state.inspection.planned_for_time = moment(state.inspection.planned_for_time, 'HH:mm').format('hh:mm A');
            } else if (state.inspection.planned_for_time === '') {
                state.inspection.planned_for_time = null;
            }

            let inspectionReportDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.inspection,
                state.inspection.id + "/process_inspection_report_document/"
                )
            state.inspection.inspectionReportDocumentUrl = inspectionReportDocumentUrl; 
            let rendererDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.inspection,
                state.inspection.id + "/process_renderer_document/"
                )
            state.inspection.rendererDocumentUrl = rendererDocumentUrl; 
            let commsLogsDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.inspection,
                state.inspection.id + "/process_comms_log_document/"
                )
            state.inspection.commsLogsDocumentUrl = commsLogsDocumentUrl; 
            let createInspectionProcessCommsLogsDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.inspection,
                state.inspection.id + "/create_inspection_process_comms_log_document/"
                )
            state.inspection.createInspectionProcessCommsLogsDocumentUrl = createInspectionProcessCommsLogsDocumentUrl; 
        },
        updatePlannedForTime(state, time) {
            state.inspection.planned_for_time = time;
        },
        updatePartyInspected(state, data) {
            if (data.data_type === 'individual') {
                state.inspection.party_inspected = data.data_type;
                state.inspection.individual_inspected_id = data.id;
                if (state.inspection.organisation_inspected_id) {
                    state.inspection.organisation_inspected_id = null;
                }
            }
            if (data.data_type === 'organisation') {
                state.inspection.party_inspected = data.data_type;
                state.inspection.organisation_inspected_id = data.id;
                if (state.inspection.individual_inspected_id) {
                    state.inspection.individual_inspected_id = null;
                }
            }
        },
        updateRelatedItems(state, related_items) {
            state.inspection.related_items = related_items;
        },
        updateLocationPoint(state, point) {
            state.inspection.location.geometry.coordinates = point;
        },
        updateLocationAddress(state, location_properties) {
            state.inspection.location.properties = location_properties;
        },
        updateLocationAddressEmpty(state) {
            state.inspection.location.properties.town_suburb = "";
            state.inspection.location.properties.street = "";
            state.inspection.location.properties.state = "";
            state.inspection.location.properties.postcode = "";
            state.inspection.location.properties.country = "";
        },
        updateLocationDetailsFieldEmpty(state) {
            state.inspection.location.properties.details = "";
        },
    },
    actions: {
        async loadInspection({ dispatch, commit }, { inspection_id }) {
            try {
                const returnedInspection = await fetch_util.fetchUrl(
                    helpers.add_endpoint_json(
                        api_endpoints.inspection, 
                        inspection_id)
                    );

                /* Set Inspection object */
                await dispatch("setInspection", returnedInspection);

                for (let form_data_record of returnedInspection.data) {
                    await dispatch("setFormValue", {
                        key: form_data_record.field_name,
                        value: {
                            "value": form_data_record.value,
                            "comment_value": form_data_record.comment,
                            "deficiency_value": form_data_record.deficiency,
                        }
                    }, {
                        root: true
                    });
                }

            } catch (err) {
                console.log(err);
            }
        },
        
        async saveInspection({ dispatch, state, rootGetters }, { create, internal }) {
            let inspectionId = null;
            let savedInspection = null;
            var error = false;
            try {
                let payload = new Object();
                Object.assign(payload, state.inspection);
                console.log(payload);
                if (payload.planned_for_date) {
                    payload.planned_for_date = moment(payload.planned_for_date, 'YYYY-MM-DD').format('YYYY-MM-DD');
                } else if (payload.planned_for_date === '') {
                    payload.planned_for_date = null;
                }
                if (payload.planned_for_time) {
                    payload.planned_for_time = moment(payload.planned_for_time, 'hh:mm A').format('HH:mm');
                } else if (payload.planned_for_time === '') {
                    payload.planned_for_time = null;
                }
                // Renderer data
                if (state.inspection.schema) {
                if (state.inspection.schema.length > 0) {
                    payload.renderer_data = rootGetters.renderer_form_data;
                    }
                }

                let fetchUrl = null;
                if (create) {
                    fetchUrl = api_endpoints.inspection;
                    savedInspection = await fetch_util.fetchUrl(fetchUrl,{method:'POST', body:JSON.stringify(payload)});
                } else {
                    // update Inspection
                    fetchUrl = helpers.add_endpoint_join(
                        api_endpoints.inspection,
                        //state.inspection.id + "/inspection_save/"
                        state.inspection.id + '/'
                        )
                    savedInspection = await fetch_util.fetchUrl(fetchUrl,{method:'PUT', body:JSON.stringify(payload)});
                }
                await dispatch("setInspection", savedInspection);
                inspectionId = savedInspection;

            } catch (err) {
                error = true;
                console.log(err);
                if (internal) {
                    // return "There was an error saving the record";
                    return err;
                } else {
                    await swal.fire("Error", "There was an error saving the record", "error");
                }
                //return window.location.href = "/internal/inspection/";
                //console.log(savedInspection);
            } finally {
                // internal arg used when file upload triggers record creation
                if (internal && !error) {
                    console.log("modal file create")
                }
                // update inspection
                else if (!create && !error) {
                    await swal.fire("Saved", "The record has been saved", "success");
                }
                return savedInspection;
            }
        },
        
        setInspection({ commit, }, inspection) {
            commit("updateInspection", inspection);
        },
        setPlannedForTime({ commit }, time ) {
            commit("updatePlannedForTime", time);
        },
        setPartyInspected({ commit, }, data) {
            commit("updatePartyInspected", data);
        },
        setRelatedItems({ commit }, related_items ) {
            commit("updateRelatedItems", related_items);
        },
    },
};
