# Install script for directory: /mnt/c/VirLab/SPAdes-3.13.0/ext/src

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/mnt/c/VirLab/SPAdes-3.13.0")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "RelWithAsserts")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/jemalloc/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/nlopt/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/python_libs/joblib2/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/python_libs/joblib3/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/python_libs/pyyaml2/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/python_libs/pyyaml3/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/ConsensusCore/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/bamtools/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/samtools/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/cppformat/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/ssw/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/cityhash/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/getopt_pp/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/llvm/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/htrie/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/bwa/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/gqf/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/edlib/cmake_install.cmake")
  include("/mnt/c/VirLab/SPAdes-3.13.0/build_spades/ext/gfa1/cmake_install.cmake")

endif()

