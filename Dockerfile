FROM fedora:latest

RUN apt-get update

ENV src_path /opt/shiroyuki/papier

RUN dnf install -y python3 python3-devel python3-pip ruby ruby-devel rubygems
RUN pip3 install -q gallium imagination docutils flask jinja2
RUN gem install -q github-markup github-markdown

# Temporary measure until the native support for RST+docutils is implemented.
RUN dnf install -y python-pip
RUN pip install -q docutils

WORKDIR ${src_path}

ADD . ${src_path}
RUN pip3 install .
