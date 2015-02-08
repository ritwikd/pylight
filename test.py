"""
Very simple play with libpulseaudio

pip install libpulseaudio

Help with the API:
http://www.ypass.net/blog/2009/10/pulseaudio-an-async-example-to-get-device-lists/
http://freedesktop.org/software/pulseaudio/doxygen/index.html
"""

import logging

from ctypes import *
from pulseaudio.lib_pulseaudio import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - '
                           '%(message)s'
                    )

ctypes_log = logging.getLogger('ctypes')

ctypes_log.info("Setting up mappings")
###########################
#### CTYPES FUNCTIONS START

PA_SET_STATE_CALLBACK = CFUNCTYPE(None, POINTER(pa_context), c_void_p)

#### CTYPES FUNCTIONS DONE
##########################
ctypes_log.debug("Setup done")


class PulseAudio(object):
    _main_loop = None
    _api = None
    _context = None

    _app_name = None

    logger = logging.getLogger("PulseAudio")

    STATE_MAP = {
        PA_CONTEXT_AUTHORIZING: "authorizing",
        PA_CONTEXT_CONNECTING: "connecting",
        PA_CONTEXT_FAILED: "failed",
        PA_CONTEXT_NOAUTOSPAWN: "no auto spawn",
        PA_CONTEXT_NOFAIL: "no fail",
        PA_CONTEXT_NOFLAGS: "no flags",
        PA_CONTEXT_READY: "ready",
        PA_CONTEXT_SETTING_NAME: "setting name",
        PA_CONTEXT_TERMINATED: "terminated",
        PA_CONTEXT_UNCONNECTED: "unconnected",
    }
    DISCONNECT_STATES = (PA_CONTEXT_FAILED, PA_CONTEXT_TERMINATED)
    DONT_IGNORE_STATES = DISCONNECT_STATES + (PA_CONTEXT_READY,)

    def __init__(self, main_loop=None, api=None, context=None, app_name=None):
        self._main_loop = main_loop
        self._api = api
        self._context = context
        self._app_name = app_name
        self._server = None
        self._state_changed = PA_SET_STATE_CALLBACK(self.state_changed)

    @property
    def main_loop(self):
        if not self._main_loop:
            self._main_loop = pa_mainloop_new()

        return self._main_loop

    @property
    def api(self):
        if not self._api:
            self._api = pa_mainloop_get_api(self.main_loop)

        return self._api

    @property
    def context(self):
        if not self._context:
            if not self._app_name:
                raise NameError("No pa_context or app name to create it with "
                                "has been given")

            self._context = pa_context_new(self.api, self._app_name)
            self._setup_context_events()

        return self._context

    def _setup_context_events(self):
        pa_context_set_state_callback(self.context, self._state_changed, None)

    def connect(self, server=None, flags=0):
        if server is not None:
            server = c_char_p(server)
        
        pa_context_connect(self.context, server, flags, None)
        print self.context.server

    def state_changed(self, context, userdata):
        """
        PulseAudio state has changed (ready, disconnected, etc)
        """
        state = pa_context_get_state(context)

        if state not in self.DONT_IGNORE_STATES:
            self.logger.debug("PA state changed (ignoring): %s",
                              self.STATE_MAP[state]
                              )
            return

        self.logger.debug("PA state changed: %s", self.STATE_MAP[state])

        if state == PA_CONTEXT_READY:
            self.logger.info("READY FOR WORK")
        elif state in self.DISCONNECT_STATES:
            self.logger.error("DISCONNECTED")


pa = PulseAudio(app_name='test')
pa.connect()

while True:
    # Iterate the main loop, block until something happens
    pa_mainloop_iterate(pa.main_loop, c_int(1), None)

    # This would be for non-blocking main loop
    # pa_mainloop_iterate(pa.main_loop, c_int(0), None)
