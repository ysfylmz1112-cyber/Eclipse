cmake_minimum_required(VERSION 3.25)
project(TutulmaNative VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(TutulmaNative WIN32
    src/main.cpp
    src/Game.cpp
    src/Game.h
    src/RendererBetter.cpp
    src/Renderer.h
    src/Camera.cpp
    src/Camera.h
    src/World.cpp
    src/World.h
)

target_compile_definitions(TutulmaNative PRIVATE
    UNICODE
    _UNICODE
    NOMINMAX
    WIN32_LEAN_AND_MEAN
)

target_link_libraries(TutulmaNative PRIVATE
    d3d11
    dxgi
    d3dcompiler
)

if(MSVC)
    target_compile_options(TutulmaNative PRIVATE /W4 /permissive- /EHsc)
endif()

set_target_properties(TutulmaNative PROPERTIES
    VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
)
