FROM debian:latest

RUN apt-get update

ENV src_path /opt/shiroyuki/papier

RUN apt-get install -yq python3 python3-dev python3-pip ruby ruby-dev rubygems
RUN pip3 install -q gallium docutils flask jinja2
RUN gem install -q github-markup github-markdown

# Temporary measure until the native support for RST+docutils is implemented.
RUN apt-get install -y python-pip
RUN pip install -q docutils

WORKDIR ${src_path}

ADD . ${src_path}
RUN pip3 install .
