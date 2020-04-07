# Install script for directory: /mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3

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

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xruntimex" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/spades/joblib3" TYPE FILE FILES
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/__init__.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/disk.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/format_stack.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/func_inspect.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/_compat.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/hashing.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/logger.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/memory.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/my_exceptions.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/numpy_pickle.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/parallel.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/testing.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/_memory_helpers.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/_multiprocessing_helpers.py"
    "/mnt/c/VirLab/SPAdes-3.13.0/ext/src/python_libs/joblib3/pool.py"
    )
endif()

