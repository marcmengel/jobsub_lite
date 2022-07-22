{% extends "submit.cmd" %}

{% block universe_exe %}
universe           = vanilla
executable         = sambegin.sh
arguments          =
{% endblock universe_exe %}

{% block queue%}
queue 1
{% endblock %}
