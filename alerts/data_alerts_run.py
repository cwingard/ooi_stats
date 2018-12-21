#!/usr/bin/env python

import alerts.data_alerts_functions as af
import netrc

nrc = netrc.netrc()
api_key, username, api_token = nrc.authenticators('ooinet.oceanobservatories.org')

# arrays = ['RS','CE','CP','GA','GI','GP','GS']
arrays = ['CE']

ca_recipients = ['']
ea_recipients = [username]
cgsn_recipients = ['']

global_ranges = af.request_gr(api_key, api_token)

for array in arrays:
    param_most_recent, stream_most_recent, method_most_recent, refdes_most_recent = af.get_most_recent(array)

    alert_deployment_data = af.alert_request_deployments(array, api_key, api_token)

    not_operational = af.request_annotations(array, api_key, api_token)

    request_urls, request_inputs = af.alert_build_requests(array, alert_deployment_data)

    missing_gr_qc_values, missing_science_classification = af.check_sci_v_gr(array, global_ranges, request_inputs)

    ooi_parameter_data_gr = af.send_gr_data_requests(request_urls, global_ranges, api_key, api_token)

    param_final, stream_final, method_final, refdes_final = af.alert_create_all_outputs(ooi_parameter_data_gr,
                                                                                        request_inputs)

    param_final_out, stream_final_out, \
        method_final_out, refdes_final_out = af.alert_create_missing_output(array, param_final, stream_final,
                                                                            method_final, refdes_final,
                                                                            missing_gr_qc_values)

    no_data_not_annotated, annotated_and_not_operational, data_but_annotated = af.compare_operational(not_operational,
                                                                                                      stream_final_out,
                                                                                                      request_inputs)

    stream_difference_new, stream_difference_resumed = af.stream_compare_output(array, stream_final_out,
                                                                                stream_most_recent, request_inputs)

    param_difference_new, param_difference_resumed = af.parameter_compare_output(param_final_out, param_most_recent,
                                                                                 request_inputs)

    af.alert_send(array,
                  no_data_not_annotated,
                  annotated_and_not_operational,
                  data_but_annotated,
                  stream_difference_new,
                  stream_difference_resumed,
                  param_final_out, 
                  param_difference_new,
                  param_difference_resumed,
                  missing_gr_qc_values, 
                  missing_science_classification,
                  ca_recipients,
                  ea_recipients,
                  cgsn_recipients)
