FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y git libleveldb-dev clang valgrind cmake build-essential

RUN git clone --recursive https://github.com/ethereum/aleth.git /aleth
WORKDIR /aleth

RUN mkdir /aleth/build
RUN cd /aleth/build && cmake .. -DCMAKE_BUILD_TYPE=Debug -DHUNTER_STATUS_DEBUG=ON
RUN cd /aleth/build && make -j5
RUN ln -sr /aleth/build/aleth/aleth /usr/local/bin/aleth
ENTRYPOINT ["/usr/local/bin/aleth"]
