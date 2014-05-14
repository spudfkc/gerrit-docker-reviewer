FROM spudfkc/java7

# TODO - bundle agent

# JAVA_HOME needed for IBM-UCD install
ENV JAVA_HOME /usr/lib/jvm/java-7-oracle

# Expose HTTP port for web UI
EXPOSE 8080

# Expose JMS port for agent connection
EXPOSE 7918

# Add install files to the Docker container
RUN mkdir -p /opt/temp/ibm-ucd-install/
ADD ibm-ucd-install /opt/temp/ibm-ucd-install/

# Install IBM-UCD server
RUN chmod +x /opt/temp/ibm-ucd-install/install-server.sh
RUN /opt/temp/ibm-ucd-install/install-server.sh
RUN rm -rf /opt/temp/

# Set entrypoint for server start
ENTRYPOINT ["/bin/sh", "/opt/ibm-ucd/server/bin/server"]
CMD ["--help"]
