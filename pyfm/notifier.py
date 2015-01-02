# -*- coding: utf-8 -*-
import os
import platform
import subprocess
import tempfile

SYSTEM = platform.system()
PY_MAIN_VERSION = int(platform.python_version_tuple()[0])
PYOBJC = False

if PY_MAIN_VERSION < 3:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

if SYSTEM == 'Darwin':
    try:
        import objc
        from Foundation import NSDate, NSURL, NSUserNotification, NSUserNotificationCenter
        from AppKit import NSImage
        PYOBJC = True

        def swizzle(cls, SEL, func):
            old_IMP = cls.instanceMethodForSelector_(SEL)

            def wrapper(self, *args, **kwargs):
                return func(self, old_IMP, *args, **kwargs)
            new_IMP = objc.selector(wrapper, selector=old_IMP.selector,
                                    signature=old_IMP.signature)
            objc.classAddMethod(cls, SEL, new_IMP)

        def swizzled_bundleIdentifier(self, original):
            # Use iTunes icon for notification
            return 'com.apple.itunes'

    except ImportError:
        PYOBJC = False


class Notifier(object):

    def __init__(self):
        self.tempfile_dir = None
        self.notify = None
        self.bin_path = None
        self.notify_available = True

        if SYSTEM == 'Darwin' and PYOBJC:
            def _pyobjc_notify(message, title=None, subtitle=None, appIcon=None, contentImage=None, open_URL=None, delay=0, sound=False):

                swizzle(objc.lookUpClass('NSBundle'),
                        b'bundleIdentifier',
                        swizzled_bundleIdentifier)
                notification = NSUserNotification.alloc().init()
                notification.setInformativeText_(message)
                if title:
                    notification.setTitle_(title)
                if subtitle:
                    notification.setSubtitle_(subtitle)
                if appIcon:
                    url = NSURL.alloc().initWithString_(appIcon)
                    image = NSImage.alloc().initWithContentsOfURL_(url)
                    notification.set_identityImage_(image)
                if contentImage:
                    url = NSURL.alloc().initWithString_(contentImage)
                    image = NSImage.alloc().initWithContentsOfURL_(url)
                    notification.setContentImage_(image)

                if sound:
                    notification.setSoundName_(
                        "NSUserNotificationDefaultSoundName")
                notification.setDeliveryDate_(
                    NSDate.dateWithTimeInterval_sinceDate_(delay, NSDate.date()))
                NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(
                    notification)

            self.notify = _pyobjc_notify
        else:
            self.notify_available = False

        if SYSTEM == "Linux":
            proc = subprocess.Popen(
                ["which", "notify-send"], stdout=subprocess.PIPE)
            env_bin_path = proc.communicate()[0].strip()
            if env_bin_path and os.path.exists(env_bin_path):
                self.bin_path = os.path.realpath(env_bin_path)
                self.notify = self._notify_send_notify
                self.notify_available = True
            elif os.path.exists("/usr/bin/notify-send"):
                self.bin_path = os.path.join("/usr/bin/", "notify-send")
                self.notify = self._notify_send_notify
                self.notify_available = True
            else:
                self.notify_available = False

        if not self.notify_available:
            print("Notify not available.")
            self.notify = self._notify_not_available

    def _notify_not_available(self, *args, **kwargs):
        pass

    def _notify_send_notify(self, message, title=None, subtitle=None, appIcon=None, contentImage=None, open_URL=None, delay=0, sound=False):
        # Download the image
        self.tempfile_dir = tempfile.mkdtemp()
        subprocess.Popen([
            'curl',
            '-o',
            self.tempfile_dir + '/' + str(title.__hash__()) + '.jpg',
            appIcon],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        import time
        time.sleep(0.5)

        subprocess.Popen([
            self.bin_path,
            '-i',
            self.tempfile_dir + '/' + str(title.__hash__()) + '.jpg',
            title,
            subtitle],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )


Notifier = Notifier()
