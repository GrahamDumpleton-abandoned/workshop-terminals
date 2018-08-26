FROM centos/s2i-base-centos7:latest

# Install OpenShift client.

ENV OC_VERSION=3.9.31
RUN curl -s -o /tmp/oc.tar.gz "https://mirror.openshift.com/pub/openshift-v3/clients/$OC_VERSION/linux/oc.tar.gz" && \
    tar -C /usr/local/bin -zxvf /tmp/oc.tar.gz oc && \
    rm /tmp/oc.tar.gz && \
    curl -sL -o /usr/local/bin/odo https://github.com/redhat-developer/odo/releases/download/v0.0.10/odo-linux-amd64 && \
    chmod +x /usr/local/bin/odo

# Common environment variables.

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    PIP_NO_CACHE_DIR=off

# Install Butterfly using system Python 2.7.

RUN HOME=/opt/butterfly && \
    mkdir -p /opt/butterfly && \
    curl -s -o /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    /usr/bin/python /tmp/get-pip.py --user && \
    rm -f /tmp/get-pip.py && \
    $HOME/.local/bin/pip install --no-cache-dir --user virtualenv && \
    $HOME/.local/bin/virtualenv /opt/butterfly && \
    source /opt/butterfly/bin/activate && \
    pip install https://github.com/GrahamDumpleton/butterfly/archive/uri-root-path.zip && \
    ln -s /opt/butterfly/bin/butterfly.server.py /usr/local/bin/ && \
    ln -s /opt/butterfly/bin/butterfly /usr/local/bin/ && \
    mkdir /opt/butterfly/etc && \
    chown -R 1001:0 /opt/butterfly/etc && \
    fix-permissions /opt/butterfly/etc

# Install Python 3.6.

ENV PYTHON_VERSION=3.6
RUN HOME=/root && \
    INSTALL_PKGS="rh-python36 rh-python36-python-devel \
        rh-python36-python-setuptools rh-python36-python-pip nss_wrapper \
        httpd24 httpd24-httpd-devel httpd24-mod_ssl httpd24-mod_auth_kerb \
        httpd24-mod_ldap httpd24-mod_session atlas-devel gcc-gfortran \
        libffi-devel libtool-ltdl enchant" && \
    yum install -y centos-release-scl && \
    yum -y --setopt=tsflags=nodocs install --enablerepo=centosplus $INSTALL_PKGS && \
    rpm -V $INSTALL_PKGS && \
    # Remove centos-logos (httpd dependency) to keep image size smaller.
    rpm -e --nodeps centos-logos && \
    yum -y clean all --enablerepo='*'

# Install Java JDK 8, Maven 3.3, Gradle 2.6.

RUN HOME=/root && \
    INSTALL_PKGS="bc java-1.8.0-openjdk java-1.8.0-openjdk-devel" && \
    yum install -y --enablerepo=centosplus $INSTALL_PKGS && \
    rpm -V $INSTALL_PKGS && \
    yum -y clean all --enablerepo='*'

ENV MAVEN_VERSION 3.3.9
RUN HOME=/root && \
    (curl -0 http://www.eu.apache.org/dist/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz | \
    tar -zx -C /usr/local) && \
    mv /usr/local/apache-maven-$MAVEN_VERSION /usr/local/maven && \
    ln -sf /usr/local/maven/bin/mvn /usr/local/bin/mvn

ENV GRADLE_VERSION 2.6
RUN HOME=/root && \
    curl -sL -0 https://services.gradle.org/distributions/gradle-$GRADLE_VERSION-bin.zip -o /tmp/gradle-$GRADLE_VERSION-bin.zip && \
    unzip /tmp/gradle-$GRADLE_VERSION-bin.zip -d /usr/local/ && \
    rm /tmp/gradle-$GRADLE_VERSION-bin.zip && \
    mv /usr/local/gradle-$GRADLE_VERSION /usr/local/gradle && \
    ln -sf /usr/local/gradle/bin/gradle /usr/local/bin/gradle

COPY settings.xml /opt/app-root/src/.m2/

RUN echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
    chmod g+w /etc/passwd

RUN chown -R 1001:0 /opt/app-root && \
    fix-permissions /opt/app-root

EXPOSE 8080

USER 1001

RUN source scl_source enable rh-python36 && \
    virtualenv /opt/app-root && \
    source /opt/app-root/bin/activate && \
    pip install -U pip setuptools wheel && \
    echo "source scl_source enable httpd24 $NODEJS_SCL rh-python36" >> /opt/app-root/etc/scl_enable && \
    echo "source /opt/app-root/bin/activate" >> /opt/app-root/etc/scl_enable && \
    fix-permissions /opt/app-root

COPY start-butterfly.sh /opt/butterfly/bin/
COPY start-terminal.sh /opt/butterfly/bin/
COPY setup-volume.sh /opt/butterfly/bin/

COPY builder /usr/libexec/s2i

LABEL io.k8s.display-name="Java/Python/NodeJS S2I builder image." \
      io.openshift.expose-services="8080:http" \
      io.openshift.tags="builder,maven-3,gradle-2.6,java,python-3.6,nodejs" \
      io.openshift.s2i.scripts-url=image:///usr/libexec/s2i

CMD ["/opt/butterfly/bin/start-butterfly.sh"]
