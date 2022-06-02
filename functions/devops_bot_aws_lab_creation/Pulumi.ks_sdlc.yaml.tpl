config:
  app:instance_size: c5.xlarge
  app:root_size: {{ root_size }}
  app:kdata_size: {{ kdata }}
  app:local_size: {{ local }}
  db:binlog_size: {{ binlog }}
  db:data1_size: {{ data1 }}
  db:data2_size: {{ data2 }}
  db:root_size: {{ db_root_size }}
  db:instance_size: r5.xlarge
  db:tmp_size: 20
  db:tmpdb_size: {{ tmpdb }}
  ks:id: {{ ks_name }}
  {% if source_ks_id is defined %}
  ks:source_mysql_ks: ks{{ source_ks_id }}
  {% endif %}
  ks:tags:
    Email: {{ email }}
    User: {{ user_slack_id }}
  registration:krem: {{ is_memsql }}
