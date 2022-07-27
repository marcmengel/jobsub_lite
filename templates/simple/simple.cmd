{% set filebase %}{{executable|basename}}{{date}}{{uuid}}cluster.$(Cluster).$(Process){% endset %}
{%extends "submit.cmd" %}

