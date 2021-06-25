#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/aria/catkin_ws1/src/turtlebot3/turtlebot3_teleop"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/aria/catkin_ws1/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/aria/catkin_ws1/install/lib/python3/dist-packages:/home/aria/catkin_ws1/build/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/aria/catkin_ws1/build" \
    "/usr/bin/python3" \
    "/home/aria/catkin_ws1/src/turtlebot3/turtlebot3_teleop/setup.py" \
     \
    build --build-base "/home/aria/catkin_ws1/build/turtlebot3/turtlebot3_teleop" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/home/aria/catkin_ws1/install" --install-scripts="/home/aria/catkin_ws1/install/bin"
