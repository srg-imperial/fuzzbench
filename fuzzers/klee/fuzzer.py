# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Integration code for KLEE"""

import os
import shutil
import subprocess

from fuzzers import utils

# OUT environment variable is the location of build directory (default is /out).


def build():
    """Build fuzzer."""
    cflags = [
        '-O1',
        '-g',
        '-Xclang',
        '-disable-llvm-passes',
        '-D__NO_STRING_INLINES',
        '-D_FORTIFY_SOURCE=0',
        '-U__OPTIMIZE__',
    ]
    utils.append_flags('CFLAGS', cflags)
    utils.append_flags('CXXFLAGS', cflags)

    os.environ['CC'] = 'wllvm'
    os.environ['LLVM_COMPILER'] = 'clang'
    os.environ['LLVM_CC_NAME'] = 'clang-6.0'
    os.environ['LLVM_LINK_NAME'] = 'llvm-link-6.0'
    os.environ['LLVM_CXX_NAME'] = 'clang++-6.0'
    os.environ['CXX'] = 'wllvm++'
    os.environ['FUZZER_LIB'] = '/tmp/KleeFuzzTarget.o'

    
    utils.build_benchmark()

    print('[post_build] Copying klee to $OUT directory')
    # Copy over honggfuzz's main fuzzing binary.
    shutil.copy('/tmp/klee_build60stp_z3/bin/klee', os.environ['OUT'])
    shutil.copy('/tmp/zlib/zlib-1.2.11/libz.bca', os.environ['OUT'])
    shutil.copytree('/tmp/llvm-60-install_O_ND_NA/lib', os.environ['OUT'] + '/lib')
    shutil.copy('/tmp/z3-4.8.4-install/lib/libz3.so', os.environ['OUT'] + '/lib')
    shutil.copytree('/tmp/minisat-install/lib', os.environ['OUT'] + '/lib1')
    shutil.copytree('/tmp/stp-2.3.3-install/lib', os.environ['OUT'] + '/lib2')
    shutil.copytree('/tmp/klee_build60stp_z3/', os.environ['OUT'] + '/klee_build60stp_z3')
    subprocess.call(['ls', os.environ['OUT']])
    subprocess.call(['bash', '-c', 'find $OUT -executable -type f -exec file \'{}\' \; | grep ELF | cut -d: -f1 | xargs -n 1 extract-bc'])


def fuzz(input_corpus, output_corpus, target_binary):
    """Run fuzzer."""
    # Honggfuzz needs the output directory to exist.
    if not os.path.exists(output_corpus):
        os.makedirs(output_corpus)

    print('[run_fuzzer] Running target with honggfuzz')
    print(target_binary)
    os.environ['LD_LIBRARY_PATH']='/out/lib:/out/lib1:/out/lib2'
    shutil.copytree('klee_build60stp_z3', '/tmp/klee_build60stp_z3')
    subprocess.call([
        './klee', '-solver-backend=z3','-libc=uclibc',  '-posix-runtime', '-link-llvm-lib=libz.bca', target_binary + ".bc"
    ])
