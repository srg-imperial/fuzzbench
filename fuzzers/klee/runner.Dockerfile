ARG parent_image=gcr.io/fuzzbench/base-builder
FROM $parent_image
RUN apt install -y libtcmalloc-minimal4 libgoogle-perftools-dev libsqlite3-dev
