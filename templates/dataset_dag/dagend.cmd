{% set filebase %}{{executable|basename}}{{date}}{{uuid}}cluster.$(Cluster).$(Process){% endset %}

{% extends "submit.cmd" %}

{% block universe_exe %}
universe           = vanilla
executable         = samend.sh
arguments          =
transfer_executable = True
{% endblock universe_exe %}

{# dagbegin.cmd has this, should we?
+RUN_ON_HEADNODE= True
#}

{% block queue %}
queue 1
{% endblock %}
