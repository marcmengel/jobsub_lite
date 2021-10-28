# generated by jobsub_lite 
# {%if debug%}debug{%endif%}
universe           = vanilla
executable         = sambegin.sh
arguments          =

{% set filebase %}{{executable|basename}}{{date}}{{uuid}}cluster.$(Cluster).$(Process){% endset %}
output             = {{filebase}}.out
error              = {{filebase}}.err
log                = {{filebase}}.log
environment        = CLUSTER=$(Cluster);PROCESS=$(Process);CONDOR_TMP={{dir}};BEARER_TOKEN_FILE=.condor_creds/{{group}}.use;CONDOR_EXEC=/tmp;DAGMANJOBID=$(DAGManJobId);GRID_USER={{user}};JOBSUBJOBID=$(CLUSTER).$(PROCESS)@{{schedd}};EXPERIMENT={{group}};{{environment|join(';')}}
rank                  = Mips / 2 + Memory
notification  = Error
+RUN_ON_HEADNODE= True
rank               = Mips / 2 + Memory
job_lease_duration = 3600
notification       = Never
transfer_error     = True
transfer_executable= True
when_to_transfer_output = ON_EXIT_OR_EVICT
transfer_output_files = .empty_file
{%if    cpu %}request_cpus = {{cpu}}{%endif%}
{%if memory %}request_memory = {{memory}}{%endif%}
{%if   disk %}request_disk = {{disk}}KB{%endif%}
{%if     OS %}+DesiredOS={{OS}}{%endif%}
+JobsubClientDN="{{clientdn}}"
+JobsubClientIpAddress="{{ipaddr}}"
+Owner="{{user}}"
+JobsubServerVersion="{{jobsub_version}}"
+JobsubClientVersion="{{jobsub_version}}"
+JobsubClientKerberosPrincipal="{{kerberosprincipal}}"
+JOB_EXPECTED_MAX_LIFETIME = {{expected_lifetime}}
notify_user = {{email_to}}
+AccountingGroup = "group_{{group}}.{{user}}"
+Jobsub_Group="{{group}}"
+JobsubJobId="$(CLUSTER).$(PROCESS)@{{schedd}}"
+Drain = False
{%if blacklist %}
+Blacklist_Sites = "{{blacklist}}"
{% endif %}
+GeneratedBy ="{{version}} {{schedd}}"
{{resource_provides_quoted|join("\n+DESIRED_")}}
{{lines|join("\n+")}}
requirements  = target.machine =!= MachineAttrMachine1 && target.machine =!= MachineAttrMachine2  && (isUndefined(DesiredOS) || stringListsIntersect(toUpper(DesiredOS),IFOS_installed)) && (stringListsIntersect(toUpper(target.HAS_usage_model), toUpper(my.DESIRED_usage_model))) {%if append_condor_requirements %} && {{append_condor_requirements}} {%endif%}

use_oauth_services = {{group}}

queue 1
