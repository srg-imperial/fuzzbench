ARG parent_image=gcr.io/fuzzbench/base-builder
FROM $parent_image
RUN true
ENV COVERAGE=0
ENV USE_TCMALLOC=1
ENV BASE=/tmp
ENV LLVM_VERSION=6.0
ENV ENABLE_OPTIMIZED=1
ENV ENABLE_DEBUG=0
ENV DISABLE_ASSERTIONS=1
ENV REQUIRES_RTTI=0
ENV SOLVERS=STP:Z3
ENV GTEST_VERSION=1.7.0
ENV UCLIBC_VERSION=klee_uclibc_v1.2
ENV TCMALLOC_VERSION=2.7
ENV SANITIZER_BUILD=
ENV STP_VERSION=2.3.3
ENV MINISAT_VERSION=master
ENV Z3_VERSION=4.8.4
ENV USE_LIBCXX=0
ENV KLEE_RUNTIME_BUILD="Debug+Asserts"
ENV CXXFLAGS=
LABEL maintainer="KLEE-OSS"


RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install sudo file python3-dateutil && \
    rm -rf /var/lib/apt/lists/* 

RUN git clone https://github.com/klee/klee /tmp/klee_src && \
	/tmp/klee_src/scripts/build/build.sh --debug --install-system-deps klee &&\
	  pip3 install flask wllvm && \
    rm -rf /var/lib/apt/lists/*

ADD KleeFuzzTarget.c /tmp
ENV LLVM_CC_NAME=clang-6.0
ENV LLVM_LINK_NAME=llvm-link-6.0
ENV LLVM_AR_NAME=llvm-ar-6.0
ENV LLVM_COMPILER=clang

RUN cd tmp && wllvm -c KleeFuzzTarget.c  -o KleeFuzzTarget.o

# ===== ZLIB ======
RUN mkdir -p /tmp/zlib && cd /tmp/zlib && \
		wget -nc "https://zlib.net/zlib-1.2.11.tar.gz" && \
    tar -xvf zlib-1.2.11.tar.gz && \
    cd zlib-1.2.11 && \
    CC=wllvm CFLAGS="-fno-builtin-memcpy -DDEBUG -g -O1 -Xclang -disable-llvm-passes -D__NO_STRING_INLINES  -D_FORTIFY_SOURCE=0 -U__OPTIMIZE__"  \
      ./configure --static && \
    make -j5  && extract-bc libz.a
