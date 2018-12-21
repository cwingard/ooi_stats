#!/usr/bin/env python

import alerts.engineering_alerts_functions as af
import netrc

nrc = netrc.netrc()
api_key, username, api_token = nrc.authenticators('ooinet.oceanobservatories.org')

# arrays = ['RS','CE','CP','GA','GI','GP','GS']
arrays = ['CE']

ca_recipients = ['']
ea_recipients = [username]
cgsn_recipients = ['']

for array in arrays:
    stream_most_recent = af.get_most_recent_eng(array)

    alert_deployment_data = af.alert_request_eng_deployments(array, api_key, api_token)

    not_operational = af.request_annotations(array, api_key, api_token)

    request_urls, request_inputs = af.alert_build_eng_requests(array, alert_deployment_data)

    eng_streams_data = af.send_eng_data_requests(array, request_urls, api_key, api_token)

    stream_final = af.alert_create_eng_outputs(eng_streams_data, request_inputs)

    stream_final_out = af.alert_create_missing_output(array, stream_final)

    no_data_not_annotated, annotated_and_not_operational, data_but_annotated = af.compare_operational(not_operational,
                                                                                                      stream_final_out,
                                                                                                      request_inputs)

    stream_difference_new, stream_difference_resumed = af.stream_compare_output(array, stream_final_out,
                                                                                stream_most_recent, request_inputs)

    af.alert_send(array, no_data_not_annotated, annotated_and_not_operational, data_but_annotated,
                  stream_difference_new, stream_difference_resumed, ca_recipients, ea_recipients, cgsn_recipients)
