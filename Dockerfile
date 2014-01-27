FROM naccc/java7

ENV JAVA_HOME /usr/lib/jvm/java-7-oracle

EXPOSE 8080
EXPOSE 7918

RUN mkdir /opt/ibm-ucd-install

ADD ibm-ucd-install /opt/ibm-ucd-install

RUN chmod +x /opt/ibm-ucd-install/install-server.sh

RUN /opt/ibm-ucd-install/install-server.sh

#RUN /bin/bash /opt/udeploy/servers/1/bin/server start

ENTRYPOINT ["/bin/bash", "/opt/udeploy/servers/1/bin/server", "start"]
