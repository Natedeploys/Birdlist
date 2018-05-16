# Dockerfile
# Birdlist Copyright

FROM ubuntu:14.04
MAINTAINER Institute of Neuroinformatics <code@ini.uzh.ch>

# ENV (available to all future RUN, persisted in images)
ENV TERM linux
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive

RUN sed -i 's/^mesg n$/tty -s \&\& mesg n/g' /root/.profile

# Add files from ./docker/_template
ADD _template /

RUN apt-get update
RUN apt-get -y install apache2 libapache2-mod-php5 libapache2-mod-python javascript-common

ADD _build /root/build
RUN run-parts --regex "^[0-9]+\-[0-9a-z-]+\.sh$" /root/build/bin

# USER primus
# WORKDIR /home/primus

# EXPOSE network ports
#EXPOSE 80 443
