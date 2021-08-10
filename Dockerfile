FROM ubuntu:20.04 as builder

# Locale
ENV LC_ALL C
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# ensure any pipes fail correctly, may impact other things
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# work in an area that will get discarded
WORKDIR /tmp/build

# Prevent interactive options during installs
ENV DEBIAN_FRONTEND=noninteractive

# apt stuff
# hadolint ignore=DL3008
RUN apt-get -yq update \
&& apt-get -yq install --no-install-recommends software-properties-common \
&& add-apt-repository ppa:deadsnakes/ppa \
&& apt-get -yq install --no-install-recommends python3.9 \
&& update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1

# not in final image
# hadolint ignore=DL3008
RUN apt-get -yq update \
&& apt-get -yq install --no-install-recommends \
    build-essential \
    python3.9-dev \
    python3.9-distutils \
    python3.9-venv \
    curl \
    git \
&& curl -sSL --retry 10 https://bootstrap.pypa.io/get-pip.py > get-pip.py \
&& python3.9 get-pip.py

# base environment
ENV OPT /opt/wsi-t78
ENV VIRTUAL_ENV=$OPT/venv
RUN python3.9 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY c_sar_denarius/ c_sar_denarius/
COPY README.md setup.py ./
COPY tests/ tests/
COPY .coveragerc .
# hadolint ignore=DL3013
RUN pip install --no-cache-dir -r tests/requirements-test.txt \
&& python3.9 ./setup.py develop \
&& pip install --no-cache-dir sauth@git+git://github.com/elfgoh/sauth.git@15dbca865332e7b83ccf5d9d227d0321a88132ca \
&& tests/scripts/run_unit_tests.sh

# generate the coverage report (and junit.xml) in for info and later use
RUN mkdir -p /var/www/c_sar_denarius && mv htmlcov /var/www/c_sar_denarius/test-coverage && mv junit.xml /var/www/c_sar_denarius/.

# as we use COPY we can cleanup stuff from the testing layers and actually get a smaller image
RUN pip uninstall -yr tests/requirements-test.txt

# deploy properly and ensure permissions correct
RUN python3.9 ./setup.py install \
&& find $OPT -type d -exec chmod o+rx {} \; \
&& find $OPT -type f -exec chmod o+r {} \;

########################## FINAL IMAGE ##########################
FROM ubuntu:20.04

# Locale
ENV LC_ALL C
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Prevent interactive options during installs
ENV DEBIAN_FRONTEND=noninteractive

# apt stuff
# hadolint ignore=DL3008
RUN apt-get -yq update \
&& apt-get -yq install --no-install-recommends software-properties-common \
&& add-apt-repository ppa:deadsnakes/ppa \
&& apt-get -yq install --no-install-recommends python3.9 \
# make sure all security patches are applied
&& apt-get -yq update && apt-get install -yq --no-install-recommends unattended-upgrades \
&& unattended-upgrade -d -v \
&& apt-get remove -yq unattended-upgrades \
&& apt-get autoremove -yq \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* \
&& update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1

ENV OPT /opt/wsi-t78
ENV VIRTUAL_ENV=$OPT/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=builder $OPT $OPT

RUN adduser --disabled-password --gecos '' ubuntu && chsh -s /bin/bash && mkdir -p /home/ubuntu
USER ubuntu

RUN c-sar-denarius --version

WORKDIR /home/ubuntu

CMD ["/bin/bash"]
