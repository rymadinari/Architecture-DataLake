# Variables d'environnement du TP Jour 2
# Utilisation : source ingestion/scripts/env-j2.sh
# (installation dans ~/opt car pas de droits sudo sur le poste)

export JAVA_HOME_HADOOP=$HOME/opt/jdk-17
export JAVA_HOME_NIFI=$HOME/opt/jdk-21

export HADOOP_HOME=$HOME/opt/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export NIFI_HOME=$HOME/opt/nifi

# Par défaut le terminal utilise Java 17 (pour Hadoop)
export JAVA_HOME=$JAVA_HOME_HADOOP
export PATH=$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH

# Dossiers locaux utilisés par NiFi
export NIFI_DATA=$HOME/nifi-data
